#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TERS KAPI — fonlamasi POZITIF olani shortlamak.

============================ ON-KAYIT (kosturulmadan ONCE) ============================
NEREDEN CIKTI: O_kapi_kontrol.py fonlama dilimlerinde en ust dilim
  (funding +1,00 .. +43,60 %/8s) NET +1,8413 verdi. Bot TAM TERSINI yapiyor
  (funding <= -0,05 -> SHORT), ve o kapi kontrolunden -0,0795 KOTU cikti.

⚠️ BU BIR DILIM TARAMASINDAN CIKTI. Sekiz dilime bakildi, en iyisi secildi.
  CLAUDE.md: "en iyi hucre secilmez". Bu yuzden burada ON-KAYITLA sinaniyor.

MEKANIZMA (a priori, sonuctan turemiyor): pozitif fonlama = LONG'lar kalabalik.
  Onlari shortlamak (a) kalabalik pozisyonun cozulmesine oynar (b) fonlamayi
  TAHSIL EDER. Botun mevcut kapisi tam tersi: kalabalik short'a katilir ve oder.

KOLLAR (esik SECILMEZ — botun kendi esiginin AYNASI):
  MEVCUT : funding <= -0,05   (botun bugunku kapisi)
  TERS    : funding >= +0,05  (aynasi)
  KONTROL : arada (-0,05 < f < +0,05)

GECME OLCUTU — TERS kapi icin dordu de gerekli:
  1. NET, MEVCUT kapidan yuksek
  2. NET, KONTROL kumesinden de yuksek
  3. AY-KUMELI t > +2,0
  4. IKI ZAMAN YARISINDA da yuksek  ·  uc rejimde ters isaret yok

BEKLENTI (sonuc gorulmeden): KARARSIZ, gecmeye yakin.
  Lehte: mekanizma yorumlanabilir ve fonlama isareti LEHE doner (odeme -> tahsil);
    bugunku kontrol grubu zaten fonlama tahsil ederek kapiyi yeniyordu.
  Aleyhte: dilim taramasindan cikti; bu oturumda 8 iz tam bu asamada coktu;
    ve pozitif-fonlama coinleri PUMP olabilir -> short squeeze riski.
=======================================================================================
"""
import json, os, sys, collections, random, statistics as stx, bisect, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir

HEDEF, UFUK, MAL = 10.0, 72, 0.1726
ESIK = 0.05
random.seed(41)
K = collections.defaultdict(lambda: {"ham": [], "fon": [], "net": [], "ts": [], "rej": []})
rej = ir.btc_rejim()

for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    fp = os.path.join(ir.FUND, fn)
    if not os.path.exists(fp): continue
    try:
        fr = json.load(open(fp, encoding="utf-8"))
        b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if not fr or len(b) < ir.ISINMA + UFUK + 50: continue
    ft = [x["t"] for x in fr]
    atrs = ir.atr_serisi(b)
    faz = random.randint(0, 23)
    for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
        x = b[i]
        if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
        if (x["c"]/b[i-24]["c"]-1)*100 >= ir.PUMP: continue
        k = bisect.bisect_right(ft, x["t"]) - 1
        if k < 0: continue
        o = fr[k]["r"]*100
        kume = "MEVCUT (f<=-0,05)" if o <= -ESIK else ("TERS (f>=+0,05)" if o >= ESIK else "KONTROL (arasi)")
        gi = i+1
        if not atrs[i] or gi >= len(b): continue
        ref = b[gi]["o"]
        if ref <= 0: continue
        stop = ir.stop_hesapla(b, i, ref, atrs[i]); sp = (stop-ref)/ref*100
        if sp <= 0 or sp < ir.ASGARI_STOP: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        hed = ref*(1-HEDEF/100)
        cj = hm = None
        for j in range(gi, son):
            if b[j]["h"] >= stop: cj, hm = j, -sp; break
            if b[j]["l"] <= hed: cj, hm = j, HEDEF; break
        if cj is None: cj = son-1; hm = (ref-b[son-1]["c"])/ref*100
        f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
        d = K[kume]
        d["ham"].append(hm); d["fon"].append(f); d["net"].append(hm-MAL+f)
        d["ts"].append(b[gi]["t"]); d["rej"].append(rej.get(b[gi]["t"]//3600000, "NOTR"))

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

def kumeli(v, ts):
    a = collections.defaultdict(list)
    for z, t in zip(v, ts): a[ay(t)].append(z)
    ok = [m for m in a if len(a[m]) >= 20]
    if len(ok) < 3: return None
    ms = [stx.mean(a[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5
    return stx.mean(ms), (stx.mean(ms)/se if se else 0), len(ok), sum(1 for z in ms if z > 0)

print("TERS KAPI — on-kayitli sinav (SHORT, ayni mekanik, 2 yil)")
print("=" * 110)
print("%-20s %8s %10s %10s %10s %11s %9s %10s"
      % ("kume", "N", "BRUT", "fonlama", "NET", "ay-kumeli t", "poz ay", "medyan"))
S = {}
for kume in ("MEVCUT (f<=-0,05)", "KONTROL (arasi)", "TERS (f>=+0,05)"):
    d = K.get(kume)
    if not d or len(d["net"]) < 500: continue
    kn = kumeli(d["net"], d["ts"])
    S[kume] = d
    print("%-20s %8d %+10.4f %+10.4f %+10.4f %+11.2f %6d/%-3d %+10.4f"
          % (kume, len(d["net"]), stx.mean(d["ham"]), stx.mean(d["fon"]),
             stx.mean(d["net"]), kn[1] if kn else 0, kn[3] if kn else 0,
             kn[2] if kn else 0, stx.median(d["net"])))

t = S.get("TERS (f>=+0,05)")
if t:
    print("\nOLCUT KONTROLU")
    for ad in ("MEVCUT (f<=-0,05)", "KONTROL (arasi)"):
        if ad in S:
            f = stx.mean(t["net"]) - stx.mean(S[ad]["net"])
            print("  1-2. TERS eksi %-20s : %+.4f  %s" % (ad, f, "OK" if f > 0 else "DUSTU"))
    kn = kumeli(t["net"], t["ts"])
    print("  3.   ay-kumeli t = %+.2f  %s" % (kn[1], "OK" if kn[1] > 2.0 else "DUSTU"))
    srt = sorted(zip(t["net"], t["ts"]), key=lambda z: z[1]); y = len(srt)//2
    A = stx.mean([z[0] for z in srt[:y]]); B = stx.mean([z[0] for z in srt[y:]])
    print("  4a.  A yarisi %+.4f · B yarisi %+.4f  %s" % (A, B, "OK" if A > 0 and B > 0 else "DUSTU"))
    print("  4b.  rejim:", end=" ")
    for r in ("AYI", "NOTR", "BOGA"):
        v = [z for z, rr in zip(t["net"], t["rej"]) if rr == r]
        if len(v) >= 50: print("%s %+.4f " % (r, stx.mean(v)), end="")
    print()
