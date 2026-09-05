#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKOR — GERCEK DEFTERDE ve NEDEN BOS? (2026-09-05)

Kullanici: "skor hicbir ise yaramiyorsa neden kullaniyoruz · 5 bilesen nasil
  etkisiz olur anlamiyorum."

🔴 ITIRAZ HAKLI: bugunku skor olcumu SENTETIK evrende yapildi ve bugun UC KEZ
   sentetik olcum gercek veriyle ters dustu. Bu betik skoru GERCEK DEFTERDE
   (botun fiilen actigi pozisyonlar) sinar ve "neden bos" sorusuna MEKANIZMA arar.

UC SORU:
  A) Gercek defterde skor sonucu ongoruyor mu?
  B) ARALIK SIKISMASI: kapi skor>=45 istedigi icin bot yalniz UST bandi goruyor;
     bilgi bandin ICINDE yok olmus olabilir.
  C) MEKANIZMA: skor YON mu OYNAKLIK mi olcuyor? (CLAUDE.md kayitli ders:
     "yon degil sadece hareket ongoren her sinyal degersizdir, cunku stop
     mesafesi hareketle buyur")

BETIMLEYICI. On-kayit yok, hukum yok. Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, statistics as stx, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IZLEME = os.path.join(KOK, "pozisyon_izleme.jsonl")
DEFTER = os.path.join(KOK, "testbot_islemler.jsonl")


def ilk_izleme():
    """id -> ILK izleme kaydi (giris anindaki ozellikler)."""
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
            if o is None or (r.get("ts") or "") < (o.get("ts") or ""):
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
        no = ana.get("notional") or 0.0
        usd = sum(k.get("sonuc_usdt") or 0.0 for k in ks)
        out[i] = {"usd": usd, "net": (usd / no * 100) if no else None,
                  "yon": ana.get("yon"), "gun": (ana.get("ts") or "")[:10],
                  "sebep": ana.get("sebep"), "sym": ana.get("sym")}
    return out


def gun_t(ps, alan="net"):
    g = collections.defaultdict(list)
    for p in ps:
        g[p["gun"]].append(p[alan])
    v = [sum(x) / len(x) for x in g.values()]
    if len(v) < 3:
        return None, None, None, len(v)
    m = sum(v) / len(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, (m / se if se else None), 2 * se, len(v)


def korelasyon(xs, ys):
    if len(xs) < 10:
        return None
    mx, my = stx.mean(xs), stx.mean(ys)
    pay = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    px = math.sqrt(sum((a - mx) ** 2 for a in xs))
    py = math.sqrt(sum((b - my) ** 2 for b in ys))
    return pay / (px * py) if px and py else None


def main():
    print("=" * 88)
    print("SKOR — GERCEK DEFTERDE ve NEDEN BOS?")
    print("=" * 88)
    print("🔴 Bugunku skor olcumu SENTETIK'ti; bugun UC KEZ sentetik-gercek celiskisi")
    print("   cikti. Bu betik GERCEK DEFTERI kullanir.\n")

    iz, df = ilk_izleme(), defter()
    ps = []
    for i, d in df.items():
        z = iz.get(i)
        if not z or d["net"] is None:
            continue
        sk = z.get("score")
        if sk is None:
            continue
        ps.append({"id": i, "skor": sk, "net": d["net"], "usd": d["usd"],
                   "yon": d["yon"], "gun": d["gun"], "sebep": d["sebep"],
                   "stop_m": z.get("stop_mesafe_pct"), "atr": z.get("atr_giriste"),
                   "giris": z.get("giris"), "vol_x": z.get("vol_x"),
                   "oi24": z.get("oi24"), "comp": z.get("comp"),
                   "pos": z.get("pos"), "last1": z.get("last1"),
                   "funding": z.get("funding"), "mfe": z.get("mfe_pct")})
    print("olculebilen pozisyon: %d\n" % len(ps))
    if len(ps) < 40:
        print("yetersiz")
        return

    # --- B) ARALIK SIKISMASI ---
    sk = [p["skor"] for p in ps]
    print("### B) ARALIK SIKISMASI — bot skorun hangi bandini goruyor?")
    s2 = sorted(sk)
    print("   min %.1f · %%25 %.1f · medyan %.1f · %%75 %.1f · maks %.1f"
          % (s2[0], s2[len(s2) // 4], s2[len(s2) // 2], s2[3 * len(s2) // 4], s2[-1]))
    print("   skor<45 olan pozisyon: %d (%%%.1f)   <- kapi 45 istiyor"
          % (sum(1 for x in sk if x < 45), sum(1 for x in sk if x < 45) / len(sk) * 100))
    print()

    # --- A) SKOR SONUCU ONGORUYOR MU ---
    print("### A) GERCEK DEFTERDE skor sonucu ongoruyor mu? (skor dilimleri)")
    ps.sort(key=lambda p: p["skor"])
    n4 = len(ps) // 4
    dilim = [("Q1 (dusuk)", ps[:n4]), ("Q2", ps[n4:2 * n4]),
             ("Q3", ps[2 * n4:3 * n4]), ("Q4 (yuksek)", ps[3 * n4:])]
    print("   %-13s %5s %9s %11s %11s %10s %9s" %
          ("dilim", "N", "skor ort", "net% ort", "dolar ort", "kazanan", "stop% ort"))
    for ad, g in dilim:
        if not g:
            continue
        stopm = [p["stop_m"] for p in g if p["stop_m"] is not None]
        print("   %-13s %5d %9.1f %+11.3f %+11.2f %9.1f%% %9.2f" %
              (ad, len(g), stx.mean([p["skor"] for p in g]),
               stx.mean([p["net"] for p in g]), stx.mean([p["usd"] for p in g]),
               sum(1 for p in g if p["usd"] > 0) / len(g) * 100,
               stx.mean(stopm) if stopm else 0))
    a, b = dilim[3][1], dilim[0][1]
    # gun-kumeli iki ornek
    def gg(x):
        d = collections.defaultdict(list)
        for p in x:
            d[p["gun"]].append(p["net"])
        return [sum(v) / len(v) for v in d.values()]
    va, vb = gg(a), gg(b)
    if len(va) >= 3 and len(vb) >= 3:
        ma, mb = stx.mean(va), stx.mean(vb)
        se = math.sqrt(stx.variance(va) / len(va) + stx.variance(vb) / len(vb))
        print("   Q4 - Q1 : %+.3f%%  t_gun %+.2f  MDE %.3f  -> %s"
              % (ma - mb, (ma - mb) / se if se else 0, 2 * se,
                 "GORULUR" if abs(ma - mb) >= 2 * se else "goremiyoruz"))
    print()

    # --- C) MEKANIZMA: skor YON mu OYNAKLIK mi ---
    print("### C) MEKANIZMA — skor NEYI olcuyor?")
    print("   (CLAUDE.md: 'yon degil sadece hareket ongoren sinyal degersizdir,")
    print("    cunku stop mesafesi hareketle buyur')")
    esle = [(p["skor"], p["stop_m"]) for p in ps if p["stop_m"] is not None]
    r1 = korelasyon([x[0] for x in esle], [x[1] for x in esle])
    print("   skor ~ STOP MESAFESI (%%)   : r = %s   <- oynaklik olcusu"
          % (("%+.3f" % r1) if r1 is not None else "yok"))
    esle2 = [(p["skor"], abs(p["mfe"])) for p in ps if p["mfe"] is not None]
    r2 = korelasyon([x[0] for x in esle2], [x[1] for x in esle2])
    print("   skor ~ |MFE| (hareket buyuklugu) : r = %s   <- HAREKET"
          % (("%+.3f" % r2) if r2 is not None else "yok"))
    r3 = korelasyon([p["skor"] for p in ps], [p["net"] for p in ps])
    print("   skor ~ net%% (YON+sonuc)          : r = %s   <- YON"
          % (("%+.3f" % r3) if r3 is not None else "yok"))
    print()
    print("   stop mesafesi, skor dilimine gore:")
    for ad, g in dilim:
        sm = [p["stop_m"] for p in g if p["stop_m"] is not None]
        if sm:
            print("      %-13s stop %%%.2f   MFE medyan %+.2f%%"
                  % (ad, stx.mean(sm),
                     stx.median([p["mfe"] for p in g if p["mfe"] is not None] or [0])))
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
