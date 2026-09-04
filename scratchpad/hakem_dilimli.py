#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HAKEM PENCERESI — DILIMLI RAPOR. SALT OKUMA.
CLAUDE.md: pencere sonucu EQUITY'den turetilir, kasa sifirlamasi DUSULUR."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, collections, datetime as dt, statistics as stt

T0 = "2026-08-12 01:17:00"
# Dilimler KANITTAN: equity kutugu durum gecisleri + durum.md'nin btc_pay fren kaydi
DILIM = [
    ("A1  btc_pay SHORT freni ACIK",  "2026-08-12 01:17:00", "2026-08-19 13:44:00"),
    ("A2  btc_pay freni KAPALI",      "2026-08-19 13:44:00", "2026-08-19 19:30:00"),
    ("A3  btc_pay freni ACIK",        "2026-08-19 19:30:00", "2026-08-19 21:40:00"),
    ("B   frensiz SHORT + dusus freni", "2026-08-19 21:40:00", "2026-08-22 16:06:21"),
    ("C   *** DURDU (HALT_DUSUS) ***", "2026-08-22 16:06:21", "2026-08-24 01:24:35"),
    ("D   elle DEVAM (zirve sifir)",   "2026-08-24 01:24:35", "2026-08-26 17:58:52"),
    ("E   *** DURDU (HALT_DUSUS) ***", "2026-08-26 17:58:52", "2026-08-28 00:02:05"),
    ("F   dusus freni KAPALI (=0)",    "2026-08-28 00:02:05", "2099-01-01 00:00:00"),
]

K = [json.loads(l) for l in open("testbot_islemler.jsonl", encoding="utf-8") if l.strip()]
g = {}
for r in K:
    t = dt.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S") \
        - dt.timedelta(hours=float(r.get("tutma_saat") or 0))
    if r["id"] not in g or t < g[r["id"]]:
        g[r["id"]] = t
pnl, meta, fnd = collections.defaultdict(float), {}, collections.defaultdict(float)
for r in K:
    pnl[r["id"]] += float(r.get("sonuc_usdt") or 0)
    if r.get("funding_usdt") is not None:
        fnd[r["id"]] += float(r["funding_usdt"])
    if not r.get("kismi"):
        meta[r["id"]] = r

E = [json.loads(l) for l in open("testbot_equity.jsonl", encoding="utf-8") if l.strip()]
ST = json.load(open("testbot_state.json", encoding="utf-8"))
KS = ST["_kasa_sifirlama"]


def eq(t):
    v = [r for r in E if r["ts"] < t]
    return v[-1]["equity"] if v else None


print("=" * 108)
print("HAKEM PENCERESI — DILIMLI  (taban %s)" % T0)
print("=" * 108)
print("  ⚠️ KASA SIFIRLAMASI PENCERE ICINDE: %s  %+.2f $  -> DILIM A1'den DUSULUR"
      % (KS["ts"], KS["delta"]))
print("")
print("  %-32s %6s %9s %8s %8s %6s %9s"
      % ("dilim", "poz", "P&L", "kazanma", "ort", "oran", "equity D"))
top_poz = top_pnl = 0
for ad, a, b in DILIM:
    ids = [i for i in meta if a <= g[i].strftime("%Y-%m-%d %H:%M:%S") < b]
    v = [pnl[i] for i in ids]
    e0, e1 = eq(a), (eq(b) if b < "2099" else ST["equity"])
    ed = (e1 - e0) if (e0 and e1) else float("nan")
    if a <= KS["ts"] < b:
        ed -= KS["delta"]
    top_poz += len(v)
    top_pnl += sum(v)
    if v:
        kz = [x for x in v if x > 0]
        kb = [-x for x in v if x <= 0]
        oran = (stt.mean(kz) / stt.mean(kb)) if (kz and kb) else float("nan")
        print("  %-32s %6d %+9.0f %7.0f%% %+8.1f %6.2f %+9.0f"
              % (ad, len(v), sum(v), 100 * len(kz) / len(v), stt.mean(v), oran, ed))
    else:
        print("  %-32s %6d %9s %8s %8s %6s %+9.0f" % (ad, 0, "—", "—", "—", "—", ed))

print("")
print("  %-32s %6d %+9.0f" % ("TOPLAM (acilan pozisyon)", top_poz, top_pnl))

print("")
print("=" * 108)
print("PENCERE SONUCU — EQUITY'DEN TURETILDI (CLAUDE.md zorunlu yontem)")
print("=" * 108)
e0 = eq(T0)
e1 = ST["equity"]
real = e1 - e0 - KS["delta"]
print("  equity pencere basi            %10.2f" % e0)
print("  equity SIMDI                   %10.2f" % e1)
print("  kasa sifirlamasi (DUSULUR)     %10.2f" % KS["delta"])
print("  " + "-" * 44)
print("  PENCERE REALIZE                %+10.2f" % real)
print("")
pen_pnl = sum(pnl[i] for i in meta if g[i].strftime("%Y-%m-%d %H:%M:%S") >= T0)
print("  defter P&L (pencerede acilan)  %+10.2f" % pen_pnl)
print("  fark (fonlama + ucret + sinir) %+10.2f" % (real - pen_pnl))
print("")
print("  acik pozisyon: %d  ->  bu rakam REALIZE, acik kar/zarar DAHIL DEGIL"
      % len(ST.get("acik_pozisyonlar", [])))
print("")
print("  %s" % ("🔴 PENCERE EKSI KAPANDI" if real < 0 else "✅ PENCERE ARTI KAPANDI"))
