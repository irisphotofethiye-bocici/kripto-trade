# -*- coding: utf-8 -*-
"""YIGIN, BOTUN GERCEK POZISYONLARININ KACINI KESERDI?

Filtreler (S_yigin'in 4. adimi):
  1. chg24 < %20          (pump engeli — bot zaten uyguluyor)
  2. fiyat > $0,07        (ucuz disla)
  3. funding > -0,05      (funding kapisini KALDIR = o girisleri ELE)
  4. btc_pay bant != UST
  + LONG kapali

⚠️ N kucuk (~117). Bu TARIF, kanit degil.
"""
import json, os, sys, datetime, statistics as stx
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PROJE = os.path.dirname(os.path.dirname(HERE))
import ortak

# btc_pay bandi: gunluk log + 3 gunluk degisim
r = [json.loads(l) for l in open(os.path.join(PROJE, "btc_pay_log.jsonl"), encoding="utf-8") if l.strip()]
r.sort(key=lambda x: x["gun"])
xs = {x["gun"]: x["btc_d_xs"] for x in r}
UST = 0.287
def bant(gun):
    d0 = (datetime.date.fromisoformat(gun) - datetime.timedelta(days=3)).isoformat()
    if gun not in xs or d0 not in xs: return None
    return "UST" if (xs[gun]-xs[d0]) >= UST else "diger"

poz = ortak.poz_yukle("muhasebe_11agu")
print("BOTUN GERCEK POZISYONLARI — yigin kacini keserdi?")
print("=" * 92)
print("toplam kapanmis pozisyon: %d  (SHORT %d · LONG %d)  ·  gercek P&L %+.2f $"
      % (len(poz), sum(1 for p in poz if p["yon"] == "SHORT"),
         sum(1 for p in poz if p["yon"] == "LONG"), sum(p["pnl"] for p in poz)))
print()

def deger(p, ad):
    if ad == "chg24":
        v = p.get("a_chg24")
        return v if v is not None else p.get("d_chg24_giriste")
    if ad == "fiyat": return p.get("a_price") or p.get("giris_fiyat")
    if ad == "funding": return p.get("a_funding")
    return None

ADIMLAR = [
    ("0. hepsi", lambda p: True),
    ("1. + LONG kapali", lambda p: p["yon"] == "SHORT"),
    ("2. + pump engeli <%20", lambda p: p["yon"] == "SHORT"
     and (deger(p, "chg24") is not None and deger(p, "chg24") < 20)),
    ("3. + ucuz disla >$0,07", lambda p: p["yon"] == "SHORT"
     and (deger(p, "chg24") is not None and deger(p, "chg24") < 20)
     and (deger(p, "fiyat") is not None and deger(p, "fiyat") > 0.07)),
    ("4. + funding > -0,05", lambda p: p["yon"] == "SHORT"
     and (deger(p, "chg24") is not None and deger(p, "chg24") < 20)
     and (deger(p, "fiyat") is not None and deger(p, "fiyat") > 0.07)
     and (deger(p, "funding") is not None and deger(p, "funding") > -0.05)),
    ("5. + btc_pay != UST", lambda p: p["yon"] == "SHORT"
     and (deger(p, "chg24") is not None and deger(p, "chg24") < 20)
     and (deger(p, "fiyat") is not None and deger(p, "fiyat") > 0.07)
     and (deger(p, "funding") is not None and deger(p, "funding") > -0.05)
     and bant(p["giris_ts"][:10]) == "diger"),
]
print("%-26s %8s %8s %12s %10s %10s" % ("adim", "kalan", "kesilen", "P&L", "medyan", "kazanan"))
onc = len(poz)
for ad, fn in ADIMLAR:
    g = [p for p in poz if fn(p)]
    if not g:
        print("%-26s %8d %8d   —" % (ad, 0, onc)); continue
    v = [p["pnl"] for p in g]
    print("%-26s %8d %8d %+12.2f %+10.2f %8d/%-3d"
          % (ad, len(g), onc-len(g), sum(v), stx.median(v),
             sum(1 for z in v if z > 0), len(g)))
    onc = len(g)

son = [p for p in poz if ADIMLAR[-1][1](p)]
print()
print("SONUC")
print("  %d pozisyonun %d'i acilirdi  ->  %%%.0f'i KESILIRDI"
      % (len(poz), len(son), 100*(1-len(son)/len(poz))))
print("  gercek toplam  %+9.2f $" % sum(p["pnl"] for p in poz))
print("  yigin toplami  %+9.2f $" % sum(p["pnl"] for p in son))
print()
print("  ACILAN pozisyonlar:")
for p in sorted(son, key=lambda z: z["giris_ts"]):
    print("     %s %-7s %-5s chg24 %+6.1f  fiyat %-10.6g funding %+7.4f  P&L %+8.2f"
          % (p["giris_ts"][5:16], p["sym"], p["yon"], deger(p, "chg24") or 0,
             deger(p, "fiyat") or 0, deger(p, "funding") or 0, p["pnl"]))
print()
print("  KESILEN en buyuk 8 zarar:")
kes = [p for p in poz if not ADIMLAR[-1][1](p)]
for p in sorted(kes, key=lambda z: z["pnl"])[:8]:
    sb = []
    if p["yon"] != "SHORT": sb.append("LONG")
    c = deger(p, "chg24")
    if c is not None and c >= 20: sb.append("pump")
    f = deger(p, "fiyat")
    if f is not None and f <= 0.07: sb.append("ucuz")
    fu = deger(p, "funding")
    if fu is not None and fu <= -0.05: sb.append("funding-kapisi")
    if bant(p["giris_ts"][:10]) == "UST": sb.append("btc_pay-UST")
    print("     %-7s %-5s P&L %+8.2f   eleyen: %s" % (p["sym"], p["yon"], p["pnl"], ", ".join(sb) or "?"))
