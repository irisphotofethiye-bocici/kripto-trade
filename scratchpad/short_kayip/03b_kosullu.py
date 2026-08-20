# -*- coding: utf-8 -*-
"""KOSULLU TEST — kapi mi degisti, GIRDI mi?

Onceki adim: fren-sifir gunlerde long payi %7,4 -> %24,0 (p=0,002).
AMA ayni gun aday havuzunun medyani +13,80% ve adaylarin %84'u yukseliyordu.

SORU: AYNI OZELLIKTEKI bir aday, 08-20'de sicrama oncesine gore daha mi
sik LONG etiketi aliyor? Evetse KAPI degisti. Hayirsa yalniz GIRDI degisti.

Yontem: adaylar chg24'e gore kovalara bolunur, her kovada LONG orani
iki donemde karsilastirilir. Fren-sifir gunler.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
FREN_SIFIR = {"2026-08-11","2026-08-12","2026-08-13","2026-08-14",
              "2026-08-15","2026-08-16","2026-08-17","2026-08-20"}
SICRAMA = "2026-08-18"

kar = []
with open(os.path.join(PROJE,"testbot_aday_arsiv.jsonl"),encoding="utf-8") as f:
    for line in f:
        line=line.strip()
        if not line: continue
        x=json.loads(line)
        g=x["ts"][:10]
        if g not in FREN_SIFIR: continue
        k=x.get("karar") or ""
        if not (k.startswith("LONG") or k.startswith("SHORT")): continue
        if x.get("chg24") is None: continue
        kar.append({"gun":g,"long":1 if k.startswith("LONG") else 0,
                    "chg24":x["chg24"],"pos":x.get("pos"),"smart":x.get("smart"),
                    "donem":"sonrasi" if g>=SICRAMA else "oncesi"})

print("KOSULLU TEST — kapi mi degisti, girdi mi?")
print("="*84)
print("fren-sifir gunlerdeki LONG/SHORT karari: %d"%len(kar))
o=[z for z in kar if z["donem"]=="oncesi"]; s=[z for z in kar if z["donem"]=="sonrasi"]
print("  oncesi N=%d  long payi %%%.1f"%(len(o),100*sum(z['long'] for z in o)/len(o)))
print("  sonrasi N=%d  long payi %%%.1f"%(len(s),100*sum(z['long'] for z in s)/len(s)))

print("\n### chg24 KOVALARINDA long orani (ayni girdi, iki donem)")
kov=[(-1e9,0,"dusen"),(0,5,"0-5%"),(5,10,"5-10%"),(10,20,"10-20%"),(20,1e9,">20%")]
print("%-10s %22s %22s   %s"%("kova","ONCESI","SONRASI","fark"))
for a,b,ad in kov:
    oo=[z for z in o if a<=z["chg24"]<b]; ss=[z for z in s if a<=z["chg24"]<b]
    if len(oo)<5 or len(ss)<5:
        print("%-10s  N oncesi %3d / sonrasi %3d  -> N yetersiz"%(ad,len(oo),len(ss))); continue
    po=100*sum(z['long'] for z in oo)/len(oo); ps=100*sum(z['long'] for z in ss)/len(ss)
    print("%-10s  N=%3d long %%%5.1f      N=%3d long %%%5.1f     %+6.1f puan"%(ad,len(oo),po,len(ss),ps,ps-po))

print("\n### AYNI KOVA DAGILIMIYLA yeniden agirliklandirma")
print("(sonrasi'nin kova dagilimi, ONCESI'nin kova-ici long oranlariyla)")
kd={}
for a,b,ad in kov:
    oo=[z for z in o if a<=z["chg24"]<b]; ss=[z for z in s if a<=z["chg24"]<b]
    kd[ad]=(len(ss), (sum(z['long'] for z in oo)/len(oo)) if oo else None, len(oo))
bek=0.0; kaps=0
for ad,(ns,po,no) in kd.items():
    if po is None: continue
    bek+=ns*po; kaps+=ns
if kaps:
    print("  ONCESI kapi davranisi + SONRASI havuzu  ->  beklenen long payi %%%.1f"%(100*bek/kaps))
    print("  GERCEK sonrasi long payi                ->                     %%%.1f"%(100*sum(z['long'] for z in s)/len(s)))
    print("  aciklanamayan artik                     ->                     %+.1f puan"%(
      100*sum(z['long'] for z in s)/len(s)-100*bek/kaps))
    print("\n  YORUM: artik ~0 ise KAPI DEGISMEDI, yalniz havuz degisti.")
    print("         artik buyukse kapi ayni girdide farkli davranmis demektir.")
