#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TabFM REGRESYON agirligini SURDURULEBILIR sekilde indirir (6,29 GB).

xet protokolu tikandi (43 MB'da kesintili, ~29 KB/sn). Bu betik duz HTTPS
Range istegi kullanir: yarim kalirsa kaldigi yerden devam eder, ilerlemeyi
dosyaya yazar. Tekrar tekrar cagrilabilir.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, time, urllib.request, json

HERE = os.path.dirname(os.path.abspath(__file__))
HEDEF = os.path.join(HERE, "agirlik", "regression")
os.makedirs(HEDEF, exist_ok=True)
BASE = "https://huggingface.co/google/tabfm-1.0.0-pytorch/resolve/main/regression/"
KUCUK = ["config.json"]
BUYUK = "model.safetensors"


def kucuk_indir(ad):
    p = os.path.join(HEDEF, ad)
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return
    with urllib.request.urlopen(BASE + ad, timeout=120) as r, open(p, "wb") as f:
        f.write(r.read())
    print("  indi: %s (%d bayt)" % (ad, os.path.getsize(p)))


def boyut():
    r = urllib.request.urlopen(urllib.request.Request(BASE + BUYUK, method="HEAD"), timeout=120)
    return int(r.headers["Content-Length"])


def surdur(toplam):
    p = os.path.join(HEDEF, BUYUK)
    var = os.path.getsize(p) if os.path.exists(p) else 0
    if var >= toplam:
        print("  TAMAM: %s zaten tam (%.2f GB)" % (BUYUK, var / 2**30))
        return True
    req = urllib.request.Request(BASE + BUYUK, headers={"Range": "bytes=%d-" % var})
    t0, bas = time.time(), var
    with urllib.request.urlopen(req, timeout=180) as r, open(p, "ab") as f:
        son = time.time()
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
            var += len(b)
            if time.time() - son >= 30:
                son = time.time()
                dt = son - t0
                hiz = (var - bas) / dt
                kalan = (toplam - var) / hiz if hiz > 0 else 0
                print("   %6.2f / %.2f GB  (%%%4.1f)  %5.0f KB/sn  kalan ~%.1f saat"
                      % (var / 2**30, toplam / 2**30, 100 * var / toplam,
                         hiz / 1024, kalan / 3600), flush=True)
    return os.path.getsize(p) >= toplam


for a in KUCUK:
    try:
        kucuk_indir(a)
    except Exception as e:
        print("  uyari %s: %s" % (a, e))

TOP = boyut()
print("hedef: %s  %.2f GB" % (BUYUK, TOP / 2**30), flush=True)
for deneme in range(1, 200):
    try:
        if surdur(TOP):
            print("INDIRME TAMAM -> %s" % HEDEF)
            break
    except Exception as e:
        v = os.path.join(HEDEF, BUYUK)
        n = os.path.getsize(v) if os.path.exists(v) else 0
        print("  kopma #%d (%.2f GB'de): %s -> 10 sn sonra devam"
              % (deneme, n / 2**30, str(e)[:60]), flush=True)
        time.sleep(10)
