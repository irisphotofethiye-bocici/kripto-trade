#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ILK GIRIS IYI, TEKRAR GIRIS KOTU MU? — GERCEK DEFTER (2026-09-05)

ON-KAYIT: ON_KAYIT_ilk_tekrar_giris.md, commit 00f5d5a — KOSTURULMADAN ONCE.

🔴 BIRINCIL OLCUT GUN-ESLESMIS: tekrarlar kotu gunlerde yogunlasiyor olabilir;
   ayrilmazsa "tekrar kotu" degil "o gun kotuydu" olcuruz.
🔴 CLAUDE.md: kayitlar id ile BIRLESTIRILIR (P&L toplarken suzgec YOK).

Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, statistics as stx, collections, datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFTER = os.path.join(KOK, "testbot_islemler.jsonl")


def pozisyonlar():
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
    out = []
    for i, ks in g.items():
        ana = next((k for k in ks if not k.get("kismi")), ks[0])
        usd = sum(k.get("sonuc_usdt") or 0.0 for k in ks)
        no = ana.get("notional") or 0.0
        out.append({
            "id": i, "sym": ana.get("sym"), "yon": ana.get("yon"),
            "ts": ana.get("ts") or "", "gun": (ana.get("ts") or "")[:10],
            "usd": usd, "notional": no,
            "net": (usd / no * 100) if no else None,
            "r": ana.get("r"), "rejim": ana.get("rejim_giriste"),
            "sebep": ana.get("sebep"), "tutma": ana.get("tutma_saat"),
        })
    out.sort(key=lambda x: x["ts"])
    return [p for p in out if p["net"] is not None and p["ts"]]


def etiketle(ps):
    say = collections.Counter()
    onceki_ts = {}
    for p in ps:
        say[p["sym"]] += 1
        p["sira"] = say[p["sym"]]
        p["ilk"] = (p["sira"] == 1)
        o = onceki_ts.get(p["sym"])
        p["oncekinden_saat"] = None
        if o:
            try:
                a = dt.datetime.strptime(o, "%Y-%m-%d %H:%M:%S")
                b = dt.datetime.strptime(p["ts"], "%Y-%m-%d %H:%M:%S")
                p["oncekinden_saat"] = (b - a).total_seconds() / 3600
            except Exception:
                pass
        onceki_ts[p["sym"]] = p["ts"]
    return ps


def kumeli_t(ciftler):
    """ciftler: {kume: (ilk_liste, tekrar_liste)} -> (ort_fark, t, MDE, n_kume)
    Yalniz IKISI DE dolu olan kumeler kullanilir (ESLESMIS)."""
    farklar = []
    for k, (a, b) in ciftler.items():
        if a and b:
            farklar.append(sum(a) / len(a) - sum(b) / len(b))
    n = len(farklar)
    if n < 3:
        return None, None, None, n
    m = sum(farklar) / n
    se = stx.stdev(farklar) / math.sqrt(n)
    return m, (m / se if se else None), (2.0 * se if se else None), n


def esle(ps, anahtar, alan="net"):
    d = collections.defaultdict(lambda: ([], []))
    for p in ps:
        (d[p[anahtar]][0] if p["ilk"] else d[p[anahtar]][1]).append(p[alan])
    return d


def oz(ad, ps, alan="net"):
    if not ps:
        print("  %-22s (yok)" % ad)
        return
    v = [p[alan] for p in ps]
    print("  %-22s N=%-4d ort %+8.3f%s  medyan %+8.3f  kazanan %%%.1f"
          % (ad, len(ps), stx.mean(v), "%" if alan == "net" else " $",
             stx.median(v), sum(1 for x in v if x > 0) / len(v) * 100))


def main():
    print("=" * 92)
    print("ILK GIRIS IYI, TEKRAR GIRIS KOTU MU? — GERCEK DEFTER")
    print("=" * 92)
    print("ON-KAYIT: ON_KAYIT_ilk_tekrar_giris.md commit 00f5d5a — KOSMADAN once")
    print("🔴 BIRINCIL: GUN-ESLESMIS karsilastirma (kotu-gun karistiricisi)\n")

    ps = etiketle(pozisyonlar())
    ilk = [p for p in ps if p["ilk"]]
    tek = [p for p in ps if not p["ilk"]]
    print("pozisyon: %d  ·  ayri sembol: %d  ·  ILK %d / TEKRAR %d  (%%%.1f tekrar)"
          % (len(ps), len({p["sym"] for p in ps}), len(ilk), len(tek),
             len(tek) / len(ps) * 100))
    print()

    print("### HAVUZLANMIS (ikincil)")
    oz("ILK giris", ilk); oz("TEKRAR giris", tek)
    print("  ---- dolar ----")
    oz("ILK giris", ilk, "usd"); oz("TEKRAR giris", tek, "usd")
    hav = stx.mean([p["net"] for p in ilk]) - stx.mean([p["net"] for p in tek])
    hav_usd = stx.mean([p["usd"] for p in ilk]) - stx.mean([p["usd"] for p in tek])
    print("  havuzlanmis fark: %+.3f%%  ·  %+.2f $" % (hav, hav_usd))
    print()

    print("### 🔴 GUN-ESLESMIS (BIRINCIL)")
    m, t, mde, n = kumeli_t(esle(ps, "gun", "net"))
    print("  net%%   fark %+.3f%%  t %s  MDE %s  (eslesmis gun=%d)  -> %s"
          % (m if m is not None else 0, ("%.2f" % t) if t else "yok",
             ("%.3f" % mde) if mde else "yok", n,
             "GORULUR" if (m is not None and mde and abs(m) >= mde) else "goremiyoruz"))
    mu, tu, mdeu, nu = kumeli_t(esle(ps, "gun", "usd"))
    print("  dolar  fark %+.2f $  t %s  MDE %s  (eslesmis gun=%d)"
          % (mu if mu is not None else 0, ("%.2f" % tu) if tu else "yok",
             ("%.2f" % mdeu) if mdeu else "yok", nu))
    print()

    print("### SEMBOL-ESLESMIS (K2)")
    ms, ts_, mdes, ns = kumeli_t(esle(ps, "sym", "net"))
    print("  net%%   fark %+.3f%%  t %s  MDE %s  (eslesmis sembol=%d)"
          % (ms if ms is not None else 0, ("%.2f" % ts_) if ts_ else "yok",
             ("%.3f" % mdes) if mdes else "yok", ns))
    print()

    print("### GIRIS SIRASINA GORE (ek rapor)")
    print("  %-8s %5s %10s %11s %9s" % ("sira", "N", "net% ort", "dolar ort", "kazanan"))
    for s in (1, 2, 3, 4):
        g = [p for p in ps if (p["sira"] == s if s < 4 else p["sira"] >= 4)]
        if not g:
            continue
        ad = str(s) if s < 4 else "4+"
        print("  %-8s %5d %+10.3f%% %+11.2f %8.1f%%" %
              (ad, len(g), stx.mean([p["net"] for p in g]),
               stx.mean([p["usd"] for p in g]),
               sum(1 for p in g if p["usd"] > 0) / len(g) * 100))
    print()

    print("### YOGUNLASMA — en cok girilen 10 sembol")
    c = collections.Counter(p["sym"] for p in ps)
    print("  %-12s %5s %11s %11s" % ("sembol", "giris", "toplam $", "ort $"))
    ust = 0
    for sym, k in c.most_common(10):
        g = [p for p in ps if p["sym"] == sym]
        ust += k - 1
        print("  %-12s %5d %+11.2f %+11.2f" % (sym, k, sum(p["usd"] for p in g),
                                               sum(p["usd"] for p in g) / k))
    print("  -> en cok girilen 10 sembol tum TEKRARLARIN %%%.0f'ini tasiyor"
          % (ust / len(tek) * 100 if tek else 0))
    print()

    print("### ASCII DISI SEMBOL ADLARI (kullanicinin isaret ettigi coin)")
    ad_disi = sorted({p["sym"] for p in ps if any(ord(ch) > 127 for ch in (p["sym"] or ""))})
    if ad_disi:
        for sym in ad_disi:
            g = [p for p in ps if p["sym"] == sym]
            print("  %-14s giris=%-3d toplam %+9.2f $  ort %+8.2f $  kazanan %%%.0f"
                  % (sym, len(g), sum(p["usd"] for p in g),
                     sum(p["usd"] for p in g) / len(g),
                     sum(1 for p in g if p["usd"] > 0) / len(g) * 100))
    else:
        print("  (ASCII disi sembol adi YOK — sembol adlari latin harflerle kayitli)")
    print()

    print("### TEKRARLAR ONCEKINDEN KAC SAAT SONRA")
    ss = [p["oncekinden_saat"] for p in tek if p["oncekinden_saat"] is not None]
    if ss:
        ss.sort()
        print("  medyan %.1f saat · %%25 %.1f · %%75 %.1f · 4 saatten kisa: %d (%%%.0f)"
              % (ss[len(ss) // 2], ss[len(ss) // 4], ss[3 * len(ss) // 4],
                 sum(1 for x in ss if x < 4), sum(1 for x in ss if x < 4) / len(ss) * 100))
    print()

    print("=" * 92)
    print("HUKUM — ON_KAYIT_ilk_tekrar_giris.md bolum 5")
    print("=" * 92)
    K1 = (m is not None and m > 0 and t is not None and t >= 2.0)
    print("K1  gun-eslesmis fark > 0 ve t >= +2,0 : %+.3f%% t=%s -> %s"
          % (m if m is not None else 0, ("%.2f" % t) if t else "yok", "GECTI" if K1 else "DUSTU"))
    K2 = (ms is not None and m is not None and ms * m > 0)
    print("K2  sembol-kumeli ayni isaret : %+.3f%% -> %s"
          % (ms if ms is not None else 0, "GECTI" if K2 else "DUSTU"))
    K3 = (m is not None and mde is not None and abs(m) >= mde)
    print("K3  |fark| >= MDE : %s -> %s"
          % (("%.3f vs %.3f" % (abs(m), mde)) if m is not None else "yok",
             "GORULUR" if K3 else "GOREMIYORUZ"))
    K4 = (mu is not None and m is not None and mu * m > 0)
    print("K4  dolarda ayni isaret : %+.2f $ -> %s"
          % (mu if mu is not None else 0, "GECTI" if K4 else "DUSTU"))
    dusen = [a for a, v in (("K1", K1), ("K2", K2), ("K3", K3), ("K4", K4)) if not v]
    if not dusen:
        h = "GECTI"
    elif K1 and K3:
        h = "ZAYIF (dusen: %s)" % ", ".join(dusen)
    else:
        h = "DUSTU (dusen: %s)" % ", ".join(dusen)
    print("\nSONUC: %s" % h)
    print("\nBot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
