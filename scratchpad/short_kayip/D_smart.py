# -*- coding: utf-8 -*-
"""IZ D — YONU BELIRLEYEN `smart` (Pillar D) BILGI TASIYOR MU?

testbot.py'nin HER karar dali `smart`a bakiyor:
  smart=="LONG"  -> LONG dallari
  smart=="SHORT" -> SHORT dallari
  smart=="NOTR"  -> iki yonlu fade dali
Yani yon secimi bu etikete bagli. Etiket bilgi tasimiyorsa yon secimi gurultudur.

YONTEM (CLAUDE.md: sinyal MEKANIKTEN ARINIK olculur):
  ham ileri getiri (stop/hedef YOK, maliyet YOK) — 1s / 6s / 24s / 72s
  Bagimsiz olay = sembol x SAAT (ayni saatteki tekrarlar tek sayilir)
  GUN-KUMELI istatistik + sans olcumu (etiket karistirma, GUN ICINDE)
"""
import json, os, sys, collections, statistics as stx, datetime, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PROJE = os.path.dirname(os.path.dirname(HERE))
import ortak

random.seed(41)
UFUKLAR = [(1, "1s"), (6, "6s"), (24, "24s"), (72, "72s")]

# --- olaylari topla ---
ev = {}
with open(os.path.join(PROJE, "testbot_aday_arsiv.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        x = json.loads(line)
        if x["ts"][:10] < "2026-08-11": continue
        if x.get("smart") is None: continue
        k = (x["sym"], x["ts"][:13])
        if k not in ev: ev[k] = x
print("bagimsiz olay: %d · sembol: %d" % (len(ev), len({k[0] for k in ev})))

syms = sorted({k[0] for k in ev})
print("fiyat verisi cekiliyor (%d sembol)..." % len(syms))
ok = 0
for i, s in enumerate(syms, 1):
    if ortak.mumlar(s): ok += 1
    if i % 40 == 0: print("   %d/%d" % (i, len(syms)), flush=True)
print("   veri alinan: %d/%d\n" % (ok, len(syms)))

# --- ham ileri getiri ---
kayit = []
for (sym, saat), x in ev.items():
    b = ortak.mumlar(sym)
    if not b: continue
    t0 = int(datetime.datetime.strptime(x["ts"], "%Y-%m-%d %H:%M").timestamp() * 1000)
    ic = [z for z in b if z["t"] >= t0]
    if len(ic) < 13: continue
    ref = ic[0]["o"]
    if ref <= 0: continue
    d = {"smart": x["smart"], "gun": x["ts"][:10], "sym": sym,
         "taker": x.get("taker"), "pos": x.get("pos"), "stage": x.get("stage")}
    for saat_n, ad in UFUKLAR:
        j = saat_n * 12
        d[ad] = (ic[j]["c"]/ref-1)*100 if j < len(ic) else None
    kayit.append(d)
print("olculebilen olay: %d\n" % len(kayit))

def gun_kumeli(v):
    g = collections.defaultdict(list)
    for net, gun in v: g[gun].append(net)
    ok = [k for k in g if len(g[k]) >= 10]
    if len(ok) < 3: return None
    m = [stx.mean(g[k]) for k in ok]
    se = stx.stdev(m)/len(m)**0.5
    return stx.mean(m), (stx.mean(m)/se if se else 0), len(ok), sum(1 for x in m if x > 0)

print("=" * 92)
print("SORU 1 — `smart` etiketi ham ileri getiriyi ayiriyor mu?")
print("=" * 92)
for saat_n, ad in UFUKLAR:
    print("\n--- ufuk %s" % ad)
    print("   %-6s %7s %10s %10s %8s %8s" % ("smart", "N", "ort %", "gun ort", "gun-t", "poz gun"))
    ort = {}
    for sm in ("LONG", "NOTR", "SHORT"):
        v = [(d[ad], d["gun"]) for d in kayit if d["smart"] == sm and d.get(ad) is not None]
        if len(v) < 50:
            print("   %-6s %7d  N yetersiz" % (sm, len(v))); continue
        k = gun_kumeli(v)
        ort[sm] = stx.mean([z[0] for z in v])
        if k is None:
            print("   %-6s %7d %+10.3f  gun yetersiz" % (sm, len(v), ort[sm]))
        else:
            print("   %-6s %7d %+10.3f %+10.3f %+8.2f %5d/%-3d" % (sm, len(v), ort[sm], k[0], k[1], k[3], k[2]))
    if "LONG" in ort and "SHORT" in ort:
        print("   -> LONG eksi SHORT: %+.3f puan  %s" % (ort["LONG"]-ort["SHORT"],
              "(etiket DOGRU yonde)" if ort["LONG"] > ort["SHORT"] else "(etiket TERS yonde)"))

# --- SANS OLCUMU: gun icinde etiket karistirma ---
print("\n" + "=" * 92)
print("SANS OLCUMU — gun icinde `smart` etiketleri karistirilir (1000 tur)")
print("=" * 92)
for saat_n, ad in UFUKLAR:
    v = [d for d in kayit if d.get(ad) is not None]
    gg = collections.defaultdict(list)
    for d in v: gg[d["gun"]].append((d["smart"], d[ad]))
    ger = {}
    for sm in ("LONG", "SHORT"):
        sec = [z[1] for d in v if d["smart"] == sm for z in [(0, d[ad])]]
        if sec: ger[sm] = stx.mean(sec)
    if "LONG" not in ger or "SHORT" not in ger: continue
    gf = ger["LONG"] - ger["SHORT"]
    sahte = []
    for _ in range(1000):
        L, S = [], []
        for gun, lst in gg.items():
            etk = [e for e, _n in lst]; nets = [n for _e, n in lst]
            random.shuffle(etk)
            for e, n in zip(etk, nets):
                if e == "LONG": L.append(n)
                elif e == "SHORT": S.append(n)
        if L and S: sahte.append(stx.mean(L)-stx.mean(S))
    p = sum(1 for x in sahte if abs(x) >= abs(gf))/len(sahte)
    print("  %-4s LONG-SHORT farki %+7.3f · sahte ort %+7.3f (sd %.3f) · p=%.3f %s"
          % (ad, gf, stx.mean(sahte), stx.pstdev(sahte), p,
             "<-- SANSTAN FARKLI" if p < 0.05 else ""))
