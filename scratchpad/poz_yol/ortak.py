#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POZISYON YOLU — veri yukleyici ve birlestirici.

UC KAYNAK, UC AYRI DOGA — karistirilmadan birlestirilir:

  1) pozisyon_izleme.jsonl   5 dk · 78 alan · 2026-08-13 19:32 -> simdi
     ⚠️ ALANLARIN HEPSI CANLI DEGIL. Olculdu (68 pozisyon, >=20 goruntu,
        pozisyon icindeki benzersiz deger orani):
           fiyat/pnl_pct %77 · hacim_* %94-100 · taker_15/60 · d_taker %96-98
           chg24 %98 · funding %57 · score %56          -> CANLI
           oi3/oi24 %10 · top_ls/glob_ls %7 · vol_x %8  -> DONMUS (radar temposu)
        Cunku izleyici.py:355-362 bu alanlari radar kaydindan KOPYALIYOR.
        Bu yuzden OI ve long/short BURADAN OKUNMAZ -> (2)'den gelir.

  2) scratchpad/perp_seri/   5 dk · Binance futures/data · 29 gunluk pencere
     oi · top_ls · glob_ls · taker · kline(5m, tbv dahil)
     ⚠️ Binance bu uclari SABIT 30 GUN tutuyor. Pencere kayiyor.

  3) testbot_islemler.jsonl  pozisyonun SONUCU (kapanis kaydi/kayitlari)
     ⚠️ TP1_KISMI satirlari pozisyonu BOLER. Sayarken kismi haric, TOPLARKEN
        dahil (CLAUDE.md: "suzgec saymak icindir, toplamak icin degil").

SALT OKUMA. Bot dosyalarina yazmaz.
"""
import json, os, sys, bisect, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
SERI = os.path.join(SCRATCH, "perp_seri")

IZLEME = os.path.join(PROJE, "pozisyon_izleme.jsonl")
ISLEMLER = os.path.join(PROJE, "testbot_islemler.jsonl")
DURUM = os.path.join(PROJE, "testbot_state.json")

F = "%Y-%m-%d %H:%M:%S"

# izleyici'nin KENDI hesapladigi, 5 dk tazelenen alanlar (yukaridaki olcume gore)
CANLI_ALAN = ["pnl_pct", "pnl_r", "fiyat", "d_pnl_pct", "chg24", "funding", "score",
              "taker_15", "taker_60", "d_taker", "hacim_15_usdt", "hacim_60_usdt",
              "hacim_x", "hacim_dakika", "islem_15", "ort_islem_usdt",
              "stopa_uzaklik_pct", "hedefe_uzaklik_pct", "mfe_pct", "mae_pct"]

# radar'dan KOPYALANAN — izlemeden okunursa yaniltir, perp_seri'den gelir
DONMUS_ALAN = ["oi3", "oi24", "top_ls", "glob_ls", "taker", "vol_x", "pos", "atr_canli"]


def _ms(ts_str):
    return int(datetime.datetime.strptime(ts_str, F).timestamp() * 1000)


def sonuclar():
    """id -> {sym, yon, net_usdt, sebep, kapanis_ts, kismi_var, r, kapi, rejim, chg24_giriste}

    net_usdt kismi kayitlari DAHIL toplar; 'sebep' NIHAI kapanisin sebebidir."""
    g = collections.defaultdict(list)
    with open(ISLEMLER, encoding="utf-8") as fh:
        for satir in fh:
            if satir.strip():
                x = json.loads(satir)
                g[x["id"]].append(x)
    out = {}
    for i, v in g.items():
        v.sort(key=lambda z: z["ts"])
        son = v[-1]
        out[i] = {"sym": son["sym"], "yon": son["yon"],
                  "net_usdt": sum(t.get("sonuc_usdt") or 0 for t in v),
                  "sebep": son["sebep"], "kapanis_ts": son["ts"],
                  "kismi_var": any(t.get("kismi") for t in v),
                  "r": son.get("r"), "kaynak": son.get("kaynak"),
                  "rejim_giriste": son.get("rejim_giriste"),
                  "chg24_giriste": son.get("chg24_giriste"),
                  "smart_giriste": son.get("smart_giriste"),
                  "tutma_saat": max(t.get("tutma_saat") or 0 for t in v),
                  "giris": son.get("giris"), "cikis": son.get("cikis")}
    return out


def izleme_serileri():
    """id -> [anlik goruntu]  (zamana gore sirali, YALNIZ canli alanlar guvenilir)"""
    poz = collections.defaultdict(list)
    with open(IZLEME, encoding="utf-8") as fh:
        for satir in fh:
            if not satir.strip():
                continue
            try:
                x = json.loads(satir)
            except Exception:
                continue
            if x.get("id") is not None:
                poz[x["id"]].append(x)
    for v in poz.values():
        v.sort(key=lambda z: z["ts"])
    return dict(poz)


_SERI_ONBELLEK = {}


def perp_seri(sym, uc):
    """perp_seri/{sym}_{uc}.json -> [(t_ms, deger_dict)] zamana gore sirali. Yoksa []."""
    anahtar = (sym, uc)
    if anahtar in _SERI_ONBELLEK:
        return _SERI_ONBELLEK[anahtar]
    yol = os.path.join(SERI, "%s_%s.json" % (sym, uc))
    out = []
    if os.path.exists(yol):
        try:
            with open(yol, encoding="utf-8") as f:
                d = json.load(f)
            zaman = "t" if uc == "kline" else "timestamp"
            out = sorted(((int(x[zaman]), x) for x in d), key=lambda z: z[0])
        except Exception:
            out = []
    _SERI_ONBELLEK[anahtar] = out
    return out


def _en_yakin(seri, t_ms, tolerans_dk=10):
    """seri icinde t_ms'e en yakin kaydi dondurur (tolerans disindaysa None).

    NEDEN TOLERANS: 5 dk izgarada eslesmeyen an, en yakin bar ile doldurulur;
    ama boslukta 'en yakin' saatler oteye dusebilir -> sessizce yanlis eslesme."""
    if not seri:
        return None
    ts = [z[0] for z in seri]
    i = bisect.bisect_left(ts, t_ms)
    aday = []
    if i < len(ts):
        aday.append(seri[i])
    if i > 0:
        aday.append(seri[i - 1])
    if not aday:
        return None
    en = min(aday, key=lambda z: abs(z[0] - t_ms))
    return en[1] if abs(en[0] - t_ms) <= tolerans_dk * 60000 else None


def zenginlestir(goruntu, sym):
    """Bir izleme anlik goruntusune perp_seri'den GERCEK OI/long-short/taker ekler.

    Yeni alanlar '_s' ekiyle yazilir ki izleyici'nin DONMUS alanlariyla
    karistirilmasin: oi_s · oi_deger_s · top_ls_s · glob_ls_s · taker_orani_s ·
    hacim_5m_s · taker_alis_5m_s."""
    t = _ms(goruntu["ts"])
    out = dict(goruntu)
    x = _en_yakin(perp_seri(sym, "oi"), t)
    if x:
        out["oi_s"] = float(x["sumOpenInterest"])
        out["oi_deger_s"] = float(x["sumOpenInterestValue"])
    x = _en_yakin(perp_seri(sym, "top_ls"), t)
    if x:
        out["top_ls_s"] = float(x["longShortRatio"])
    x = _en_yakin(perp_seri(sym, "glob_ls"), t)
    if x:
        out["glob_ls_s"] = float(x["longShortRatio"])
    x = _en_yakin(perp_seri(sym, "taker"), t)
    if x:
        out["taker_orani_s"] = float(x["buySellRatio"])
        out["taker_alis_5m_s"] = float(x["buyVol"])
        out["taker_satis_5m_s"] = float(x["sellVol"])
    x = _en_yakin(perp_seri(sym, "kline"), t)
    if x:
        out["hacim_5m_s"] = x["qv"]
        out["tbv_5m_s"] = x["tqv"]
        out["kapanis_5m_s"] = x["c"]
    return out


def pozisyonlar(en_az_goruntu=10, yalniz_kapali=True, zengin=True):
    """-> [{"id","sonuc","seri"}]  seri = zenginlestirilmis anlik goruntuler."""
    son = sonuclar()
    izl = izleme_serileri()
    out = []
    for i, v in izl.items():
        if yalniz_kapali and i not in son:
            continue
        if len(v) < en_az_goruntu:
            continue
        sym = v[0]["sym"]
        seri = [zenginlestir(g, sym) for g in v] if zengin else v
        out.append({"id": i, "sym": sym, "yon": v[0]["yon"],
                    "sonuc": son.get(i), "seri": seri})
    out.sort(key=lambda z: z["seri"][0]["ts"])
    return out


def kapsama_raporu():
    """perp_seri hangi pozisyonlari gercekten kapsiyor — sessiz eksik olmasin."""
    p = pozisyonlar(en_az_goruntu=1)
    tam, kismi, yok = 0, 0, 0
    for z in p:
        var = sum(1 for g in z["seri"] if "oi_s" in g)
        if var == len(z["seri"]):
            tam += 1
        elif var:
            kismi += 1
        else:
            yok += 1
    return {"pozisyon": len(p), "OI_tam": tam, "OI_kismi": kismi, "OI_yok": yok}


if __name__ == "__main__":
    r = kapsama_raporu()
    print("POZISYON YOLU — kapsama")
    for k, v in r.items():
        print("   %-10s %d" % (k, v))
    p = pozisyonlar()
    print("\nen az 10 goruntulu kapali pozisyon: %d" % len(p))
    if p:
        z = p[len(p) // 2]
        print("ornek id%d %s %s · %d goruntu · sonuc %+.2f$ (%s)"
              % (z["id"], z["sym"], z["yon"], len(z["seri"]),
                 z["sonuc"]["net_usdt"], z["sonuc"]["sebep"]))
        g = z["seri"][0]
        yeni = sorted(k for k in g if k.endswith("_s"))
        print("perp_seri'den eklenen alanlar: %s" % (yeni or "YOK — indirme bitmemis olabilir"))
        sys.stdout.flush()
