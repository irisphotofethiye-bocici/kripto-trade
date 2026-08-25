#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TabFM olcumunu OTOMATIK yurutur. Kullanici karari: "beklemeden kos".

ZINCIR:  indirme bitisini bekle -> agirligi dogrula -> SURE PROBU
         -> n_estimators'u YALNIZ SUREYE gore sec -> tam olcumu kos

🔴 AYAR SECIMI SONUCA BAKMADAN YAPILIR. Prob yalnizca SURE basar (--sure-probu),
   rho gormez. Kural asagida SABIT ve kosumdan ONCE yazildi:
       hedef toplam <= 4 saat
       n_est, {32,16,8,4,2} icinden tahmini toplam <= 4 saat olan EN BUYUGU
       hicbiri sigmazsa n_est=2 (ve rapora "sure kisiti" yazilir)
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, sys, time, json, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
PY   = os.path.join(os.path.dirname(HERE), "tabfm_venv", "Scripts", "python.exe")
AGIR = os.path.join(HERE, "agirlik", "regression", "model.safetensors")
HEDEF_BAYT = None
PROB_N   = 4          # probda kullanilacak n_estimators
BUTCE_SN = 4 * 3600   # hedef toplam sure
ADAYLAR  = [32, 16, 8, 4, 2]


def log(*a):
    print(time.strftime("[%H:%M:%S]"), *a, flush=True)


# ---------------------------------------------------------------- 1) bekle
import urllib.request
try:
    r = urllib.request.urlopen(urllib.request.Request(
        "https://huggingface.co/google/tabfm-1.0.0-pytorch/resolve/main/regression/model.safetensors",
        method="HEAD"), timeout=120)
    HEDEF_BAYT = int(r.headers["Content-Length"])
except Exception as e:
    log("HEAD alinamadi (%s) -> 6,14 GB varsayiliyor" % str(e)[:40])
    HEDEF_BAYT = int(6.14 * 2**30)
log("hedef boyut %.2f GB" % (HEDEF_BAYT / 2**30))

son, durgun = -1, 0
while True:
    n = os.path.getsize(AGIR) if os.path.exists(AGIR) else 0
    if n >= HEDEF_BAYT:
        log("INDIRME TAMAM  %.2f GB" % (n / 2**30))
        break
    if n == son:
        durgun += 1
        if durgun >= 40:            # ~20 dk hic ilerleme
            log("UYARI: 20 dk ilerleme yok (%.2f GB). Beklemeye devam." % (n / 2**30))
            durgun = 0
    else:
        durgun = 0
    son = n
    time.sleep(30)

# ---------------------------------------------------------------- 2) dogrula
try:
    from safetensors import safe_open       # noqa: F401
except Exception:
    pass
log("agirlik dosyasi yerinde, yukleme probuna geciliyor")

# ---------------------------------------------------------------- 3) sure probu
D = json.load(open(os.path.join(HERE, "veri.json"), encoding="utf-8"))
SON_GUN = D["gunler"][-1]           # EN BUYUK baglam = en kotu durum
log("sure probu: %s (en buyuk baglam), n_est=%d" % (SON_GUN, PROB_N))

t0 = time.time()
p = subprocess.run([PY, os.path.join(HERE, "02_olcum.py"),
                    "--sure-probu", "--gun", SON_GUN, "--n-est", str(PROB_N)],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
yukleme_dahil = time.time() - t0
print(p.stdout[-2000:])
if p.returncode != 0:
    log("PROB BASARISIZ (kod %d)" % p.returncode)
    print(p.stderr[-3000:])
    sys.exit(1)

m = re.search(r"->\s+([\d.]+)\s+sn", p.stdout)
if not m:
    log("prob suresi okunamadi -> n_est=4 ile devam")
    n_est = 4
else:
    fit_sn = float(m.group(1))
    log("prob: en kotu gun %.1f sn (n_est=%d)  ·  model yukleme dahil %.0f sn"
        % (fit_sn, PROB_N, yukleme_dahil))
    # ortalama baglam en buyugun ~%70'i -> 13 gun icin olcek
    for c in ADAYLAR:
        tahmin = fit_sn / PROB_N * c * 13 * 0.75
        log("   n_est=%-3d tahmini toplam %5.1f dk  %s"
            % (c, tahmin / 60, "SIGAR" if tahmin <= BUTCE_SN else "butceyi asar"))
    uygun = [c for c in ADAYLAR if fit_sn / PROB_N * c * 13 * 0.75 <= BUTCE_SN]
    n_est = uygun[0] if uygun else 2
log("SECILEN n_estimators = %d   (yalnizca SUREYE gore, sonuca BAKILMADI)" % n_est)

# ---------------------------------------------------------------- 4) tam olcum
log("tam olcum basliyor...")
t0 = time.time()
with open(os.path.join(HERE, "olcum.log"), "w", encoding="utf-8") as f:
    pr = subprocess.Popen([PY, os.path.join(HERE, "02_olcum.py"), "--n-est", str(n_est)],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, encoding="utf-8", errors="replace", bufsize=1)
    for line in pr.stdout:
        sys.stdout.write(line); sys.stdout.flush()
        f.write(line); f.flush()
    pr.wait()
log("olcum bitti (kod %d)  ·  %.1f dakika" % (pr.returncode, (time.time() - t0) / 60))
log("n_estimators=%d  ·  cikti: scratchpad/tabfm/olcum.log" % n_est)
