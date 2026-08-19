# -*- coding: utf-8 -*-
"""FREN GEC MI CALISIYOR? — btc_pay_log uzerinde TANIMSAL cozumleme (2026-08-19)

ON-KAYIT YOK: bu bir GETIRI olcumu degil, gostergenin KENDI mekanigini
tarif eder. Hicbir esik taranmaz, hicbir kural onerilmez.

SORU iki parcali:
  (1) DEVREYE GIRERKEN gec mi?  -> UST gunlerinde 3g degisimi hangi YASTAKI
      gunluk adim tasiyor?  (0 = bugunun kendi hareketi, 2 = iki gun onceki)
  (2) BIRAKIRKEN gec mi?  -> UST serisi biterken xs GERCEKTEN dustu mu,
      yoksa referans noktasi yuruudugu icin mi kalkti?
"""
import json, collections, statistics as stx

r = [json.loads(l) for l in open("btc_pay_log.jsonl", encoding="utf-8") if l.strip()]
r.sort(key=lambda x: x["gun"])
xs = [x["btc_d_xs"] for x in r]
gun = [x["gun"] for x in r]
UST = 0.287

d3 = [None]*3 + [xs[i] - xs[i-3] for i in range(3, len(xs))]
g1 = [None] + [xs[i] - xs[i-1] for i in range(1, len(xs))]     # gunluk adim
bant = [(d is not None and d >= UST) for d in d3]

# --- (1) UST gunlerinde en buyuk katkiyi hangi YAS tasiyor ---
yas = collections.Counter()
for i in range(3, len(xs)):
    if not bant[i]:
        continue
    kat = {0: g1[i], 1: g1[i-1], 2: g1[i-2]}
    yas[max(kat, key=lambda k: kat[k])] += 1
top = sum(yas.values())
print("UST gunu sayisi: %d / %d  (%%%.1f)" % (top, len(xs)-3, 100*top/(len(xs)-3)))
print("\n(1) DEVREYE GIRERKEN — 3g degisimini en cok hangi YASTAKI adim tasiyor:")
for k in (0, 1, 2):
    print("    %d gun onceki adim : %4d gun  (%%%.1f)%s"
          % (k, yas[k], 100*yas[k]/top, "   <-- BUGUNUN hareketi" if k == 0 else ""))

# --- serileri cikar ---
seri, i = [], 3
while i < len(xs):
    if bant[i]:
        j = i
        while j+1 < len(xs) and bant[j+1]:
            j += 1
        seri.append((i, j))
        i = j+1
    else:
        i += 1
uz = [j-i+1 for i, j in seri]
print("\nUST serisi: %d adet · medyan %d gun · ortalama %.1f · en uzun %d"
      % (len(seri), stx.median(uz), stx.mean(uz), max(uz)))

# --- (2) seri biterken xs gercekten dustu mu? ---
dusus, rolloff = 0, 0
for i, j in seri:
    k = j+1
    if k >= len(xs):
        continue
    if xs[k] < xs[j]:
        dusus += 1
    else:
        rolloff += 1          # xs artti/sabit AMA fren kalkti -> referans yurudu
n = dusus + rolloff
print("\n(2) BIRAKIRKEN — fren kalktigi gun BTC payi ne yapmisti:")
print("    GERCEKTEN dustu        : %3d / %d  (%%%.1f)" % (dusus, n, 100*dusus/n))
print("    ARTTI ama fren kalkti  : %3d / %d  (%%%.1f)   <-- referans yurudu"
      % (rolloff, n, 100*rolloff/n))

# --- gunluk adimin buyuklugu: sicrama ne kadar nadir ---
ad = [abs(x) for x in g1[1:]]
print("\nGunluk |adim| : medyan %.4f · %%90 dilim %.4f · 08-18 sicramasi 0.3022 (%%%.1f dilim)"
      % (stx.median(ad), sorted(ad)[int(len(ad)*0.9)],
         100*sum(1 for a in ad if a <= 0.3022)/len(ad)))
