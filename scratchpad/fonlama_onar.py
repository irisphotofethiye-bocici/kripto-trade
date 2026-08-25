#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FONLAMA BIRIM ONARIMI — DEGISIM NOKTASI yontemi.

NEDEN: veri_guncelle.py:97 `*100`'u atlamisti (2026-08-25 duzeltildi); o betigin
   ekledigi kayitlar KESIR yazildi, oysa funding_gecmis YUZDE tutar.

⚠️ IKI YANLIS SURUM YASANDI, IKISI DE BURAYA YAZILI:
   1) SABIT ESIK (0,0009): yuksek-fonlamali sembollerde kesir degerleri esigi
      astigi icin 20 dosya kacti; dosyalar KISMEN onarildi.
   2) SABIT TARIH (t >= 08-11): dosyalarin sinirlari FARKLI. Gec baslayanlarin
      DOGRU yuzde kayitlari da 100 ile carpildi -> 22 dosyada max|r| = 10..17
      (fonlama tavani %2). Yani "sabit kesim yeni bozulma uretir" uyarisi
      dogruydu ve yine de yapildi.

YONTEM — esik de sabit tarih de YOK:
   YEDEK (onarim oncesi anlik goruntu) her dosya icin temizdir:
      [ ... YUZDE kayitlar ... | ... KESIR kayitlar ... ]  tek adim.
   Adim yeri, 08-08 sonrasi tum bolme noktalari arasinda
      medyan(oncesi) / medyan(sonrasi)
   oranini EN BUYUK yapan nokta olarak bulunur. Oran >= 20 ise kirilma kabul
   edilir; degilse dosyaya DOKUNULMAZ.
   Onarim YEDEK degerleri uzerinden yazilir -> onceki hatali gecisler de
   kendiliginden geri alinir. IDEMPOTENT.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, json, sys, datetime, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
FON = os.path.join(HERE, "funding_gecmis")
YEDEK = os.path.join(HERE, "funding_yedek_20260825")
ARAMA_BAS = int(datetime.datetime(2026, 8, 8, 0, 0).timestamp() * 1000)
MIN_ORAN = 20.0
MIN_KAYIT = 5
KURU = "--kuru" in sys.argv
if not os.path.isdir(YEDEK):
    raise SystemExit("YEDEK BULUNAMADI: %s" % YEDEK)
g = lambda t: datetime.datetime.utcfromtimestamp(t / 1000).strftime("%Y-%m-%d %H:%M")

def _geri_al(d, yb):
    """Yedekte bulunan her kaydi AYNEN geri yazar. -> degisen kayit sayisi.
    [2026-08-25] Sinir guvenle belirlenemeyen dosya, BULUNDUGU HALE dondurulur;
    onceki hatali gecislerin izi birakilmaz. 'Supheda DAIMA statuko'."""
    n = 0
    for x in d:
        if "r" in x and x["t"] in yb and abs(x["r"] - yb[x["t"]]) > 1e-12:
            x["r"] = yb[x["t"]]; n += 1
    return n


dosya = kayit = 0
geri_alinan = 0
dokunulmayan = 0
sinirlar = {}
for ad in sorted(os.listdir(FON)):
    if not ad.endswith(".json"): continue
    yy = os.path.join(YEDEK, ad); yol = os.path.join(FON, ad)
    if not os.path.exists(yy): dokunulmayan += 1; continue
    try:
        with open(yy, encoding="utf-8") as f: yd = json.load(f)
        with open(yol, encoding="utf-8") as f: d = json.load(f)
    except Exception:
        dokunulmayan += 1; continue
    ysir = [x for x in yd if "r" in x and x["r"]]
    aday = [i for i, x in enumerate(ysir) if x["t"] >= ARAMA_BAS]
    if len(aday) < MIN_KAYIT * 2:
        yb0 = {x["t"]: x["r"] for x in yd if "r" in x}
        n = _geri_al(d, yb0)
        if n and not KURU:
            tmp = yol + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(d, f)
            os.replace(tmp, yol)
        if n: geri_alinan += 1
        dokunulmayan += 1; continue
    # [DUZELTME] YALNIZ oran maksimizasyonu YETMEDI: medyan saglam oldugu icin
    #   erken bolmeler de yuksek oran veriyor ve argmax arama penceresinin
    #   BASINA yapisiyordu (300 dosya 08-08 00:00 gosterdi). Ek YEREL kosul:
    #   sinirdan HEMEN ONCEKI kayit YUZDE, sinirdaki kayit KESIR olmali.
    taban_v = [abs(x["r"]) for x in ysir if x["t"] < ARAMA_BAS]
    if len(taban_v) < 30:
        yb0 = {x["t"]: x["r"] for x in yd if "r" in x}
        n = _geri_al(d, yb0)
        if n and not KURU:
            tmp = yol + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(d, f)
            os.replace(tmp, yol)
        if n: geri_alinan += 1
        dokunulmayan += 1; continue
    yerel = sx.median(taban_v) / 20.0
    adaylar = []
    for i in aday:
        if i == 0: continue
        if abs(ysir[i]["r"]) >= yerel: continue          # sinirdaki kayit KESIR olmali
        if abs(ysir[i-1]["r"]) < yerel: continue         # onceki kayit YUZDE olmali
        onc = [abs(x["r"]) for x in ysir[:i]]
        son = [abs(x["r"]) for x in ysir[i:]]
        if len(onc) < 30 or len(son) < MIN_KAYIT: continue
        # [DUZELTME 2] BLOK SAFLIGI. Yerel kosul tek basina yetmedi: tek bir
        #   kucuk deger onu tetikliyor, oran ise ILERIDEKI kesir blogundan
        #   yuksek cikiyordu -> 33 dosyada sinir 08-08..08-10'a kayiyordu
        #   (ANKR · BLUR · BCH ...). Gercek sinirdan SONRASININ neredeyse
        #   TAMAMI kesir olmalidir.
        saf = sum(1 for v in son if v < yerel) / float(len(son))
        if saf < 0.90: continue
        mo, ms = sx.median(onc), sx.median(son)
        if ms <= 0: continue
        adaylar.append((mo / ms, i))
    # [DUZELTME 4] KABUL SARTI = BUYUKLUK MANTIGI.
    #   Sinir bir bar erken secilirse, o barin DOGRU yuzde kayitlari da 100 ile
    #   carpilir ve sonuc Binance fonlama TAVANINI asar. Olculdu: 33 dosyada
    #   max|r| 2,7..11,7'ye firladi, hepsinin zirvesi 2026-08-11.
    #   Bu yuzden aday sinirlar orana gore SIRALANIR ve tavani asmayan ILK
    #   aday secilir. Tavan: dosyanin kendi tarihsel azamisi (yedekten), en az %2.
    yb = {x["t"]: x["r"] for x in yd if "r" in x}
    tavan = max(2.0, max((abs(v) for v in yb.values()), default=2.0)) * 1.05
    adaylar.sort(reverse=True)
    sinir = en_oran = None
    for oran, i in adaylar:
        if oran < MIN_ORAN: break
        t_i = ysir[i]["t"]
        enb = max((abs(yb[t] * 100) if t >= t_i else abs(yb[t])) for t in yb)
        if enb <= tavan:
            sinir, en_oran = t_i, oran; break
    if sinir is None:
        n = _geri_al(d, yb)
        if n and not KURU:
            tmp = yol + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(d, f)
            os.replace(tmp, yol)
        if n: geri_alinan += 1
        dokunulmayan += 1; continue
    sinirlar[ad[:-5]] = (sinir, en_oran)
    # [DUZELTME 3] TAM GERI YAZIM. Onceki surum yalniz sinirdan SONRASINI
    #   duzeltiyordu; onceki hatali gecisin sinir ONCESINDE yaptigi carpmalar
    #   ayakta kaliyordu -> 132 dosyada max|r| fonlama tavanini (%2) asti.
    #   Cozum: yedekte bulunan HER kayit yedekten yeniden yazilir;
    #   sinirdan itibaren *100, oncesinde AYNEN. Tam idempotent.
    n = 0
    for x in d:
        if "r" not in x: continue
        e = yb.get(x["t"])
        if e is None: continue                      # bugunku duzeltilmis indirme
        yeni = e * 100 if x["t"] >= sinir else e
        if abs(x["r"] - yeni) > 1e-12:
            x["r"] = yeni; n += 1
    if n:
        if not KURU:
            tmp = yol + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(d, f)
            os.replace(tmp, yol)
        dosya += 1; kayit += n

print("FONLAMA BIRIM ONARIMI — degisim noktasi%s" % ("   [KURU KOSUM]" if KURU else ""))
print("  kirilma bulunan dosya : %d" % len(sinirlar))
print("  yazilan dosya         : %d      kayit: %s" % (dosya, format(kayit, ",")))
print("  dokunulmayan          : %d      (yedege geri alinan: %d)" % (dokunulmayan, geri_alinan))
if sinirlar:
    import collections
    c = collections.Counter(g(v[0])[:13] for v in sinirlar.values())
    print("  sinir dagilimi (ilk 8):")
    for s, n in sorted(c.items())[:8]:
        print("     %s  %d dosya" % (s, n))
