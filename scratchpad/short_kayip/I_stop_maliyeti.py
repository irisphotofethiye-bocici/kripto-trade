# -*- coding: utf-8 -*-
"""IZ I — STOPU NEDEN BU KADAR PAHALIYA ODUYORUZ?

Gozlem: stop-olma orani her hucrede %67-79. Ve ham getiri mekaniklinin 3 KATI.
SORU: stop nerede duruyor, ve stop olan islemlerin kaci ASLINDA kazanacakti?

OLCUM (SHORT, botun kendi kapilari, 2 yil):
  1. stop mesafesi ATR CINSINDEN kac birim
  2. stop olan islemler: stop OLMASAYDI ufuk icinde hedefe varir miydi?
     -> "YANLIS STOP" orani = stopun gercek maliyeti
  3. yanlis stoplarin zaman profili: stop ne kadar erken geliyor
"""
import json, os, sys, random, statistics as stx
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ileri_rr as ir
import bisect

HEDEF, UFUK = 10.0, 72
random.seed(41)
d = {"n": 0, "stop": 0, "hedef": 0, "sure": 0,
     "atr_birim": [], "sp": [], "stop_bar": [],
     "yanlis": 0, "yanlis_bar": [], "dogru": 0}

for fn in sorted(os.listdir(ir.KLINE)):
    if not fn.endswith(".json"): continue
    try: b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
    except Exception: continue
    if len(b) < ir.ISINMA + UFUK + 50: continue
    fp = os.path.join(ir.FUND, fn); fr = []
    if os.path.exists(fp):
        try: fr = json.load(open(fp, encoding="utf-8"))
        except Exception: fr = []
    ft = [x["t"] for x in fr]
    atrs = ir.atr_serisi(b)
    ma50 = ir.ma_serisi(b, 50)
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
        stop = ir.stop_hesapla(b, i, ref, atrs[i])
        sp = (stop-ref)/ref*100
        if sp <= 0 or sp < ir.ASGARI_STOP: continue
        son = min(gi+UFUK, len(b))
        if son-gi < 4: continue
        hed = ref*(1-HEDEF/100)
        d["n"] += 1
        d["sp"].append(sp)
        d["atr_birim"].append((stop-ref)/atrs[i])
        # stopLU oynatma
        tip, sbar = "sure", None
        for j in range(gi, son):
            if b[j]["h"] >= stop: tip, sbar = "stop", j-gi; break
            if b[j]["l"] <= hed:  tip = "hedef"; break
        d[tip] += 1
        if tip != "stop": continue
        d["stop_bar"].append(sbar)
        # STOPSUZ devam: ufuk icinde hedefe varir miydi?
        varir = False
        for j in range(gi, son):
            if b[j]["l"] <= hed: varir = True; break
        if varir:
            d["yanlis"] += 1; d["yanlis_bar"].append(sbar)
        else:
            d["dogru"] += 1

n = d["n"]
print("IZ I — STOPUN GERCEK MALIYETI (SHORT, botun kapilari, 2 yil)")
print("=" * 84)
print("olay: %d" % n)
print()
print("1) STOP NEREDE DURUYOR")
print("   mesafe %%          : medyan %.2f · %%25 %.2f · %%75 %.2f"
      % (stx.median(d["sp"]), sorted(d["sp"])[n//4], sorted(d["sp"])[3*n//4]))
ab = d["atr_birim"]
print("   ATR CINSINDEN     : medyan %.2f x ATR · %%25 %.2f · %%75 %.2f"
      % (stx.median(ab), sorted(ab)[n//4], sorted(ab)[3*n//4]))
print("   72 saatlik rastgele yuruyusun beklenen menzili ~ sqrt(72) = %.1f x ATR" % (72**0.5))
print("   -> stop, ufkun beklenen menzilinin %%%.1f'i kadar uzakta"
      % (100*stx.median(ab)/(72**0.5)))
print()
print("2) SONUC DAGILIMI")
for k, ad in (("stop", "STOP"), ("hedef", "HEDEF"), ("sure", "SURE")):
    print("   %-6s %6d  (%%%.1f)" % (ad, d[k], 100*d[k]/n))
print()
print("3) YANLIS STOP — stop olmasaydi hedefe varacak olanlar")
st = d["stop"]
print("   stop olan               : %6d" % st)
print("   bunlarin HEDEFE varirdi : %6d  (%%%.1f)  <-- YANLIS STOP" % (d["yanlis"], 100*d["yanlis"]/st))
print("   gercekten kotu giris    : %6d  (%%%.1f)" % (d["dogru"], 100*d["dogru"]/st))
print()
print("   yanlis stoplarin toplam olaya orani: %%%.1f" % (100*d["yanlis"]/n))
print("   kaybedilen: %d islem x (+%.0f%% hedef + stop kaybi) " % (d["yanlis"], HEDEF))
kayip = d["yanlis"] * (HEDEF + stx.median(d["sp"])) / n
print("   -> olay basina kaybedilen kaba deger: %.3f puan" % kayip)
print()
print("4) STOP NE KADAR ERKEN GELIYOR")
print("   tum stoplar   : medyan %d. saat · %%25 %d · %%75 %d"
      % (stx.median(d["stop_bar"]), sorted(d["stop_bar"])[st//4], sorted(d["stop_bar"])[3*st//4]))
yb = d["yanlis_bar"]
print("   YANLIS stoplar: medyan %d. saat · %%25 %d · %%75 %d"
      % (stx.median(yb), sorted(yb)[len(yb)//4], sorted(yb)[3*len(yb)//4]))
erken = sum(1 for x in yb if x <= 6)
print("   yanlis stoplarin %%%.0f'i ilk 6 SAATTE geliyor" % (100*erken/len(yb)))
