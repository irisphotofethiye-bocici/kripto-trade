#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""37_pos_mekanik.py SONUCUNUN AYRISTIRILMASI — olcut DEGISTIRMEZ, TANI koyar.

NEDEN: 37 dort kapiyi da gecti ama rakam INANDIRICI DEGIL.
   DERIN-AYI, LONG, alt kol NET = +7,145 / islem.
   Stop %5 · hedef %10 ile bir islemin net'i FONLAMA HARIC en fazla
   +10 - 0,1726 olabilir; SURE ile cikanlar -5..+10 arasinda SIKISIK.
   Ust sinir hesabi: 0,094x10 + 0,397x(-5) + 0,509x(<=10) - 0,17 = EN COK +4,04
   -> +7,145 bu sinirin USTUNDE. Farki yaratan tek sey FONLAMA olabilir.

HIPOTEZ: dusuk `pos` (20 barlik dibe yakin) coinlerde fonlama DERIN NEGATIF;
   LONG onu TAHSIL EDIYOR. Yani `pos` yeni bilgi tasimiyor, FONLAMANIN VEKILI.
   Bu tam olarak CLAUDE.md'nin "karistirici kontrolu zorunlu" kuralinin konusu
   ve 37'nin ON-KAYDINDA BU KONTROL YOKTU.

AYRISTIRMA (hepsi ayni orneklem, LONG, stop %5):
   1) HAM                 mekanik yok, fonlama yok
   2) MEKANIK, fonlama YOK   stop/hedef/maliyet var
   3) MEKANIK + FONLAMA      37'nin raporladigi
   4) HAM + FONLAMA          mekanik yok, fonlama var
   + kollarin FONLAMA ORTALAMASI ve stopun KURTARDIGI buyukluk

OLCUT DEGISTIRILMEZ (CLAUDE.md D/9). Bu betik yalniz TANI koyar.
SALT OKUMA.
"""
import os, sys, json, datetime, collections, bisect, statistics as sx, math

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
KLINE = os.path.join(SCRATCH, "klines_1h_uzun")
FUND = os.path.join(SCRATCH, "funding_gecmis")

UFUK, ADIM, MIN_QV = 24, 4, 125000
STOP, HEDEF, MALIYET = 5.0, 10.0, 0.1726


def ms(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp() * 1000)


PENCERE = [
    ("ATH 24-09/12", ms("2024-09-15"), ms("2024-12-15")),
    ("ATH 25-06/10", ms("2025-06-01"), ms("2025-10-15")),
    ("TOPARLANMA 25-04", ms("2025-04-03"), ms("2025-05-15")),
    ("DERIN-AYI 26-01", ms("2026-01-05"), ms("2026-03-20")),
    ("AYI 26-06/08", ms("2026-06-24"), ms("2026-08-19")),
]


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
            sonbar = min(i + UFUK, len(b) - 1)
            sl, tp = ref * (1 - STOP / 100), ref * (1 + HEDEF / 100)
            mek, tip, cj = None, "SURE", sonbar
            for j in range(i + 1, sonbar + 1):
                z = b[j]
                if z["l"] <= sl:
                    mek, tip, cj = -STOP, "STOP", j
                    break
                if z["h"] >= tp:
                    mek, tip, cj = HEDEF, "HEDEF", j
                    break
            ham = (b[sonbar]["c"] - ref) / ref * 100
            if mek is None:
                mek = ham
            fon_mek = fon_ham = 0.0
            if ft:
                a0 = bisect.bisect_right(ft, b[i + 1]["t"])
                fon_mek = -sum(fr[k] for k in range(a0, bisect.bisect_right(ft, b[cj]["t"])))
                fon_ham = -sum(fr[k] for k in range(a0, bisect.bisect_right(ft, b[sonbar]["t"])))
            kova[ad].append({
                "sym": sym,
                "gun": datetime.datetime.fromtimestamp(x["t"] / 1000).strftime("%Y-%m-%d"),
                "pos": (x["c"] - lo) / (hi - lo),
                "ham": ham,
                "mek_fonsuz": mek - MALIYET,
                "mek_fonlu": mek - MALIYET + fon_mek,
                "ham_fonlu": ham + fon_ham,
                "fon": fon_mek,
                "kurtarma": (mek - ham) if tip == "STOP" else 0.0,
                "tip": tip})
        if n % 200 == 0:
            print("  ... %d/%d" % (n, len(dosya)))
            sys.stdout.flush()
    return kova


def kol_ayir(v):
    d = sorted(x["pos"] for x in v)
    q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
    return ([x for x in v if x["pos"] <= q1], [x for x in v if x["pos"] >= q3])


def gun_fark(v, alan):
    g = collections.defaultdict(lambda: [[], []])
    d = sorted(x["pos"] for x in v)
    q1, q3 = d[len(d) // 4], d[3 * len(d) // 4]
    for x in v:
        if x["pos"] <= q1:
            g[x["gun"]][0].append(x[alan])
        elif x["pos"] >= q3:
            g[x["gun"]][1].append(x[alan])
    f = [sx.mean(a) - sx.mean(b) for a, b in g.values() if len(a) >= 5 and len(b) >= 5]
    if len(f) < 8:
        return None, None
    m, sd = sx.mean(f), sx.pstdev(f)
    return m, (m / (sd / math.sqrt(len(f))) if sd > 0 else None)


if __name__ == "__main__":
    print("AYRISTIRMA — 37_pos_mekanik.py sonucunun TANISI (olcut degismez)")
    print("LONG · stop %%%.0f · hedef %%%.0f · maliyet %%%.4f" % (STOP, HEDEF, MALIYET))
    kova = topla()
    for ad, _, _ in PENCERE:
        v = kova[ad]
        if len(v) < 300:
            continue
        alt, ust = kol_ayir(v)
        print("\n" + "=" * 96)
        print("%s   N=%d  (alt %d · ust %d)" % (ad, len(v), len(alt), len(ust)))
        print("=" * 96)
        print("  %-24s %10s %10s %10s %8s" % ("olcu", "ALT kol", "UST kol", "FARK", "gun-t"))
        print("  " + "-" * 66)
        for etiket, alan in (("1 HAM (mekanik/fon yok)", "ham"),
                             ("2 MEKANIK, fonlama YOK", "mek_fonsuz"),
                             ("3 MEKANIK + FONLAMA", "mek_fonlu"),
                             ("4 HAM + FONLAMA", "ham_fonlu")):
            m, t = gun_fark(v, alan)
            print("  %-24s %+10.3f %+10.3f %+10.3f %8s"
                  % (etiket, sx.mean(x[alan] for x in alt), sx.mean(x[alan] for x in ust),
                     m if m is not None else float("nan"),
                     ("%+.2f" % t) if t is not None else "-"))
        print("  " + "-" * 66)
        print("  FONLAMA ortalamasi       %+10.3f %+10.3f %+10.3f   <- LONG'un TAHSIL ettigi"
              % (sx.mean(x["fon"] for x in alt), sx.mean(x["fon"] for x in ust),
                 sx.mean(x["fon"] for x in alt) - sx.mean(x["fon"] for x in ust)))
        ks_a = [x["kurtarma"] for x in alt if x["tip"] == "STOP"]
        ks_u = [x["kurtarma"] for x in ust if x["tip"] == "STOP"]
        print("  STOP kurtarmasi (stop olanlarda, ham'a gore kazanc)")
        print("     alt %+8.3f x %%%4.1f = %+7.3f   |   ust %+8.3f x %%%4.1f = %+7.3f"
              % (sx.mean(ks_a) if ks_a else 0, 100 * len(ks_a) / len(alt),
                 (sx.mean(ks_a) * len(ks_a) / len(alt)) if ks_a else 0,
                 sx.mean(ks_u) if ks_u else 0, 100 * len(ks_u) / len(ust),
                 (sx.mean(ks_u) * len(ks_u) / len(ust)) if ks_u else 0))
        en_kotu = sorted(ks_a)[:max(1, len(ks_a) // 100)]
        print("     alt kolda stopun kurtardigi EN BUYUK %%1: ortalama %+.1f puan"
              % (sx.mean(en_kotu) if en_kotu else 0))
    print("\nTANI BETIGI. Hukum ON_KAYIT_pos_mekanik.md karar tablosuna gore verilir.")
    print("Bot dosyalarina yazim: YOK")
