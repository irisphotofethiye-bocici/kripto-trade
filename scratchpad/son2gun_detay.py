#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SON 2 GUN — DETAY: fren aritmetigi, yon kirilimi, kayip yogunlasmasi.
SALT OKUMA. Bota DOKUNMAZ."""
# [2026-08-25] cp1254 TUZAGI — kalici kapatma.
#   Windows konsolu cp1254; print() icindeki emoji/varyasyon secici CIKTI
#   YONLENDIRILDIGINDE UnicodeEncodeError firlatiyor ve betik COKUYOR.
#   Bu sinif bu projede BES kez isirdi. Emoji ayiklamak yerine stdout
#   guvenli hale getirilir; hata sinifi disiplinle degil ARACLA kapanir.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, datetime, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
SIMDI = datetime.datetime.now()
BAS = SIMDI - datetime.timedelta(days=2)


def jl(y):
    p = os.path.join(PROJE, y)
    out = []
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for s in f:
                if s.strip():
                    try:
                        out.append(json.loads(s))
                    except Exception:
                        pass
    return out


st = json.load(open(os.path.join(PROJE, "testbot_state.json"), encoding="utf-8"))
print("=" * 92)
print("1) DUSUS FRENI ARITMETIGI")
print("=" * 92)
ef = st.get("efektif_equity")
zirve = st.get("zirve_equity")
print("   baslangic bakiye     %10.2f" % (st.get("baslangic_bakiye") or 0))
print("   zirve_equity         %10.2f   <- frenin referansi" % (zirve or 0))
print("   equity (gerceklesmis)%10.2f" % (st.get("equity") or 0))
print("   efektif_equity       %10.2f   (gerceklesmis + acik P&L)" % (ef or 0))
if zirve:
    print("   zirveden dusus       %+9.2f%%" % ((ef / zirve - 1) * 100))
print("   durum                %s" % st.get("durum"))
print("   kumulatif_funding    %+10.4f   (2026-07-23'ten beri, PENCEREYE AIT DEGIL)"
      % (st.get("kumulatif_funding") or 0))
print("   kumulatif_giris_ucret%+10.4f   (ayni not)"
      % (st.get("kumulatif_giris_ucret") or 0))

print("\n" + "=" * 92)
print("2) TESTBOT — 2 GUNDE KAPANAN POZISYONLAR (id ile birlestirildi)")
print("=" * 92)
kay = [x for x in jl("testbot_islemler.jsonl")
       if datetime.datetime.strptime(x["ts"], F) >= BAS]
g = collections.defaultdict(list)
for x in kay:
    g[x["id"]].append(x)

satir = []
for i, v in g.items():
    v.sort(key=lambda z: z["ts"])
    son = v[-1]
    satir.append({"sym": son["sym"], "yon": son["yon"],
                  "net": sum((t.get("sonuc_usdt") or 0) for t in v),
                  "sebep": son.get("sebep"), "ts": son["ts"],
                  "kapi": (son.get("sebep_giris") or "?")[:28],
                  "tut": max((t.get("tutma_saat") or 0) for t in v),
                  "kismi": any(t.get("kismi") for t in v)})
satir.sort(key=lambda z: z["net"])

print("   YON KIRILIMI")
for yon in ("LONG", "SHORT"):
    w = [z for z in satir if z["yon"] == yon]
    if w:
        kz = sum(1 for z in w if z["net"] > 0)
        print("     %-6s N=%2d  toplam %+9.2f  kazanan %d (%%%.0f)  ort %+7.2f"
              % (yon, len(w), sum(z["net"] for z in w), kz, 100.0 * kz / len(w),
                 sum(z["net"] for z in w) / len(w)))

print("\n   KAPANIS SEBEBI")
for s, n in collections.Counter(z["sebep"] for z in satir).most_common():
    w = [z for z in satir if z["sebep"] == s]
    print("     %-16s %2d islem  toplam %+9.2f" % (s, n, sum(z["net"] for z in w)))

print("\n   EN KOTU 6")
for z in satir[:6]:
    print("     %-10s %-5s %+9.2f  %-14s %4.1f sa  %s"
          % (z["sym"], z["yon"], z["net"], z["sebep"], z["tut"], z["ts"][5:16]))
print("   EN IYI 4")
for z in satir[-4:][::-1]:
    print("     %-10s %-5s %+9.2f  %-14s %4.1f sa  %s"
          % (z["sym"], z["yon"], z["net"], z["sebep"], z["tut"], z["ts"][5:16]))

print("\n   FREN ONCESI / SONRASI (fren 08-22 16:06:21)")
fren = datetime.datetime(2026, 8, 22, 16, 6, 21)
for ad, kos in (("fren ONCESI", lambda z: datetime.datetime.strptime(z["ts"], F) < fren),
                ("fren SONRASI", lambda z: datetime.datetime.strptime(z["ts"], F) >= fren)):
    w = [z for z in satir if kos(z)]
    if w:
        print("     %-13s N=%2d  toplam %+9.2f" % (ad, len(w), sum(z["net"] for z in w)))

print("\n" + "=" * 92)
print("3) GOLGE — ayni pencerede ne yapti (yon kirilimi)")
print("=" * 92)
kg = [x for x in jl("golge_islemler.jsonl")
      if datetime.datetime.strptime(x["ts"], F) >= BAS]
gg = collections.defaultdict(list)
for x in kg:
    gg[x["id"]].append(x)
gs = []
for i, v in gg.items():
    son = sorted(v, key=lambda z: z["ts"])[-1]
    gs.append({"yon": son["yon"], "net": sum((t.get("sonuc_usdt") or 0) for t in v),
               "kaynak": son.get("kaynak") or "?"})
for yon in ("LONG", "SHORT"):
    w = [z for z in gs if z["yon"] == yon]
    if w:
        kz = sum(1 for z in w if z["net"] > 0)
        print("     %-6s N=%2d  toplam %+9.2f  kazanan %d (%%%.0f)"
              % (yon, len(w), sum(z["net"] for z in w), kz, 100.0 * kz / len(w)))
print("   KAYNAK (golge iki is birden yapiyor):")
for k, n in collections.Counter(z["kaynak"] for z in gs).most_common(6):
    w = [z for z in gs if z["kaynak"] == k]
    print("     %-24s %2d islem  toplam %+9.2f" % (k[:24], n, sum(z["net"] for z in w)))

print("\n" + "=" * 92)
print("4) ACIK POZISYON — MELANIA (testbot + ayna)")
print("=" * 92)
izl = [x for x in jl("pozisyon_izleme.jsonl") if x.get("sym") == "MELANIA"]
if izl:
    s = izl[-1]
    print("   son goruntu %s   pnl %+.2f%%  (%+.2f $)  yas %.1f sa"
          % (s["ts"][5:16], s.get("pnl_pct") or 0, s.get("pnl_usd") or 0,
             s.get("yas_saat") or 0))
    print("   giris %.6f  fiyat %.6f  stop %s  tp2 %s"
          % (s.get("giris") or 0, s.get("fiyat") or 0, s.get("stop"), s.get("tp2")))
    print("   tepe %.2f%%  dip %.2f%%  mfe %.2f  mae %.2f"
          % (s.get("tepe_pnl_pct") or 0, s.get("dip_pnl_pct") or 0,
             s.get("mfe_pct") or 0, s.get("mae_pct") or 0))
else:
    print("   izleme kaydi yok")

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
