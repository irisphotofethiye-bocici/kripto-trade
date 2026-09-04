#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RISK PARITESI — tutuyor mu, nerede kiriliyor?
On-kayit: ON_KAYIT_risk_paritesi.md (commit cd97004, KOSUMDAN ONCE). Olcutler SABIT.

🔑 ARTEFAKTTAN BAGIMSIZ BUYUKLUK: R = fiyat hareketi / stop mesafesi.
   Hem pay hem payda giriste belirlenir, BOYUTTAN BAGIMSIZDIR.
   SigmaR > 0 ise "her islemde ayni dolar riski alinsaydi defter artida olurdu"
   ifadesi ARITMETIK olarak dogrudur.
⚠️ risk$~R korelasyonu ARTEFAKT tasir (R = net/risk, ortak payda) -> yalniz
   betimleyici raporlanir, HUKME DAYANAK YAPILMAZ.

Bolum 3 (mekanik) hicbir SONUC degiskeni kullanmaz — saf muhasebe.
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, math, bisect, datetime, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(PROJE, "kripto-config.json"), encoding="utf-8"))
T = CFG.get("testbot", {})
RISK_PCT = float(T.get("islem_risk_pct", 1.5))
KMIN, KMAX = float(T.get("kaldirac_min", 3)), float(T.get("kaldirac_max", 10))
F = "%Y-%m-%d %H:%M:%S"


def t_ist(v):
    if len(v) < 3:
        return (sum(v) / len(v) if v else 0.0), None, len(v)
    m, sd = sum(v) / len(v), statistics.stdev(v)
    se = sd / math.sqrt(len(v))
    return m, (m / se if se else None), len(v)


def main():
    # ---------------------------------------------------------- equity serisi
    eq_ts, eq_val = [], []
    for l in open(os.path.join(PROJE, "testbot_equity.jsonl"), encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("ts") and r.get("equity") is not None:
            try:
                d = datetime.datetime.strptime(r["ts"], F)
            except Exception:
                continue
            eq_ts.append(d)
            # efektif equity = gerceklesmis + acik P&L (boyut bunun uzerinden)
            eq_val.append(float(r["equity"]) + float(r.get("acik_pnl") or 0.0))
    idx = sorted(range(len(eq_ts)), key=lambda i: eq_ts[i])
    eq_ts = [eq_ts[i] for i in idx]
    eq_val = [eq_val[i] for i in idx]

    def equity_at(d):
        j = bisect.bisect_right(eq_ts, d) - 1
        return eq_val[j] if j >= 0 else (eq_val[0] if eq_val else None)

    # ---------------------------------------------------------- pozisyonlar
    ham = collections.defaultdict(list)
    for l in open(os.path.join(PROJE, "testbot_islemler.jsonl"), encoding="utf-8"):
        l = l.strip()
        if l:
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("id") is not None:
                ham[r["id"]].append(r)
    poz = {}
    for i, v in ham.items():
        v.sort(key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        no = ilk.get("notional") or 0
        if no <= 0:
            continue
        net = sum((t.get("sonuc_usdt") or 0) for t in v)
        fl = [t.get("funding_usdt") for t in v if t.get("funding_usdt") is not None]
        net += sum(fl) if fl else 0.0
        tut = max((t.get("tutma_saat") or 0) for t in v)
        try:
            gir = datetime.datetime.strptime(son["ts"], F) - datetime.timedelta(hours=tut)
        except Exception:
            gir = None
        poz[i] = {"id": i, "no": no, "marjin": ilk.get("marjin") or 0,
                  "kaldirac": ilk.get("kaldirac") or 0, "net": net,
                  "smart": str(ilk.get("smart_giriste") or "NOTR"),
                  "gir": gir, "sebep": son.get("sebep")}

    # ---------------------------------------------------------- stop mesafesi
    st = {}
    for l in open(os.path.join(PROJE, "pozisyon_izleme.jsonl"), encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        i, s = r.get("id"), r.get("stop_mesafe_pct")
        if i is None or s is None:
            continue
        t = r.get("ts") or ""
        if i not in st or t < st[i][0]:
            st[i] = (t, abs(float(s)))

    W = []
    for i, p in poz.items():
        if i not in st or st[i][1] <= 0 or p["gir"] is None:
            continue
        sf = st[i][1] / 100.0
        risk = sf * p["no"]
        if risk <= 0:
            continue
        eq = equity_at(p["gir"])
        if not eq or eq <= 0:
            continue
        hedef = eq * RISK_PCT / 100.0
        hedef_yari = hedef / 2.0 if p["smart"] not in ("NOTR", "None", "") else hedef
        W.append(dict(p, stop_frac=sf, risk=risk, R=p["net"] / risk,
                      equity=eq, hedef=hedef, hedef_smart=hedef_yari))
    W.sort(key=lambda p: p["gir"])
    n = len(W)

    print("RISK PARITESI — tutuyor mu, nerede kiriliyor?")
    print("on-kayit ON_KAYIT_risk_paritesi.md (cd97004) · olcutler SABIT")
    print("=" * 100)
    print("pozisyon %d · %s .. %s · islem_risk_pct %%%.2f · kaldirac [%.0f, %.0f]"
          % (n, W[0]["gir"].date(), W[-1]["gir"].date(), RISK_PCT, KMIN, KMAX))

    # ------------------------------------------------------------- K1 / K2 / K3
    R = [p["R"] for p in W]
    print("\n" + "=" * 100)
    print("1) BIRINCIL — SigmaR, kronolojik iki yari  (ARTEFAKTTAN BAGIMSIZ)")
    print("-" * 100)
    y = n // 2
    print("  %-8s %5s %-24s %11s %11s %8s" % ("yari", "N", "donem", "SigmaR", "ort R", "t"))
    ok = {}
    for ad, w in (("A", W[:y]), ("B", W[y:]), ("HAVUZ", W)):
        rr = [p["R"] for p in w]
        m, t, _ = t_ist(rr)
        ok[ad] = sum(rr)
        print("  %-8s %5d %-24s %+10.2f %+10.3f %8s"
              % (ad, len(w), "%s .. %s" % (w[0]["gir"].date(), w[-1]["gir"].date()),
                 sum(rr), m, ("%+.2f" % t) if t else "-"))
    k1 = ok["A"] > 0 and ok["B"] > 0
    mh, th, _ = t_ist(R)
    k2 = mh > 0 and th is not None and th >= 2.0
    s = sorted(R)
    kes = s[5:-5]
    ys = len(kes) // 2
    k3 = sum(kes[:ys]) > 0 and sum(kes[ys:]) > 0 if len(kes) > 20 else False
    print("\n  K1  SigmaR iki yarida da > 0 : %-6s (A %+.2f · B %+.2f)"
          % ("GECTI" if k1 else "DUSTU", ok["A"], ok["B"]))
    print("  K2  ort R > 0 ve t >= +2,0   : %-6s (%.3f / %s)"
          % ("GECTI" if k2 else "DUSTU", mh, ("%+.2f" % th) if th else "-"))
    print("  K3  uc 5'er atilinca ayakta  : %-6s" % ("GECTI" if k3 else "DUSTU"))
    hk = "GECTI" if (k1 and k2 and k3) else ("ZAYIF" if (k1 and k2) else "DUSTU")
    print("  -> HUKUM: %s" % hk)

    # ------------------------------------------------------------- mekanik
    print("\n" + "=" * 100)
    print("2) MEKANIK — hicbir SONUC degiskeni kullanilmadi (saf muhasebe)")
    print("-" * 100)
    oran = [p["risk"] / p["hedef"] for p in W]
    oran_s = [p["risk"] / p["hedef_smart"] for p in W]
    q = lambda v, x: sorted(v)[min(len(v) - 1, int(x * len(v)))]
    print("  gerceklesen_risk / hedef_risk        : medyan %.3f · %%10 %.3f · %%90 %.3f"
          % (q(oran, .5), q(oran, .1), q(oran, .9)))
    print("  (smart-yarilamasi uygulanmis hedefe) : medyan %.3f · %%10 %.3f · %%90 %.3f"
          % (q(oran_s, .5), q(oran_s, .1), q(oran_s, .9)))
    band = sum(1 for x in oran_s if 0.8 <= x <= 1.2)
    alt = sum(1 for x in oran_s if x < 0.8)
    ust = sum(1 for x in oran_s if x > 1.2)
    print("  hedefin +-%%20 bandinda  : %d (%%%.0f)" % (band, 100.0 * band / n))
    print("  hedefin ALTINDA (<0,8)  : %d (%%%.0f)" % (alt, 100.0 * alt / n))
    print("  hedefin USTUNDE (>1,2)  : %d (%%%.0f)" % (ust, 100.0 * ust / n))

    print("\n  HANGI KISIT BAGLIYOR (kaldiraca gore):")
    kl = collections.Counter()
    for p in W:
        k = p["kaldirac"]
        if k <= KMIN:
            kl["kaldirac_min (%.0f) bagladi" % KMIN] += 1
        elif k >= KMAX:
            kl["kaldirac_max (%.0f) bagladi" % KMAX] += 1
        else:
            kl["ara deger (kirpma yok)"] += 1
    for a, b in kl.most_common():
        print("    %-32s %4d  (%%%.0f)" % (a, b, 100.0 * b / n))

    print("\n  EQUITY ne kadar acikliyor? (hedef zaten equity'ye ORANTILI — tasarim)")
    print("    equity  ilk %.0f $ -> son %.0f $  (%.2f kat)"
          % (W[0]["equity"], W[-1]["equity"], W[0]["equity"] / W[-1]["equity"]))
    rs = [p["risk"] for p in W]
    print("    gerceklesen risk  min %.1f · medyan %.1f · max %.1f  (max/min %.1f kat)"
          % (min(rs), statistics.median(rs), max(rs), max(rs) / min(rs)))
    print("    hedef risk        min %.1f · medyan %.1f · max %.1f  (max/min %.1f kat)"
          % (min(p["hedef_smart"] for p in W), statistics.median([p["hedef_smart"] for p in W]),
             max(p["hedef_smart"] for p in W),
             max(p["hedef_smart"] for p in W) / min(p["hedef_smart"] for p in W)))
    print("    -> gerceklesen yayilim hedef yayiliminin YANINDA ne kadar buyuk?")

    # ------------------------------------------------------------- karsi-olgu
    print("\n" + "=" * 100)
    print("3) KARSI-OLGU — yalniz K1 gecerse anlamli")
    print("-" * 100)
    med_risk = statistics.median(rs)
    ort_hedef = sum(p["hedef_smart"] for p in W) / n
    g = sum(p["net"] for p in W)
    print("  gercek P&L                              : %+10.2f $" % g)
    print("  esit risk @ gerceklesen medyan (%.1f $)  : %+10.2f $" % (med_risk, med_risk * sum(R)))
    print("  esit risk @ hedef ortalamasi   (%.1f $)  : %+10.2f $" % (ort_hedef, ort_hedef * sum(R)))
    print("  -> ikisi arasindaki fark: 'parite tutsaydi' vs 'HEDEFLENEN seviyede tutsaydi'")

    # ------------------------------------------------------------- betimleyici
    print("\n" + "=" * 100)
    print("4) BETIMLEYICI — HUKME DAYANAK DEGIL (artefakt tasir)")
    print("-" * 100)
    sr = sorted(W, key=lambda p: p["risk"])
    d = n // 4
    print("  %-12s %5s %10s %11s %11s %9s" % ("risk dilimi", "N", "ort risk", "SigmaR", "net $", "kazanan"))
    for i, ad in enumerate(("Q1 dusuk", "Q2", "Q3", "Q4 yuksek")):
        w = sr[i * d:(i + 1) * d] if i < 3 else sr[3 * d:]
        print("  %-12s %5d %9.2f $ %+10.2f %+10.2f %8.0f%%"
              % (ad, len(w), sum(p["risk"] for p in w) / len(w), sum(p["R"] for p in w),
                 sum(p["net"] for p in w), 100.0 * sum(1 for p in w if p["net"] > 0) / len(w)))
    print("  ⚠️ Bu tablodaki risk~R iliskisi R=net/risk ortak paydasindan ETKILENIR.")
    print("     Hukum yalniz bolum 1'deki SigmaR'a dayanir.")

    print("\n" + "=" * 100)
    print("⚠️ GECSE BILE KOD DEGISIKLIGI ONERISI DEGIL (on-kayit s.6):")
    print("   sonraki asama PORTFOY SIMULASYONU — 8 slot · marjin tavani · dusus")
    print("   freni karsi-olguda yok sayiliyor. Riski buyutmek dususu de buyutur.")
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
