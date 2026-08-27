#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""defter2 / defter3 durumu + YON etkisi (ortusen pencere). SALT OKUMA.
Sayim: kismi suzulur. Toplam: suzulmez, id ile birlestirilir (CLAUDE.md)."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt

D3_BAS = "2026-08-25 16:12:12"       # defter3'un dogusu = ortusen pencere basi


def oku(a):
    return [json.loads(l) for l in open(a, encoding="utf-8") if l.strip()]


def gts(K):
    g = {}
    for r in K:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        if r["id"] not in g or t < g[r["id"]]:
            g[r["id"]] = t
    return g


def topla(K, G, t0=None):
    """id -> (pnl, funding, meta). t0 verilirse girisi t0'dan sonra olanlar."""
    pnl, fnd, meta = collections.defaultdict(float), collections.defaultdict(float), {}
    for r in K:
        if t0 and G[r["id"]].strftime("%Y-%m-%d %H:%M:%S") < t0:
            continue
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
        if r.get("funding_usdt") is not None:
            fnd[r["id"]] += float(r["funding_usdt"])
        if not r.get("kismi"):
            meta[r["id"]] = r
    return pnl, fnd, meta


def eq0(ef, t):
    e = [r for r in oku(ef) if r["ts"] < t]
    return e[-1] if e else None


print("=" * 98)
print("1) TAM OMUR — her defter kendi baslangicindan bugune")
print("=" * 98)
DEF = {}
for ad, i, e, s in (("defter2", "defter2_islemler.jsonl", "defter2_equity.jsonl", "defter2_state.json"),
                    ("defter3", "defter3_islemler.jsonl", "defter3_equity.jsonl", "defter3_state.json"),
                    ("testbot", "testbot_islemler.jsonl", "testbot_equity.jsonl", "testbot_state.json")):
    K = oku(i); G = gts(K); st = json.load(open(s, encoding="utf-8"))
    DEF[ad] = (K, G, st, e)
    pnl, fnd, meta = topla(K, G)
    npoz = len(meta)
    kz = sum(1 for v in pnl.values() if v > 0)
    b0, b = st["baslangic_ts"], st["baslangic_bakiye"]
    print("  %-8s %s -> simdi  (%.1f gun)" % (ad, b0[:16],
          (dt.datetime.now() - dt.datetime.strptime(b0, "%Y-%m-%d %H:%M:%S")).total_seconds() / 86400))
    print("     kasa %8.2f -> %8.2f   %+9.2f  (%%%+.2f)   acik %d  durum %s"
          % (b, st["equity"], st["equity"] - b, 100.0 * (st["equity"] - b) / b,
             len(st.get("acik_pozisyonlar", [])), st.get("durum")))
    print("     %3d poz kapandi · kazanma %%%.1f · defter P&L %+9.2f · fonlama %+8.2f · ucret -%.2f"
          % (npoz, 100.0 * kz / max(len(pnl), 1), sum(pnl.values()), sum(fnd.values()),
             st["kumulatif_giris_ucret"]))
    ks = float((st.get("_kasa_sifirlama") or {}).get("delta") or 0.0)
    mut = (b + sum(pnl.values()) + st["kumulatif_funding"]
           - st["kumulatif_giris_ucret"] + ks)
    print("     MUTABAKAT: baslangic %+.2f  P&L %+.2f  fonlama(state) %+.2f  ucret %+.2f  kasa-sifir %+.2f"
          % (b, sum(pnl.values()), st["kumulatif_funding"],
             -st["kumulatif_giris_ucret"], ks))
    print("                = %.2f  vs equity %.2f  -> SAPMA %+.2f"
          % (mut, st["equity"], mut - st["equity"]))
    print("")

print("=" * 98)
print("2) ORTUSEN PENCERE — %s -> simdi   (defter3'un dogumu)" % D3_BAS[:16])
print("   defter2 ile defter3 arasindaki TEK fark YON. Ayni evren, ayni cikis, ayni boyut.")
print("=" * 98)
ORT = {}
for ad in ("defter2", "defter3", "testbot"):
    K, G, st, ef = DEF[ad]
    e = eq0(ef, D3_BAS) or {"equity": st["baslangic_bakiye"], "ts": st["baslangic_ts"]}
    pnl, fnd, meta = topla(K, G, D3_BAS)
    kz = sum(1 for v in pnl.values() if v > 0)
    ORT[ad] = (pnl, fnd, meta)
    print("  %-8s equity %8.2f -> %8.2f  = %+8.2f (%%%+.2f)   %3d poz  kazanma %%%.1f  fonlama %+7.2f"
          % (ad, e["equity"], st["equity"], st["equity"] - e["equity"],
             100.0 * (st["equity"] - e["equity"]) / e["equity"],
             len(meta), 100.0 * kz / max(len(pnl), 1), sum(fnd.values())))

print("")
print("=" * 98)
print("3) YONUN ETKISI — chg24 isaretine gore ayrilmis (ortusen pencere)")
print("   chg24>=0 : IKI DEFTER DE SHORT  (kontrol dilimi, ayni olmali)")
print("   chg24<0  : defter2 SHORT / defter3 LONG  (TEK AYRISMA NOKTASI)")
print("=" * 98)
for dilim, kos in (("chg24>=0 (ikisi de SHORT)", lambda c: c >= 0),
                   ("chg24<0  (D2 SHORT / D3 LONG)", lambda c: c < 0)):
    print("  --- %s ---" % dilim)
    for ad in ("defter2", "defter3"):
        pnl, fnd, meta = ORT[ad]
        ids = [i for i, m in meta.items() if kos(float(m.get("chg24_giriste") or 0))]
        v = [pnl[i] for i in ids]
        yon = collections.Counter(meta[i]["yon"] for i in ids)
        kz = sum(1 for x in v if x > 0)
        print("     %-8s %2d poz  P&L %+8.2f  kazanma %%%.0f  yon %s"
              % (ad, len(ids), sum(v), 100.0 * kz / max(len(v), 1), dict(yon)))
    print("")

print("=" * 98)
print("4) AYNI SEMBOL — iki defterin ORTUSEN pencerede ortak isimleri")
print("=" * 98)
m2 = ORT["defter2"][2]; m3 = ORT["defter3"][2]
s2 = {m["sym"]: i for i, m in m2.items()}
s3 = {m["sym"]: i for i, m in m3.items()}
ortak = sorted(set(s2) & set(s3))
print("  ortak sembol: %d  (D2 %d · D3 %d)" % (len(ortak), len(m2), len(m3)))
print("  %-10s %-7s %9s   %-7s %9s   %s" % ("sym", "D2 yon", "D2 P&L", "D3 yon", "D3 P&L", "chg24"))
t2 = t3 = 0.0
for s in ortak:
    i2, i3 = s2[s], s3[s]
    p2, p3 = ORT["defter2"][0][i2], ORT["defter3"][0][i3]
    t2 += p2; t3 += p3
    print("  %-10s %-7s %+9.2f   %-7s %+9.2f   %+.1f%s"
          % (s, m2[i2]["yon"], p2, m3[i3]["yon"], p3,
             float(m3[i3].get("chg24_giriste") or 0),
             "   <- YON FARKLI" if m2[i2]["yon"] != m3[i3]["yon"] else ""))
print("  %-10s %-7s %+9.2f   %-7s %+9.2f" % ("TOPLAM", "", t2, "", t3))

print("")
print("=" * 98)
print("5) SU AN ACIK")
print("=" * 98)
for ad in ("defter2", "defter3"):
    st = DEF[ad][2]
    for p in st.get("acik_pozisyonlar", []):
        print("  %-8s %-8s %-5s giris %s  marjin %.0f  chg24 %s"
              % (ad, p.get("sym"), p.get("yon"), p.get("giris_ts"),
                 p.get("marjin", 0), p.get("chg24_giriste")))
