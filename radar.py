#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RADAR - Faz 3/6: hareketten ONCE veya tam baslarken yakalama (öncü imza taramasi).
"Sonradan en cok artan"i DEGIL, yukselisi tetikleyen oncu kosullari arar:
  - OI fiyat yatayken hizli sisiyor (pozisyon kuruluyor)
  - funding negatife/asiriya kayiyor (squeeze yakiti) ama fiyat daha oynamadi
  - volatilite sikismasi (coiling) -> ilk genisleme
  - hacim tabandan uyaniyor
2 asama: (1) Binance 24h ticker'dan likit + henuz-patlamamis havuz; (2) her aday icin 1h klines + OI + funding.
Anahtarsiz Binance. Kullanim: python radar.py [--n 35] [--min_vol 8] [--chg_max 15]
UYARI: bu ONCU olasilik tahminidir, garanti DEGIL; yon yukari da asagi da olabilir.
"""
import json, os, sys, urllib.request, statistics, argparse, datetime
import olcucu
import evren

# pythonw.exe (zamanlayici) altinda sys.stdout/err = None -> print() patlar.
# Devnull'a yonlendir; gercek uyarilar zaten radar_alerts.log'a yaziliyor.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

FAPI = "https://fapi.binance.com"
BAD = ("UPUSDT", "DOWNUSDT", "BULLUSDT", "BEARUSDT")

def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "radar/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=20))

def klines(sym, n=50):
    d = get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h&limit={n}")
    return [{"h": float(k[2]), "l": float(k[3]), "c": float(k[4]),
             "v": float(k[5]), "qv": float(k[7])} for k in d]

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def funding(sym):
    try:
        return float(get(f"{FAPI}/fapi/v1/premiumIndex?symbol={sym}USDT")["lastFundingRate"]) * 100
    except Exception:
        return None

def oi_changes(sym):
    try:
        d = get(f"{FAPI}/futures/data/openInterestHist?symbol={sym}USDT&period=1h&limit=24")
        if len(d) < 5:
            return None, None
        oi = [float(x["sumOpenInterest"]) for x in d]
        ch24 = (oi[-1] - oi[0]) / oi[0] * 100 if oi[0] else None
        ch3 = (oi[-1] - oi[-4]) / oi[-4] * 100 if oi[-4] else None
        return ch24, ch3
    except Exception:
        return None, None

def pillar_d(sym):
    """Pillar D - aggressor + smart-money (AAVE-vs-LAB ayirt edici filtre, 2026-06-24 dersi).
    3 ucretsiz Binance cagrisi; SADECE kisa listeye uygulanir (rate-limit dostu)."""
    out = {"top_ls": None, "glob_ls": None, "taker": None}
    for k, ep, alan in (("top_ls", "topLongShortPositionRatio", "longShortRatio"),
                        ("glob_ls", "globalLongShortAccountRatio", "longShortRatio"),
                        ("taker", "takerlongshortRatio", "buySellRatio")):
        try:
            d = get(f"{FAPI}/futures/data/{ep}?symbol={sym}USDT&period=1h&limit=1")
            out[k] = round(float(d[-1][alan]), 2) if d else None
        except Exception:
            pass
    t = out["top_ls"]
    out["smart"] = None if t is None else ("LONG" if t >= 1.2 else ("SHORT" if t <= 0.83 else "NOTR"))
    return out

def btc_ref():
    """BTC perp referansi: son 3 bar (3h) ve 24s % degisim. AYRISMA icin bir kez hesaplanir."""
    try:
        bk = get(f"{FAPI}/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=25")
        cl = [float(k[4]) for k in bk]
        chg3 = (cl[-1] - cl[-4]) / cl[-4] * 100 if len(cl) >= 4 and cl[-4] else 0.0
        chg24 = (cl[-1] - cl[0]) / cl[0] * 100 if cl and cl[0] else 0.0
        return round(chg3, 2), round(chg24, 2)
    except Exception:
        return 0.0, 0.0

def analyze(sym, btc_chg3=0.0):
    b = klines(sym, 50)
    if len(b) < 25:
        return None
    price = b[-1]["c"]
    a = olcucu.atr(b)
    if not a or not price:
        return None
    # sikisma: son 6 barin TR ort / ATR14
    trs = [max(b[i]["h"]-b[i]["l"], abs(b[i]["h"]-b[i-1]["c"]), abs(b[i]["l"]-b[i-1]["c"])) for i in range(len(b)-6, len(b))]
    comp = statistics.mean(trs) / a
    # hacim patlamasi: son bar qv / son 24 medyan
    med = statistics.median([x["qv"] for x in b[-24:]])
    vol_x = (b[-1]["qv"] / med) if med else 0
    # 20-bar aralikta konum
    hi = max(x["h"] for x in b[-20:]); lo = min(x["l"] for x in b[-20:])
    pos = (price - lo) / (hi - lo) if hi > lo else 0.5
    last1 = (b[-1]["c"] - b[-2]["c"]) / b[-2]["c"] * 100
    last3 = (b[-1]["c"] - b[-4]["c"]) / b[-4]["c"] * 100
    f = funding(sym)
    oi24, oi3 = oi_changes(sym)

    # --- skor (0-100) ---
    s_oi = clamp((oi24 or 0)/20)*25 + clamp((oi3 or 0)/8)*10
    # negatif funding = squeeze yakiti AMA yalniz fiyat dusmuyorsa (yoksa bu sadece dususte short baskisi)
    squeeze_bonus = 8 if (f is not None and f < -0.01 and last3 >= -1 and (oi3 or 0) >= 0) else 0
    s_fund = clamp(abs(f or 0)/0.05)*15 + squeeze_bonus
    s_comp = clamp((0.8 - comp)/0.5)*20
    s_vol = clamp((vol_x - 1.5)/3)*20
    s_brk = clamp((pos - 0.7)/0.3)*10 + clamp(last1/4)*5
    score = round(s_oi + s_fund + s_comp + s_vol + s_brk, 1)

    # asama etiketi (radar_active.json KAPISI - DEGISMEDI)
    if vol_x > 2.5 and last1 > 2 and (oi3 or 0) > 3:
        stage = "BASLIYOR"        # hareket tam basliyor
    elif comp < 0.65 and abs(last3) < 4 and (oi24 or 0) > 8:
        stage = "HAZIRLANIYOR"    # coiled + pozisyon, fiyat hala yatay
    else:
        stage = "izle"

    # --- DENEYSEL oncu-sekil etiketleri (KAPI DEGIL; sadece gorunurluk + arsiv, henuz dogrulanmadi) ---
    # Sekil 3 DIP_YAKIT: asiri neg funding (short kalabalik) + dipte + OI dagilmamis = short-squeeze yakiti
    # oi24 >= -1: gurultu seviyesi duzlugu tolere et, gercek dagilma (-3%+) elensin (kullanici karari 2026-06-24)
    dip_yakit = bool(f is not None and f < -0.05 and pos < 0.25 and (oi24 or 0) >= -1)
    # Sekil 4 AYRISMA: BTC duz/asagi iken coin yukari ayrisiyor = bagimsiz goreli guc (PENGU arketipi)
    rel3 = round(last3 - btc_chg3, 2)
    ayrisma = bool(last3 > 0 and btc_chg3 <= 0 and rel3 > 3)

    return {"sym": sym, "price": round(price, 6), "score": score, "stage": stage, "comp": round(comp, 2),
            "vol_x": round(vol_x, 1), "oi24": oi24, "oi3": oi3, "funding": f,
            "pos": round(pos, 2), "last1": round(last1, 1), "last3": round(last3, 1),
            "dip_yakit": dip_yakit, "ayrisma": ayrisma, "rel3": rel3}

def erken_kusak_tara(cryptos, haric=None, btc_chg3=0.0):
    """ERKEN KUSAK (2026-07-06): pump'i ERKEN yakalama evreni. Haftanin buyuk kazananlari (TLM +282%,
    VANRY +154%, HMSTR +107%) ana havuza HIC girmedi: (1) hacim-sirali ilk-N pump oncesi dusuk-hacimli
    coini gormuyor, (2) chg_max pump baslayinca eliyor - kor nokta yapisal.
    Bu kusak: bugunku hacmi onceki 7 gunun MEDYANINA gore >= erken_vol_x KAT uyanmis AMA 24s degisimi
    hala kucuk (<= erken_chg24_max) coinler. 'Hacim once, fiyat sonra' hipotezi (ALLO 06-28 kaniti:
    erken skor 40.5 HAZIRLANIYOR @ $0.304 -> +42%). KAPI DEGIL - gorunurluk + ERKEN-etiketli arsiv
    (forward-return olcumu birikince arsiv_analiz ile edge dogrulanir; alarm entegrasyonu ONDAN SONRA)."""
    min_vol = evren.esik("erken_min_vol_musd", 3.0) * 1e6
    chg_max = evren.esik("erken_chg24_max", 15.0)
    vol_x_esik = evren.esik("erken_vol_x", 3.0)
    top_n = int(evren.esik("erken_top_n", 15))
    haric = haric or set()
    # tum-semboller ticker'i buyuk payload -> standart 20sn timeout yetmeyebiliyor; genis timeout + 1 tekrar
    tks = None
    for _ in range(2):
        try:
            req = urllib.request.Request(f"{FAPI}/fapi/v1/ticker/24hr", headers={"User-Agent": "radar/1.0"})
            tks = json.load(urllib.request.urlopen(req, timeout=60))
            break
        except Exception:
            continue
    if not tks:
        return []
    adaylar = []
    for t in tks:
        s = t.get("symbol", "")
        if not s.endswith("USDT") or any(b in s for b in BAD):
            continue
        sym = s[:-4]
        if sym in haric:
            continue
        try:
            qv = float(t["quoteVolume"]); chg = float(t["priceChangePercent"])
        except Exception:
            continue
        if qv >= min_vol and abs(chg) <= chg_max:
            adaylar.append((sym, qv, chg))
    adaylar.sort(key=lambda x: -x[1])
    out = []
    for sym, qv, chg in adaylar[:120]:  # kline yuku siniri (~120 cagri / 15dk — rate-limit dostu)
        try:
            d = get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1d&limit=8")
            if len(d) < 8:
                continue  # 1 haftadan yeni listing -> medyan anlamsiz, atla
            onceki7 = [float(k[7]) for k in d[:-1]]
            med = statistics.median(onceki7)
            vx = qv / med if med else 0.0
            if vx >= vol_x_esik:
                out.append({"sym": sym, "vol_x_gun": round(vx, 1), "chg24": round(chg, 1),
                            "vol_musd": round(qv / 1e6, 1)})
        except Exception:
            continue
    out.sort(key=lambda r: -r["vol_x_gun"])
    out = out[:top_n]
    dusuk_float_esik = evren.esik("dusuk_float_oran", 0.25)
    for r in out:  # kisa listeye analyze + Pillar D (arsiv forward-return olcumu icin skor/etiket sart)
        try:
            an = analyze(r["sym"], btc_chg3)
            if an:
                cg = cryptos.get(r["sym"]) or {}
                mc = cg.get("mcap")
                an["mcap"] = (f"${mc/1e6:.0f}M" if mc else "?")
                an["float_oran"] = cg.get("float_oran")
                an["dusuk_float"] = bool(an["float_oran"] is not None and an["float_oran"] < dusuk_float_esik)
                an.update(pillar_d(r["sym"]))
                r.update(an)
        except Exception:
            continue
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=35, help="aday sayisi (asama-2)")
    ap.add_argument("--min_vol", type=float, default=8.0, help="min 24s hacim (milyon $)")
    ap.add_argument("--chg_max", type=float, default=15.0, help="zaten patlamis (>%) olanlari ele")
    ap.add_argument("--watch", action="store_true", help="yeni sinyalleri radar_alerts.log'a yaz (zamanlayici icin)")
    a = ap.parse_args()

    # Kripto evreni + havuz - ORTAK modul evren.py (m7 drift duzeltmesi: stable/gold da elenir)
    HERE = os.path.dirname(os.path.abspath(__file__))
    cryptos = evren.cg_universe()
    pool = [s for s, _, _ in evren.binance_pool("fapi", a.min_vol, a.chg_max, cryptos)[:a.n]]

    # AYRISMA icin BTC referansi - bir kez hesapla, tum coinlerde kullan
    btc_chg3, btc_chg24 = btc_ref()

    dusuk_float_esik = evren.esik("dusuk_float_oran", 0.25)
    rows = []
    for sym in pool:
        try:
            r = analyze(sym, btc_chg3)
            if r:
                cg = cryptos.get(sym) or {}
                mc = cg.get("mcap")
                r["mcap"] = (f"${mc/1e6:.0f}M" if mc else "?")
                # float/unlock filtresi (RE/FOGO dersi): dusuk float + acilmamis arz = yapisal neg funding
                fo = cg.get("float_oran")
                r["float_oran"] = fo
                r["dusuk_float"] = bool(fo is not None and fo < dusuk_float_esik)
                rows.append(r)
        except Exception:
            continue
    rows.sort(key=lambda r: -r["score"])

    # REJIM (hipotez#1: yon = rejim; AYI -> yuksek skor = SHORT adayi) + Pillar D (kisa listeye)
    rejim = evren.btc_rejim()
    alert_esik = evren.esik("radar_alert_skor", 40.0)
    for r in rows:
        if r["score"] >= 30 or r["stage"] in ("BASLIYOR", "HAZIRLANIYOR"):
            r.update(pillar_d(r["sym"]))
        else:
            r.update({"top_ls": None, "glob_ls": None, "taker": None, "smart": None})

    # ERKEN KUSAK: hacim-uyanisi taramasi (ana havuzun kor noktasi; TLM/VANRY/HMSTR dersi 2026-07-06)
    erken_rows = erken_kusak_tara(cryptos, haric=set(pool), btc_chg3=btc_chg3)

    # --- KALICI ARSIV (append-only): her tarama turunda TUM adaylar + sekil etiketleri + timestamp.
    # context'e yuklenmez; sadece diske. Hangi seklin gercekten kazandigini sonradan analiz icin veri seti.
    ts0 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        with open(os.path.join(HERE, "radar_archive.jsonl"), "a", encoding="utf-8") as af:
            for r in rows:
                rec = {"ts": ts0, "btc_chg3": btc_chg3, "btc_chg24": btc_chg24,
                       "sym": r["sym"], "price": r.get("price"), "score": r["score"], "stage": r["stage"],
                       "comp": r["comp"], "vol_x": r["vol_x"], "oi24": r["oi24"], "oi3": r["oi3"],
                       "funding": r["funding"], "pos": r["pos"], "last1": r["last1"], "last3": r["last3"],
                       "mcap": r.get("mcap"), "dip_yakit": r["dip_yakit"],
                       "ayrisma": r["ayrisma"], "rel3": r["rel3"],
                       "rejim": rejim.get("rejim"), "top_ls": r.get("top_ls"), "glob_ls": r.get("glob_ls"),
                       "taker": r.get("taker"), "smart": r.get("smart"),
                       "float_oran": r.get("float_oran"), "dusuk_float": r.get("dusuk_float")}
                af.write(json.dumps(rec, ensure_ascii=False) + "\n")
            # ERKEN kusak ayni arsive "erken": true etiketiyle yazilir (forward-return olcum verisi)
            for r in erken_rows:
                if r.get("score") is None:
                    continue  # analyze basarisiz olduysa olcum verisi eksik, arsive yazma
                rec = {"ts": ts0, "btc_chg3": btc_chg3, "btc_chg24": btc_chg24, "erken": True,
                       "vol_x_gun": r.get("vol_x_gun"), "chg24": r.get("chg24"),
                       "sym": r["sym"], "price": r.get("price"), "score": r.get("score"), "stage": r.get("stage"),
                       "comp": r.get("comp"), "vol_x": r.get("vol_x"), "oi24": r.get("oi24"), "oi3": r.get("oi3"),
                       "funding": r.get("funding"), "pos": r.get("pos"), "last1": r.get("last1"), "last3": r.get("last3"),
                       "mcap": r.get("mcap"), "dip_yakit": r.get("dip_yakit"),
                       "ayrisma": r.get("ayrisma"), "rel3": r.get("rel3"),
                       "rejim": rejim.get("rejim"), "top_ls": r.get("top_ls"), "glob_ls": r.get("glob_ls"),
                       "taker": r.get("taker"), "smart": r.get("smart"),
                       "float_oran": r.get("float_oran"), "dusuk_float": r.get("dusuk_float")}
                af.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # --- WATCH modu: onceki tarama ile kiyasla, YENI sinyalleri logla (zamanlayici icin) ---
    if a.watch:
        statef = os.path.join(HERE, "radar_state.json")
        logf = os.path.join(HERE, "radar_alerts.log")
        try:
            prev = json.load(open(statef, encoding="utf-8"))
        except Exception:
            prev = {}
        alerts = []
        for r in rows:
            p = prev.get(r["sym"])
            pscore = p["score"] if p else 0
            pstage = p["stage"] if p else None
            if r["stage"] in ("BASLIYOR", "HAZIRLANIYOR"):
                if pstage not in ("BASLIYOR", "HAZIRLANIYOR") or (r["score"] - pscore >= 10):
                    alerts.append(r)
            elif r["score"] >= 40 and pscore < 40:
                alerts.append(r)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        if alerts:
            with open(logf, "a", encoding="utf-8") as fh:
                for r in alerts:
                    fh.write(f"{ts} | {r['stage']:12} | {r['sym']:8} px={r.get('price')} skor={r['score']} mcap={r['mcap']} "
                             f"OI24={r['oi24']} OI3={r['oi3']} fund={r['funding']} volx={r['vol_x']} "
                             f"sikis={r['comp']} konum={r['pos']} son1s={r['last1']} "
                             f"dipyakit={r['dip_yakit']} ayrisma={r['ayrisma']} rel3={r['rel3']} "
                             f"rejim={rejim.get('rejim')} smart={r.get('smart')} top_ls={r.get('top_ls')} "
                             f"taker={r.get('taker')} dusukfloat={r.get('dusuk_float')}\n")
            print(f"[{ts}] {len(alerts)} YENI uyari -> radar_alerts.log")
            for r in alerts:
                print(f"  ALERT {r['stage']:12} {r['sym']:8} skor={r['score']}")
        else:
            print(f"[{ts}] yeni uyari yok ({len(rows)} coin tarandi)")
        # CANLI snapshot - her calismada YENIDEN yazilir (birikme YOK; eski/yeni karismaz).
        # "Su an ne sicak" icin BUNU oku; radar_alerts.log = sadece gecmis gunluk.
        # KAPSAM (FOGO-70 duzeltmesi 2026-07-02): stage aktif OLANLAR + skor>=alert_esik "izle" satirlari.
        # Eski hali sadece stage'e bakiyordu -> arsivdeki en guclu sinyal (FOGO skor70, stage=izle) kacmisti.
        active = [r for r in rows if r["stage"] in ("BASLIYOR", "HAZIRLANIYOR") or r["score"] >= alert_esik]
        json.dump({"guncelleme": ts, "tarandi": len(rows), "rejim": rejim,
                   "aktif_sinyaller": [{"sym": r["sym"], "price": r.get("price"), "stage": r["stage"], "score": r["score"],
                                        "kaynak": ("stage" if r["stage"] in ("BASLIYOR", "HAZIRLANIYOR") else "skor"),
                                        "oi24": r["oi24"], "oi3": r["oi3"], "funding": r["funding"],
                                        "comp": r["comp"], "vol_x": r["vol_x"], "pos": r["pos"],
                                        "last1": r["last1"], "mcap": r["mcap"],
                                        "smart": r.get("smart"), "top_ls": r.get("top_ls"), "taker": r.get("taker"),
                                        "dusuk_float": r.get("dusuk_float")} for r in active],
                   # ERKEN kusak (hacim uyanmis, fiyat henuz oynamamis) — KAPI DEGIL, gorunurluk/olcum
                   "erken_kusak": [{"sym": r["sym"], "vol_x_gun": r.get("vol_x_gun"), "chg24": r.get("chg24"),
                                    "vol_musd": r.get("vol_musd"), "price": r.get("price"),
                                    "score": r.get("score"), "stage": r.get("stage"), "pos": r.get("pos"),
                                    "funding": r.get("funding"), "oi24": r.get("oi24"), "mcap": r.get("mcap"),
                                    "smart": r.get("smart"), "taker": r.get("taker"),
                                    "dusuk_float": r.get("dusuk_float")} for r in erken_rows]},
                  open(os.path.join(HERE, "radar_active.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        # alert log'u sinirla: son 300 satir (sinirsiz buyumeyi onle)
        try:
            if os.path.exists(logf):
                ln = open(logf, encoding="utf-8").read().splitlines()
                if len(ln) > 300:
                    open(logf, "w", encoding="utf-8").write("\n".join(ln[-300:]) + "\n")
        except Exception:
            pass
        # state: havuzdan gecici dusen coin 8 tarama boyunca hatirlanir (m8: yeniden-giris "YENI sinyal" gurultusunu keser)
        yeni_state = {r["sym"]: {"stage": r["stage"], "score": r["score"], "miss": 0} for r in rows}
        for psym, p in prev.items():
            if psym not in yeni_state and p.get("miss", 0) < 8:
                yeni_state[psym] = {"stage": p.get("stage"), "score": p.get("score", 0), "miss": p.get("miss", 0) + 1}
        json.dump(yeni_state, open(statef, "w", encoding="utf-8"))
        return

    def shape_tag(r):
        t = []
        if r.get("dip_yakit"):
            t.append("DIP_YAKIT" + ("!FLOAT" if r.get("dusuk_float") else ""))
        elif r.get("dusuk_float"):
            t.append("DUSUK_FLOAT")
        if r.get("ayrisma"):
            t.append(f"AYRISMA(+{r['rel3']})")
        return " ".join(t) if t else "-"

    def show(title, items):
        print(f"\n## {title}")
        print(f"  {'COIN':8} {'skor':>5} {'mcap':>8} {'sikis':>5} {'volx':>5} {'OI24':>6} {'OI3s':>6} {'fund%':>7} {'konum':>5} {'son1s':>6} {'smart':>5} {'taker':>5}  sekil")
        for r in items:
            print(f"  {r['sym']:8} {r['score']:>5} {r['mcap']:>8} {r['comp']:>5} {r['vol_x']:>5} "
                  f"{('%+.0f'%r['oi24']) if r['oi24'] is not None else '-':>6} "
                  f"{('%+.0f'%r['oi3']) if r['oi3'] is not None else '-':>6} "
                  f"{('%.3f'%r['funding']) if r['funding'] is not None else '-':>7} "
                  f"{r['pos']:>5} {('%+.1f'%r['last1']):>6} "
                  f"{(r.get('smart') or '-')[:5]:>5} {(('%.2f'%r['taker']) if r.get('taker') is not None else '-'):>5}  {shape_tag(r)}")

    print("=== RADAR (oncu imza; garanti DEGIL) ===")
    print(f"(BTC ref: chg3={btc_chg3}%  chg24={btc_chg24}%)")
    print(f"REJIM: {rejim.get('rejim')} (BTC {rejim.get('btc')} vs SMA20 {rejim.get('sma20')}"
          + (f" | BTC.D {rejim['btc_d']}" if rejim.get("btc_d") else "") + ")")
    if rejim.get("rejim") == "AYI":
        print("  -> AYI: yuksek skor (45+) = SHORT adayi (hipotez#1); LONG scalp bu rejimde -EV cikti. Giris guce karsi, dipte degil (ders#4).")
    elif rejim.get("rejim") == "BOGA":
        print("  -> BOGA: hipotez#1/#2 ayi-verisiyle olculdu; boga'da yon-edge YENIDEN test edilmeli (arsiv_analiz.py), korle uygulama.")
    show("BASLIYOR - hareket tam baslıyor (vol+OI+ilk bar)", [r for r in rows if r["stage"] == "BASLIYOR"][:8])
    show("HAZIRLANIYOR - coiled + pozisyon, fiyat hala yatay", [r for r in rows if r["stage"] == "HAZIRLANIYOR"][:8])
    if erken_rows:
        print(f"\n## ERKEN KUSAK - hacim uyanmis (7g medyanin >= {evren.esik('erken_vol_x', 3.0):.0f}x), fiyat henuz oynamamis (KAPI DEGIL)")
        print(f"  {'COIN':8} {'volXgun':>7} {'chg24':>6} {'hacimM':>7} {'skor':>5} {'stage':>12} {'konum':>5} {'fund%':>7} {'smart':>5}")
        for r in erken_rows:
            print(f"  {r['sym']:8} {r.get('vol_x_gun', 0):>7} {r.get('chg24', 0):>+6.1f} {r.get('vol_musd', 0):>7} "
                  f"{(r.get('score') if r.get('score') is not None else '-'):>5} {(r.get('stage') or '-'):>12} "
                  f"{(r.get('pos') if r.get('pos') is not None else '-'):>5} "
                  f"{('%.3f' % r['funding']) if r.get('funding') is not None else '-':>7} {(r.get('smart') or '-')[:5]:>5}")
    show("DIP_YAKIT - neg-funding dip / squeeze kurulumu (DENEYSEL etiket, kapi DEGIL)", [r for r in rows if r.get("dip_yakit")][:8])
    show("AYRISMA - BTC'ye karsi goreli guc (DENEYSEL etiket, kapi DEGIL)", [r for r in rows if r.get("ayrisma")][:8])
    show("EN YUKSEK SKOR (genel, ilk 10)", rows[:10])
    print("\nNot: oncu olasilik; yon yukari da asagi da olabilir. DIP_YAKIT/AYRISMA = DENEYSEL etiket (kapi DEGIL; AYRISMA ayi-rejiminde NEGATIF-edge cikti). "
          "DIP_YAKIT + DUSUK_FLOAT = squeeze degil dusen-bicak riski (RE/FOGO). smart=top-trader yonu, taker=aggressor (Pillar D). Kisa liste -> CEO derin analiz + Bekci.")

if __name__ == "__main__":
    main()
