#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IZ E — `top_ls` GENIS SINAV: radar_archive, 49 gun.

=========================== ON-KAYIT (kosturulmadan ONCE yazildi) ============================
KESIF (11-17 Agustos, 7 gun, N=1312): top_ls ileri 72s getiriyi ayiriyor.
  gun ici sira korelasyonu +0,273 · 7/7 gun pozitif · t=+7,07
  dilimler: top_ls<1,43 -> -8..-18%  ·  top_ls>1,43 -> +4..+7%

SINAV: radar_archive.jsonl · 2026-07-02 .. 2026-08-20 · 38.841 kayit · 394 sembol.
  Bu, yapilabilecek EN GENIS sinav — Binance futures/data uclari 30 gun geriye
  gidiyor, yani 2 yillik sinav IMKANSIZ. Arsiv tek kaynak.

🔴 KESIF PENCERESI SINAVIN ICINDE. O yuzden BIRINCIL HUKUM, kesif gunleri
   (11-17 Agustos) CIKARILARAK verilir. Bu gercek bir holdout'tur (42 gun).

GECME OLCUTU — dordu de gerekli (KESIF DISI 42 gunde):
  1. Gun ici sira korelasyonu POZITIF, gun-kumeli t > +2,0
  2. Iki zaman yarisinda da pozitif
  3. Ust tercil ile alt tercil arasinda tutarli fark (isaret ayni)
  4. chg24 sabitlenince ayrim duruyor (karistirici kontrolu)

BEKLENTI (sonuc gorulmeden): KARARSIZ, gecmeye yakin.
  Lehte: kesifte gun-kumeli t=+7,07 cok guclu ve 7/7 gun tutarli; mekanizma
    yorumlanabilir (buyuk hesaplarin konumu).
  Aleyhte: bu oturumda 3 iz tam bu asamada coktu (<-40 LONG, >40 LONG,
    trailing). Ayrica top_ls AYNI BANTTAN (Binance perp) — CLAUDE.md'nin
    "her yeni aday fiyatin baska ifadesi cikiyor" uyarisi geceli.

ESIK TARAMASI YASAK. Dilimler ONDALIK olarak sabit; "en iyi esik" aranmaz.
KARAR CIKARILMAYACAK — kullanici talimati, yalniz olcum.
==============================================================================================
"""
import json, os, sys, collections, statistics as stx, datetime, math

HERE = os.path.dirname(os.path.abspath(__file__))
PROJE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, PROJE)
import evren

MUM1H = os.path.join(HERE, "mum1h")
os.makedirs(MUM1H, exist_ok=True)
BAS = datetime.datetime(2026, 7, 1)
KESIF = {"2026-08-%02d" % d for d in range(11, 18)}
UFUK = 72


def mum1h(sym):
    yol = os.path.join(MUM1H, sym + ".json")
    if os.path.exists(yol):
        try:
            with open(yol, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    try:
        d = evren.get("https://fapi.binance.com/fapi/v1/klines?symbol=%sUSDT&interval=1h"
                      "&startTime=%d&limit=1500" % (sym, int(BAS.timestamp()*1000)), timeout=25)
        out = [{"t": int(k[0]), "o": float(k[1]), "c": float(k[4])} for k in d]
    except Exception:
        out = []
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(out, f)
    return out


# ---------- ARSIV BOSLUK DENETIMI (CLAUDE.md sarti) ----------
print("ARSIV BOSLUK DENETIMI — radar_bosluk.jsonl YOK (mekanizma 08-17'de basladi).")
print("Bosluk arsivin KENDI zaman damgalarindan turetiliyor (tum pencereyi kapsar).")
tsler = set()
kayit = []
with open(os.path.join(PROJE, "radar_archive.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        x = json.loads(line)
        if x.get("top_ls") is None: continue
        tsler.add(x["ts"])
        kayit.append(x)
tl = sorted(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M") for t in tsler)
bosluk = [(a, b, (b-a).total_seconds()/60) for a, b in zip(tl, tl[1:]) if (b-a).total_seconds()/60 > 30]
print("  ayrik tur damgasi: %d · %s .. %s" % (len(tl), tl[0], tl[-1]))
print("  30 dk'dan uzun boslik: %d" % len(bosluk))
top = sum(b[2] for b in bosluk)
kapsam = (tl[-1]-tl[0]).total_seconds()/60
print("  toplam bosluk %.0f dk / pencere %.0f dk  ->  kayip %%%.1f" % (top, kapsam, 100*top/kapsam))
for a, b, d in sorted(bosluk, key=lambda z: -z[2])[:5]:
    print("     %s -> %s  (%.0f dk)" % (a.strftime("%m-%d %H:%M"), b.strftime("%m-%d %H:%M"), d))
print()

# ---------- olaylari tekille: sembol x SAAT ----------
ev = {}
for x in kayit:
    k = (x["sym"], x["ts"][:13])
    if k not in ev:
        ev[k] = x
print("bagimsiz olay (sembol x saat): %d · sembol: %d" % (len(ev), len({k[0] for k in ev})))

syms = sorted({k[0] for k in ev})
print("1s mum cekiliyor (%d sembol)..." % len(syms))
for i, s in enumerate(syms, 1):
    mum1h(s)
    if i % 60 == 0: print("   %d/%d" % (i, len(syms)), flush=True)

veri = []
for (sym, saat), x in ev.items():
    b = mum1h(sym)
    if not b: continue
    t0 = int(datetime.datetime.strptime(x["ts"], "%Y-%m-%d %H:%M").timestamp()*1000)
    ic = [z for z in b if z["t"] >= t0]
    if len(ic) < UFUK+1: continue
    ref = ic[0]["o"]
    if ref <= 0: continue
    veri.append({"top_ls": x["top_ls"], "gun": x["ts"][:10], "sym": sym,
                 "chg24": None, "r72": (ic[UFUK]["c"]/ref-1)*100,
                 "kesif": x["ts"][:10] in KESIF})
print("72s ufku TAM olan olay: %d  (kesif %d · KESIF DISI %d)\n"
      % (len(veri), sum(1 for d in veri if d["kesif"]), sum(1 for d in veri if not d["kesif"])))


def sira_kor(v):
    """gun ici sira korelasyonu -> (gun sayisi, ortalama, t, pozitif gun)"""
    g = collections.defaultdict(list)
    for d in v: g[d["gun"]].append(d)
    rs = []
    for gun, lst in g.items():
        if len(lst) < 20: continue
        a = sorted(range(len(lst)), key=lambda i: lst[i]["top_ls"])
        b = sorted(range(len(lst)), key=lambda i: lst[i]["r72"])
        ra = {j: i for i, j in enumerate(a)}; rb = {j: i for i, j in enumerate(b)}
        xs = [ra[i] for i in range(len(lst))]; ys = [rb[i] for i in range(len(lst))]
        mx, my = stx.mean(xs), stx.mean(ys)
        cv = sum((p-mx)*(q-my) for p, q in zip(xs, ys))
        sx = math.sqrt(sum((p-mx)**2 for p in xs)); sy = math.sqrt(sum((q-my)**2 for q in ys))
        if sx and sy: rs.append(cv/(sx*sy))
    if len(rs) < 3: return None
    se = stx.stdev(rs)/len(rs)**0.5
    return len(rs), stx.mean(rs), (stx.mean(rs)/se if se else 0), sum(1 for x in rs if x > 0)


def dilimler(v, n=10):
    s = sorted(v, key=lambda d: d["top_ls"])
    b = len(s)//n
    out = []
    for i in range(n):
        g = s[i*b:(i+1)*b] if i < n-1 else s[(n-1)*b:]
        out.append((g[0]["top_ls"], g[-1]["top_ls"], len(g), stx.mean([d["r72"] for d in g])))
    return out


for etiket, v in (("KESIF DISI 42 gun (BIRINCIL HUKUM)", [d for d in veri if not d["kesif"]]),
                  ("kesif 7 gun (referans)", [d for d in veri if d["kesif"]]),
                  ("TUMU 49 gun", veri)):
    print("=" * 92)
    print("%s   N=%d" % (etiket, len(v)))
    print("=" * 92)
    if len(v) < 200:
        print("  N yetersiz\n"); continue
    k = sira_kor(v)
    if k: print("  OLCUT 1 — gun ici sira korelasyonu: %d gun · ort %+.4f · t=%+.2f · pozitif %d/%d"
                % (k[0], k[1], k[2], k[3], k[0]))
    srt = sorted(v, key=lambda d: d["gun"])
    yar = len(srt)//2
    for et, dilim in (("A yarisi", srt[:yar]), ("B yarisi", srt[yar:])):
        kk = sira_kor(dilim)
        if kk: print("  OLCUT 2 — %s: ort %+.4f · t=%+.2f · pozitif %d/%d" % (et, kk[1], kk[2], kk[3], kk[0]))
    print("  OLCUT 3 — ondalik dilimler:")
    for lo, hi, n, m in dilimler(v):
        print("     %6.2f - %-7.2f  N=%5d  r72 %+8.2f" % (lo, hi, n, m))
    t3 = dilimler(v, 3)
    print("     -> ust tercil %+.2f  ·  alt tercil %+.2f  ·  fark %+.2f"
          % (t3[2][3], t3[0][3], t3[2][3]-t3[0][3]))
    print()
