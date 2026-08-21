#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GERIYE DONUK BOSLUK HARITASI — radar_archive'in delik yerleri isaretlenir.

NEDEN: radar.py bosluk kaydini 2026-08-17 23:15'te (commit 08d7d59) ogrendi.
O tarihten SONRA hic bosluk olmadi -> dosya hic olusmadi. Ama ONCESINDE
86 bosluk var ve hepsi ISARETSIZ. CLAUDE.md: "radar_archive NOKTASAL veridir,
radar_bosluk.jsonl de okunur; yoksa eksik pencerede calisildigi FARK EDILMEZ."

Boskluklarin sebebi olculdu degil, KULLANICI BEYANI: PC kapaliydi.

radar.py'ye DOKUNULMAZ (kodu dogru). radar_archive'a DOKUNULMAZ (salt okuma).
Yalniz radar_bosluk.jsonl'e `kaynak: "geriye_donuk"` alanli kayit eklenir;
canli kayitlar (kaynak alani YOK) ayirt edilebilir kalir.
"""
import os, sys, json, datetime

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARSIV = os.path.join(PROJE, "radar_archive.jsonl")
BOSLUK = os.path.join(PROJE, "radar_bosluk.jsonl")
BEKLENEN_TUR_DK = 15.0          # radar.py ile AYNI
ESIK_KAT = 2.0                  # radar.py ile AYNI
F = "%Y-%m-%d %H:%M"


def tur_damgalari():
    ts, onceki = [], None
    with open(ARSIV, encoding="utf-8") as f:
        for satir in f:
            if not satir.strip():
                continue
            try:
                t = json.loads(satir)["ts"]
            except Exception:
                continue
            if t != onceki:
                ts.append(t)
                onceki = t
    return sorted({datetime.datetime.strptime(t[:16], F) for t in ts})


def mevcut_kayitlar():
    if not os.path.exists(BOSLUK):
        return set()
    var = set()
    with open(BOSLUK, encoding="utf-8") as f:
        for satir in f:
            if satir.strip():
                try:
                    var.add(json.loads(satir)["ts"])
                except Exception:
                    pass
    return var


if __name__ == "__main__":
    kuru = "--yaz" not in sys.argv
    d = tur_damgalari()
    var = mevcut_kayitlar()
    yeni = []
    for i in range(1, len(d)):
        dk = (d[i] - d[i - 1]).total_seconds() / 60.0
        if dk <= BEKLENEN_TUR_DK * ESIK_KAT:
            continue
        ts = d[i].strftime("%Y-%m-%d %H:%M:00")
        if ts in var:
            continue
        yeni.append({"ts": ts, "onceki_ts": d[i - 1].strftime("%Y-%m-%d %H:%M:00"),
                     "bosluk_dk": round(dk, 1), "beklenen_tur_dk": BEKLENEN_TUR_DK,
                     "kayip_tur_tahmini": max(0, int(round(dk / BEKLENEN_TUR_DK)) - 1),
                     "kaynak": "geriye_donuk"})
    kapsam = (d[-1] - d[0]).total_seconds() / 60 / BEKLENEN_TUR_DK
    kayip = sum(x["kayip_tur_tahmini"] for x in yeni)
    print("radar_archive : %s -> %s" % (d[0], d[-1]))
    print("gerceklesen tur: %d   ·   beklenen: %d" % (len(d), kapsam))
    print("yeni bosluk kaydi: %d   ·   tahmini kayip tur: %d (%%%.1f)"
          % (len(yeni), kayip, 100 * kayip / kapsam))
    print("toplam kayip sure: %.1f saat" % (sum(x["bosluk_dk"] for x in yeni) / 60))
    if yeni:
        print("\nen buyuk 6:")
        for x in sorted(yeni, key=lambda z: -z["bosluk_dk"])[:6]:
            print("   %s -> %s  %7.1f dk (%.1f saat)"
                  % (x["onceki_ts"][:16], x["ts"][:16], x["bosluk_dk"], x["bosluk_dk"] / 60))
    if kuru:
        print("\nKURU KOSUM — dosyaya YAZILMADI. Yazmak icin: --yaz")
    else:
        with open(BOSLUK, "a", encoding="utf-8") as f:
            for x in sorted(yeni, key=lambda z: z["ts"]):
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print("\n%s dosyasina %d kayit eklendi (kaynak: geriye_donuk)" % (BOSLUK, len(yeni)))
    print("radar_archive'a yazim: YOK · radar.py degismedi")
