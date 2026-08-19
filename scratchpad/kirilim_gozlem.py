# -*- coding: utf-8 -*-
"""BTC KIRILIM PENCERESI — canli gozlem toplayicisi (2026-08-19).

[NEDEN VAR] BTC 44 gunluk sikisma araligini (62.8k-64.9k kapanis, %3,4 genislik)
2026-08-19 15:00 UTC saatinde kirdi: 65.895 -> 70.450 tepe -> 68.523 kapanis,
hacim 103.352 BTC (onceki saatlerin ~30 kati). Bot 111/121 pozisyonla YAPISAL
SHORT (%92) ve tezi "MA50+ucuz" = MA50'nin cok ustundeki ucuz coinleri satmak,
yani ORTALAMAYA DONUS. Genis bir melt-up bu tezin en kotu ortamidir.

[NE TOPLAR] Her cagride tek satir JSONL — piyasa + botun o andaki hali yan yana.
Sonradan "kirilim aninda bot ne yapiyordu" sorusu ancak boyle cevaplanabilir;
radar_archive NOKTASAL veridir ve bu ozel soruyu tasimaz.

[ON-KAYIT — sonucu gormeden yazildi]
  H1 Genis melt-up'ta MA50+ucuz SHORT'lari daha sik stoplanir.
     Olcut: kirilim penceresinde SHORT stop orani, pencere oncesi 30 gunun
     SHORT stop oranini en az 15 puan asarsa H1 desteklenir.
  H2 Bot kirilimi GORMEZ, short acmaya devam eder (rejim korumasi yok).
     Olcut: kirilimden sonraki 24 saatte acilan LONG payi < %20 ise H2 dogrudur.
  BEKLENTI: H2'nin dogru cikmasi kuvvetle muhtemel (rejim_giriste alani var ama
  yon secimine girmiyor); H1 belirsiz — alt'lar BTC'den az yukselirse SHORT'lar
  kurtulabilir. Nitekim ilk anlik goruntude 3 short net +15,50 idi.

  ⚠ BU BIR VERI TOPLAMADIR, KURAL DEGIL. Hukum penceresi dolmadan yazilmaz;
  "en iyi hucre secilmez" kurali burada da gecerli.

[BOTA DOKUNMAZ] Ayri surec, salt-okunur. testbot_state.json yalniz OKUNUR.
"""
import json, os, sys, time, datetime, urllib.request, argparse

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATEF = os.path.join(KOK, "testbot_state.json")
CIKTI = os.path.join(KOK, "scratchpad", "kirilim_gozlem.jsonl")
FAPI = "https://fapi.binance.com"


def _get(u, tekrar=2):
    for i in range(tekrar + 1):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "gozlem/1.0"})
            return json.load(urllib.request.urlopen(req, timeout=20))
        except Exception:
            if i == tekrar:
                return None
            time.sleep(2)


def anlik():
    d = {"ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         "ts_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}

    # --- PIYASA ---
    fi = _get(f"{FAPI}/fapi/v1/ticker/price")
    c24 = _get(f"{FAPI}/fapi/v1/ticker/24hr")
    if fi and c24:
        fiyat = {x["symbol"]: float(x["price"]) for x in fi}
        chg = {x["symbol"]: float(x["priceChangePercent"]) for x in c24}
        d["btc"] = fiyat.get("BTCUSDT")
        d["btc_chg24"] = chg.get("BTCUSDT")
        d["eth"] = fiyat.get("ETHUSDT")
        d["eth_chg24"] = chg.get("ETHUSDT")
        usdt = [v for k, v in chg.items() if k.endswith("USDT")]
        d["perp_sayisi"] = len(usdt)
        d["yukselen_pay"] = round(sum(1 for v in usdt if v > 0) / len(usdt), 4) if usdt else None
        # genislik: alt'lar BTC'yi geciyor mu (BTC.D vekili)
        d["btc_ustu_pay"] = round(sum(1 for v in usdt if v > (chg.get("BTCUSDT") or 0)) / len(usdt), 4) if usdt else None

    oi = _get(f"{FAPI}/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&limit=2")
    if oi and len(oi) >= 2:
        d["btc_oi"] = float(oi[-1]["sumOpenInterest"])
        d["btc_oi_5m_pct"] = round(100 * (float(oi[-1]["sumOpenInterest"]) -
                                          float(oi[-2]["sumOpenInterest"])) /
                                   float(oi[-2]["sumOpenInterest"]), 3)
    ls = _get(f"{FAPI}/futures/data/takerlongshortRatio?symbol=BTCUSDT&period=5m&limit=1")
    if ls:
        d["btc_taker_ls"] = round(float(ls[-1]["buySellRatio"]), 3)
    pr = _get(f"{FAPI}/fapi/v1/premiumIndex?symbol=BTCUSDT")
    if pr:
        d["btc_funding_oran"] = float(pr["lastFundingRate"])
        d["btc_mark"] = float(pr["markPrice"])

    # --- BOT (SALT-OKUNUR) ---
    try:
        s = json.load(open(STATEF, encoding="utf-8"))
    except Exception as e:
        d["bot_hata"] = str(e)[:120]
        return d
    ap = s.get("acik_pozisyonlar", [])
    d["equity"] = round(s.get("equity", 0), 2)
    d["durum"] = s.get("durum")
    d["son_cycle_ts"] = s.get("son_cycle_ts")
    d["kesilen_tur"] = s.get("kesilen_tur")
    d["bekleyen_sayisi"] = len(s.get("bekleyenler") or [])
    d["cooldown_sayisi"] = len(s.get("cooldown") or {})
    d["acik_sayisi"] = len(ap)
    d["acik_long"] = sum(1 for p in ap if p.get("yon") == "LONG")
    d["acik_short"] = sum(1 for p in ap if p.get("yon") == "SHORT")

    gerceklesmemis, poz = 0.0, []
    for p in ap:
        f = (fiyat.get(p["sym"] + "USDT") if fi else None)
        kayit = {"sym": p["sym"], "yon": p["yon"], "giris": p["giris"],
                 "stop": p["stop"], "giris_ts": p.get("giris_ts"),
                 "tp1_alindi": bool(p.get("tp1_alindi")),
                 "risk_usdt": p.get("risk_usdt"),
                 "chg24_giriste": p.get("chg24_giriste"),
                 "rejim_giriste": p.get("rejim_giriste"),
                 "smart_giriste": p.get("smart_giriste"),
                 "fiyat": f, "chg24": (chg.get(p["sym"] + "USDT") if c24 else None)}
        if f:
            # kalan miktar: TP1 alindiysa yari kapandi
            mik = p["miktar"] * (0.5 if p.get("tp1_alindi") else 1.0)
            pnl = (p["giris"] - f) * mik if p["yon"] == "SHORT" else (f - p["giris"]) * mik
            kayit["pnl"] = round(pnl, 2)
            kayit["r"] = round(pnl / p["risk_usdt"], 3) if p.get("risk_usdt") else None
            # stop'a uzaklik: SHORT'ta stop YUKARIDA
            kayit["stop_uzaklik_pct"] = round(100 * (p["stop"] - f) / f, 3)
            gerceklesmemis += pnl
        poz.append(kayit)
    d["gerceklesmemis"] = round(gerceklesmemis, 2)
    d["etkin_kasa"] = round(s.get("equity", 0) + gerceklesmemis, 2)   # CLAUDE.md: etkin != realize
    d["pozisyonlar"] = poz
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aralik", type=int, default=300, help="saniye (0 = tek atis)")
    ap.add_argument("--sure", type=int, default=0, help="toplam saniye (0 = sinirsiz)")
    a = ap.parse_args()
    bas = time.time()
    while True:
        d = anlik()
        with open(CIKTI, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
            fh.flush(); os.fsync(fh.fileno())
        print(f"{d['ts']}  BTC {d.get('btc')}  ({d.get('btc_chg24')}%)  "
              f"yukselen %{100*(d.get('yukselen_pay') or 0):.0f}  |  "
              f"acik {d.get('acik_sayisi')} (L{d.get('acik_long')}/S{d.get('acik_short')})  "
              f"gerceklesmemis {d.get('gerceklesmemis')}  etkin {d.get('etkin_kasa')}",
              flush=True)
        if a.aralik <= 0:
            break
        if a.sure and time.time() - bas >= a.sure:
            break
        time.sleep(a.aralik)
    return 0


if __name__ == "__main__":
    sys.exit(main())
