#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pos SINYALININ MEKANIK ASAMASI — on-kayit ON_KAYIT_pos_mekanik.md (commit cdbc4b5).

Ham asama (24_rejim_kararliligi.py): "cok kosan gorece geri kalir", 5/5 pencere.
Bu betik AYNI orneklem uzerine stop/hedef/maliyet/fonlama ekler.

OLCUTLER ON-KAYITTA SABIT — burada TEKRAR EDILMEZ, sadece hesaplanip basilir.

TASARIM 24_rejim_kararliligi.py dosyasindan DEGISTIRILMEDEN alindi:
   pos = (c - lo20)/(hi20 - lo20) · ADIM=4 · MIN_QV=125000 · ufuk 24sa
   giris = b[i+1].o · ceyrekler PENCERE ICINDE · gun-kumeli eslesmis fark

MEKANIK (ham asamada olmayan tek sey):
   stop %3/%5/%8 (birincil %5) · hedef %10 sabit
   maliyet %0,1726 (OLCULMUS; olcum_ortak.MALIYET=0,13 ESKI varsayim)
   fonlama tutma suresince kesilen dilimler, yone gore isaretli
   ayni barda stop+hedef -> STOP oncelikli (kotumser, tek yonlu)

SALT OKUMA. Bot dosyalarina yazim YOK.
"""
import os, sys, json, datetime, collections, bisect, statistics as sx, math

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
FUND = os.path.join(SCRATCH, "funding_gecmis")

UFUK = 24
ADIM = 4
MIN_QV = 125000
STOPLAR = [3.0, 5.0, 8.0]
BIRINCIL = 5.0
HEDEF = 10.0
MALIYET = 0.1726            # olculmus (slipaj dogrulamasi)


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp() * 1000)


PENCERE = [
    ("ATH 24-09/12", ms("2024-09-15"), ms("2024-12-15")),
    ("ATH 25-06/10", ms("2025-06-01"), ms("2025-10-15")),
    ("TOPARLANMA 25-04", ms("2025-04-03"), ms("2025-05-15")),
    ("DERIN-AYI 26-01", ms("2026-01-05"), ms("2026-03-20")),
    ("AYI 26-06/08", ms("2026-06-24"), ms("2026-08-19")),
]


def simule(b, i, ref, yon, ft, fr):
    """-> {stop_pct: (net, tip, tutma_saat)} · ayni barda stop+hedef -> STOP."""
    out = {}
    t0 = b[i + 1]["t"]
    sonbar = min(i + UFUK, len(b) - 1)
    for sp in STOPLAR:
        if yon == "LONG":
            sl, tp = ref * (1 - sp / 100), ref * (1 + HEDEF / 100)
        else:
            sl, tp = ref * (1 + sp / 100), ref * (1 - HEDEF / 100)
        ham, tip, cj = None, "SURE", sonbar
        for j in range(i + 1, sonbar + 1):
            x = b[j]
            vur_s = (x["l"] <= sl) if yon == "LONG" else (x["h"] >= sl)
            vur_h = (x["h"] >= tp) if yon == "LONG" else (x["l"] <= tp)
            if vur_s:                      # STOP oncelikli (kotumser)
                ham, tip, cj = -sp, "STOP", j
                break
            if vur_h:
                ham, tip, cj = HEDEF, "HEDEF", j
                break
        if ham is None:
            c = b[sonbar]["c"]
            ham = ((c - ref) if yon == "LONG" else (ref - c)) / ref * 100
        f = 0.0
        if ft:
            a, z = bisect.bisect_right(ft, t0), bisect.bisect_right(ft, b[cj]["t"])
            s = sum(fr[k] for k in range(a, z))
            f = s if yon == "SHORT" else -s
        out[sp] = (ham - MALIYET + f, tip, cj - i)
    return out


def topla():
    kova = {ad: [] for ad, _, _ in PENCERE}
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
        ft, fr = [], []
        fp = os.path.join(FUND, fn)
        if os.path.exists(fp):
            try:
                with open(fp, encoding="utf-8") as f:
                    d = json.load(f)
                ft = [x["t"] for x in d]
                # funding_indir.py:67 ZATEN yuzdeye ceviriyor (fundingRate*100).
                #    Ekstra *100 fonlamayi 100 KAT buyutuyordu — 2026-08-21 duzeltildi.
                fr = [x["r"] for x in d]
            except Exception:
                pass
        for i in range(48, len(b) - UFUK - 2, ADIM):
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
            pen = b[i - 20:i + 1]
            lo = min(z["l"] for z in pen)
            hi = max(z["h"] for z in pen)
            ref = b[i + 1]["o"]
            if ref <= 0 or hi <= lo:
                continue
            dt = datetime.datetime.fromtimestamp(x["t"] / 1000)
            r = {"sym": sym, "gun": dt.strftime("%Y-%m-%d"), "saat": dt.hour,
                 "pos": (x["c"] - lo) / (hi - lo),
                 "ham": (b[i + UFUK]["c"] - ref) / ref * 100}
            for yon in ("LONG", "SHORT"):
                for sp, (net, tip, tut) in simule(b, i, ref, yon, ft, fr).items():
                    r["%s_%d" % (yon, int(sp))] = net
                    if sp == BIRINCIL:
                        r["%s_tip" % yon] = tip
                        r["%s_tut" % yon] = tut
            kova[ad].append(r)
        if n % 150 == 0:
            print("  ... %d/%d sembol" % (n, len(dosya)))
            sys.stdout.flush()
    return kova


def gun_t(v, alan, cikar=()):
    """gun-kumeli ESLESMIS fark: her gun ort(alt ceyrek) - ort(ust ceyrek)."""
    w = [x for x in v if isinstance(x.get(alan), (int, float)) and x["sym"] not in cikar]
    if len(w) < 300:
        return None, None, None, 0
    d = sorted(x["pos"] for x in w)
    q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
    if q1 >= q3:
        return None, None, None, 0
    g = collections.defaultdict(lambda: [[], []])
    for x in w:
        if x["pos"] <= q1:
            g[x["gun"]][0].append(x[alan])
        elif x["pos"] >= q3:
            g[x["gun"]][1].append(x[alan])
    gunluk = [(sx.mean(a) - sx.mean(b2), sx.mean(a), sx.mean(b2))
              for a, b2 in g.values() if len(a) >= 5 and len(b2) >= 5]
    if len(gunluk) < 8:
        return None, None, None, len(gunluk)
    fark = [z[0] for z in gunluk]
    m, sd = sx.mean(fark), sx.pstdev(fark)
    t = m / (sd / math.sqrt(len(fark))) if sd > 0 else None
    return m, t, (sx.mean(z[1] for z in gunluk), sx.mean(z[2] for z in gunluk)), len(gunluk)


def yogun_cikar(v, alan):
    """farka en cok katki yapan 3 sembol (alt kol toplami - ust kol toplami)."""
    d = sorted(x["pos"] for x in v if isinstance(x.get(alan), (int, float)))
    if len(d) < 300:
        return set()
    q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
    kat = collections.defaultdict(float)
    for x in v:
        y = x.get(alan)
        if not isinstance(y, (int, float)):
            continue
        if x["pos"] <= q1:
            kat[x["sym"]] += y
        elif x["pos"] >= q3:
            kat[x["sym"]] -= y
    return {k for k, _ in sorted(kat.items(), key=lambda z: -z[1])[:3]}


def tani(v, yon):
    d = sorted(x["pos"] for x in v)
    q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
    out = []
    for ad, kos in (("alt", lambda p: p <= q1), ("ust", lambda p: p >= q3)):
        w = [x for x in v if kos(x["pos"]) and x.get("%s_tip" % yon)]
        if not w:
            out.append((ad, 0, 0, 0))
            continue
        c = collections.Counter(x["%s_tip" % yon] for x in w)
        out.append((ad, 100 * c["STOP"] / len(w), 100 * c["HEDEF"] / len(w),
                    sx.mean(x["%s_tut" % yon] for x in w)))
    return out


if __name__ == "__main__":
    print("pos MEKANIK ASAMASI — on-kayit ON_KAYIT_pos_mekanik.md (cdbc4b5)")
    print("maliyet %%%.4f (olculmus) · hedef %%%.0f · ufuk %dsa · ADIM %d"
          % (MALIYET, HEDEF, UFUK, ADIM))
    kova = topla()

    sonuc = collections.defaultdict(dict)
    for ad, _, _ in PENCERE:
        v = kova[ad]
        print("\n" + "=" * 100)
        print("%s   N=%d aday · %d sembol · %d gun"
              % (ad, len(v), len({x["sym"] for x in v}), len({x["gun"] for x in v})))
        print("=" * 100)
        if len(v) < 300:
            print("  N yetersiz")
            continue
        m, t, kol, ng = gun_t(v, "ham")
        if m is not None:
            print("  HAM (kiyas)      fark %+7.3f  gun-t %+6.2f   alt %+7.3f  ust %+7.3f  (%d gun)"
                  % (m, t, kol[0], kol[1], ng))
        for yon in ("LONG", "SHORT"):
            print("  --- %s" % yon)
            for sp in STOPLAR:
                alan = "%s_%d" % (yon, int(sp))
                m, t, kol, ng = gun_t(v, alan)
                if m is None:
                    print("      stop %%%-3.0f  N yetersiz" % sp)
                    continue
                cik = yogun_cikar(v, alan)
                m2, t2, _, _ = gun_t(v, alan, cikar=cik)
                print("      stop %%%-3.0f fark %+7.3f gun-t %+6.2f  alt %+7.3f ust %+7.3f"
                      "  | en iyi 3 cik. %+7.3f (t %+5.2f)"
                      % (sp, m, t, kol[0], kol[1],
                         m2 if m2 is not None else float("nan"),
                         t2 if t2 is not None else float("nan")))
                sonuc[(yon, sp)][ad] = (m, t, kol[0], kol[1], m2)
            for k, s_, h_, tt in tani(v, yon):
                print("      TANI %-3s kol: stop-olma %%%4.1f · hedef %%%4.1f · tutma %4.1f sa"
                      % (k, s_, h_, tt))

    print("\n" + "=" * 100)
    print("KAPI DEGERLENDIRMESI — olcutler ON_KAYIT_pos_mekanik.md dosyasinda sabit")
    print("=" * 100)
    adlar = [a for a, _, _ in PENCERE]

    def say(yon, sp, kos):
        return sum(1 for a in adlar if a in sonuc[(yon, sp)] and kos(sonuc[(yon, sp)][a]))

    a1 = say("LONG", BIRINCIL, lambda z: z[0] > 0)
    a2 = say("LONG", BIRINCIL, lambda z: z[1] is not None and z[1] >= 2.0)
    a3 = all(say("LONG", sp, lambda z: z[0] > 0) >= 4 for sp in STOPLAR)
    a4 = say("LONG", BIRINCIL, lambda z: z[4] is not None and z[4] > 0)
    b1 = say("LONG", BIRINCIL, lambda z: z[2] > 0)
    c1 = say("SHORT", BIRINCIL, lambda z: z[0] < 0)
    print("  A1 LONG stop%%5 fark>0        : %d/5   (gecmesi icin >=4)   %s"
          % (a1, "GECTI" if a1 >= 4 else "DUSTU"))
    print("  A2 gun-t >= +2,0             : %d/5   (gecmesi icin >=3)   %s"
          % (a2, "GECTI" if a2 >= 3 else "DUSTU"))
    print("  A3 uc stopta da >=4/5        : %s" % ("GECTI" if a3 else "DUSTU"))
    print("  A4 en iyi 3 sembol cikinca   : %d/5   (gecmesi icin >=4)   %s"
          % (a4, "GECTI" if a4 >= 4 else "DUSTU"))
    A = a1 >= 4 and a2 >= 3 and a3 and a4 >= 4
    print("  --> KAPI A : %s" % ("GECTI" if A else "DUSTU"))
    print("  B1 dusuk-pos LONG net > 0    : %d/5   (gecmesi icin >=3)   %s"
          % (b1, "GECTI" if b1 >= 3 else "DUSTU"))
    print("  C1 SHORT'ta fark TERS isaret : %d/5   (gecmesi icin >=4)   %s"
          % (c1, "GECTI" if c1 >= 4 else "DUSTU"))
    print("\nHUKUM: karar tablosu ON_KAYIT_pos_mekanik.md dosyasinda.")
    print("Bot dosyalarina yazim: YOK")
