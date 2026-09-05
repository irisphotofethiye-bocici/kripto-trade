#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CIKIS VERIMI — lehimize giden hareketin ne kadarini aliyoruz? (2026-09-05)

🔴 BETIMLEYICI. On-kayit yok, hukum yok, kural cikmaz.
   Amac: yeni bot icin "fark yaratacak ne var" sorusuna VERI uretmek.

VERI: pozisyon_izleme.jsonl -> her id icin SON kayit (mfe_pct/mae_pct birikmis)
      testbot_islemler.jsonl -> gercek sonuc (id ile birlestirilmis)

⚠️ PROJE GECMISI: cikisi SIKILASTIRAN 29 varyantin 29'u da kaldi; gecen TEK
   varyant cikisi GEVSETIYORDU (sabit %10 hedef). Buradan cikacak her oneri
   bu sicile karsi savunma yapmak zorunda.

Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, statistics as stx, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IZLEME = os.path.join(KOK, "pozisyon_izleme.jsonl")
DEFTER = os.path.join(KOK, "testbot_islemler.jsonl")


def son_izleme():
    """id -> son izleme kaydi (mfe/mae birikmis)."""
    out = {}
    with open(IZLEME, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            i = r.get("id")
            if i is None:
                continue
            o = out.get(i)
            if o is None or (r.get("ts") or "") >= (o.get("ts") or ""):
                out[i] = r
    return out


def defter():
    g = collections.defaultdict(list)
    for line in open(DEFTER, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        g[r.get("id")].append(r)
    out = {}
    for i, ks in g.items():
        ana = next((k for k in ks if not k.get("kismi")), ks[0])
        out[i] = {"usd": sum(k.get("sonuc_usdt") or 0.0 for k in ks),
                  "yon": ana.get("yon"), "sebep": ana.get("sebep"),
                  "notional": ana.get("notional") or 0.0,
                  "ts": ana.get("ts") or "", "sym": ana.get("sym"),
                  "tp1": bool(ana.get("kismi")) or any(k.get("kismi") for k in ks)}
    return out


def yuzdelik(v, q):
    s = sorted(v)
    return s[min(int(len(s) * q), len(s) - 1)]


def main():
    print("=" * 88)
    print("CIKIS VERIMI — lehimize giden hareketin ne kadarini aliyoruz?")
    print("=" * 88)
    print("🔴 Betimleyici. On-kayit yok, hukum yok.")
    print("⚠️ Proje sicili: cikisi SIKILASTIRAN 29/29 kaldi; gecen tek varyant")
    print("   cikisi GEVSETIYORDU. Buradan cikacak oneri buna karsi savunmali.\n")

    iz = son_izleme()
    df = defter()
    ort = [i for i in df if i in iz]
    print("defter pozisyon: %d · izleme kaydi olan: %d\n" % (len(df), len(ort)))

    kay = []
    for i in ort:
        z, d = iz[i], df[i]
        mfe = z.get("mfe_pct")
        mae = z.get("mae_pct")
        no = d["notional"]
        if mfe is None or not no:
            continue
        ger = d["usd"] / no * 100          # gerceklesen net %
        kay.append({"id": i, "yon": d["yon"], "mfe": mfe, "mae": mae,
                    "ger": ger, "usd": d["usd"], "sebep": d["sebep"],
                    "tp1": d["tp1"], "sym": d["sym"],
                    "tepe": z.get("tepe_pnl_pct"), "stop_m": z.get("stop_mesafe_pct")})
    print("olculebilen pozisyon: %d\n" % len(kay))

    for ad, ps in (("TUMU", kay),
                   ("LONG", [k for k in kay if k["yon"] == "LONG"]),
                   ("SHORT", [k for k in kay if k["yon"] == "SHORT"])):
        if len(ps) < 10:
            continue
        mfe = [p["mfe"] for p in ps]
        ger = [p["ger"] for p in ps]
        mae = [p["mae"] for p in ps if p["mae"] is not None]
        print("### %s   N=%d" % (ad, len(ps)))
        print("   MFE (lehimize EN COK)   medyan %+7.2f%%  · %%25 %+6.2f · %%75 %+6.2f"
              % (stx.median(mfe), yuzdelik(mfe, .25), yuzdelik(mfe, .75)))
        print("   GERCEKLESEN             medyan %+7.2f%%  · ort %+6.2f"
              % (stx.median(ger), stx.mean(ger)))
        if mae:
            print("   MAE (aleyhimize EN COK) medyan %+7.2f%%" % stx.median(mae))
        # kar tepesinden geri verme
        gv = [p for p in ps if p["mfe"] > 0]
        if gv:
            oran = [max(0.0, p["ger"]) / p["mfe"] for p in gv if p["mfe"] > 0]
            print("   YAKALAMA ORANI (gerceklesen/MFE, negatifler 0 sayildi):")
            print("      medyan %%%.1f  ·  ort %%%.1f" % (stx.median(oran) * 100,
                                                          stx.mean(oran) * 100))
        # artiya gecip zararla kapananlar
        for esik in (1.0, 3.0, 5.0, 10.0):
            a = [p for p in ps if p["mfe"] >= esik]
            if not a:
                continue
            z = sum(1 for p in a if p["usd"] < 0)
            print("      MFE >= %%%-4.0f : %3d pozisyon, bunlarin %3d'u ZARARLA kapandi (%%%.0f)"
                  % (esik, len(a), z, z / len(a) * 100))
        print()

    print("### CIKIS SEBEBINE GORE — MFE ve gerceklesen")
    seb = collections.defaultdict(list)
    for p in kay:
        seb[p["sebep"] or "?"].append(p)
    print("   %-16s %5s %11s %12s %10s" % ("sebep", "N", "MFE med", "gercek med", "toplam $"))
    for s, ps in sorted(seb.items(), key=lambda x: -len(x[1])):
        print("   %-16s %5d %+10.2f%% %+11.2f%% %+10.2f"
              % (s, len(ps), stx.median([p["mfe"] for p in ps]),
                 stx.median([p["ger"] for p in ps]), sum(p["usd"] for p in ps)))
    print()

    print("### EN BUYUK KACIRILANLAR (MFE yuksek ama zararla kapanmis)")
    kac = sorted([p for p in kay if p["usd"] < 0 and p["mfe"] > 0],
                 key=lambda p: -p["mfe"])[:10]
    print("   %-10s %-6s %9s %10s %10s %s" % ("sembol", "yon", "MFE%", "gercek%", "dolar", "sebep"))
    for p in kac:
        print("   %-10s %-6s %+9.2f %+10.2f %+10.2f %s"
              % (p["sym"], p["yon"], p["mfe"], p["ger"], p["usd"], p["sebep"]))
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
