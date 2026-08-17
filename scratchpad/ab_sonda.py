# -*- coding: utf-8 -*-
"""A/B SONDASI — keep-alive olcumunun KONTROL GRUBU (2026-08-17).

[NEDEN VAR] `sure_sn` keep-alive icin KIRLI bir vekil: turun suresi taranan sembol
sayisiyla dogru orantili ve o sayi turdan tura oynuyor. Turlar hizlandiginda
"keep-alive mi, o saatte havuz mu kucuktu, yoksa ag mi iyilesti" sorusu sure
verisinden CEVAPLANAMAZ. Bu projede ayni soru daha once cevapsiz kaldi ve hala
Bekleyen'de duruyor (MA50+ucuz: "kuralin mi, radarin on elemesinin mi").

[NE OLCER] Mekanizmanin kendisini, havuz boyutundan BAGIMSIZ:
    A kolu — her cagride YENI baglanti (keep-alive oncesi davranis)
    B kolu — ayni baglanti yeniden kullanilir (keep-alive davranisi)
Ayni uc noktaya, ayni anda, sirayla.

[AYRIM KURALI]
    turlar hizlandi + sonda 2,0x gosteriyor          -> KEEP-ALIVE
    turlar hizlandi + sondanin A KOLU da dustu       -> AG iyilesmis
    turlar hizlanmadi + sonda 2,0x                   -> mekanizma calisiyor,
                                                        darbogaz baska yerde

[MALIYET] 2 x N hafif istek (ticker/price, agirlik 1). N=12 -> 24 cagri, gunluk
butcenin ~%0,03'u. Bota DOKUNMAZ: ayri surec, salt-okunur, kendi baglantisi.
"""
import sys, os, time, json, statistics as st, datetime, argparse
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import urllib.request, urllib3

URL = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT"
KAYIT = os.path.join(KOK, "scratchpad", "ab_sonda_kayit.jsonl")


def kol_a(n):
    """Her cagride YENI baglanti — keep-alive ONCESI davranisin birebir taklidi."""
    sureler = []
    for _ in range(n):
        t = time.time()
        req = urllib.request.Request(URL, headers={"User-Agent": "sonda/1.0"})
        json.load(urllib.request.urlopen(req, timeout=25))
        sureler.append(time.time() - t)
    return sureler


def kol_b(n):
    """Tek havuz, baglanti yeniden kullanilir — keep-alive davranisi."""
    havuz = urllib3.PoolManager(maxsize=4, retries=False,
                                headers={"User-Agent": "sonda/1.0",
                                         "Connection": "keep-alive"})
    havuz.request("GET", URL, timeout=urllib3.Timeout(connect=10, read=25))  # isinma
    sureler = []
    for _ in range(n):
        t = time.time()
        havuz.request("GET", URL, timeout=urllib3.Timeout(connect=10, read=25))
        sureler.append(time.time() - t)
    return sureler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--not", dest="notu", default="")
    a = ap.parse_args()

    A = kol_a(a.n)
    B = kol_b(a.n)
    mA, mB = st.median(A), st.median(B)
    kayit = {
        "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "n": a.n,
        "A_yeni_baglanti_medyan": round(mA, 4),
        "B_keepalive_medyan": round(mB, 4),
        "oran": round(mA / mB, 2) if mB else None,
        "A_min": round(min(A), 4), "A_maks": round(max(A), 4),
        "B_min": round(min(B), 4), "B_maks": round(max(B), 4),
        "not": a.notu,
    }
    with open(KAYIT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    print(f"{kayit['ts']}  A(yeni baglanti) {mA:.3f} sn | B(keep-alive) {mB:.3f} sn "
          f"| ORAN {kayit['oran']}x   {a.notu}")

    gecmis = [json.loads(l) for l in open(KAYIT, encoding="utf-8") if l.strip()]
    if len(gecmis) > 1:
        print("  gecmis sondalar:")
        for g in gecmis:
            print(f"    {g['ts']}  A {g['A_yeni_baglanti_medyan']:.3f}  "
                  f"B {g['B_keepalive_medyan']:.3f}  oran {g['oran']}x  {g.get('not','')}")


if __name__ == "__main__":
    main()
