# -*- coding: utf-8 -*-
"""ADIM 3 — FONLAMA ZAMANLAMASI: kenari odemeden yakalanabilir mi?

BULGU (adim 2): kenar ve fonlama AYNI olgu. En derin dilimde brut +0,6044,
fonlama -0,4479. Fonlama 8 SAATTE BIR kesiliyor; brut kenar SUREKLI.
Ortalama tutma 6 saat -> bircok islem kesintiye yakalanmayabilir.

⚠️ FAZ KILIDI: SEYRELT=24 ile "fonlamaya kalan saat" SEMBOL BASINA SABIT olur
(24 ve 8'in ortak boleni var). CLAUDE.md'de kayitli: bir kova orneklemin %62'sini
tasimisti. COZUM: her ornege BAGIMSIZ rastgele kaydirma. Dagilim raporlanir.

DEGISKEN: girişte fonlama kesintisine KALAN SAAT (0-7). Bu GIRISTE BILINIR,
sonuctan turemez — dolayisiyla tutma-suresi totolojisi YOK.

ESIK TARAMASI YOK: sekiz kova, fonlama periyodunun kendi yapisi.
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

HEDEF, UFUK = 10.0, 72
MALIYET_GERCEK = 0.1726
random.seed(41)
K = collections.defaultdict(lambda: {"ham": [], "fon": [], "ts": [], "kesinti": []})

for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    try: b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if len(b) < ir.ISINMA + UFUK + 50: continue
    fp = os.path.join(ir.FUND, fn); fr = []
    if os.path.exists(fp):
        try: fr = json.load(open(fp, encoding="utf-8"))
        except Exception: fr = []
    if not fr: continue
    ft = [x["t"] for x in fr]
    atrs = ir.atr_serisi(b)
    i = ir.ISINMA
    while i < len(b) - UFUK - 2:
        # HER ORNEGE BAGIMSIZ kaydirma (faz kilidini kirar)
        i += 24
        j0 = i + random.randint(-11, 12)
        if j0 < ir.ISINMA or j0 >= len(b) - UFUK - 2: continue
        x = b[j0]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or j0 < 24: continue
        if (x["c"]/b[j0-24]["c"]-1)*100 >= ir.PUMP: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0 or fr[k]["r"]*100 > ir.FUND_ESIK: continue     # A kapisi (kenarin kaynagi)
        gi = j0+1
        if not atrs[j0] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        stop = ir.stop_hesapla(b, j0, ref, atrs[j0]); sp = (stop-ref)/ref*100
        if sp <= 0 or sp < ir.ASGARI_STOP: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        # sonraki fonlama kesintisine KALAN SAAT (giriste bilinir)
        nx = bisect.bisect_right(ft, b[gi]["t"])
        if nx >= len(ft): continue
        kalan = int(round((ft[nx]-b[gi]["t"])/3600000.0))
        if not (0 <= kalan <= 8): continue
        hed = ref*(1-HEDEF/100)
        cj = hm = None
        for j in range(gi, son):
            if b[j]["h"] >= stop: cj, hm = j, -sp; break
            if b[j]["l"] <= hed: cj, hm = j, HEDEF; break
        if cj is None: cj = son-1; hm = (ref-b[son-1]["c"])/ref*100
        f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
        kes = bisect.bisect_right(ft, b[cj]["t"]) - bisect.bisect_right(ft, b[gi]["t"])
        d = K[min(kalan, 7)]
        d["ham"].append(hm); d["fon"].append(f); d["ts"].append(b[gi]["t"]); d["kesinti"].append(kes)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

top = sum(len(K[k]["ham"]) for k in K)
print("ADIM 3 — FONLAMA ZAMANLAMASI (A kapisi, 2 yil, N=%d)" % top)
print("=" * 100)
print("FAZ KONTROLU — kovalar dengeli mi? (SEYRELT=24 faz kilidi kirildi mi)")
for k in sorted(K):
    n = len(K[k]["ham"])
    print("   kalan %d saat: N=%6d  (%%%.1f)%s" % (k, n, 100*n/top,
          "   <-- FAZ KILIDI VAR" if 100*n/top > 25 else ""))
print()
print("%-14s %8s %10s %10s %10s %11s %10s" %
      ("kalan saat", "N", "BRUT", "fonlama", "NET", "ay-kumeli t", "kesinti ort"))
for k in sorted(K):
    d = K[k]
    n = len(d["ham"])
    if n < 200: continue
    net = [h - MALIYET_GERCEK + f for h, f in zip(d["ham"], d["fon"])]
    a = collections.defaultdict(list)
    for v, t in zip(net, d["ts"]): a[ay(t)].append(v)
    ok = [m for m in a if len(a[m]) >= 20]
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5 if len(ms) > 2 else 0
    print("%-14d %8d %+10.4f %+10.4f %+10.4f %+11.2f %10.2f"
          % (k, n, stx.mean(d["ham"]), stx.mean(d["fon"]), stx.mean(net),
             (stx.mean(ms)/se if se else 0), stx.mean(d["kesinti"])))
print()
print("KESINTI SAYISINA gore (giriste BILINMEZ — tarif amacli, kural DEGIL):")
kk = collections.defaultdict(lambda: {"ham": [], "fon": []})
for k in K:
    for h, f, ke in zip(K[k]["ham"], K[k]["fon"], K[k]["kesinti"]):
        kk[min(ke, 4)]["ham"].append(h); kk[min(ke, 4)]["fon"].append(f)
print("%-14s %8s %10s %10s %10s" % ("kesinti", "N", "BRUT", "fonlama", "NET"))
for k in sorted(kk):
    d = kk[k]
    if len(d["ham"]) < 200: continue
    print("%-14d %8d %+10.4f %+10.4f %+10.4f"
          % (k, len(d["ham"]), stx.mean(d["ham"]), stx.mean(d["fon"]),
             stx.mean([h-MALIYET_GERCEK+f for h, f in zip(d["ham"], d["fon"])])))
