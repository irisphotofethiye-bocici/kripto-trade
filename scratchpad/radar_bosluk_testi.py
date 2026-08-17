# -*- coding: utf-8 -*-
"""Radar kare kaybi isaretleme — dogrulama + gecmis bosluk olcumu (2026-08-17).

CLAUDE.md "TEST YAZARKEN": diske yazan her yol stub'lanir. Burada yazan tek yol
_bosluk_yaz; radar.HERE gecici klasore cevrilerek gercek dosyaya yazim ONLENIR.
Testin sonunda gercek radar_bosluk.jsonl'in olusmadigi DOGRULANIR.
"""
import sys, os, json, tempfile, shutil, datetime
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import radar

GERCEK_BOSLUK = os.path.join(KOK, "radar_bosluk.jsonl")
vardi_once = os.path.exists(GERCEK_BOSLUK)

hata = 0
def kontrol(ad, kosul, detay=""):
    global hata
    print(("  OK   " if kosul else "  HATA ") + ad + ("  " + detay if detay else ""))
    if not kosul:
        hata += 1

# ---- HERE'i gecici klasore cevir: yazimlar oraya gitsin -------------------------
gecici = tempfile.mkdtemp(prefix="radar_bosluk_test_")
_orij_here = radar.HERE
radar.HERE = gecici
BOSLUK = os.path.join(gecici, radar.BOSLUK_DOSYA)

def bosluk_kayitlari():
    if not os.path.exists(BOSLUK):
        return []
    return [json.loads(l) for l in open(BOSLUK, encoding="utf-8") if l.strip()]

print("=" * 66)
print("1) _son_arsiv_ts gercek arsivin son damgasini okuyor mu (salt-okunur)")
ts = radar._son_arsiv_ts(os.path.join(_orij_here, "radar_archive.jsonl"))
kontrol("damga okundu", bool(ts), f"ts={ts}")
kontrol("bicim dogru", bool(ts) and len(ts) >= 16 and ts[4] == "-" and ts[13] == ":")

print()
print("2) Olmayan / bozuk dosyada cokmuyor")
kontrol("olmayan dosya -> None", radar._son_arsiv_ts(os.path.join(gecici, "yok.jsonl")) is None)
bozuk = os.path.join(gecici, "bozuk.jsonl")
open(bozuk, "w", encoding="utf-8").write("bu json degil\n")
kontrol("bozuk satir -> None", radar._son_arsiv_ts(bozuk) is None)

print()
print("3) NORMAL tur (15 dk) bosluk kaydi YAZMAMALI")
radar._bosluk_yaz("2026-08-17 22:41", "2026-08-17 22:56")
kontrol("kayit yok", len(bosluk_kayitlari()) == 0, f"n={len(bosluk_kayitlari())}")

print()
print("4) Esik SINIRI (tam 30 dk = 2x) yazmamali, 31 dk yazmali")
radar._bosluk_yaz("2026-08-17 22:26", "2026-08-17 22:56")     # tam 30 -> yazmaz
kontrol("30 dk yazmadi", len(bosluk_kayitlari()) == 0)
radar._bosluk_yaz("2026-08-17 22:25", "2026-08-17 22:56")     # 31 -> yazar
kontrol("31 dk yazdi", len(bosluk_kayitlari()) == 1)

print()
print("5) GERCEK kesinti (124 dk — 13-16 Agustos'un en uzunu) dogru hesaplaniyor mu")
radar._bosluk_yaz("2026-08-17 20:52", "2026-08-17 22:56")
k = bosluk_kayitlari()[-1]
kontrol("bosluk_dk = 124", abs(k["bosluk_dk"] - 124.0) < 0.01, f"{k['bosluk_dk']}")
kontrol("kayip tur tahmini = 7", k["kayip_tur_tahmini"] == 7, f"{k['kayip_tur_tahmini']}")
kontrol("onceki_ts saklandi", k["onceki_ts"] == "2026-08-17 20:52")

print()
print("6) onceki_ts yoksa (ilk calisma) sessizce atlanir")
n0 = len(bosluk_kayitlari())
radar._bosluk_yaz(None, "2026-08-17 22:56")
radar._bosluk_yaz("", "2026-08-17 22:56")
kontrol("kayit artmadi", len(bosluk_kayitlari()) == n0)

print()
print("7) Bozuk damga cokmemeli")
n0 = len(bosluk_kayitlari())
radar._bosluk_yaz("bozuk-tarih", "2026-08-17 22:56")
kontrol("cokmedi, yazmadi", len(bosluk_kayitlari()) == n0)

# ---- GECMIS BOSLUK OLCUMU (salt-okunur) ----------------------------------------
print()
print("=" * 66)
print("GECMIS OLCUM — radar_archive.jsonl'deki gercek bosluklar")
arsiv = os.path.join(_orij_here, "radar_archive.jsonl")
damgalar, onceki = [], None
with open(arsiv, encoding="utf-8") as fh:
    for l in fh:
        try:
            t = l.split('"', 4)[3]
        except Exception:
            continue
        if t != onceki:
            damgalar.append(t); onceki = t
print(f"  ayri tarama turu      : {len(damgalar)}")
f = "%Y-%m-%d %H:%M"
bosluklar = []
for a, b in zip(damgalar, damgalar[1:]):
    try:
        dk = (datetime.datetime.strptime(b[:16], f) - datetime.datetime.strptime(a[:16], f)).total_seconds() / 60
    except Exception:
        continue
    if dk > radar.BEKLENEN_TUR_DK * radar.BOSLUK_ESIK_KAT:
        bosluklar.append((a, b, dk))
kayip = sum(int(round(d / radar.BEKLENEN_TUR_DK)) - 1 for _, _, d in bosluklar)
beklenen = len(damgalar) + kayip
print(f"  esigi asan bosluk     : {len(bosluklar)}")
print(f"  tahmini KAYIP tur     : {kayip}")
print(f"  kayip orani           : %{100.0 * kayip / beklenen:.1f}  (durum.md tahmini: %7-14)")
print(f"  en uzun bosluk        : {round(max((d for _, _, d in bosluklar), default=0))} dk")
print("  en uzun 5 kesinti:")
for a, b, d in sorted(bosluklar, key=lambda x: -x[2])[:5]:
    print(f"    {a} -> {b}   {round(d)} dk (~{int(round(d/15))-1} tur)")

# ---- TEMIZLIK + DOGRULAMA ------------------------------------------------------
radar.HERE = _orij_here
shutil.rmtree(gecici, ignore_errors=True)
print()
print("=" * 66)
simdi_var = os.path.exists(GERCEK_BOSLUK)
kontrol("gercek radar_bosluk.jsonl'e yazim YOK", simdi_var == vardi_once,
        f"once={vardi_once} sonra={simdi_var}")
print(f"SONUC: {'HEPSI GECTI' if hata == 0 else str(hata) + ' HATA'}")
sys.exit(1 if hata else 0)
