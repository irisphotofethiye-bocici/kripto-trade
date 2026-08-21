#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TAVAN OLCUMU — aranacak bir sey var mi? (ONGORU MERDIVENI)

KULLANICI (2026-08-21): "bu kadar veri cektik, hicbir veri sinyal vermiyor mu?"

SIMDIYE KADAR hep "su kural ise yariyor mu" diye soruldu; 9 cikis fikri de
dustu. HIC SORULMAYAN soru: aranacak SEY ne kadar var?

  mukemmel cikis (tepede cik)  ne kazandirirdi?
  hic ongorusuz cikis          ne kazandiriyor?
  arasindaki MESAFE            = aranabilecek toplam bilgi

Mesafe kucukse ARAMA BITER (sinyal yok degil, ODUL yok).
Mesafe buyukse problem "sinyal yok" degil, "yanlis yerde ariyoruz".

SIZINTIYI ONLEYEN TASARIM (32_rastgele_kontrol.py'nin hatasi buydu):
  Rastgele cikis pozisyonun OMRUNU biliyordu -> kisa omurluda erken cikiyordu.
  BURADA: her pozisyon ayni N barlik pencereye KIRPILIR. Butun kollar ayni
  pencereyi gorur. Sabit-bar kolu her pozisyonda AYNI j'de cikar. Omur bilgisi
  hicbir kola sizmaz.

ONGORU MERDIVENI — k bar ileri gorebilen kahin:
  k=0    hic ongoru yok       -> sabit bar j'de cik (j taranir)
  k=1    1 bar (5 dk) ileri   -> "sonraki bar daha dusukse cik"
  k=3    3 bar (15 dk) ileri
  k=6/12 30 dk / 60 dk ileri
  k=inf  tum pencereyi bilir  -> TEPEDE cik (ulasilamaz tavan)

IKI AYRI TAVAN (hangisinde para var?):
  ZAMANLAMA KAHINI : hangi ANDA cikacagini bilir
  SECIM KAHINI     : hangi POZISYONUN kazanacagini bilir (sonuna kadar tutar)

MALIYET SABIT: her kolda tam 1 giris + 1 cikis var -> maliyet MESAFEYI
  degistirmez. Brut raporlanir, bu acikca yazilir.

HUKUM YAZILMAZ. SALT OKUMA.
"""
import os, sys, datetime, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak                                                    # noqa: E402

F = "%Y-%m-%d %H:%M:%S"
BOLEN = datetime.datetime(2026, 8, 19, 18, 15)
UFUK = [12, 24, 72, 144]          # 1sa · 2sa · 6sa · 12sa (5 dk bar)
KADEME = [1, 3, 6, 12]            # k bar ileri goren kahin


def hazirla():
    out = []
    for p in ortak.pozisyonlar(en_az_goruntu=13, zengin=False):
        pnl = [g.get("pnl_pct") for g in p["seri"]]
        if any(x is None for x in pnl):
            continue
        out.append({"sym": p["sym"], "yon": p["yon"], "pnl": pnl,
                    "gir": datetime.datetime.strptime(p["seri"][0]["ts"], F),
                    "sonuc": p["sonuc"]})
    return out


def kahin_k(w, k):
    """k bar ileri goren kahin: sonraki k barin HEPSI daha dusukse CIK."""
    n = len(w)
    for i in range(1, n - 1):
        if all(w[j] <= w[i] for j in range(i + 1, min(i + 1 + k, n))):
            return w[i]
    return w[-1]


def sabit_bar(P, j, N):
    return sx.mean(p["pnl"][j] for p in P if len(p["pnl"]) > N - 1)


def rapor(P, ad):
    print("\n" + "=" * 96)
    print("%s   N=%d pozisyon" % (ad, len(P)))
    print("=" * 96)
    if len(P) < 20:
        print("  N yetersiz")
        return
    for N in UFUK:
        # HAYATTA-KALMA YANLILIGI DUZELTMESI: pencereden ONCE kapanan pozisyon
        # orneklemden DUSMEZ; kapanis degerinde sabit tutulur (kapali pozisyon
        # daha fazla kar/zarar uretmez). Yoksa erken olenler elenir ve "TUT"
        # kolu sahte iyi gorunur: 86 -> 26 pozisyona dusuyordu.
        Q, kirpik = [], 0
        for z in P:
            w = z["pnl"][:N]
            if len(w) < N:
                kirpik += 1
                w = w + [w[-1]] * (N - len(w))
            z["_w"] = w
            Q.append(z)
        if len(Q) < 20:
            print("  --- pencere %3d bar: N=%d YETERSIZ" % (N, len(Q)))
            continue
        W = [z["_w"] for z in Q]
        tut = sx.mean(w[-1] for w in W)              # k=0, sona kadar tut
        tepe = sx.mean(max(w) for w in W)            # k=sonsuz
        dip = sx.mean(min(w) for w in W)
        # k=0: en iyi SABIT bar (butun pozisyonlarda ayni j)
        sabit = [(sx.mean(w[j] for w in W), j) for j in range(1, N)]
        en_sabit, en_j = max(sabit)
        ort_sabit = sx.mean(x[0] for x in sabit)
        print("\n  --- pencere %3d bar (%2d sa) · %d pozisyon" % (N, N // 12, len(Q)))
        print("      ONGORU MERDIVENI (islem basi BRUT puan; maliyet her kolda ayni)")
        print("      %-34s %9s %9s" % ("kol", "getiri", "tavanin"))
        acik = tepe - tut
        def sat(ad2, v):
            pay = (v - tut) / acik * 100 if acik > 1e-9 else float("nan")
            print("      %-34s %+9.3f %8.0f%%" % (ad2, v, pay))
        sat("sona kadar TUT  (referans)", tut)
        sat("rastgele sabit bar (ort)", ort_sabit)
        sat("en iyi sabit bar (j=%d, %d dk)" % (en_j, en_j * 5), en_sabit)
        for k in KADEME:
            sat("kahin k=%-2d (%3d dk ileri gorur)" % (k, k * 5), sx.mean(kahin_k(w, k) for w in W))
        sat("KAHIN k=sonsuz (TEPEDE cikar)", tepe)
        print("      %-34s %+9.3f" % ("(en kotu: DIPTE cikar)", dip))
        print("      ARANABILIR TOPLAM MESAFE (tepe - tut)  = %+.3f puan" % acik)
        # SECIM kahini: kaybedeni hic acmasak
        kaz = [w[-1] for w in W if w[-1] > 0]
        secim = sum(kaz) / len(W)
        print("      SECIM kahini (kaybedeni hic acma)      = %+.3f puan  (%d/%d kazanan)"
              % (secim, len(kaz), len(W)))
        print("      ZAMANLAMA mesafesi %+.3f  ·  SECIM mesafesi %+.3f"
              % (acik, secim - tut))


if __name__ == "__main__":
    P = hazirla()
    print("TAVAN OLCUMU — ongoru merdiveni · %d pozisyon (>=13 goruntu)" % len(P))
    print("sizinti YOK: her kol ayni N barlik pencereyi gorur, omur bilgisi kullanilmaz")
    a = [p for p in P if p["gir"] < BOLEN]
    b = [p for p in P if p["gir"] >= BOLEN]
    rapor(a, "A) NOTR/AYI   .. 08-19 18:15")
    rapor(b, "B) BOGA       08-19 18:15 ..")
    rapor(P, "C) HEPSI (kiyas icin)")
    print("\nHUKUM YAZILMADI. bot dosyalarina yazim: YOK")
