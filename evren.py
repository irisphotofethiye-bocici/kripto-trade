#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVREN — ortak kripto evren + rejim modulu (2026-07-02 revizyonu, m7 duzeltmesi).
radar / tarayici / piyasa_yapisi ayni evren kodunu 3 kopya tasiyordu (drift basladi:
radar stable/gold elemiyordu). Tek kaynak artik burasi.

Icerik:
  - cg_universe(): CoinGecko top-750 -> {SYM: {mcap, circ, total, float_oran}}
  - binance_pool(): likit USDT havuzu (stable/gold/tokenize-hisse/kaldirac-token elenir)
  - btc_rejim(): BTC gunluk SMA20 + piyasa_yapisi_log son satiri -> AYI/BOGA/NOTR
  - esik(): kripto-config.json -> esikler (tek dogruluk kaynagi; yoksa varsayilan)
Deterministik, 0 token. Bagimlilik yok (stdlib).
"""
import json, os, time, urllib.request, urllib.error, datetime, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "kripto-config.json")
SPOT = "https://api.binance.com"
FAPI = "https://fapi.binance.com"
STABLES = {"USDT", "USDC", "DAI", "BUSD", "TUSD", "FDUSD", "USDE", "USDD", "PYUSD",
           "RLUSD", "USD1", "USDP", "GUSD", "USDB", "USDX"}
GOLD = {"PAXG", "XAUT", "XAU"}
BAD = ("UPUSDT", "DOWNUSDT", "BULLUSDT", "BEARUSDT")

_cfg_cache = None


def cfg():
    global _cfg_cache
    if _cfg_cache is None:
        try:
            _cfg_cache = json.load(open(CFG, encoding="utf-8"))
        except Exception:
            _cfg_cache = {}
    return _cfg_cache


def cg_key():
    return cfg().get("coingecko_demo_key", "")


def esik(ad, varsayilan):
    """kripto-config.json -> esikler[ad]; yoksa varsayilan (kod ve config ayni degeri tasir)."""
    try:
        return float(cfg().get("esikler", {}).get(ad, varsayilan))
    except Exception:
        return varsayilan


_ban_until = 0.0  # Binance 418 sogutma penceresi (2026-07-08, rate-limit direnc katmani)


def get(u, headers=None, timeout=25):
    """Paylasimli HTTP getirici — TEK dogruluk kaynagi (radar/testbot/olcucu/piyasa_yapisi/panel buradan cagirir).
    429 (rate-limit uyarisi): Retry-After bekle, BIR KEZ tekrar dene. 418 (IP ban): retry YOK, sogutma
    penceresi baslat — pencere icinde YENI network cagrisi yapilmadan hemen hata donulur (banı uzatmamak
    icin; cagiran taraflardaki mevcut 'except Exception' sarmalayicilari degismeden calismaya devam eder)."""
    global _ban_until
    if _ban_until and time.time() < _ban_until:
        raise RuntimeError(f"Binance IP-ban sogutma penceresinde (kalan {_ban_until - time.time():.0f}sn) -> istek atlandi: {u}")
    req = urllib.request.Request(u, headers=headers or {"User-Agent": "evren/1.0"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        if e.code == 418:
            _ban_until = time.time() + 120.0
            print(f"BINANCE 418 (IP BAN) -> 120sn sogutma baslatildi: {u}")
            raise
        if e.code == 429:
            try:
                bekle = float(e.headers.get("Retry-After", 3))
            except Exception:
                bekle = 3.0
            time.sleep(bekle)
            try:
                return json.load(urllib.request.urlopen(req, timeout=timeout))
            except urllib.error.HTTPError as e2:
                if e2.code == 418:
                    _ban_until = time.time() + 120.0
                print(f"BINANCE {e2.code} (429 sonrasi tekrar basarisiz) -> {u}")
                raise
        raise


def cg_universe(key=None, pages=(1, 2, 3)):
    """CoinGecko markets -> {SYM: {mcap, circ, total, float_oran}}.
    float_oran = circulating/total (dusuk-float/unlock filtresi icin; RE/FOGO dersi)."""
    key = key if key is not None else cg_key()
    out = {}
    for pg in pages:
        try:
            url = (f"https://api.coingecko.com/api/v3/coins/markets"
                   f"?vs_currency=usd&order=market_cap_desc&per_page=250&page={pg}")
            for c in get(url, {"x-cg-demo-api-key": key, "User-Agent": "evren/1.0"}):
                sym = c["symbol"].upper()
                if sym in out:
                    continue
                circ, tot = c.get("circulating_supply"), c.get("total_supply")
                fo = (circ / tot) if (circ and tot and tot > 0) else None
                out[sym] = {"mcap": c.get("market_cap"), "circ": circ, "total": tot,
                            "float_oran": round(fo, 3) if fo is not None else None}
        except Exception:
            pass
    return out


def raw_tickers(kaynak="fapi", timeout=60, retries=2):
    """Tum-sembol 24hr ticker, HAM liste (buyuk payload -> genis timeout + birkac deneme).
    binance_pool() ve radar.erken_kusak_tara() AYNI cagriyi bagimsiz tekrarliyordu (2026-07-08
    duzeltmesi) -> tek yerden cekilir, ikisine de tickers= parametresiyle gecirilir."""
    base = FAPI + "/fapi/v1/ticker/24hr" if kaynak == "fapi" else SPOT + "/api/v3/ticker/24hr"
    for _ in range(retries):
        try:
            return get(base, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code == 418:
                raise
        except Exception:
            pass
    return []


def binance_pool(kaynak="fapi", min_vol_musd=8.0, chg_max=None, cryptos=None, tickers=None):
    """Likit USDT havuzu: [(sym, quoteVol, chg24), ...] hacme gore sirali.
    Eleme: BAD kaldirac-tokenlari, stable, altin-pegli, (cryptos verildiyse) kripto-olmayan.
    tickers: onceden raw_tickers() ile cekilmis liste verilirse tekrar network cagrisi yapilmaz."""
    t = tickers if tickers is not None else raw_tickers(kaynak)
    pool = []
    for x in t:
        s = x.get("symbol", "")
        if not s.endswith("USDT") or any(s.endswith(b) for b in BAD):
            continue
        sym = s[:-4]
        if sym in STABLES or sym in GOLD or "USD" in sym:
            continue
        if cryptos is not None and cryptos and sym not in cryptos:
            continue
        try:
            chg = float(x["priceChangePercent"]); qv = float(x["quoteVolume"])
        except Exception:
            continue
        if qv < min_vol_musd * 1e6:
            continue
        if chg_max is not None and abs(chg) > chg_max:
            continue
        pool.append((sym, qv, chg))
    pool.sort(key=lambda r: -r[1])
    return pool


def gunluk_kapanis(sym, n=31, quote="USDT"):
    """Gunluk kapanis serisi (Binance spot). Hata/veri yok -> None."""
    try:
        d = get(f"{SPOT}/api/v3/klines?symbol={sym}{quote}&interval=1d&limit={n}")
        return [float(k[4]) for k in d]
    except Exception:
        return None


def oran_degisim(ac, bc, k):
    """alt/BTC oraninin son k bardaki yuzde degisimi. ac/bc = gunluk kapanis serileri."""
    if not ac or not bc or len(ac) <= k or len(bc) <= k:
        return None
    if bc[-1] == 0 or bc[-1-k] == 0 or ac[-1-k] == 0:
        return None
    rn, rp = ac[-1] / bc[-1], ac[-1-k] / bc[-1-k]
    return round((rn / rp - 1) * 100, 2) if rp else None


def alt_btc(sym, btc_kapanis=None):
    """ALT/BTC PARITESI — 'USD'de yesil ama BTC'ye karsi kirmizi' tuzaginin olcumu.
    (kullanici teknigi 2026-06-25; piyasa_yapisi.py'nin tek-coin ve PAYLASILAN hali —
    formul iki yerde kopyalanmasin diye buraya tasindi, 2026-08-10.)

    ONEMLI AYRIM: SURDURULEBILIR (7-30g) alt/BTC trendi = gercek liderlik/alfa.
    3-SAATLIK goreli guc (eski AYRISMA etiketi) BASKA bir seydi ve olcumde
    negatif-edge cikti -> burada kisa pencere KASITLI OLARAK YOK.

    KAPI DEGIL, OLCUMDUR: hicbir karar fonksiyonu bunu okumaz; panelde gosterilir,
    ileride forward-return biriktirilip (25-30 olay) ancak o zaman kapi tartisilir."""
    if sym.upper() == "BTC":
        return None
    bc = btc_kapanis or gunluk_kapanis("BTC")
    ac = gunluk_kapanis(sym)
    if not ac or not bc:
        return None
    r24, r7, r30 = (oran_degisim(ac, bc, 1), oran_degisim(ac, bc, 7), oran_degisim(ac, bc, 30))
    usd7 = round((ac[-1] / ac[-8] - 1) * 100, 2) if len(ac) >= 8 else None
    # Yorum: USD yonu ile BTC-goreli yonu AYRISTIR (tuzagin adi konsun)
    if r7 is None:
        yorum = None
    elif r7 > 0 and r30 is not None and r30 > 0:
        yorum = "GERCEK GUC (BTC'yi surdurulebilir geciyor)"
    elif r7 > 0:
        yorum = "kisa vadede BTC'yi geciyor (30g henuz teyit degil)"
    elif r30 is not None and r30 > 0:
        yorum = "liderlik SOGUYOR (30g hala BTC ustunde, 7g dondu)"
    elif (usd7 or 0) > 0:
        yorum = "BTC-BETASI TUZAGI (USD'de yesil, BTC'ye karsi geride)"
    else:
        yorum = "hem USD hem BTC'ye karsi zayif"
    return {"r24": r24, "r7": r7, "r30": r30, "usd7": usd7, "yorum": yorum}


def btc_rejim():
    """Rejim tespiti — F10 SEZON×HAVA katmanlama (2026-07-22, tur-2 Faz 1).
    Eski tek-katman (1d SMA20+egim) kil-payi farki bile kesin BOGA/AYI diyordu -> 2026 boyunca
    yanlis 'BOGA' (F10 replay: 35 islemin hicbiri gercek TAM_BOGA degildi, -$440 kayip).
    Yeni: SEZON (haftalik 20-ort+egim, yavas) × HAVA (gunluk SMA20 + olu bant + histerezis, hizli).
    Capraz -> TAM_BOGA/TEPKI_RALLISI/DERIN_AYI/BOGA_DUZELTME/BELIRSIZ. 'rejim' alani GERIYE-UYUMLU
    3'lu uzaya (BOGA/AYI/NOTR) map'lenir; mevcut karar_yon degismeden dogru davranir
    (TEPKI_RALLISI->AYI: long-aday kapanir, fade acilir). Saf fiyat (fundamental CEO'da).
    Belirsizlik BIRINCI SINIF: kil-payi -> NOTR (SXT 'kil-payi-boga' hatasi imkansiz)."""
    rejim, detay = "BILINMIYOR", {}
    try:
        d = get(f"{SPOT}/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=40")
        cl = [float(k[4]) for k in d]
        w = get(f"{SPOT}/api/v3/klines?symbol=BTCUSDT&interval=1w&limit=30")
        wc = [float(k[4]) for k in w]
        # SEZON (yavas): haftalik kapanis vs son 20 kapali hafta ort + egim
        sezon = "?"
        if len(wc) >= 21:
            w_ort = statistics.mean(wc[-21:-1])
            w_egim = wc[-1] - wc[-21]
            if wc[-1] > w_ort and w_egim > 0:
                sezon = "BOGA"
            elif wc[-1] < w_ort and w_egim < 0:
                sezon = "AYI"
            else:
                sezon = "NOTR"
        # HAVA (hizli): gunluk SMA20 + olu bant + histerezis (flip-flop yok)
        olu = esik("f10_olu_bant_pct", 2.0)
        hist = int(esik("f10_histerezis_gun", 3))
        ham = []
        for i in range(20, len(cl)):
            sma = statistics.mean(cl[i-20:i])
            uz = (cl[i] - sma) / sma * 100
            ham.append("NOTR" if abs(uz) < olu else ("BOGA" if uz > 0 else "AYI"))
        hava = ham[0] if ham else "NOTR"
        for i in range(len(ham)):
            if i < hist:
                hava = ham[i]
            else:
                pen = ham[i-hist+1:i+1]
                if all(x == pen[0] for x in pen):
                    hava = pen[0]
        # capraz F10 etiket
        if sezon == "AYI" and hava == "BOGA":
            f10 = "TEPKI_RALLISI"
        elif sezon == "BOGA" and hava == "BOGA":
            f10 = "TAM_BOGA"
        elif sezon == "AYI" and hava == "AYI":
            f10 = "DERIN_AYI"
        elif sezon == "BOGA" and hava == "AYI":
            f10 = "BOGA_DUZELTME"
        else:
            f10 = "BELIRSIZ"
        # 3'lu map (geriye-uyum: karar_yon BOGA/AYI/NOTR bekler; yon dogru tarafa duser)
        if f10 == "TAM_BOGA":
            rejim = "BOGA"
        elif f10 in ("TEPKI_RALLISI", "DERIN_AYI"):
            rejim = "AYI"
        else:  # BOGA_DUZELTME, BELIRSIZ -> temkin
            rejim = "NOTR"
        detay = {"btc": round(cl[-1], 0), "sma20": round(statistics.mean(cl[-20:]), 0),
                 "sezon": sezon, "hava": hava, "f10": f10}
    except Exception:
        pass
    # piyasa_yapisi trend logu (varsa ve <24h taze ise) baglama eklenir
    try:
        logf = os.path.join(HERE, "piyasa_yapisi_log.jsonl")
        lines = [l for l in open(logf, encoding="utf-8").read().splitlines() if l.strip()]
        last = json.loads(lines[-1])
        yas_saat = (datetime.datetime.now()
                    - datetime.datetime.strptime(last["ts"], "%Y-%m-%d %H:%M")).total_seconds() / 3600
        if yas_saat < 24:
            detay.update({"btc_d": last.get("btc_d"), "usdt_d": last.get("usdt_d"),
                          "stable_d": last.get("stable_d")})
    except Exception:
        pass
    return {"rejim": rejim, **detay}


def para_rejim_etiket(total_chg, btcd_chg, t3_chg):
    """TOTAL-trendi × rotasyon -> (etiket, aciklama). Saf sinyal, I/O YOK (pure).
    Katman-1 TOTAL trendi = kriptoya taze para giriyor mu; Katman-2 rotasyon = major mi alt mi.
    Olu-bant %2 (f10_olu_bant mantigi): kucuk salinim 'taze giris' sayilmaz.
    Panel (gosterge) + testbot para-kapisi ORTAK kaynagi (drift olmasin diye tek yerde)."""
    if total_chg is None:
        return (None, None)
    if total_chg >= 2.0:
        if btcd_chg is not None and btcd_chg < 0 and (t3_chg or 0) > 0:
            return ("PARA GIRIYOR -> ALTLARA", "kriptoya taze para + alt-rotasyon (risk-on, boga-lehine)")
        if btcd_chg is not None and btcd_chg > 0:
            return ("PARA GIRIYOR -> MAJORLERE", "kriptoya taze para ama BTC/majore yigiliyor (BTC-onculu, erken)")
        return ("PARA GIRIYOR -> dengeli", "kriptoya taze para, rotasyon net degil")
    if total_chg <= -2.0:
        return ("PARA CIKIYOR", "kriptodan cikis (risk-off); yukselisler zayif, fade-dostu")
    return ("PARA DURGUN", "taze giris yok; pump'lar rotasyon/kaldirac -> fade-dostu")


def para_rejim(geri=14):
    """piyasa_yapisi_log'dan money-regime (2026-07-23, kullanici karari: giris-kapisina baglandi).
    Panel gostergesi ile ayni tanim; testbot 'PARA CIKIYOR' iken long-veto uygular (LONG-kisitlayici,
    opener DEGIL — F10 dersi: long-gevsetme=kayip). Log yok/az ise None (kapi devreye girmez, fail-open).
    geri=14 ~ 7 gun (piyasa_yapisi ~2x/gun loglanir; panel 'gun': geri//2)."""
    try:
        logf = os.path.join(HERE, "piyasa_yapisi_log.jsonl")
        lines = [json.loads(l) for l in open(logf, encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        return None
    if len(lines) < 2:
        return None
    son = lines[-1]
    ilk = lines[-geri] if len(lines) >= geri else lines[0]
    def yuzde(a, b): return round((a - b) / b * 100, 1) if b else 0.0
    def t3(d): return d["total"] * (1 - d["btc_d"] / 100 - d.get("eth_d", 0) / 100)
    try:
        total_chg = yuzde(son["total"], ilk["total"])
        btcd_chg = round(son["btc_d"] - ilk["btc_d"], 2)
        t3_chg = yuzde(t3(son), t3(ilk))
    except Exception:
        return None
    etiket, aciklama = para_rejim_etiket(total_chg, btcd_chg, t3_chg)
    return {"rejim": etiket, "not": aciklama, "total_chg": total_chg,
            "btcd_chg": btcd_chg, "t3_chg": t3_chg, "total_t": round(son["total"] / 1e12, 3)}


# ---------------------------------------------------------------------------
# BTC'nin RISK-VARLIK PAYI (stablecoin HARIC) — 2026-08-04, olculdu ve dogrulandi
#
# NEDEN AYRI BIR LOG: mevcut piyasa_yapisi_log.jsonl bu sinyali URETEMIYOR.
#   Olculen seri (CoinGecko top-130, GUNLUK anlik goruntu) ile logdan hesaplanan
#   3-gunluk degisim arasinda korelasyon -0.12, ISARET UYUSMASI %47 (yazi-tura).
#   Sebep: log gunde ~2 kez DUZENSIZ saatlerde yaziyor; 3 gunluk fark bu gurultude
#   kayboluyor. Logdan besleseydik olculen sinyali degil GURULTUYU baglamis olurduk.
#   Bu yuzden ayri, GUNDE BIR, sabit yontemli anlik goruntu tutulur.
# TUTARLILIK DOGRULANDI: canli coins/markets top-130 vs gecmis market_chart serisi ->
#   TOTAL farki %+0.03, BTC_D_XS farki -0.062 puan (ayni olcek).
# ---------------------------------------------------------------------------
BTC_PAY_LOGF = os.path.join(HERE, "btc_pay_log.jsonl")
_STABLE_ID = {"tether", "usd-coin", "dai", "first-digital-usd", "usds", "ethena-usde"}


def btc_pay_guncelle():
    """Gunde BIR kez CoinGecko top-130 mcap anlik goruntusu -> btc_pay_log.jsonl.
    Ayni gun icin kayit varsa hicbir sey yapmaz (tekrar cagrilmasi zararsiz).
    Hata halinde sessizce None doner — olcum katmani karar akisini durdurmaz."""
    try:
        bugun = datetime.datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(BTC_PAY_LOGF):
            with open(BTC_PAY_LOGF, encoding="utf-8") as f:
                for satir in f:
                    if f'"gun": "{bugun}"' in satir or f'"gun":"{bugun}"' in satir:
                        return None
        k = cg_key()
        u = ("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
             "&order=market_cap_desc&per_page=130&page=1")
        if k:
            u += "&x_cg_demo_api_key=" + k
        d = get(u, timeout=30)
        top = sum(x.get("market_cap") or 0 for x in d)
        stb = sum(x.get("market_cap") or 0 for x in d if x.get("id") in _STABLE_ID)
        btc = next((x.get("market_cap") or 0 for x in d if x.get("id") == "bitcoin"), 0)
        if top <= 0 or btc <= 0 or (top - stb) <= 0:
            return None
        kayit = {"gun": bugun, "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                 "total": top, "stable": stb, "btc": btc,
                 "btc_d_xs": round(btc / (top - stb) * 100, 4), "kapsam": len(d)}
        with open(BTC_PAY_LOGF, "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
        return kayit
    except Exception:
        return None


def btc_pay_akisi(gun=3):
    """BTC'nin risk-varlik payinin (stablecoin haric) son 'gun' gunluk PUAN degisimi.

    Donus: {"xs":..., "degisim":..., "bant":"ALT"|"ORTA"|"UST", "gun_farki":N} | None
    None = veri yetersiz -> KAPI DEVREYE GIRMEZ (fail-open, mevcut davranis korunur).

    OLCUM (12 ay, 103 sembol, 37.271 gozlem, gercek holdout — PARA_SONUC.md):
      BTC_D_XS 3g ALT ceyrek  -> SHORT R kesif +0.27 / sakli +0.16  (temel +0.06/+0.04)
      BTC_D_XS 3g UST ceyrek  -> SHORT R kesif -0.02 / sakli -0.03
      UST ceyrek + para durgun -> LONG R kesif +0.24 / sakli +0.16 (rastgele -0.07/-0.04)
      Kesif 8 ay / sakli 4 ay ayrimi +0.45 vs +0.46, saklida dilimler mukemmel sirali.
    SINIR: 12 ayin tamami DUSEN piyasa. Yukselen piyasada iliski tersine donebilir."""
    try:
        if not os.path.exists(BTC_PAY_LOGF):
            return None
        satirlar = [json.loads(l) for l in open(BTC_PAY_LOGF, encoding="utf-8") if l.strip()]
    except Exception:
        return None
    if len(satirlar) < gun + 1:
        return None
    satirlar.sort(key=lambda r: r.get("gun", ""))
    son = satirlar[-1]
    hedef = (datetime.datetime.strptime(son["gun"], "%Y-%m-%d")
             - datetime.timedelta(days=gun)).strftime("%Y-%m-%d")
    onc = min(satirlar[:-1], key=lambda r: abs(
        (datetime.datetime.strptime(r["gun"], "%Y-%m-%d")
         - datetime.datetime.strptime(hedef, "%Y-%m-%d")).days))
    fark_gun = abs((datetime.datetime.strptime(onc["gun"], "%Y-%m-%d")
                    - datetime.datetime.strptime(hedef, "%Y-%m-%d")).days)
    if fark_gun > 1:
        return None                      # 3 gun oncesine +-1 gun icinde kayit yoksa kapi kapali
    bayat = (datetime.datetime.now() - datetime.datetime.strptime(son["gun"], "%Y-%m-%d")).days
    if bayat > 2:
        return None                      # anlik goruntu bayatladi -> guvenme
    d = son["btc_d_xs"] - onc["btc_d_xs"]
    ust = esik("btcd_xs_ust", 0.287)
    alt = esik("btcd_xs_alt", -0.318)
    bant = "UST" if d >= ust else ("ALT" if d <= alt else "ORTA")
    return {"xs": son["btc_d_xs"], "degisim": round(d, 4), "bant": bant,
            "gun_farki": gun, "son_gun": son["gun"], "onceki_gun": onc["gun"]}


if __name__ == "__main__":
    print(json.dumps({"rejim": btc_rejim(), "btc_pay": btc_pay_akisi(),
                      "esik_ornek": {"funding_long_veto_pct": esik("funding_long_veto_pct", 0.03)}},
                     ensure_ascii=False, indent=2))
