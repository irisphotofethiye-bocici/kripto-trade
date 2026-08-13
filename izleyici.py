#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POZISYON IZLEYICI — acik pozisyonun "hangi durumda inip ciktigi" (2026-08-13, kullanici karari).

SORDUGU SORU: bot bir pozisyondayken o coinin radar olcumleri ne diyor, ve pozisyon
    o anda ne yapiyor? Kapanisa kadar her karesi kaydedilirse sonradan sorulabilir:
    "hangi kosulda poz iniyor, hangi kosulda cikiyor?"

NEDEN BU VERI YOKTU: testbot._cikar_havuzdan (testbot.py:962) acik pozisyonu olan
    sembolleri tarama havuzundan CIKARIYOR. Yani bot bir coine girdigi andan itibaren
    onu bir daha olcmuyor. Giriste ne gordugunu biliyoruz, girisTEN SONRA ne oldugunu
    bilmiyorduk.

NEDEN AYRI SUREC: botun turu zaten sinirda (son 14 turun 4'u 7,5 dakikayi asmis).
    Bu betik AYRI zamanli gorev olarak kosar; botun tur suresine SIFIR etkisi vardir
    ve cokerse bot bundan haberdar bile olmaz.

RISK: YOK. testbot_state.json'i yalnizca OKUR. Botun hicbir dosyasina yazmaz,
    testbot._DEFTER'e DOKUNMAZ, bildirim GONDERMEZ. Kendi uc dosyasi disina cikmaz.

DOSYALAR
    pozisyon_izleme.jsonl : her calistirmada her acik pozisyon icin BIR satir
    pozisyon_ozet.jsonl   : pozisyon kapandiginda TEK ozet satir
    izleyici_state.json   : calistirmalar arasi biriken sayaclar (ATOMIK yazilir)

Kullanim:
    python izleyici.py --once            zamanli gorev bunu cagirir
    python izleyici.py --once --kuru     hicbir dosyaya yazmadan ekrana bas
    python izleyici.py --doldur          tek seferlik: gecmis pozisyonlari 1m mumlardan doldur
    python izleyici.py --durum           toplanan verinin ozeti
"""
import json, os, sys, argparse, datetime, time

import testbot
import radar
import evren

HERE = os.path.dirname(os.path.abspath(__file__))
IZLEME = os.path.join(HERE, "pozisyon_izleme.jsonl")
OZET = os.path.join(HERE, "pozisyon_ozet.jsonl")
STATEF = os.path.join(HERE, "izleyici_state.json")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ---------- durum dosyasi ----------

def yukle():
    try:
        return json.load(open(STATEF, encoding="utf-8"))
    except Exception:
        return {"pozisyonlar": {}, "son_calisma": None}


def kaydet(st):
    """ATOMIK. [DERS 2026-08-12] golge.py duz json.dump kullaniyordu; bir tur kayitlari
    yazdi ama durumu kaydedemedi -> ayni pozisyon iki kez kapandi, defter 314$ sapti."""
    gecici = STATEF + ".tmp"
    with open(gecici, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=2)
        fh.flush(); os.fsync(fh.fileno())
    os.replace(gecici, STATEF)


# ---------- yardimcilar ----------

def kapi_adi(sebep):
    s = str(sebep or "")
    if s.startswith("A+B"):
        return "A+B"
    if s.startswith("MA50"):
        return "MA50+ucuz"
    return (s.split(":")[0] or "?")[:16]


def yon_isaret(yon):
    return 1 if yon == "LONG" else -1


def pnl_yuzde(giris, fiyat, yon):
    """Girise gore YON DUZELTILMIS yuzde hareket. SHORT'ta fiyat dusunce artar."""
    if not giris:
        return 0.0
    return (fiyat - giris) / giris * 100 * yon_isaret(yon)


def mumlari_ozetle(barlar, giris, yon, birik):
    """1 dakikalik mumlardan sayaclari GUNCELLE (birikimli, yerinde degistirir).

    arti/eksi dakika : her barin KAPANISI girisin lehinde mi
    mfe/mae          : bar HIGH/LOW'larindan en iyi / en kotu uzanim
    Dakika cozunurlugu bilerek: 5 dakikada bir orneklemek 'ne kadar artida kaldi'yi
    kaba olcerdi. Maliyeti pozisyon basina 1 ek cagri."""
    isaret = yon_isaret(yon)
    for b in barlar:
        if b["t"] <= (birik.get("son_bar_t") or 0):
            continue          # ayni bari iki kez sayma
        birik["son_bar_t"] = b["t"]
        kap = pnl_yuzde(giris, b["c"], yon)
        if kap > 0:
            birik["arti_dakika"] = birik.get("arti_dakika", 0) + 1
        elif kap < 0:
            birik["eksi_dakika"] = birik.get("eksi_dakika", 0) + 1
        else:
            birik["notr_dakika"] = birik.get("notr_dakika", 0) + 1
        # lehte ucu: LONG'da high, SHORT'ta low
        leh = b["h"] if isaret > 0 else b["l"]
        aleyh = b["l"] if isaret > 0 else b["h"]
        m_leh, m_aleyh = pnl_yuzde(giris, leh, yon), pnl_yuzde(giris, aleyh, yon)
        ts = datetime.datetime.fromtimestamp(b["t"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        if m_leh > birik.get("mfe_pct", -10 ** 9):
            birik["mfe_pct"] = round(m_leh, 4); birik["tepe_ts"] = ts
        if m_aleyh < birik.get("mae_pct", 10 ** 9):
            birik["mae_pct"] = round(m_aleyh, 4); birik["dip_ts"] = ts
        if kap > birik.get("tepe_pnl_pct", -10 ** 9):
            birik["tepe_pnl_pct"] = round(kap, 4)
        if kap < birik.get("dip_pnl_pct", 10 ** 9):
            birik["dip_pnl_pct"] = round(kap, 4)
    return birik


def yeni_birik():
    return {"arti_dakika": 0, "eksi_dakika": 0, "notr_dakika": 0,
            "mfe_pct": -10 ** 9, "mae_pct": 10 ** 9,
            "tepe_pnl_pct": -10 ** 9, "dip_pnl_pct": 10 ** 9,
            "tepe_ts": None, "dip_ts": None, "son_bar_t": 0,
            "anlik_goruntu": 0, "son_pnl_pct": None}


def _temiz(b):
    """Sonsuz baslangic degerlerini disariya sizdirma."""
    o = dict(b)
    for k in ("mfe_pct", "tepe_pnl_pct"):
        if o.get(k) == -10 ** 9:
            o[k] = None
    for k in ("mae_pct", "dip_pnl_pct"):
        if o.get(k) == 10 ** 9:
            o[k] = None
    top = o.get("arti_dakika", 0) + o.get("eksi_dakika", 0) + o.get("notr_dakika", 0)
    o["toplam_dakika"] = top
    o["arti_oran"] = round(o.get("arti_dakika", 0) / top * 100, 1) if top else None
    o.pop("son_bar_t", None)
    return o


def tum_mumlar(sym, bas_ms, son_ms=None):
    """Uzun araliklar icin 1000'lik parcalar halinde 1 dakikalik mum ceker."""
    out, t = [], bas_ms
    son_ms = son_ms or int(time.time() * 1000)
    while t < son_ms:
        d = testbot.klines_since(sym, "1m", t, limit=1000)
        if not d:
            break
        d = [x for x in d if x["t"] <= son_ms]
        out += d
        if len(d) < 900:
            break
        yeni = d[-1]["t"] + 60000
        if yeni <= t:
            break
        t = yeni
        time.sleep(0.15)
    return out


# ---------- anlik goruntu ----------

def anlik_goruntu(pos, birik, btc_chg3, fiyat_harita, chg24_harita=None,
                  cg=None, kuru=False):
    """Tek pozisyon icin bir satir uretir. Cagiran try/except icinde tutmali."""
    sym, yon, giris = pos["sym"], pos["yon"], pos["giris"]
    fiyat = fiyat_harita.get(sym + "USDT") or testbot.fiyat_fapi(sym) or giris

    # --- 1 dakikalik mumlarla sayaclari guncelle ---
    bas = (birik.get("son_bar_t") or 0) + 60000
    if bas <= 60000:
        bas = testbot.to_ms(pos["giris_ts"])
    barlar = tum_mumlar(sym, bas)
    mumlari_ozetle(barlar, giris, yon, birik)

    # --- radar olcumu (mevcut arsivlerle AYNI sema) ---
    r = radar.analyze(sym, btc_chg3) or {}
    # radar.analyze bu alanlari BOS birakir; radar.py onlari yalnizca KISA LISTEYE
    # uygular (rate-limit dostu olsun diye). Pozisyon izlemede tam bu olculer —
    # agresor dengesi ve akilli para yonu — "poz neden hareket ediyor"un merkezinde,
    # o yuzden burada acikca dolduruluyor. Maliyeti pozisyon basina 3 ucretsiz cagri.
    try:
        r.update(radar.pillar_d(sym))
    except Exception:
        pass
    if chg24_harita and r.get("chg24") is None:
        r["chg24"] = chg24_harita.get(sym)
    if cg and sym in cg:
        c = cg[sym]
        mc, fo = c.get("mcap"), c.get("float_oran")
        r["mcap"] = f"${mc/1e6:.0f}M" if mc else None
        r["float_oran"] = fo
        r["dusuk_float"] = bool(fo is not None and fo < evren.esik("dusuk_float_oran", 0.25))

    pp = pnl_yuzde(giris, fiyat, yon)
    isaret = yon_isaret(yon)
    pnl_usd = (fiyat - giris) * pos["miktar"] * isaret
    risk = pos.get("risk_usdt") or 0
    stop, tp2 = pos.get("stop"), pos.get("tp2")
    stop_mesafe = abs(stop - giris) / giris * 100 if stop and giris else None
    d_pnl = None if birik.get("son_pnl_pct") is None else round(pp - birik["son_pnl_pct"], 4)
    yas = (testbot.now_dt() - testbot.parse_iso(pos["giris_ts"])).total_seconds() / 3600

    kayit = {
        "ts": testbot.now_iso(), "kaynak": "canli", "radar_izi": bool(r),
        # kimlik
        "id": pos["id"], "sym": sym, "yon": yon, "kapi": kapi_adi(pos.get("sebep_giris")),
        "giris_ts": pos["giris_ts"], "yas_saat": round(yas, 2),
        # pozisyon durumu
        "giris": giris, "fiyat": fiyat,
        "pnl_pct": round(pp, 4), "pnl_usd": round(pnl_usd, 2),
        "pnl_r": round(pnl_usd / risk, 3) if risk else None,
        "d_pnl_pct": d_pnl,
        "stop": stop, "tp2": tp2,
        "stopa_uzaklik_pct": round(abs(fiyat - stop) / fiyat * 100, 3) if stop and fiyat else None,
        "hedefe_uzaklik_pct": round(abs(tp2 - fiyat) / fiyat * 100, 3) if tp2 and fiyat else None,
        "stop_mesafe_pct": round(stop_mesafe, 3) if stop_mesafe else None,
        "tp1_alindi": pos.get("tp1_alindi"), "marjin": pos.get("marjin"),
        "miktar": pos.get("miktar"), "kaldirac": pos.get("kaldirac"),
        "notional": round(pos["miktar"] * giris, 2),
        "atr_canli": pos.get("atr_canli"), "atr_giriste": pos.get("atr_giriste"),
        # radar olcumu
        "score": r.get("score"), "stage": r.get("stage"), "comp": r.get("comp"),
        "vol_x": r.get("vol_x"), "pos": r.get("pos"),
        "last1": r.get("last1"), "last3": r.get("last3"), "chg24": r.get("chg24"),
        "funding": r.get("funding"), "oi24": r.get("oi24"), "oi3": r.get("oi3"),
        "taker": r.get("taker"), "smart": r.get("smart"),
        "ma50_mesafe": r.get("ma50_mesafe"), "rel3": r.get("rel3"),
        "ayrisma": r.get("ayrisma"), "dip_yakit": r.get("dip_yakit"),
        "float_oran": r.get("float_oran"), "dusuk_float": r.get("dusuk_float"),
        "top_ls": r.get("top_ls"), "glob_ls": r.get("glob_ls"), "mcap": r.get("mcap"),
        "btc_chg3": btc_chg3,
    }
    kayit.update({k: v for k, v in _temiz(birik).items()
                  if k not in ("anlik_goruntu", "son_pnl_pct")})
    if not kuru:
        birik["son_pnl_pct"] = round(pp, 4)
        birik["anlik_goruntu"] = birik.get("anlik_goruntu", 0) + 1
    return kayit


# ---------- kapanis ozeti ----------

def _islem_sonucu(pid):
    """Kapanan pozisyonun sonucunu botun defterinden id ile eslestir."""
    try:
        kay = [json.loads(l) for l in
               open(testbot.ISLEMLERF, encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        return {}
    v = [k for k in kay if k.get("id") == pid]
    if not v:
        return {}
    son = [k for k in v if not k.get("kismi")]
    s = son[-1] if son else v[-1]
    return {"sonuc_sebep": s.get("sebep"), "sonuc_ts": s.get("ts"),
            "sonuc_usdt": round(sum(k["sonuc_usdt"] for k in v), 2),
            "sonuc_r": s.get("r"), "tutma_saat": s.get("tutma_saat"),
            "kismi_alindi": any(k.get("kismi") for k in v)}


def ozet_yaz(pid, kap, kuru=False):
    kayit = {"ts": testbot.now_iso(), "kaynak": kap.get("kaynak", "canli"),
             "id": int(pid), "sym": kap.get("sym"), "yon": kap.get("yon"),
             "kapi": kap.get("kapi"), "giris_ts": kap.get("giris_ts"),
             "giris": kap.get("giris"),
             "radar_izi": kap.get("radar_izi", True),
             "anlik_goruntu_sayisi": kap.get("birik", {}).get("anlik_goruntu", 0),
             "giris_radar": kap.get("giris_radar"), "son_radar": kap.get("son_radar")}
    kayit.update(_temiz(kap.get("birik") or {}))
    kayit.pop("son_pnl_pct", None); kayit.pop("anlik_goruntu", None)
    kayit.update(_islem_sonucu(int(pid)))
    if not kuru:
        testbot._append_jsonl(OZET, kayit)
    return kayit


# ---------- ana akis ----------

def tur(kuru=False):
    bst = testbot._load_state()
    if not bst:
        print("Bot durumu okunamadi."); return
    st = yukle()
    acik = {str(p["id"]): p for p in bst.get("acik_pozisyonlar") or []}
    izlenen = st.get("pozisyonlar") or {}

    try:
        btc_chg3, _ = radar.btc_ref()
    except Exception:
        btc_chg3 = 0.0
    fiyatlar = testbot._tum_fiyatlar() or {}
    # TEK cagriyla butun 24s degisimler + onbellekli CoinGecko evreni (mcap/float)
    chg24 = {}
    try:
        for t in (evren.raw_tickers("fapi") or []):
            s = t.get("symbol", "")
            if s.endswith("USDT"):
                chg24[s[:-4]] = round(float(t.get("priceChangePercent") or 0), 3)
    except Exception:
        pass
    try:
        cg = evren.cg_universe() or {}
    except Exception:
        cg = {}

    yazildi = 0
    for pid, pos in acik.items():
        try:
            kap = izlenen.get(pid)
            if not kap:
                kap = {"sym": pos["sym"], "yon": pos["yon"], "kapi": kapi_adi(pos.get("sebep_giris")),
                       "giris_ts": pos["giris_ts"], "giris": pos["giris"],
                       "birik": yeni_birik(), "giris_radar": None, "son_radar": None}
                izlenen[pid] = kap
            kayit = anlik_goruntu(pos, kap["birik"], btc_chg3, fiyatlar,
                                  chg24_harita=chg24, cg=cg, kuru=kuru)
            radar_ozet = {k: kayit.get(k) for k in
                          ("score", "stage", "comp", "vol_x", "pos", "funding", "oi24", "taker", "smart")}
            if kap.get("giris_radar") is None and kayit.get("radar_izi"):
                kap["giris_radar"] = radar_ozet
            if kayit.get("radar_izi"):
                kap["son_radar"] = radar_ozet
            if kuru:
                print(json.dumps(kayit, ensure_ascii=False, indent=2))
            else:
                testbot._append_jsonl(IZLEME, kayit)
            yazildi += 1
        except Exception as e:
            print(f"  {pos.get('sym')}: atlandi ({str(e)[:70]})")

    # --- kapananlar: izlenende var, botun acik listesinde YOK ---
    kapanan = [pid for pid in list(izlenen) if pid not in acik]
    for pid in kapanan:
        try:
            o = ozet_yaz(pid, izlenen[pid], kuru=kuru)
            print(f"  KAPANDI {o.get('sym')} -> ozet yazildi "
                  f"(arti {o.get('arti_dakika')}dk / eksi {o.get('eksi_dakika')}dk, "
                  f"sonuc {o.get('sonuc_sebep')} {o.get('sonuc_usdt')}$)")
            if not kuru:
                izlenen.pop(pid, None)
        except Exception as e:
            print(f"  ozet yazilamadi (id={pid}): {str(e)[:70]}")

    if not kuru:
        st["pozisyonlar"] = izlenen
        st["son_calisma"] = testbot.now_iso()
        kaydet(st)
    print(f"[{testbot.now_iso()}] izleyici: {yazildi} anlik goruntu, "
          f"{len(kapanan)} kapanis{' (KURU)' if kuru else ''}")


def doldur(kuru=False):
    """TEK SEFERLIK: gecmis pozisyonlari 1 dakikalik mumlardan geriye donuk doldur.

    Radar olcumleri geri URETILEMEZ (noktasal veriler) -> satirlar radar_izi=false ile
    isaretlenir, sonraki cozumlemede canli satirlarla karistirilmasin."""
    bst = testbot._load_state()
    try:
        kay = [json.loads(l) for l in
               open(testbot.ISLEMLERF, encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        kay = []
    try:
        var = {json.loads(l)["id"] for l in open(OZET, encoding="utf-8") if l.strip()}
    except Exception:
        var = set()

    # kapanmis pozisyonlar: id -> giris/cikis
    poz = {}
    for k in kay:
        p = poz.setdefault(k["id"], {"sym": k["sym"], "yon": k["yon"], "giris": k["giris"],
                                     "kapi": kapi_adi(k.get("sebep_giris")), "son_ts": k["ts"]})
        p["son_ts"] = max(p["son_ts"], k["ts"])
        try:
            ts = testbot.parse_iso(k["ts"])
            p["giris_ts"] = (ts - datetime.timedelta(hours=float(k.get("tutma_saat") or 0))
                             ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    acik_id = {p["id"] for p in (bst.get("acik_pozisyonlar") or [])} if bst else set()
    hedef = [(i, p) for i, p in poz.items() if i not in acik_id and i not in var]
    print(f"Doldurulacak kapanmis pozisyon: {len(hedef)}  (zaten var: {len(var)})")

    for i, p in sorted(hedef):
        try:
            bas = testbot.to_ms(p["giris_ts"])
            son = testbot.to_ms(p["son_ts"])
            barlar = tum_mumlar(p["sym"], bas, son)
            if not barlar:
                print(f"  {p['sym']:10} veri yok, atlandi"); continue
            b = yeni_birik()
            mumlari_ozetle(barlar, p["giris"], p["yon"], b)
            kap = {**p, "birik": b, "kaynak": "doldurma", "radar_izi": False,
                   "giris_radar": None, "son_radar": None}
            o = ozet_yaz(i, kap, kuru=kuru)
            print(f"  {p['sym']:10} id={i:<4} {len(barlar):5d} mum · "
                  f"arti {o.get('arti_dakika')}dk / eksi {o.get('eksi_dakika')}dk · "
                  f"MFE {o.get('mfe_pct')} MAE {o.get('mae_pct')} · {o.get('sonuc_sebep')}")
            time.sleep(0.2)
        except Exception as e:
            print(f"  {p.get('sym')}: HATA {str(e)[:70]}")
    print("Doldurma bitti." + (" (KURU — yazilmadi)" if kuru else ""))


def durum():
    st = yukle()
    print("=== POZISYON IZLEYICI ===")
    print(f"son calisma: {st.get('son_calisma')}")
    izl = st.get("pozisyonlar") or {}
    print(f"izlenen acik pozisyon: {len(izl)}")
    for pid, k in izl.items():
        b = _temiz(k.get("birik") or {})
        print(f"  id={pid:<4} {k.get('sym'):10} {k.get('kapi'):11} "
              f"kare {k.get('birik',{}).get('anlik_goruntu',0):3d} · "
              f"arti {b.get('arti_dakika')}dk / eksi {b.get('eksi_dakika')}dk "
              f"(%{b.get('arti_oran')}) · MFE {b.get('mfe_pct')} MAE {b.get('mae_pct')}")
    for ad, yol in (("anlik goruntu", IZLEME), ("kapanis ozeti", OZET)):
        n = sum(1 for _ in open(yol, encoding="utf-8")) if os.path.exists(yol) else 0
        mb = os.path.getsize(yol) / 1e6 if os.path.exists(yol) else 0
        print(f"{ad:16}: {n} satir · {mb:.2f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="bir anlik goruntu al (zamanli gorev)")
    ap.add_argument("--doldur", action="store_true", help="tek seferlik gecmis doldurma")
    ap.add_argument("--kuru", action="store_true", help="hicbir dosyaya yazma, ekrana bas")
    ap.add_argument("--durum", action="store_true")
    a = ap.parse_args()
    if a.doldur:
        doldur(a.kuru)
    elif a.durum:
        durum()
    else:
        tur(a.kuru)


if __name__ == "__main__":
    main()
