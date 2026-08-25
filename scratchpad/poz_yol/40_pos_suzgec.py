#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pos RET SUZGECI — on-kayit ON_KAYIT_pos_suzgec.md.

OLCUTLER ON-KAYITTA SABIT — burada TEKRAR EDILMEZ, hesaplanip basilir.

⚠️ ON-KAYITTAN SAPMA (kosumdan once tespit edildi, ACIKCA raporlanir):
   `BOGA_LONG` kapisi `skor` ve `smart` istiyor; ikisi de RADAR ciktisi ve
   klines_1h_uzun'dan URETILEMEZ. Bu kapi OLCULEMEDI olarak isaretlenir,
   zorlanmaz. Dolayisiyla olcut **Y1 (yon tutarliligi) da OLCULEMEDI** —
   iki kapinin ikisi de SHORT. Yerine bilgilendirici bir SIMETRI kontrolu
   raporlanir; o kontrol OLCUTLERE DAHIL DEGILDIR.

KOLLAR (ayrik, alt-kume degil):
   TUTULAN     kapiyi gecen VE suzgeci gecen
   REDDEDILEN  kapiyi gecen VE suzgece takilan
   TUMU        kapiyi gecen hepsi (gercek kiyas)
SHORT kapilarinda suzgec `pos < ESIK` olanlari REDDEDER (on-kayitta boyle yazildi:
   "cok kosan geri kalir" -> SHORT'ta yuksek pos IYI olmali).

SALT OKUMA.
"""
import os, sys, json, datetime, collections, statistics as sx, math

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
import fonlama_oku as fo                                        # noqa: E402

KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
ADIM, MIN_QV, UFUK = 4, 125000, 24
MALIYET, HEDEF = 0.1726, 10.0
STOPLAR = [3.0, 5.0, 8.0]
BIRINCIL = 5.0
ESIK, ESIK_SAGLAM = 0.75, [0.70, 0.85]
FUND_ESIK, UCUZ, MA50_MESAFE = -0.05, 0.07, 3.72


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp() * 1000)


PENCERE = [
    ("ATH 24-09/12", ms("2024-09-15"), ms("2024-12-15")),
    ("ATH 25-06/10", ms("2025-06-01"), ms("2025-10-15")),
    ("TOPARLANMA 25-04", ms("2025-04-03"), ms("2025-05-15")),
    ("DERIN-AYI 26-01", ms("2026-01-05"), ms("2026-03-20")),
    ("AYI 26-06/08", ms("2026-06-24"), ms("2026-08-19")),
]


def mekanik(b, i, ref, yon, stop, ft, fr):
    sonbar = min(i + UFUK, len(b) - 1)
    if yon == "LONG":
        sl, tp = ref * (1 - stop / 100), ref * (1 + HEDEF / 100)
    else:
        sl, tp = ref * (1 + stop / 100), ref * (1 - HEDEF / 100)
    ham, cj = None, sonbar
    for j in range(i + 1, sonbar + 1):
        x = b[j]
        vs = (x["l"] <= sl) if yon == "LONG" else (x["h"] >= sl)
        vh = (x["h"] >= tp) if yon == "LONG" else (x["l"] <= tp)
        if vs:
            ham, cj = -stop, j
            break
        if vh:
            ham, cj = HEDEF, j
            break
    if ham is None:
        c = b[sonbar]["c"]
        ham = ((c - ref) if yon == "LONG" else (ref - c)) / ref * 100
    return ham - MALIYET + fo.dilim(ft, fr, b[i + 1]["t"], b[cj]["t"], yon)


def topla():
    kova = {(k, ad): [] for k in ("A_funding", "B_ma50ucuz") for ad, _, _ in PENCERE}
    dosya = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    for n, fn in enumerate(dosya, 1):
        sym = fn[:-5]
        if sym == "BTC":
            continue
        try:
            with open(os.path.join(KLINE, fn), encoding="utf-8") as f:
                b = json.load(f)
        except Exception:
            continue
        if len(b) < 100:
            continue
        try:
            ft, fr = fo.yukle(sym)
        except fo.BirimHatasi as e:
            print("  ATLANDI %s: %s" % (sym, e))
            continue
        # MA50 (1 saatlik, 50 bar)
        ma = [None] * len(b)
        top = 0.0
        for j, x in enumerate(b):
            top += x["c"]
            if j >= 50:
                top -= b[j - 50]["c"]
            if j >= 49:
                ma[j] = top / 50.0
        for i in range(50, len(b) - UFUK - 2, ADIM):
            x = b[i]
            if (x.get("qv") or 0) < MIN_QV:
                continue
            ad = None
            for a, t0, t1 in PENCERE:
                if t0 <= x["t"] < t1:
                    ad = a
                    break
            if ad is None:
                continue
            ref = b[i + 1]["o"]
            if ref <= 0:
                continue
            pen = b[i - 20:i + 1]
            lo = min(z["l"] for z in pen)
            hi = max(z["h"] for z in pen)
            if hi <= lo:
                continue
            pos = (x["c"] - lo) / (hi - lo)
            # --- kapilar (ileri_rr ile ayni, fonlama esigi DUZELTILMIS) ---
            kapilar = []
            if ft:
                import bisect as _b
                kk = _b.bisect_right(ft, x["t"]) - 1
                if kk >= 0 and fr[kk] <= FUND_ESIK:
                    kapilar.append("A_funding")
            if ma[i] and ma[i] > 0 and x["c"] <= UCUZ:
                if (x["c"] / ma[i] - 1) * 100 >= MA50_MESAFE:
                    kapilar.append("B_ma50ucuz")
            if not kapilar:
                continue
            gun = datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d")
            r = {"sym": sym, "gun": gun, "pos": pos}
            for sp in STOPLAR:
                r["S%d" % int(sp)] = mekanik(b, i, ref, "SHORT", sp, ft, fr)
                r["L%d" % int(sp)] = mekanik(b, i, ref, "LONG", sp, ft, fr)
            for kp in kapilar:
                kova[(kp, ad)].append(r)
        if n % 150 == 0:
            print("  ... %d/%d sembol" % (n, len(dosya)))
            sys.stdout.flush()
    return kova


def gun_iki_ornek(tut, red, alan):
    """gun-kumeli iki-ornekli fark: her gun ort(TUTULAN) - ort(REDDEDILEN)."""
    g = collections.defaultdict(lambda: [[], []])
    for x in tut:
        g[x["gun"]][0].append(x[alan])
    for x in red:
        g[x["gun"]][1].append(x[alan])
    gunluk = [sx.mean(a) - sx.mean(b) for a, b in g.values() if len(a) >= 3 and len(b) >= 3]
    if len(gunluk) < 8:
        return None, None, len(gunluk)
    m, sd = sx.mean(gunluk), sx.pstdev(gunluk)
    return m, (m / (sd / math.sqrt(len(gunluk))) if sd > 0 else None), len(gunluk)


def bol(v, esik):
    """SHORT kapisi -> suzgec pos < esik olanlari REDDEDER."""
    return ([x for x in v if x["pos"] >= esik], [x for x in v if x["pos"] < esik])


if __name__ == "__main__":
    print("pos RET SUZGECI — on-kayit ON_KAYIT_pos_suzgec.md")
    print("ESIK=%.2f · stop birincil %%%.0f · ufuk %dsa · maliyet %%%.4f"
          % (ESIK, BIRINCIL, UFUK, MALIYET))
    print("⚠️ BOGA_LONG kapisi OLCULEMEDI (skor/smart klines'tan uretilemiyor)")
    print("⚠️ Olcut Y1 (yon tutarliligi) bu yuzden OLCULEMEDI\n")
    kova = topla()

    sonuc = collections.defaultdict(dict)
    for kp in ("A_funding", "B_ma50ucuz"):
        print("\n" + "=" * 104)
        print("KAPI: %s   (SHORT · suzgec: pos < %.2f REDDEDILIR)" % (kp, ESIK))
        print("=" * 104)
        print("  %-20s %6s %6s %9s %9s %9s %8s %7s %7s" %
              ("pencere", "N", "tut%", "TUTULAN", "REDDEDIL", "TUMU", "FARK", "gun-t", "T-TUMU"))
        print("  " + "-" * 96)
        for ad, _, _ in PENCERE:
            v = kova[(kp, ad)]
            if len(v) < 200:
                print("  %-20s N=%d YETERSIZ" % (ad, len(v)))
                continue
            alan = "S%d" % int(BIRINCIL)
            tut, red = bol(v, ESIK)
            if len(tut) < 60 or len(red) < 60:
                print("  %-20s kol dengesiz (tut %d / red %d)" % (ad, len(tut), len(red)))
                continue
            m, t, ng = gun_iki_ornek(tut, red, alan)
            mt = sx.mean(x[alan] for x in tut)
            mr = sx.mean(x[alan] for x in red)
            mh = sx.mean(x[alan] for x in v)
            kaps = 100.0 * len(tut) / len(v)
            sonuc[kp][ad] = (m, t, mt, mr, mh, kaps, tut, red, v)
            print("  %-20s %6d %5.1f%% %+9.3f %+9.3f %+9.3f %+8.3f %+7s %+7.3f"
                  % (ad, len(v), kaps, mt, mr, mh,
                     m if m is not None else float("nan"),
                     ("%.2f" % t) if t is not None else "-", mt - mh))

    print("\n" + "=" * 104)
    print("OLCUT DEGERLENDIRMESI (ON_KAYIT_pos_suzgec.md)")
    print("=" * 104)
    for kp in ("A_funding", "B_ma50ucuz"):
        d = sonuc[kp]
        if not d:
            print("  %-12s veri yok" % kp)
            continue
        s1 = sum(1 for a in d if d[a][0] is not None and d[a][0] > 0)
        s2 = sum(1 for a in d if d[a][1] is not None and d[a][1] >= 2.0)
        u1 = sum(1 for a in d if d[a][2] > d[a][4])
        u2 = sum(1 for a in d if d[a][2] - d[a][4] >= 0.05)
        u3 = sum(1 for a in d if d[a][5] >= 60.0)
        n = len(d)
        print("\n  %s  (olculen pencere: %d)" % (kp, n))
        print("    S1 fark>0 >=4/5            : %d/%d  %s" % (s1, n, "GECTI" if s1 >= 4 else "DUSTU"))
        print("    S2 gun-t>=2,0 >=3/5        : %d/%d  %s" % (s2, n, "GECTI" if s2 >= 3 else "DUSTU"))
        print("    U1 TUTULAN > TUMU >=4/5    : %d/%d  %s" % (u1, n, "GECTI" if u1 >= 4 else "DUSTU"))
        print("    U2 kazanc>=+0,05 >=3/5     : %d/%d  %s" % (u2, n, "GECTI" if u2 >= 3 else "DUSTU"))
        print("    U3 kapsam>=%%60 (her pen.) : %d/%d  %s" % (u3, n, "GECTI" if u3 == n else "DUSTU"))
        # S3: uc stopta da
        s3 = True
        for sp in STOPLAR:
            c = 0
            for a in d:
                _, _, _, _, _, _, tut, red, v = d[a]
                m, _, _ = gun_iki_ornek(tut, red, "S%d" % int(sp))
                if m is not None and m > 0:
                    c += 1
            if c < 4:
                s3 = False
        print("    S3 uc stopta de >=4/5      : %s" % ("GECTI" if s3 else "DUSTU"))
    print("\n  Y1 (yon tutarliligi) : OLCULEMEDI — iki kapi da SHORT, LONG kapisi replay edilemiyor")
    print("\nKarar tablosu ON_KAYIT_pos_suzgec.md'de. Bot dosyalarina yazim: YOK")
