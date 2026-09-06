#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIKISMA -> KIRILIM: oynakligi ucuzken al

ON_KAYIT_sikisma_kirilim.md · commit 03d22de — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

SALT-OKUNUR. Arsiv context'e yuklenmez. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, math, random, collections, statistics as stx
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KOK)

ARSIV = os.path.join(KOK, "radar_archive.jsonl")
KDIR = os.path.join(KOK, "scratchpad", "fund_ls", "klines")

KAYMA = 3
COOLDOWN = 4.0
KOVA_BAR = 10             # olcucu_nbar_stop
BEKLEME = 12              # saat
HEDEF_PCT = 10.0
ZAMAN_STOP = 48
MALIYET = 0.09
SANS_TEKRAR = 1           # C2: her olay icin 1 eslestirilmis rastgele an

random.seed(20260906)


def ts_ms(ts):
    d = dt.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M")
    d = (d - dt.timedelta(hours=KAYMA)).replace(minute=0, second=0, microsecond=0)
    return int(d.replace(tzinfo=dt.UTC).timestamp() * 1000)


def gun_kumeli_t(ciftler):
    g = collections.defaultdict(list)
    for gun, f in ciftler:
        g[gun].append(f)
    v = [stx.mean(x) for x in g.values()]
    if len(v) < 3:
        return 0.0, 0.0, len(v)
    m = stx.mean(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, ((m / se) if se > 0 else 0.0), len(v)


def mumlar():
    out = {}
    for f in os.listdir(KDIR):
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(KDIR, f), encoding="utf-8"))
        except Exception:
            continue
        d.sort(key=lambda x: x["t"])
        out[f[:-5]] = (d, {int(x["t"]): i for i, x in enumerate(d)})
    return out


def kirilim_sim(d, i0, hedef_pct=HEDEF_PCT, m_kova=None):
    """i0 = t0'in bar indeksi. Kova = i0 ONCESI KOVA_BAR bar.
    -> None (kirilim yok / belirsiz) veya dict"""
    if i0 < KOVA_BAR + 1 or i0 + BEKLEME + ZAMAN_STOP >= len(d):
        return None
    kova = d[i0 - KOVA_BAR:i0]
    tepe = max(b["h"] for b in kova)
    dip = min(b["l"] for b in kova)
    if tepe <= dip:
        return None
    for j in range(i0, i0 + BEKLEME):
        b = d[j]
        ust = b["h"] >= tepe
        alt = b["l"] <= dip
        if ust and alt:
            return {"durum": "belirsiz"}
        if not (ust or alt):
            continue
        yon = "LONG" if ust else "SHORT"
        giris = tepe if ust else dip
        stop = dip if ust else tepe
        genislik = abs(giris - stop) / giris * 100.0
        if genislik <= 0:
            return None
        if m_kova is not None:
            h = giris * (1 + m_kova * genislik / 100.0) if ust \
                else giris * (1 - m_kova * genislik / 100.0)
        else:
            h = giris * (1 + hedef_pct / 100.0) if ust \
                else giris * (1 - hedef_pct / 100.0)
        hp = abs(h - giris) / giris * 100.0
        for k in range(j + 1, min(j + 1 + ZAMAN_STOP, len(d))):
            bb = d[k]
            if yon == "LONG":
                if bb["l"] <= stop:
                    return _sonuc(yon, -genislik, genislik, hp, 0, k - j)
                if bb["h"] >= h:
                    return _sonuc(yon, hp, genislik, hp, 1, k - j)
            else:
                if bb["h"] >= stop:
                    return _sonuc(yon, -genislik, genislik, hp, 0, k - j)
                if bb["l"] <= h:
                    return _sonuc(yon, hp, genislik, hp, 1, k - j)
        k = min(j + ZAMAN_STOP, len(d) - 1)
        c = d[k]["c"]
        ham = ((c / giris - 1) * 100.0) if yon == "LONG" else ((giris / c - 1) * 100.0)
        return _sonuc(yon, ham, genislik, hp, 0, k - j)
    return {"durum": "kirilmadi"}


def _sonuc(yon, ham, genislik, hedef_pct, hit, sure):
    return {"durum": "ok", "yon": yon, "R": (ham - MALIYET) / genislik,
            "hit": hit, "stop_pct": genislik, "hedef_pct": hedef_pct,
            "sure": sure}


def olaylar(mum, tanim):
    """tanim: 'HAZIRLANIYOR' | 'comp'"""
    out = []
    son = {}
    with open(ARSIV, encoding="utf-8", errors="ignore") as f:
        for l in f:
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                continue
            s, p = r.get("sym"), r.get("price")
            if not s or not p or s not in mum:
                continue
            if tanim == "HAZIRLANIYOR":
                if r.get("stage") != "HAZIRLANIYOR":
                    continue
            else:
                c = r.get("comp")
                if c is None or c >= 0.65:
                    continue
            t = ts_ms(r["ts"])
            if s in son and (t - son[s]) < COOLDOWN * 3_600_000:
                continue
            son[s] = t
            out.append({"sym": s, "gun": r["ts"][:10], "t": t})
    return out


def kol_kos(olay, mum, m_kova=None):
    ok, kirilmadi, belirsiz, atlandi = [], 0, 0, 0
    sans = []
    for o in olay:
        d, ix = mum[o["sym"]]
        i0 = ix.get(o["t"])
        if i0 is None:
            atlandi += 1
            continue
        s = kirilim_sim(d, i0, m_kova=m_kova)
        if s is None:
            atlandi += 1
            continue
        if s["durum"] == "kirilmadi":
            kirilmadi += 1
            continue
        if s["durum"] == "belirsiz":
            belirsiz += 1
            continue
        s["gun"] = o["gun"]
        s["sym"] = o["sym"]
        ok.append(s)
        # C2 — ESLESTIRILMIS RASTGELE AN: ayni sembol, ayni gun, rastgele saat
        for _ in range(SANS_TEKRAR):
            gun_bas = o["t"] - (o["t"] % 86_400_000)
            rt = gun_bas + random.randrange(24) * 3_600_000
            ri = ix.get(rt)
            if ri is None:
                continue
            rs = kirilim_sim(d, ri, m_kova=m_kova)
            if rs and rs["durum"] == "ok":
                rs["gun"] = o["gun"]
                sans.append(rs)
    return ok, sans, kirilmadi, belirsiz, atlandi


def ozet(rows, ad):
    if not rows:
        return None
    R = [x["R"] for x in rows]
    hit = sum(x["hit"] for x in rows)
    sp = stx.median([x["stop_pct"] for x in rows])
    hp = stx.median([x["hedef_pct"] for x in rows])
    bb = 100.0 / (1 + hp / sp) if sp > 0 else 100.0
    return {"ad": ad, "N": len(rows), "ortR": stx.mean(R), "toplamR": sum(R),
            "isabet": 100.0 * hit / len(rows), "stop": sp, "hedef": hp,
            "basabas": bb, "sure": stx.median([x["sure"] for x in rows])}


def bas_ozet(o):
    print("   %-22s N=%4d  ort R %+7.4f  isabet %5.1f%%  stop %%%.2f  hedef %%%.1f  basabas %5.1f%%  sure %.0fs"
          % (o["ad"], o["N"], o["ortR"], o["isabet"], o["stop"], o["hedef"],
             o["basabas"], o["sure"]))


def degerlendir(ok, sans, etiket):
    o = ozet(ok, "kirilim")
    c = ozet(sans, "C2 sans")
    if not o or not c:
        print("   yetersiz")
        return None
    bas_ozet(o)
    bas_ozet(c)
    # B3/B4: gun-kumeli fark
    g = collections.defaultdict(lambda: ([], []))
    for x in ok:
        g[x["gun"]][0].append(x["R"])
    for x in sans:
        g[x["gun"]][1].append(x["R"])
    gf = [(gg, stx.mean(a) - stx.mean(b)) for gg, (a, b) in g.items()
          if len(a) >= 2 and len(b) >= 2]
    m, t, ng = gun_kumeli_t(gf)
    ra = [x["R"] for x in ok]
    rb = [x["R"] for x in sans]
    mde = 2.8 * math.sqrt((stx.variance(ra) / len(ra) if len(ra) > 1 else 0) +
                          (stx.variance(rb) / len(rb) if len(rb) > 1 else 0))
    fark = o["ortR"] - c["ortR"]
    # B5 iki yari
    gs = sorted(set(x["gun"] for x in ok))
    orta = gs[len(gs) // 2]
    ya = [x["R"] for x in ok if x["gun"] < orta]
    yb = [x["R"] for x in ok if x["gun"] >= orta]
    b5 = bool(ya and yb and (stx.mean(ya) > 0) == (stx.mean(yb) > 0))
    # B6 yogunlasma
    gd = collections.defaultdict(list)
    for x in ok:
        gd[x["gun"]].append(x["R"])
    eniyi = sorted(gd, key=lambda k: -stx.mean(gd[k]))[:2]
    kalan = [x["R"] for x in ok if x["gun"] not in eniyi]
    kalan = sorted(kalan)[:-5] if len(kalan) > 5 else kalan
    b6 = bool(kalan and stx.mean(kalan) > 0)
    B = {
        "B1 isabet > basabas": o["isabet"] > o["basabas"],
        "B2 ort R > 0": o["ortR"] > 0,
        "B3 C2 farki t >= 2,0": t >= 2.0,
        "B4 |fark| > MDE": abs(fark) > mde,
        "B5 iki yari ayni isaret": b5,
        "B6 yogunlasma": b6,
    }
    print("      C2 farki %+.4f R · gun-kumeli t %+.2f (%d gun) · MDE %.4f"
          % (fark, t, ng, mde))
    print("      yari A %+.4f · yari B %+.4f · en iyi 2 gun+5 islem cikinca %+.4f"
          % (stx.mean(ya) if ya else 0, stx.mean(yb) if yb else 0,
             stx.mean(kalan) if kalan else 0))
    for k, v in B.items():
        print("      %-26s %s" % (k, "GECTI" if v else "DUSTU"))
    hep = all(B.values())
    print("      -> %s" % ("🔑 GECTI" if hep else
                           ("DUSTU" if not (B["B1 isabet > basabas"] and B["B2 ort R > 0"])
                            else "GOREMIYORUZ / BELIRSIZ")))
    return {"etiket": etiket, "gecti": hep, "B": B, "o": o, "fark": fark, "mde": mde}


def main():
    print("=" * 104)
    print("SIKISMA -> KIRILIM — ON_KAYIT_sikisma_kirilim.md (03d22de)")
    print("🔴 Gecse bile bota KONMAZ — AYRI DEFTERLE canli test (on-kayit bolum 9).")
    print("=" * 104)
    mum = mumlar()
    print("mum: %d sembol" % len(mum))
    print()

    for tanim, etiket, birincil in (("HAZIRLANIYOR", "HAZIRLANIYOR (BIRINCIL)", True),
                                    ("comp", "comp<0.65 (ikincil)", False)):
        olay = olaylar(mum, tanim)
        ok, sans, kirilmadi, belirsiz, atlandi = kol_kos(olay, mum)
        print("### %s" % etiket)
        print("   olay %d -> kirildi %d · kirilmadi %d · belirsiz %d · veri yok %d"
              % (len(olay), len(ok), kirilmadi, belirsiz, atlandi))
        if not ok:
            print("   yetersiz")
            print()
            continue
        yd = collections.Counter(x["yon"] for x in ok)
        print("   yon: LONG %d · SHORT %d" % (yd["LONG"], yd["SHORT"]))
        print()
        r = degerlendir(ok, sans, etiket)
        print()
        if birincil and r:
            # ikincil: yon ayri ayri (hukum kurmaz)
            print("   IKINCIL — yon ayri ayri (hukum KURMAZ):")
            for y in ("LONG", "SHORT"):
                sub = [x for x in ok if x["yon"] == y]
                oo = ozet(sub, "  %s" % y)
                if oo:
                    bas_ozet(oo)
            # ikincil: m x kova hedefi
            ok2, sans2, _, _, _ = kol_kos(olay, mum, m_kova=3.0)
            oo = ozet(ok2, "hedef 3 x kova")
            if oo:
                print("   IKINCIL — hedef 3 x kova genisligi (hukum KURMAZ):")
                bas_ozet(oo)
            print()
    print("Salt-okuma. Arsiv context'e yuklenmedi. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
