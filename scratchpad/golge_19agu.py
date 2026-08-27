#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19 AGUSTOS SONRASI — testbot vs golge. SALT OKUMA.
Kurallar (CLAUDE.md): pozisyon SAYARKEN kismi suzulur, P&L TOPLARKEN suzulmez
(id ile birlestirilir). Pencere sonucu equity'den TURETILIR."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, collections, datetime as dt

T0 = "2026-08-19 00:00:00"          # kullanicinin soyledigi sinir
T0B = "2026-08-19 21:40:00"         # durum.md 'FRENSIZ' dilim sinirri


def oku(ad):
    out = []
    for ln in open(ad, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out


def eq_at(ad, t):
    """t'den ONCEKI son equity kaydi (pencere basi)."""
    son = None
    for r in oku(ad):
        if r["ts"] < t:
            son = r
        else:
            break
    return son


def giris_ts(kayitlar):
    """id -> giris ani (en erken kayittan: ts - tutma_saat)."""
    g = {}
    for r in kayitlar:
        t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
            - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
        i = r["id"]
        if i not in g or t < g[i]:
            g[i] = t
    return g


def rapor(ad_defter, isl_dosya, eq_dosya, state_dosya, t0):
    K = oku(isl_dosya)
    G = giris_ts(K)
    st = json.load(open(state_dosya, encoding="utf-8"))
    e0 = eq_at(eq_dosya, t0)
    e1 = st["equity"]

    print("=" * 96)
    print("%s   |  pencere %s -> simdi" % (ad_defter.upper(), t0))
    print("=" * 96)
    print("  equity pencere basi : %10.2f  (%s)" % (e0["equity"], e0["ts"]))
    print("  equity SIMDI        : %10.2f" % e1)
    print("  PENCERE REALIZE     : %+10.2f  <- gercek nakit degisimi" % (e1 - e0["equity"]))
    acik = st.get("acik_pozisyonlar", [])
    print("  acik pozisyon       : %d" % len(acik))

    # --- POZISYONLAR: girisi pencerede olanlar ---
    pen = [i for i, t in G.items() if t.strftime("%Y-%m-%d %H:%M:%S") >= t0]
    pen = set(pen)
    kp = [r for r in K if r["id"] in pen]
    # SAYIM: kismi suzulur
    npoz = len([r for r in kp if not r.get("kismi")])
    # TOPLAM: suzulmez, id ile birlestirilir
    pnl = collections.defaultdict(float)
    fnd = collections.defaultdict(float)
    fnd_bilinen = set()
    meta = {}
    for r in kp:
        pnl[r["id"]] += float(r.get("sonuc_usdt") or 0.0)
        if r.get("funding_usdt") is not None:
            fnd[r["id"]] += float(r["funding_usdt"])
            fnd_bilinen.add(r["id"])
        if not r.get("kismi"):
            meta[r["id"]] = r
    top = sum(pnl.values())
    tfnd = sum(fnd.values())
    kazanan = sum(1 for i, v in pnl.items() if v > 0)
    print("")
    print("  PENCEREDE ACILIP KAPANAN pozisyon : %d" % npoz)
    print("    defter P&L (fonlama HARIC)      : %+10.2f" % top)
    print("    fonlama (id ile toplandi, N=%d) : %+10.2f" % (len(fnd_bilinen), tfnd))
    print("    kazanma orani (POZISYON basi)   : %d/%d = %%%.1f"
          % (kazanan, len(pnl), 100.0 * kazanan / max(len(pnl), 1)))
    return K, G, pen, pnl, fnd, meta, (e1 - e0["equity"])


A = rapor("testbot", "testbot_islemler.jsonl", "testbot_equity.jsonl",
          "testbot_state.json", T0)
print("")
B = rapor("golge", "golge_islemler.jsonl", "golge_equity.jsonl",
          "golge_state.json", T0)

# ---- GOLGE: IKI IS AYRILIR (CLAUDE.md) ----
K, G, pen, pnl, fnd, meta, _ = B
print("")
print("=" * 96)
print("GOLGE — IKI IS AYRI SAYILIR  (CLAUDE.md: golge tek soru yalitmiyor)")
print("=" * 96)
grup = collections.defaultdict(lambda: [0, 0.0, 0.0, 0])   # n, pnl, funding, kazanan
for i in pnl:
    m = meta.get(i)
    if not m:
        continue
    k = m.get("kaynak", "?")
    tez = "pump_long_tezi" if k == "golge:pump_long_tezi" else "REDDEDILEN GIRIS"
    grup[tez][0] += 1
    grup[tez][1] += pnl[i]
    grup[tez][2] += fnd.get(i, 0.0)
    grup[tez][3] += 1 if pnl[i] > 0 else 0
print("  %-18s %5s %12s %12s %10s" % ("is", "poz", "P&L", "fonlama", "kazanma"))
for k, v in sorted(grup.items(), key=lambda x: -abs(x[1][1])):
    print("  %-18s %5d %+12.2f %+12.2f %9.1f%%"
          % (k, v[0], v[1], v[2], 100.0 * v[3] / max(v[0], 1)))

print("")
print("  KAYNAK KIRILIMI (reddedilen girisler):")
g2 = collections.defaultdict(lambda: [0, 0.0, 0])
for i in pnl:
    m = meta.get(i)
    if not m or m.get("kaynak") == "golge:pump_long_tezi":
        continue
    k = m.get("kaynak", "?")
    g2[k][0] += 1
    g2[k][1] += pnl[i]
    g2[k][2] += 1 if pnl[i] > 0 else 0
for k, v in sorted(g2.items(), key=lambda x: x[1][1]):
    print("    %-26s %3d poz  %+9.2f  kazanma %.0f%%"
          % (k, v[0], v[1], 100.0 * v[2] / max(v[0], 1)))

# ---- YON ve REJIM kirilimi (iki defter) ----
print("")
print("=" * 96)
print("YON ve REJIM — pencerede acilip kapanan pozisyonlar")
print("=" * 96)
for ad, (Kx, Gx, penx, pnlx, fndx, metax, _d) in (("testbot", A), ("golge", B)):
    print("  --- %s ---" % ad)
    for alan in ("yon", "rejim_giriste"):
        g3 = collections.defaultdict(lambda: [0, 0.0, 0])
        for i in pnlx:
            m = metax.get(i)
            if not m:
                continue
            k = str(m.get(alan))
            g3[k][0] += 1
            g3[k][1] += pnlx[i]
            g3[k][2] += 1 if pnlx[i] > 0 else 0
        for k, v in sorted(g3.items(), key=lambda x: x[1][1]):
            print("     %-8s %-8s %3d poz  %+9.2f  kazanma %.0f%%"
                  % (alan.replace("_giriste", ""), k, v[0], v[1],
                     100.0 * v[2] / max(v[0], 1)))
    print("")

# ---- MUTABAKAT ----
print("=" * 96)
print("MUTABAKAT — pencere realize ile defter P&L farki = fonlama + ucret")
print("=" * 96)
for ad, X in (("testbot", A), ("golge", B)):
    top = sum(X[3].values())
    print("  %-8s realize %+9.2f  defter P&L %+9.2f  fark %+8.2f  (fonlama %+7.2f)"
          % (ad, X[6], top, X[6] - top, sum(X[4].values())))
