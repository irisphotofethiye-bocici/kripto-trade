#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TP1 SONRASI STOP BASABASA CEKILSEYDI? — 11-12 Agustos gercek pozisyonlari (2026-08-12)

KULLANICI SORUSU: "11 ve 12'sinde girdigi pozisyonlarda TP1 calisinca stopu basabas
fiyata cekse kazanc daha fazla olur muydu? Acik olan pozlar dahil, zarardakiler dahil."

MEVCUT DAVRANIS (testbot.py:775): cikis_modu == "sabit_hedef" olan pozisyonlarda kismi
  kar alindiktan sonra stop AYNI KALIR (basabasa CEKILMEZ). Diger cikis modlarinda cekilir.

KAPSAM: kural yalnizca TP1'IN TETIKLENDIGI pozisyonlari etkiler. TP1 gormeden stop olan
  islemlerde iki senaryo BIREBIR AYNIDIR — o yuzden "kazanc farki" onlarda TANIMI GEREGI
  sifir. Yine de hepsi listelenir ki tablo eksik gorunmesin.

YONTEM: TP1 anindan itibaren 1 DAKIKALIK gercek mumlar cekilir.
  GERCEK    : kalan yari, ORIJINAL stop ile devam eder (bugun olan sey).
  ALTERNATIF: kalan yari, stop = GIRIS fiyati ile devam eder.
              Fiyat girise DEGERSE kapanir; degmezse gercekle ayni sonucu verir.
  Acik pozisyonlarda ikisi de SU ANKI fiyata gore degerlenir (gerceklesmemis).

MALIYET: cikista taker %0.045 + slipaj %0.02, canlinin aynisi. "Basabas" stop gercekte
  basabas DEGILDIR — giriste odenen ucret geri gelmez, cikista yeniden ucret odenir.
Funding ihmal (alternatif daha erken kapandigi icin bu, alternatif ALEYHINE kucuk bir
  yanliliktir — yani asagidaki fark alternatif icin biraz IYIMSERDIR).

Salt-okunur. Bota dokunmaz.
"""
import json, os, sys, time, datetime, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAPI = "https://fapi.binance.com"
TAKER, SLIP = 0.00045, 0.0002
GUNLER = ("2026-08-11", "2026-08-12")


def get(u):
    for k in range(4):
        try:
            r = urllib.request.Request(u, headers={"User-Agent": "kripto-arastirma/1.0"})
            with urllib.request.urlopen(r, timeout=25) as f:
                return json.loads(f.read().decode())
        except Exception:
            time.sleep(2 * (k + 1))
    return None


def klines(sym, bas_ms, son_ms):
    out, t = [], bas_ms
    while t < son_ms:
        d = get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1m"
                f"&startTime={t}&limit=1000")
        if not d:
            break
        out += [{"t": int(x[0]), "o": float(x[1]), "h": float(x[2]),
                 "l": float(x[3]), "c": float(x[4])} for x in d]
        yeni = int(d[-1][0]) + 60000
        if yeni <= t:
            break
        t = yeni
        time.sleep(0.35)
        if len(d) < 1000:
            break
    return [x for x in out if x["t"] <= son_ms]


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)


def cikis_pnl(giris, fiyat_piyasa, miktar, yon):
    """Canlinin maliyet muhasebesi: slipaj fiyata, taker notional'a."""
    ef = fiyat_piyasa * (1 - SLIP) if yon == "LONG" else fiyat_piyasa * (1 + SLIP)
    isaret = 1 if yon == "LONG" else -1
    return (ef - giris) * miktar * isaret - (miktar * ef) * TAKER


def main():
    kay = [json.loads(l) for l in open(os.path.join(KOK, "testbot_islemler.jsonl"),
                                       encoding="utf-8") if l.strip()]
    st = json.load(open(os.path.join(KOK, "testbot_state.json"), encoding="utf-8"))
    acik = {p["id"]: p for p in st["acik_pozisyonlar"]}

    # 11-12'de ACILAN veya o gunlerde islem goren pozisyonlari topla
    poz = {}
    for k in kay:
        poz.setdefault(k["id"], {"id": k["id"], "sym": k["sym"], "yon": k["yon"],
                                 "giris": k["giris"], "kayitlar": []})
        poz[k["id"]]["kayitlar"].append(k)
    for i, p in acik.items():
        poz.setdefault(i, {"id": i, "sym": p["sym"], "yon": p["yon"],
                           "giris": p["giris"], "kayitlar": []})

    ilgili = []
    for i, p in poz.items():
        ts = [k["ts"] for k in p["kayitlar"]]
        gts = acik[i]["giris_ts"] if i in acik else None
        if any(t[:10] in GUNLER for t in ts) or (gts and gts[:10] in GUNLER):
            ilgili.append(p)
    ilgili.sort(key=lambda p: p["id"])

    simdi = int(time.time() * 1000)
    print("=" * 118)
    print("TP1 SONRASI STOP BASABASA CEKILSEYDI? — 11-12 Agustos gercek pozisyonlari")
    print("=" * 118)

    etkilenen, etkisiz = [], []
    for p in ilgili:
        tp1 = next((k for k in p["kayitlar"] if k["sebep"] == "TP1_KISMI"), None)
        if tp1:
            etkilenen.append((p, tp1))
        else:
            etkisiz.append(p)

    print(f"\n11-12 Agustos'ta islem goren pozisyon: {len(ilgili)}")
    print(f"  TP1 TETIKLENEN (kural bunlari etkiler)     : {len(etkilenen)}")
    print(f"  TP1 gormeden kapanan (iki senaryo AYNI)    : {len(etkisiz)}")
    print("\nTP1 gormeyenler — fark TANIMI GEREGI sifir:")
    for p in etkisiz:
        son = p["kayitlar"][-1] if p["kayitlar"] else None
        if son:
            print(f"   id={p['id']:3} {p['sym']:10} {p['yon']:5} {son['sebep']:6} "
                  f"{son['sonuc_usdt']:+9.2f}$   fark 0.00$")

    print("\n" + "=" * 118)
    print("TP1 TETIKLENENLER — kalan yari iki senaryoda ne yapardi?")
    print("=" * 118)

    toplam_g, toplam_a = 0.0, 0.0
    satir = []
    for p, tp1 in etkilenen:
        sym, yon, giris = p["sym"], p["yon"], p["giris"]
        i = p["id"]
        canli = i in acik
        pos = acik.get(i)
        # kalan yari miktari: acikta pos["miktar"], kapanmista kapanis kaydinin notional'i
        kapanis = next((k for k in p["kayitlar"]
                        if k["sebep"] in ("TP2", "STOP", "SURE", "ZAMAN_STOP", "LIKIDASYON")
                        and k["ts"] > tp1["ts"]), None)
        if canli:
            miktar = pos["miktar"]
            stop_orij = pos["stop"]
        elif kapanis:
            miktar = kapanis["notional"] / kapanis["giris"]
            stop_orij = None
        else:
            continue

        bas = ms(tp1["ts"]) + 60000
        son = ms(kapanis["ts"]) if kapanis else simdi
        b = klines(sym, bas, son + 60000)
        if not b:
            print(f"   id={i} {sym}: veri alinamadi, atlandi")
            continue

        # --- GERCEK ---
        if kapanis:
            g_pnl = kapanis["sonuc_usdt"]
            g_ne = kapanis["sebep"]
        else:
            px = b[-1]["c"]
            g_pnl = (px - giris) * miktar * (1 if yon == "LONG" else -1)
            g_ne = "ACIK"

        # --- ALTERNATIF: stop = giris ---
        degdi = None
        for x in b:
            if (yon == "SHORT" and x["h"] >= giris) or (yon == "LONG" and x["l"] <= giris):
                degdi = x
                break
        if degdi:
            a_pnl = cikis_pnl(giris, giris, miktar, yon)
            a_ne = f"BASABAS {datetime.datetime.fromtimestamp(degdi['t']/1000):%d.%m %H:%M}"
        else:
            a_pnl, a_ne = g_pnl, g_ne + " (degmedi)"

        toplam_g += g_pnl
        toplam_a += a_pnl
        satir.append((i, sym, yon, tp1["ts"], tp1["sonuc_usdt"], g_ne, g_pnl, a_ne, a_pnl))

    print(f"\n{'id':>4} {'coin':10}{'TP1 zamani':18}{'TP1 kari':>10}   "
          f"{'GERCEK (kalan yari)':28}{'ALTERNATIF (basabas stop)':32}{'FARK':>10}")
    print("-" * 118)
    for i, sym, yon, t, k1, g_ne, g, a_ne, a in satir:
        print(f"{i:>4} {sym:10}{t[5:16]:18}{k1:+10.2f}   "
              f"{g_ne:<12}{g:+10.2f}$      {a_ne:<20}{a:+10.2f}$  {a-g:+10.2f}")
    print("-" * 118)
    print(f"{'TOPLAM (yalniz kalan yarilar)':>64}{toplam_g:+10.2f}$"
          f"{'':22}{toplam_a:+10.2f}$  {toplam_a-toplam_g:+10.2f}")
    print(f"\n  Not: TP1'de alinan kar ({sum(s[4] for s in satir):+.2f}$) IKI SENARYODA DA AYNI —")
    print("       o yuzden ustteki tabloya dahil edilmedi; fark yalniz KALAN YARIDAN gelir.")


if __name__ == "__main__":
    main()
