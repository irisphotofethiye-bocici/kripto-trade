#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SON 2 GUN VERI DENETIMI — bot verisini duzgun cekti mi?

⚠️ Bot 08-22 16:06'dan beri HALT_DUSUS. Beklenti:
   - radar.py AYRI zamanlanmis gorev  -> radar_archive DOLMAYA DEVAM ETMELI
   - izleyici.py AYRI gorev           -> pozisyon_izleme DOLMAYA DEVAM ETMELI
   - testbot turu kosar ama giris ARAMAZ -> testbot'un yazdigi aday kayitlari DURUR
   Bu ayrim onemli: "veri kesildi" ile "tarama durdu" ayni sey DEGIL.

radar_archive.jsonl context'e YUKLENMEZ (75+ MB) — burada toplanip ozet basilir.
SALT OKUMA.
"""
import os, json, datetime, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "%Y-%m-%d %H:%M:%S"
SIMDI = datetime.datetime.now()
BAS = SIMDI - datetime.timedelta(days=2)


def zaman(x):
    for k in ("ts", "zaman", "guncelleme"):
        v = x.get(k)
        if isinstance(v, str):
            for f in (F, "%Y-%m-%d %H:%M"):
                try:
                    return datetime.datetime.strptime(v, f)
                except Exception:
                    pass
    return None


def tara(yol, pencere=True):
    """-> (pencere_kayitlari_zamanlari, toplam_satir, bozuk_satir)"""
    p = os.path.join(PROJE, yol)
    if not os.path.exists(p):
        return None, 0, 0
    zs, n, boz = [], 0, 0
    with open(p, encoding="utf-8") as f:
        for s in f:
            s = s.strip()
            if not s:
                continue
            n += 1
            try:
                x = json.loads(s)
            except Exception:
                boz += 1
                continue
            t = zaman(x)
            if t and (not pencere or t >= BAS):
                zs.append(t)
    return sorted(zs), n, boz


def bosluk_raporu(ad, zs, beklenen_dk, esik_kat=2.5):
    if not zs:
        print("   %-26s PENCEREDE KAYIT YOK" % ad)
        return
    tek = sorted(set(zs))
    araliklar = [(tek[i + 1] - tek[i]).total_seconds() / 60 for i in range(len(tek) - 1)]
    buyuk = [a for a in araliklar if a > beklenen_dk * esik_kat]
    kapsam = 100.0
    if araliklar:
        toplam = (tek[-1] - tek[0]).total_seconds() / 60
        kayip = sum(a - beklenen_dk for a in buyuk)
        kapsam = 100.0 * (1 - kayip / toplam) if toplam > 0 else 100.0
    print("   %-26s kayit %6d  tekil an %5d  ilk %s  son %s"
          % (ad, len(zs), len(tek), tek[0].strftime("%m-%d %H:%M"),
             tek[-1].strftime("%m-%d %H:%M")))
    if araliklar:
        med = sorted(araliklar)[len(araliklar) // 2]
        print("   %-26s medyan aralik %5.1f dk (beklenen %.1f) · %d bosluk > %.0f dk · kapsam %%%.1f"
              % ("", med, beklenen_dk, len(buyuk), beklenen_dk * esik_kat, kapsam))
        if buyuk:
            en = sorted(buyuk, reverse=True)[:3]
            print("   %-26s en buyuk bosluklar: %s dk"
                  % ("", ", ".join("%.0f" % a for a in en)))
    gecikme = (SIMDI - tek[-1]).total_seconds() / 60
    print("   %-26s son kayittan bu yana %.1f dk  ->  %s"
          % ("", gecikme, "TAZE" if gecikme < beklenen_dk * 3 else "BAYAT"))


print("SON 2 GUN VERI DENETIMI  (%s .. %s)" % (BAS.strftime("%m-%d %H:%M"),
                                               SIMDI.strftime("%m-%d %H:%M")))
print("=" * 96)
print("\n1) AKIS SUREKLILIGI")
for ad, yol, dk in (("radar_archive", "radar_archive.jsonl", 15),
                    ("pozisyon_izleme", "pozisyon_izleme.jsonl", 5),
                    ("testbot_equity (tur)", "testbot_equity.jsonl", 7.5),
                    ("testbot_aday_arsiv", "testbot_aday_arsiv.jsonl", 7.5),
                    ("veto_log", "veto_log.jsonl", 7.5)):
    zs, n, boz = tara(yol)
    if zs is None:
        print("   %-26s DOSYA YOK" % ad)
        continue
    if boz:
        print("   %-26s ⚠️ BOZUK SATIR: %d" % (ad, boz))
    bosluk_raporu(ad, zs, dk)
    print()

print("2) ISARETLENMIS BOSLUKLAR (radar_bosluk.jsonl)")
p = os.path.join(PROJE, "radar_bosluk.jsonl")
if os.path.exists(p):
    kb = []
    with open(p, encoding="utf-8") as f:
        for s in f:
            if s.strip():
                try:
                    kb.append(json.loads(s))
                except Exception:
                    pass
    pen = [x for x in kb if zaman(x) and zaman(x) >= BAS]
    print("   toplam kayit %d · pencerede %d" % (len(kb), len(pen)))
    for x in pen[-8:]:
        print("      %s" % json.dumps(x, ensure_ascii=False)[:110])
else:
    print("   dosya YOK")

print("\n3) ALAN DOLULUGU — pozisyon_izleme, son 2 gun vs TUM tarih")
p = os.path.join(PROJE, "pozisyon_izleme.jsonl")
if os.path.exists(p):
    pen_say, tum_say = collections.Counter(), collections.Counter()
    pen_n = tum_n = 0
    with open(p, encoding="utf-8") as f:
        for s in f:
            if not s.strip():
                continue
            try:
                x = json.loads(s)
            except Exception:
                continue
            t = zaman(x)
            tum_n += 1
            for k, v in x.items():
                if v is not None:
                    tum_say[k] += 1
            if t and t >= BAS:
                pen_n += 1
                for k, v in x.items():
                    if v is not None:
                        pen_say[k] += 1
    onemli = ["pnl_pct", "fiyat", "chg24", "funding", "score", "taker_15", "taker_60",
              "d_taker", "hacim_15_usdt", "hacim_x", "islem_15", "oi3", "oi24",
              "top_ls", "glob_ls", "smart", "taker", "vol_x", "pos", "mfe_pct",
              "mae_pct", "stopa_uzaklik_pct", "derinlik_giriste", "defter_usdt_20"]
    print("   pencere kayit %d · tum tarih %d" % (pen_n, tum_n))
    print("   %-20s %10s %10s   %s" % ("alan", "2 gun", "tum", "durum"))
    for k in onemli:
        a = 100.0 * pen_say.get(k, 0) / pen_n if pen_n else 0
        b = 100.0 * tum_say.get(k, 0) / tum_n if tum_n else 0
        bayrak = ""
        if pen_n and a < 50 and b >= 80:
            bayrak = "  <<< PENCEREDE DUSTU"
        elif pen_n and a == 0:
            bayrak = "  <<< HIC YOK"
        print("   %-20s %9.1f%% %9.1f%%%s" % (k, a, b, bayrak))
else:
    print("   dosya YOK")

print("\n4) RADAR — pencerede kac SEMBOL tarandi (kapsam daralmis mi)")
p = os.path.join(PROJE, "radar_archive.jsonl")
if os.path.exists(p):
    gun_sym = collections.defaultdict(set)
    alan_dolu = collections.Counter()
    n = 0
    with open(p, encoding="utf-8") as f:
        for s in f:
            if not s.strip():
                continue
            try:
                x = json.loads(s)
            except Exception:
                continue
            t = zaman(x)
            if not t or t < BAS - datetime.timedelta(days=3):
                continue
            gun_sym[t.strftime("%m-%d")].add(x.get("sym"))
            if t >= BAS:
                n += 1
                for k in ("score", "stage", "pos", "chg24", "funding", "oi3", "oi24",
                          "top_ls", "glob_ls", "smart", "taker", "vol_x", "rejim"):
                    if x.get(k) is not None:
                        alan_dolu[k] += 1
    for g in sorted(gun_sym)[-5:]:
        print("   %s : %4d tekil sembol" % (g, len(gun_sym[g])))
    if n:
        print("   pencerede %d kayit · alan dolulugu:" % n)
        for k, v in sorted(alan_dolu.items(), key=lambda z: -z[1]):
            print("      %-10s %5.1f%%" % (k, 100.0 * v / n))
else:
    print("   dosya YOK")

print("\nSALT OKUMA — bot dosyalarina yazim: YOK")
