# -*- coding: utf-8 -*-
"""TimesFM kapsama testi — VERI TOPLAMA (analiz 02'de).
On-kayit: scratchpad/tfm/ON_KAYIT_kapsama.md   SALT OKUMA, bota yazmaz."""
import json, glob, os, random, time, bisect, datetime
import numpy as np, timesfm

PROJE = r"c:\Users\alper\Desktop\kripto trade"
KL = os.path.join(PROJE, "scratchpad", "klines_1h_uzun")
CIK = os.path.join(PROJE, "scratchpad", "tfm", "ham_sonuc.json")

CTX, HOR = 512, 24
UFUK = (4, 24)
KESIM = 1756684800000            # 2025-09-01 — TimesFM 2.5 yayin sonrasi
HEDEF_N = 8000
YIGIN = 64

def wilder_atr(b, i, n=14):
    """Wilder ATR — olcucu.py:98 ile ayni yontem."""
    tr = []
    for k in range(i-n, i):
        h, l, pc = b[k]["h"], b[k]["l"], b[k-1]["c"]
        tr.append(max(h-l, abs(h-pc), abs(l-pc)))
    if not tr: return None
    a = tr[0]
    for x in tr[1:]:
        a = (a*(n-1) + x)/n
    return a

# ---- BTC drawdown rejimi (16_rejim_kosullu ile ayni tanim)
rej_t, rej_v = [], []
byol = os.path.join(KL, "BTC.json")
if os.path.exists(byol):
    z = 0.0
    for x in json.load(open(byol, encoding="utf-8")):
        z = max(z, x["h"])
        dd = (x["c"]-z)/z*100 if z else 0.0
        rej_t.append(x["t"])
        rej_v.append("ATH_BOLGESI" if dd > -10 else "DUZELTME" if dd > -30 else "DERIN_AYI")
def rejim(t):
    if not rej_t: return "?"
    i = bisect.bisect_right(rej_t, t)-1
    return rej_v[i] if i >= 0 else "?"

print("model yukleniyor...", flush=True)
t0 = time.time()
m = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
m.compile(timesfm.ForecastConfig(max_context=CTX, max_horizon=HOR,
          normalize_inputs=True, use_continuous_quantile_head=True,
          force_flip_invariance=True, infer_is_positive=True, fix_quantile_crossing=True))
print("yuklendi %.0f sn" % (time.time()-t0), flush=True)

# ---- aday noktalari topla
print("aday noktalar taraniyor...", flush=True)
adaylar = []
for f in sorted(glob.glob(os.path.join(KL, "*.json"))):
    sym = os.path.basename(f)[:-5]
    try: b = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    if len(b) < CTX + HOR + 20: continue
    ilk = bisect.bisect_left([x["t"] for x in b], KESIM)
    bas = max(ilk, CTX + 15)
    for i in range(bas, len(b)-HOR):
        adaylar.append((sym, i))
print("aday nokta: %s" % format(len(adaylar), ","), flush=True)

random.seed(41)
sec = random.sample(adaylar, min(HEDEF_N, len(adaylar)))
sec.sort()                                   # sembol sembol okumak icin
print("secilen: %s" % format(len(sec), ","), flush=True)

sonuc = []
yig_g, yig_m = [], []
t0 = time.time()
akt_sym, b = None, None

def bosalt():
    if not yig_g: return
    nokta, kuantil = m.forecast(horizon=HOR, inputs=yig_g)
    for j, meta in enumerate(yig_m):
        d = dict(meta)
        for h in UFUK:
            d["q%d" % h] = [float(v) for v in kuantil[j][h-1]]
            d["p%d" % h] = float(nokta[j][h-1])
        sonuc.append(d)
    yig_g.clear(); yig_m.clear()

for sym, i in sec:
    if sym != akt_sym:
        b = json.load(open(os.path.join(KL, sym + ".json"), encoding="utf-8"))
        akt_sym = sym
    c = [x["c"] for x in b]
    if c[i] <= 0 or min(c[i-CTX:i]) <= 0: continue
    atr = wilder_atr(b, i)
    if not atr or atr <= 0: continue
    meta = {"sym": sym, "t": b[i]["t"], "son": float(c[i]), "atr": float(atr),
            "rejim": rejim(b[i]["t"]),
            "gun": datetime.datetime.utcfromtimestamp(b[i]["t"]/1000).strftime("%Y-%m-%d")}
    for h in UFUK:
        meta["ger%d" % h] = float(c[i+h])
    yig_g.append(np.array(c[i-CTX:i], dtype=np.float32))
    yig_m.append(meta)
    if len(yig_g) >= YIGIN:
        bosalt()
        if len(sonuc) % 1280 == 0:
            gec = time.time()-t0
            print("  %s / %s   %.0f sn   kalan ~%.0f dk"
                  % (format(len(sonuc), ","), format(len(sec), ","), gec,
                     (len(sec)-len(sonuc))*gec/max(len(sonuc), 1)/60), flush=True)
bosalt()

json.dump(sonuc, open(CIK, "w"))
print("\nTOPLANDI: %s nokta  ->  %s" % (format(len(sonuc), ","), CIK))
print("toplam sure: %.1f dakika" % ((time.time()-t0)/60))
