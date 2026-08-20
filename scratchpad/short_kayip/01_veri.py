#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERI KURULUMU — 11 Agustos sonrasi kapanmis pozisyonlar + giris ani alanlari.

SALT OKUMA. Yalnizca scratchpad/short_kayip/ altina yazar.

KURALLAR (CLAUDE.md):
  - P&L TOPLARKEN `kismi` suzgeci UYGULANMAZ; kayitlar `id` ile birlestirilir.
    (Suzgec SAYMAK icindir; toplamda uygulanirsa TP1'de realize edilen kar kaybolur.)
  - Pozisyon SAYARKEN her `id` bir pozisyondur.
  - Iki taban ayri uretilir (muhasebe 11 Agu 12:48 / hakem 12 Agu 01:17) —
    CLAUDE.md'deki "iki taban" tuzagi.

CIKTI: pozisyonlar.json  -> her pozisyon icin tek satir
"""
import json, os, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))

TABANLAR = {
    "muhasebe_11agu": datetime.datetime(2026, 8, 11, 12, 48),
    "hakem_12agu":    datetime.datetime(2026, 8, 12, 1, 17),
}
# Sicrama kesimi: BTC 17->18 Agustos'ta kirilim yapti; 08-18'de SHORT girisi SIFIR
# (fren o gun acikti), yani ayrim dogal olarak 08-17 sonu / 08-19 basi.
SICRAMA = datetime.datetime(2026, 8, 18)

ADAY_ALAN = ["score", "stage", "comp", "vol_x", "oi24", "oi3", "funding", "pos",
             "last1", "last3", "chg24", "mcap", "dip_yakit", "ayrisma", "rel3",
             "btc_chg3", "rejim", "top_ls", "glob_ls", "taker", "smart",
             "float_oran", "dusuk_float", "ma50_mesafe", "price"]

DEFTER_ALAN = ["kaldirac", "marjin", "notional", "skor_giriste", "smart_giriste",
               "chg24_giriste", "range_pos_giriste", "stage_giriste",
               "rejim_giriste", "funding_usdt", "derinlik_giriste"]


def kapi_adi(sebep):
    """sebep_giris metnini KAPI etiketine indirger."""
    s = (sebep or "")
    if s.startswith("GOLGE"):
        return "golge"
    if "A+B" in s and "MA50" in s:
        return "A+B & MA50"
    if "MA50+ucuz" in s or "MA50" in s:
        return "MA50+ucuz"
    if "A+B" in s or "funding" in s.lower():
        return "A+B funding"
    if "NOTR-belirsiz" in s:
        return "NOTR-belirsiz"
    if "AAVE" in s:
        return "AYI-AAVE"
    return "diger"


def yukle():
    kay = collections.defaultdict(list)
    with open(os.path.join(PROJE, "testbot_islemler.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            x = json.loads(line)
            kay[x["id"]].append(x)

    aday = collections.defaultdict(list)
    with open(os.path.join(PROJE, "testbot_aday_arsiv.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            x = json.loads(line)
            if x.get("sonuc") == "ACILDI":
                aday[x["sym"]].append(x)

    poz = []
    for pid, rs in kay.items():
        rs = sorted(rs, key=lambda z: z["ts"])
        ilk, son = rs[0], rs[-1]
        cikis_dt = datetime.datetime.strptime(son["ts"], "%Y-%m-%d %H:%M:%S")
        giris_dt = cikis_dt - datetime.timedelta(hours=son.get("tutma_saat") or 0)
        # P&L: TUM kayitlarin toplami (kismi DAHIL) -- CLAUDE.md
        pnl = sum(r.get("sonuc_usdt") or 0 for r in rs)
        d = {
            "id": pid, "sym": ilk["sym"], "yon": ilk["yon"],
            "giris_ts": giris_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "cikis_ts": son["ts"], "pnl": round(pnl, 4),
            "n_kayit": len(rs), "kismi_var": any(r.get("kismi") for r in rs),
            "sebep_cikis": son.get("sebep"), "tutma_saat": son.get("tutma_saat"),
            "giris_fiyat": ilk.get("giris"), "cikis_fiyat": son.get("cikis"),
            "kapi": kapi_adi(ilk.get("sebep_giris")),
            "sebep_giris": ilk.get("sebep_giris"),
            "donem": "oncesi" if giris_dt < SICRAMA else "sonrasi",
        }
        for a in DEFTER_ALAN:
            d["d_" + a] = ilk.get(a)
        # aday arsiviyle esle
        c = aday.get(ilk["sym"], [])
        en, fark = None, None
        for x in c:
            t = datetime.datetime.strptime(x["ts"], "%Y-%m-%d %H:%M")
            dd = abs((t - giris_dt).total_seconds())
            if fark is None or dd < fark:
                en, fark = x, dd
        if en is not None and fark <= 900:
            d["eslesti"] = True
            d["aday_ts"] = en["ts"]
            d["eslesme_dk"] = round(fark / 60, 2)
            for a in ADAY_ALAN:
                d["a_" + a] = en.get(a)
        else:
            d["eslesti"] = False
        poz.append(d)
    return poz


def main():
    poz = yukle()
    cikti = {}
    print("VERI KURULUMU — 11 Agustos sonrasi kapanmis pozisyonlar")
    print("=" * 74)
    for ad, taban in TABANLAR.items():
        alt = [p for p in poz
               if datetime.datetime.strptime(p["giris_ts"], "%Y-%m-%d %H:%M:%S") >= taban]
        cikti[ad] = alt
        s = [p for p in alt if p["yon"] == "SHORT"]
        l = [p for p in alt if p["yon"] == "LONG"]
        es = sum(1 for p in alt if p["eslesti"])
        print("\n--- TABAN %s  (%s)" % (ad, taban.strftime("%d %b %H:%M")))
        print("  pozisyon %d   SHORT %d (%+.2f)   LONG %d (%+.2f)"
              % (len(alt), len(s), sum(p["pnl"] for p in s),
                 len(l), sum(p["pnl"] for p in l)))
        print("  aday arsivi eslesmesi: %d/%d  (%%%.1f)" % (es, len(alt), 100 * es / len(alt)))
        for yon, g in (("SHORT", s), ("LONG", l)):
            for dn in ("oncesi", "sonrasi"):
                gg = [p for p in g if p["donem"] == dn]
                if gg:
                    kz = sum(1 for p in gg if p["pnl"] > 0)
                    print("    %-5s %-8s N=%3d  toplam %+9.2f  kazanan %2d (%%%.0f)"
                          % (yon, dn, len(gg), sum(p["pnl"] for p in gg), kz,
                             100 * kz / len(gg)))
        # DOGRULAMA 2: ayni toplam IKINCI yoldan (gun gun kumulatif)
        gun = collections.defaultdict(float)
        for p in alt:
            gun[p["giris_ts"][:10]] += p["pnl"]
        t1 = sum(p["pnl"] for p in alt)
        t2 = sum(gun.values())
        print("  [dogrulama] id-toplami %+.4f  vs  gun-kumulatifi %+.4f  ->  %s"
              % (t1, t2, "TUTTU" if abs(t1 - t2) < 0.01 else "TUTMADI!"))
        # DOGRULAMA 3: kismi kayitlar kayboluyor mu
        km = [p for p in alt if p["kismi_var"]]
        print("  [dogrulama] kismi kar iceren pozisyon: %d  (bunlarin toplami %+.2f)"
              % (len(km), sum(p["pnl"] for p in km)))

    yol = os.path.join(HERE, "pozisyonlar.json")
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False)
    print("\nyazildi: %s" % yol)
    print("bot dosyalarina yazim: YOK (yalniz scratchpad/short_kayip/)")


if __name__ == "__main__":
    main()
