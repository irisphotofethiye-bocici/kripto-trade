#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POZISYONLARIN GORDUGU EN YUKSEK KAGIT KAR (2026-08-12)

SORU (kullanici): 11-12 Agustos'ta acilan pozisyonlar artida ne kadar bekledi,
ve artidayken gordukleri EN YUKSEK rakam neydi?

YONTEM: her pozisyon icin giristen cikisa (acikta ise SIMDIYE) kadar 1 DAKIKALIK
barlar cekilir; her barda gerceklesmemis P&L hesaplanip TEPE noktasi bulunur.

KISMI KAR DOGRU MODELLENIR: TP1 alindiktan sonra pozisyon YARIYA iner, ama alinan
kar realize olmustur. Yani kismi sonrasi:  P&L = realize_kismi + yari_miktar x hareket
Aksi halde tepe rakami sisirilmis olurdu.

Salt-okunur; bota dokunmaz.
"""
import json, os, sys, time, datetime, urllib.request

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURA)
FAPI = "https://fapi.binance.com"


def get(url, deneme=4):
    for k in range(deneme):
        try:
            r = urllib.request.Request(url, headers={"User-Agent": "kripto-rapor/1.0"})
            with urllib.request.urlopen(r, timeout=25) as f:
                return json.loads(f.read().decode())
        except Exception:
            time.sleep(1.5 * (k + 1))
    return None


def barlar_1m(sym, bas_ms, son_ms):
    out, t = [], bas_ms
    while t < son_ms:
        d = get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1m&startTime={t}&limit=1500")
        if not d:
            break
        out += [{"t": int(x[0]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4])} for x in d]
        yeni = int(d[-1][0]) + 60000
        if yeni <= t:
            break
        t = yeni
        if len(d) < 1500:
            break
        time.sleep(0.15)
    return [b for b in out if b["t"] <= son_ms]


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)


def analiz(sym, yon, giris, miktar0, bas, son, kismi_ts=None, kismi_kar=0.0):
    """Doner: tepe_pnl, tepe_zamani, artida_gecen_dk, toplam_dk, son_pnl"""
    b = barlar_1m(sym, bas, son)
    if not b:
        return None
    yi = 1 if yon == "LONG" else -1
    kismi_ms = ms(kismi_ts) if kismi_ts else None
    tepe, tepe_t, artida, son_pnl = -1e18, None, 0, 0.0
    for x in b:
        if kismi_ms and x["t"] >= kismi_ms:
            mik, realize = miktar0 / 2.0, kismi_kar
        else:
            mik, realize = miktar0, 0.0
        # en LEHTE fiyat: SHORT icin dusuk, LONG icin yuksek
        lehte = x["l"] if yon == "SHORT" else x["h"]
        pnl_tepe = (lehte - giris) * mik * yi + realize
        if pnl_tepe > tepe:
            tepe, tepe_t = pnl_tepe, x["t"]
        kapanis_pnl = (x["c"] - giris) * mik * yi + realize
        if kapanis_pnl > 0:
            artida += 1
        son_pnl = kapanis_pnl
    return {"tepe": tepe, "tepe_t": tepe_t, "artida_dk": artida,
            "toplam_dk": len(b), "son_pnl": son_pnl}


def main():
    st = json.load(open(os.path.join(KOK, "testbot_state.json"), encoding="utf-8"))
    rows = [json.loads(l) for l in open(os.path.join(KOK, "testbot_islemler.jsonl"),
                                        encoding="utf-8") if l.strip()]
    kismi = {r["sym"]: r for r in rows if r.get("sebep") == "TP1_KISMI"}
    simdi = int(time.time() * 1000)

    kayitlar = []
    # --- acik pozisyonlar
    for p in st["acik_pozisyonlar"]:
        k = kismi.get(p["sym"])
        alindi = bool(p.get("tp1_alindi"))
        mik0 = p["miktar"] * 2 if alindi else p["miktar"]
        kayitlar.append({"sym": p["sym"], "yon": p["yon"], "giris": p["giris"],
                         "mik0": mik0, "bas": ms(p["giris_ts"]), "son": simdi,
                         "durum": "ACIK", "marjin": p["marjin"] * (2 if alindi else 1),
                         "kismi_ts": k["ts"] if (alindi and k) else None,
                         "kismi_kar": k["sonuc_usdt"] if (alindi and k) else 0.0,
                         "gerceklesen": None, "giris_ts": p["giris_ts"]})
    # --- kapanmis islemler (11 Agustos ve sonrasi)
    for r in rows:
        if r["ts"] < "2026-08-11" or r.get("sebep") == "TP1_KISMI":
            continue
        cik = ms(r["ts"])
        bas = cik - int((r.get("tutma_saat") or 0) * 3600 * 1000)
        mik0 = (r.get("notional") or 0) / r["giris"] if r.get("giris") else 0
        if mik0 <= 0:
            continue
        kayitlar.append({"sym": r["sym"], "yon": r["yon"], "giris": r["giris"],
                         "mik0": mik0, "bas": bas, "son": cik, "durum": r.get("sebep"),
                         "marjin": r.get("marjin"), "kismi_ts": None, "kismi_kar": 0.0,
                         "gerceklesen": r.get("sonuc_usdt"),
                         "giris_ts": datetime.datetime.fromtimestamp(bas/1000).strftime("%m-%d %H:%M")})
    kayitlar.sort(key=lambda x: x["bas"])

    print("=" * 118)
    print("POZISYONLARIN GORDUGU EN YUKSEK KAGIT KAR — 11-12 Agustos")
    print("=" * 118)
    print("Kaynak: 1 dakikalik barlar, giristen cikisa (acikta ise simdiye). "
          "Kismi kar dogru modellendi.\n")
    print(f"{'sembol':10}{'giris':>12}{'durum':>12}{'TEPE $':>10}{'tepe zamani':>13}"
          f"{'gerceklesen':>13}{'birakilan':>11}{'artida':>9}{'sure':>8}")
    print("-" * 118)
    top_tepe = top_ger = 0.0
    for r in kayitlar:
        a = analiz(r["sym"], r["yon"], r["giris"], r["mik0"], r["bas"], r["son"],
                   r["kismi_ts"], r["kismi_kar"])
        if not a:
            print(f"{r['sym']:10}  (veri alinamadi)")
            continue
        ger = r["gerceklesen"] if r["gerceklesen"] is not None else a["son_pnl"]
        birakilan = a["tepe"] - ger
        tt = datetime.datetime.fromtimestamp(a["tepe_t"] / 1000).strftime("%m-%d %H:%M")
        oran = a["artida_dk"] / a["toplam_dk"] * 100 if a["toplam_dk"] else 0
        top_tepe += max(a["tepe"], 0); top_ger += ger
        print(f"{r['sym']:10}{r['giris_ts'][-11:]:>12}{str(r['durum'])[:11]:>12}"
              f"{a['tepe']:+10.0f}{tt:>13}{ger:+13.0f}{birakilan:+11.0f}"
              f"{oran:8.0f}%{a['toplam_dk']/60:7.1f}s")
    print("-" * 118)
    print(f"{'TOPLAM':10}{'':12}{'':12}{top_tepe:+10.0f}{'':13}{top_ger:+13.0f}"
          f"{top_tepe - top_ger:+11.0f}")
    print("\n  TEPE $      : pozisyonun gordugu en yuksek kagit kar (kismi kar dahil)")
    print("  gerceklesen : kapanmislarda gercek sonuc, aciklarda su anki P&L")
    print("  birakilan   : tepe ile gerceklesen arasindaki fark (geri verilen kar)")
    print("  artida      : surenin yuzde kaci artida gecti (bar kapanislarina gore)")


if __name__ == "__main__":
    main()
