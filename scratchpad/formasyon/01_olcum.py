#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUM FORMASYONLARI — OLCUM (2026-09-06)

ON-KAYIT: ON_KAYIT_formasyon.md, commit dd66728 — KOSUMDAN ONCE yazildi.
Olcutler burada YENIDEN YAZILMAZ, on-kayittan AYNEN alinir:

  BIRINCIL HUCRE: pin bar · +4 saat
  F1 🔴 pin_BOGA - pin_AYI >= +0,50 puan VE gun-kumeli t >= +2,5
  F2    her yon KENDI kontrolunu gecer (BOGA>kontrol VE AYI<kontrol)
  F3    ufuk tutarliligi (+1s/+4s/+24s) >= 2/3 ayni isaret
  F4 🔑 NEGATIF KONTROL: |doji - kontrol| < MDE   (doji ONGORMEMELI)
  F5 🔴 yogunlasma: en iyi 2 gun cikinca hala >= +0,50
  GECTI = besi birden. "ZAYIF" kategorisi YOK.

  PARAMETRE TARAMASI YOK — esikler standart tanimdan (2x ve 0,10).

Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, random, datetime, statistics as stx, collections

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURASI))
KL_UZUN = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
KL_TAZE = os.path.join(KOK, "scratchpad", "taze_1h")

BAS = "2026-08-22"
SON = "2026-09-04"
TOHUM = 20260906
UFUKLAR = (("h1", 1, "+1 saat"), ("h4", 4, "+4 saat"), ("h24", 24, "+24 saat"))
BIRINCIL = "h4"
MDE = 0.965            # 00_guc.py'de OLCULDU, on-kayita yazildi
F1_ETKI = 0.50
F1_T = 2.5


# ---------------------------------------------------------------------------
def sekil(b):
    o, h, l, c = float(b["o"]), float(b["h"]), float(b["l"]), float(b["c"])
    ar = h - l
    if ar <= 0:
        return None
    gov = abs(c - o)
    return {"o": o, "h": h, "l": l, "c": c, "ar": ar, "gov": gov,
            "ust": h - max(o, c), "alt": min(o, c) - l, "gov_or": gov / ar}


def formasyon(onceki, simdi):
    """-> {ad: +1 boga | -1 ayi | 0 yonsuz}. Standart tanimlar."""
    s = sekil(simdi)
    if not s:
        return {}
    out = {}
    if s["alt"] >= 2 * s["gov"] and s["ust"] <= s["gov"]:
        out["pin"] = +1
    elif s["ust"] >= 2 * s["gov"] and s["alt"] <= s["gov"]:
        out["pin"] = -1
    if s["gov_or"] <= 0.10:
        out["doji"] = 0
    p = sekil(onceki) if onceki else None
    if p:
        if (s["c"] > s["o"] and p["c"] < p["o"]
                and s["o"] <= p["c"] and s["c"] >= p["o"]):
            out["yutan"] = +1
        elif (s["c"] < s["o"] and p["c"] > p["o"]
                and s["o"] >= p["c"] and s["c"] <= p["o"]):
            out["yutan"] = -1
    return out


def _sinama():
    """🔴 ZORUNLU (CLAUDE.md: siniflandirma yapan her betikte).
    Bilinen girdi -> beklenen etiket. Duserse betik CALISMAYI REDDEDER.
    NEGATIF DURUM ozellikle onemli: 'hareket bitisi' olcumu %99,96 etiketleyip
    olmustu — asiri etiketleme en olasi olum bicimi."""
    B = lambda o, h, l, c: {"o": o, "h": h, "l": l, "c": c}
    testler = [
        # cekic: alt fitil uzun, ust fitil yok  -> pin +1
        (None, B(100, 101, 90, 100.5), {"pin": +1}),
        # kayan yildiz: ust fitil uzun, alt yok -> pin -1
        (None, B(100, 110, 100, 100.05), {"pin": -1}),
        # doji: govde ~0
        (None, B(100, 101, 99, 100), {"doji": 0}),
        # HICBIRI: normal govdeli bar  -> BOS
        (None, B(100, 101, 99, 100.7), {}),
        # boga yutan
        (B(100, 100.5, 97.5, 98), B(97.5, 101.5, 97, 101), {"yutan": +1}),
        # ayi yutan
        (B(98, 100.5, 97.5, 100), B(100.5, 101, 97, 97.5), {"yutan": -1}),
    ]
    for i, (onc, sim, bek) in enumerate(testler, 1):
        g = formasyon(onc, sim)
        # doji tesaduefen esleseabilir; yalniz BEKLENEN anahtarlar kontrol edilir
        # ve BEKLENMEYEN 'pin'/'yutan' etiketi VARSA hata sayilir.
        for k, v in bek.items():
            if g.get(k) != v:
                raise RuntimeError("SINAMA %d DUSTU: %s -> %s (beklenen %s=%s)"
                                   % (i, sim, g, k, v))
        for k in ("pin", "yutan"):
            if k not in bek and k in g:
                raise RuntimeError("SINAMA %d DUSTU: BEKLENMEYEN etiket %s -> %s"
                                   % (i, k, g))
    print("   siniflandirma sinamasi: 6/6 GECTI (cekic · kayan yildiz · doji ·")
    print("      HICBIRI (asiri etiketleme yok) · boga yutan · ayi yutan)")


# ---------------------------------------------------------------------------
def barlar(sym):
    out = {}
    for kok in (KL_UZUN, KL_TAZE):
        p = os.path.join(kok, sym + ".json")
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        for b in d:
            out[int(b["t"]) // 3600000] = b
    return out


def kume_t(gun_farklari):
    v = [x for x in gun_farklari if x is not None]
    if len(v) < 3:
        return None, None, len(v)
    m = stx.mean(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, (m / se if se else None), len(v)


def main():
    print("=" * 96)
    print("MUM FORMASYONLARI — BOGA penceresi")
    print("=" * 96)
    print("ON-KAYIT: ON_KAYIT_formasyon.md commit dd66728 — KOSUMDAN ONCE")
    print("BIRINCIL HUCRE: pin bar · +4 saat · F1 = pin_BOGA - pin_AYI")
    print()
    print("### 0) ZORUNLU SINAMA")
    _sinama()
    print()

    semboller = sorted(set(
        [f[:-5] for f in os.listdir(KL_UZUN) if f.endswith(".json")]
        + [f[:-5] for f in os.listdir(KL_TAZE) if f.endswith(".json")]))
    bas_k = int(datetime.datetime.strptime(BAS, "%Y-%m-%d")
                .replace(tzinfo=datetime.UTC).timestamp()) // 3600
    son_k = int(datetime.datetime.strptime(SON, "%Y-%m-%d")
                .replace(tzinfo=datetime.UTC).timestamp()) // 3600 + 24

    rnd = random.Random(TOHUM)
    # kayitlar[(gun, kol)][ufuk] = [getiri...]   kol: pin+1/pin-1/yutan+1/... /kontrol
    kayit = collections.defaultdict(lambda: collections.defaultdict(list))
    n_bar = 0
    kor = {"chg": [], "volx": [], "pin": []}

    for sym in semboller:
        b = barlar(sym)
        if not b:
            continue
        gun_barlar = collections.defaultdict(list)
        for k in sorted(k for k in b if bas_k <= k < son_k):
            if (k - 1) not in b:
                continue
            if not all((k + u) in b for _, u, _ in UFUKLAR):
                continue
            gun_barlar[datetime.datetime.fromtimestamp(k * 3600, datetime.UTC)
                       .strftime("%Y-%m-%d")].append(k)
        for gun, ks in gun_barlar.items():
            n_bar += len(ks)
            form_k = []
            for k in ks:
                p0 = float(b[k]["c"])
                if not p0:
                    continue
                f = formasyon(b.get(k - 1), b[k])
                getiri = dict((ad, (float(b[k + u]["c"]) / p0 - 1) * 100)
                              for ad, u, _ in UFUKLAR)
                for adf, yon in f.items():
                    kol = "%s%+d" % (adf, yon)
                    for ad in getiri:
                        kayit[(gun, kol)][ad].append(getiri[ad])
                    if adf == "pin":
                        form_k.append(k)
                        # korelasyon icin: bu barin chg1 ve hacim carpani
                        kor["pin"].append(yon)
                        kor["chg"].append((p0 / float(b[k - 1]["c"]) - 1) * 100
                                          if float(b[k - 1]["c"]) else 0.0)
                        pen = [b[j] for j in range(k - 24, k) if j in b]
                        med = stx.median([float(x["qv"]) for x in pen]) if len(pen) >= 10 else 0
                        kor["volx"].append((float(b[k]["qv"]) / med) if med else 0)
            # KONTROL: ayni sembol-gunde, pin sayisi kadar RASTGELE bar
            if form_k and len(ks) > len(form_k):
                havuz = [k for k in ks if k not in set(form_k)]
                sec = rnd.sample(havuz, min(len(form_k), len(havuz)))
                for k in sec:
                    p0 = float(b[k]["c"])
                    if not p0:
                        continue
                    for ad, u, _ in UFUKLAR:
                        kayit[(gun, "kontrol")][ad].append(
                            (float(b[k + u]["c"]) / p0 - 1) * 100)

    gunler = sorted(set(g for g, _ in kayit))
    print("### 1) KAPSAM")
    print("   sembol: %d · olculebilir bar: %d · gun: %d (%s .. %s)"
          % (len(semboller), n_bar, len(gunler), gunler[0], gunler[-1]))
    print()

    def gun_ort(kol, ufuk):
        return dict((g, stx.mean(kayit[(g, kol)][ufuk]))
                    for g in gunler if kayit[(g, kol)][ufuk])

    def fark_serisi(kolA, kolB, ufuk):
        a, b_ = gun_ort(kolA, ufuk), gun_ort(kolB, ufuk)
        return dict((g, a[g] - b_[g]) for g in set(a) & set(b_))

    print("### 2) KOL ORTALAMALARI (%s)" % dict((a, c) for a, _, c in UFUKLAR)[BIRINCIL])
    print("   %-14s %9s %12s" % ("kol", "N", "ort getiri"))
    for kol in ("pin+1", "pin-1", "yutan+1", "yutan-1", "doji+0", "kontrol"):
        tum = [x for g in gunler for x in kayit[(g, kol)][BIRINCIL]]
        if tum:
            print("   %-14s %9d %+11.4f%%" % (kol, len(tum), stx.mean(tum)))
    print()

    # ---------------- F1 ----------------
    print("### F1 🔴 BIRINCIL — pin_BOGA - pin_AYI  (+4 saat)")
    fs = fark_serisi("pin+1", "pin-1", BIRINCIL)
    m1, t1, n1 = kume_t([fs[g] for g in sorted(fs)])
    print("   gun-eslesmis fark: %+.4f puan   t = %s   gun = %d"
          % (m1 if m1 is not None else 0, ("%.2f" % t1) if t1 else "yok", n1))
    print("   pozitif gun: %d/%d" % (sum(1 for v in fs.values() if v > 0), len(fs)))
    F1 = (m1 is not None and t1 is not None and m1 >= F1_ETKI and t1 >= F1_T)
    print("   esik: etki >= +%.2f VE t >= +%.1f" % (F1_ETKI, F1_T))
    print("   -> F1 %s" % ("GECTI" if F1 else "DUSTU"))
    if m1 is not None and abs(m1) < MDE:
        print("   📌 |etki| = %.3f < MDE %.3f  ->  'GOREMIYORUZ' bandi" % (abs(m1), MDE))
    print()

    # ---------------- SAGLAMA: ayna ----------------
    ters = fark_serisi("pin-1", "pin+1", BIRINCIL)
    mt, _, _ = kume_t([ters[g] for g in sorted(ters)])
    print("### SAGLAMA — yonler takas edilince isaret donmeli")
    print("   duz %+.4f · ters %+.4f -> %s"
          % (m1, mt, "✅ ayniyor" if abs(m1 + mt) < 1e-9 else "🔴 BETIK HATALI"))
    if abs(m1 + mt) >= 1e-9:
        return
    print()

    # ---------------- F2 ----------------
    print("### F2 — her yon KENDI kontrolunu geciyor mu?")
    fb = fark_serisi("pin+1", "kontrol", BIRINCIL)
    fa = fark_serisi("pin-1", "kontrol", BIRINCIL)
    mb, tb, nb = kume_t([fb[g] for g in sorted(fb)])
    ma, ta, na = kume_t([fa[g] for g in sorted(fa)])
    print("   pin_BOGA - kontrol : %+.4f  t %s  (pozitif olmali)"
          % (mb or 0, ("%.2f" % tb) if tb else "yok"))
    print("   pin_AYI  - kontrol : %+.4f  t %s  (negatif olmali)"
          % (ma or 0, ("%.2f" % ta) if ta else "yok"))
    F2 = (mb is not None and ma is not None and mb > 0 and ma < 0)
    print("   -> F2 %s" % ("GECTI" if F2 else "DUSTU"))
    print()

    # ---------------- F3 ----------------
    print("### F3 — ufuk tutarliligi")
    isr = []
    for ad, _, etiket in UFUKLAR:
        f = fark_serisi("pin+1", "pin-1", ad)
        mm, tt, nn = kume_t([f[g] for g in sorted(f)])
        isr.append(0 if mm is None else (1 if mm > 0 else -1))
        print("   %-10s fark %+.4f  t %s%s"
              % (etiket, mm or 0, ("%.2f" % tt) if tt else "yok",
                 "   <- BIRINCIL" if ad == BIRINCIL else ""))
    hedef = 1 if (m1 or 0) > 0 else -1
    a3 = sum(1 for x in isr if x == hedef)
    F3 = a3 >= 2
    print("   -> %d/3 ayni isaret -> F3 %s" % (a3, "GECTI" if F3 else "DUSTU"))
    print()

    # ---------------- F4 ----------------
    print("### F4 🔑 NEGATIF KONTROL — doji ONGORMEMELI")
    fd = fark_serisi("doji+0", "kontrol", BIRINCIL)
    md, td, nd = kume_t([fd[g] for g in sorted(fd)])
    F4 = (md is not None and abs(md) < MDE)
    print("   doji - kontrol: %+.4f puan  t %s  (|etki| < MDE %.3f olmali)"
          % (md or 0, ("%.2f" % td) if td else "yok", MDE))
    print("   -> F4 %s" % ("GECTI" if F4 else "DUSTU"))
    if not F4:
        print("   🔴 doji ONGORUYOR -> birincil bulgu da SUPHELI (yon degil baska sey)")
    print()

    # ---------------- F5 ----------------
    print("### F5 🔴 YOGUNLASMA — en iyi 2 gun cikarilinca")
    sirali = sorted(fs.items(), key=lambda x: -x[1])
    kalan = [v for _, v in sirali[2:]]
    m5, t5, n5 = kume_t(kalan)
    print("   en iyi 2 gun: %s" % ", ".join("%s %+.2f" % (g, v) for g, v in sirali[:2]))
    print("   cikarilinca: %+.4f puan  t %s  gun %d"
          % (m5 or 0, ("%.2f" % t5) if t5 else "yok", n5))
    F5 = (m5 is not None and m5 >= F1_ETKI)
    print("   -> F5 %s" % ("GECTI" if F5 else "DUSTU"))
    print()

    # ---------------- IKINCIL ----------------
    print("### IKINCIL (onceden ilan, GECTI'ye SAYILMAZ) — YUTAN")
    fy = fark_serisi("yutan+1", "yutan-1", BIRINCIL)
    my, ty, ny = kume_t([fy[g] for g in sorted(fy)])
    print("   yutan_BOGA - yutan_AYI (+4s): %+.4f  t %s  gun %d"
          % (my or 0, ("%.2f" % ty) if ty else "yok", ny))
    print()

    print("### EK RAPOR — 'baska adla ayni sey mi?'")
    if len(kor["pin"]) > 50:
        def kore(xs, ys):
            mx, my_ = stx.mean(xs), stx.mean(ys)
            pay = sum((a - mx) * (b_ - my_) for a, b_ in zip(xs, ys))
            px = math.sqrt(sum((a - mx) ** 2 for a in xs))
            py = math.sqrt(sum((b_ - my_) ** 2 for b_ in ys))
            return pay / (px * py) if px and py else None
        r1 = kore(kor["pin"], kor["chg"])
        r2 = kore(kor["pin"], kor["volx"])
        print("   r(pin yonu, bar getirisi) = %s   <- last1'in kiligi mi?"
              % (("%+.3f" % r1) if r1 else "yok"))
        print("   r(pin yonu, hacim carpani) = %s  <- vol_x'in kiligi mi?"
              % (("%+.3f" % r2) if r2 else "yok"))
    print()

    print("=" * 96)
    print("HUKUM — ON_KAYIT_formasyon.md bolum 6")
    print("=" * 96)
    for ad, ok in (("F1", F1), ("F2", F2), ("F3", F3), ("F4", F4), ("F5", F5)):
        print("   %s %s" % (ad, "GECTI" if ok else "DUSTU"))
    print()
    print("   SONUC: %s" % ("GECTI" if all((F1, F2, F3, F4, F5)) else "DUSTU"))
    print()
    print("   Coklu karsilastirma (on-kayitta ilan): 18 hucre")
    print("   ⚠️ Pencere TEK REJIM (14/14 BOGA) -> bulgu genellestirilemez.")
    print("   ⚠️ Etiket HAM getiri; maliyet %0,19 dahil DEGIL.")
    print()
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
