#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IZ J — SORUN ERKEN GURULTU MU? Ayirici sinav.

============================ ON-KAYIT (kosturulmadan ONCE) ============================
TESHIS: stop 1,50 x ATR uzakta; 72 saatlik ufkun dogal menzili 8,5 x ATR.
  Yani UC farkli zaman olcegi ayni islemin icinde:
     stop   1,5 x ATR   (~2 saatlik olcek)
     hedef  %10         (~4-5 x ATR)
     ufuk   72 saat     (~8,5 x ATR)
  Islemlerin %15,1'i kazanacakken stopla oluyor; bunlarin %64'u ILK 6 SAATTE.

IKI RAKIP ACIKLAMA — bu sinav onlari AYIRIR:
  (E) ERKEN GURULTU : sorun ilk saatlerdeki dalgalanma. Yalniz BASTA yer acmak yeter.
  (O) OLCEK UYUMSUZLUGU : sorun stop ile ufkun farkli olcekte olmasi. Ya stop
      butun boyunca genislemeli, ya ufuk stopa uydurulmali.

KOLLAR (hepsi GEVSETME — 28/28 sikilastirma sicili buraya uygulanmaz):
  K0 KONTROL   : bugunku hal (A-stop sabit · %10 hedef · 72s)
  K1 ERKEN-GEN : stop ilk 6 saat x2, sonra normal      <- (E) dogruysa BU kazanir
  K2 SQRT-GEN  : stop = A-stop x sqrt(1 + t/6)          <- (O) dogruysa BU kazanir
  K3 UFUK-6    : stop ayni, ufuk 72s -> 6s              <- (O)'nun diger yuzu
  K4 UFUK-12   : stop ayni, ufuk 72s -> 12s

AYIRICI OKUMA (sonuc gorulmeden yazildi):
  K1 >> K0 ve K1 ~ K2  -> sorun ERKEN GURULTU (ucuz cozum: sadece basta yer ac)
  K2 >> K1             -> sorun OLCEK; stop butun boyunca genislemeli
  K3/K4 >> K0          -> sorun ufkun uzunlugu; kisa tutmak yeter
  hicbiri > K0         -> teshis YANLIS, stop pahali degil

GECME OLCUTU (bir kol icin dordu de gerekli):
  1. islem basina net getiri K0'dan yuksek
  2. IKI ZAMAN YARISINDA da yuksek
  3. AY-KUMELI eslesmis fark t > +2,0
  4. uc rejimde ters isaret yok

BEKLENTI (sonuc gorulmeden): K3/K4'un kazanmasini bekliyorum, K1/K2'nin degil.
  Gerekce: canli defterde "1 saatte kosulsuz kapat" en iyi zaman-cikisiydi; ve
  hedef %10 iken stop 1,5 ATR ise 72 saat beklemek hedefe degil stopa calisiyor.
  Aleyhte: bu oturumda 5 iz tam bu asamada coktu.

ESIK TARAMASI YOK — 6 saat teshisten (yanlis stoplarin %64'u ilk 6 saatte),
x2 ve sqrt() ise keyfi degil olcek argumanindan geliyor.
=======================================================================================
"""
import json, os, sys, collections, random, statistics as stx, datetime, bisect, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import olcum_ortak as oo
import ileri_rr as ir

HEDEF, UFUK = 10.0, 72
ERKEN_SA, ERKEN_KAT = 6, 2.0
random.seed(41)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

def kostur():
    S = collections.defaultdict(list)
    for fn in sorted(os.listdir(ir.KLINE)):
        if not fn.endswith(".json"): continue
        sym = fn[:-5]
        try: b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
        except Exception: continue
        if len(b) < ir.ISINMA + UFUK + 50: continue
        fp = os.path.join(ir.FUND, fn); fr = []
        if os.path.exists(fp):
            try: fr = json.load(open(fp, encoding="utf-8"))
            except Exception: fr = []
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b); ma50 = ir.ma_serisi(b, 50)
        faz = random.randint(0, 23)
        for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
            if (x["c"]/b[i-24]["c"]-1)*100 >= ir.PUMP: continue
            gecti = False
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                if k >= 0 and fr[k]["r"]*100 <= ir.FUND_ESIK: gecti = True
            if not gecti and ma50[i] and ma50[i] > 0 and x["c"] <= ir.UCUZ_FIYAT:
                if (x["c"]/ma50[i]-1)*100 >= ir.MA50_MESAFE: gecti = True
            if not gecti: continue
            gi = i+1
            if not atrs[i] or gi >= len(b): continue
            ref = b[gi]["o"]
            if ref <= 0: continue
            stop0 = ir.stop_hesapla(b, i, ref, atrs[i])
            sp0 = (stop0-ref)/ref*100
            if sp0 <= 0 or sp0 < ir.ASGARI_STOP: continue
            son = min(gi+UFUK, len(b))
            if son-gi < 4: continue
            hed = ref*(1-HEDEF/100)
            t0 = b[gi]["t"]
            anahtar = (sym, t0)

            def oyna(ad, stop_fn, ufuk):
                bit = min(gi+ufuk, len(b))
                cj = hm = None
                for j in range(gi, bit):
                    t = j-gi
                    st = stop_fn(t)
                    if b[j]["h"] >= st:
                        cj, hm = j, -(st-ref)/ref*100; break
                    if b[j]["l"] <= hed:
                        cj, hm = j, HEDEF; break
                if cj is None:
                    cj = bit-1; hm = (ref-b[bit-1]["c"])/ref*100
                f = ir.fonlama_pct(ft, fr, t0, b[cj]["t"])
                S[ad].append((hm-oo.MALIYET+f, anahtar))

            oyna("K0", lambda t: stop0, UFUK)
            oyna("K1", lambda t: ref + (stop0-ref)*(ERKEN_KAT if t < ERKEN_SA else 1.0), UFUK)
            oyna("K2", lambda t: ref + (stop0-ref)*math.sqrt(1.0 + t/6.0), UFUK)
            oyna("K3", lambda t: stop0, 6)
            oyna("K4", lambda t: stop0, 12)
    return S

S = kostur()
kon = {k: v for v, k in S["K0"]}
rejim = ir.btc_rejim()
print("IZ J — SORUN ERKEN GURULTU MU? (on-kayit dosyada, N=%d)" % len(S["K0"]))
print("=" * 96)
ADLAR = [("K0", "KONTROL (bugunku)"), ("K1", "ERKEN-GEN (ilk 6s x2)"),
         ("K2", "SQRT-GEN (sqrt(1+t/6))"), ("K3", "UFUK 6 saat"), ("K4", "UFUK 12 saat")]
print("%-24s %9s %11s %11s %9s %9s" % ("kol", "islem ort", "eslesmis f.", "ay-kumeli t", "A yari", "B yari"))
for k, ad in ADLAR:
    v = [z[0] for z in S[k]]
    if k == "K0":
        print("%-24s %+9.3f %11s %11s %9s %9s" % (ad, stx.mean(v), "-", "-", "-", "-")); continue
    esles = [(x - kon[a], a) for x, a in S[k] if a in kon]
    f = [z[0] for z in esles]
    af = collections.defaultdict(list)
    for d, a in esles: af[ay(a[1])].append(d)
    ok = [m for m in af if len(af[m]) >= 20]
    ms = [stx.mean(af[m]) for m in ok]
    se = stx.stdev(ms)/len(ms)**0.5 if len(ms) > 2 else 0
    srt = sorted(esles, key=lambda z: z[1][1]); y = len(srt)//2
    A = stx.mean([z[0] for z in srt[:y]]); B = stx.mean([z[0] for z in srt[y:]])
    print("%-24s %+9.3f %+11.4f %+11.2f %+9.4f %+9.4f"
          % (ad, stx.mean(v), stx.mean(f), (stx.mean(ms)/se if se else 0), A, B))

print("\nOLCUT 4 — REJIM (eslesmis fark):")
print("%-24s %10s %10s %10s" % ("kol", "AYI", "NOTR", "BOGA"))
for k, ad in ADLAR[1:]:
    esles = [(x - kon[a], a) for x, a in S[k] if a in kon]
    sat = []
    for r in ("AYI", "NOTR", "BOGA"):
        d = [z[0] for z in esles if rejim.get(z[1][1]//3600000, "NOTR") == r]
        sat.append(stx.mean(d) if len(d) >= 50 else None)
    print("%-24s %10s %10s %10s" % (ad, *["%+.4f" % s if s is not None else "-" for s in sat]))
