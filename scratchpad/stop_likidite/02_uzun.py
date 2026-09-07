#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STOP LIKIDITE KUMESI — 2 YILLIK VERIDE (UCUNCU BAKIS)

ON_KAYIT_stop_likidite_2yil.md · commit 5a66803 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 t esigi 2,5 (ucuncu bakisin bedeli) · EKONOMIK TABAN 3,0 puan
🔴 FAZ KAYDIRILIR (hash(sembol) mod 24)
🔴 Populasyon MEKANIK — skor YOK, botun evreni DEGIL.
Yontem 01_olcum.py ile BIREBIR; yalniz giris uretimi degisti.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, math, random, collections, statistics as stx
import importlib.util as il

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)
sp2 = il.spec_from_file_location("o1", os.path.join(BURA, "01_olcum.py"))
o1 = il.module_from_spec(sp2)
sp2.loader.exec_module(o1)          # harita_kur · yogunluk_p · dilimle · gun_t · kars · katmanli
import olcucu  # noqa: E402

KDIR = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
SEYRELT = 24
PENCERE = 24
T_ESIK = 2.5          # on-kayit bolum 1 — UCUNCU BAKISIN BEDELI
TABAN_PUAN = 0.030    # on-kayit bolum 6 — EKONOMIK TABAN
KESIF_PAY = 0.60
random.seed(20260907)


def faz(sym):
    """CLAUDE.md: SEYRELT=24 FAZ KILITLER -> sembole gore kaydir."""
    h = 0
    for c in sym:
        h = (h * 131 + ord(c)) & 0xFFFFFFFF
    return h % SEYRELT


def uret():
    """Mekanik girisler: her sembolde gunde bir ornek, faz kaydirmali."""
    out = []
    yok = collections.Counter()
    dosyalar = sorted(x for x in os.listdir(KDIR) if x.endswith(".json"))
    for di, fn in enumerate(dosyalar, 1):
        sym = fn[:-5]
        try:
            d = json.load(open(os.path.join(KDIR, fn), encoding="utf-8"))
        except Exception:
            yok["dosya okunamadi"] += 1
            continue
        d.sort(key=lambda x: x["t"])
        n = len(d)
        if n < ar.YAPI_BAR + PENCERE + ar.ZAMAN_STOP + 30:
            yok["seri kisa"] += 1
            continue
        bas = max(ar.YAPI_BAR, PENCERE) + faz(sym)
        for i0 in range(bas, n - ar.ZAMAN_STOP - 1, SEYRELT):
            p = d[i0]["c"]
            if not p or p <= 0:
                continue
            bars = d[i0 - ar.YAPI_BAR:i0]
            stop = ar.stop_hesapla(bars, p)
            if stop is None:
                continue
            sf = (p - stop) / p * 100.0
            if sf < ar.ASGARI_STOP:
                yok["asgari_stop kapisi"] += 1
                continue
            atr = olcucu.atr(bars, period=14)
            if atr <= 0:
                continue
            pen = d[i0 - PENCERE:i0]
            if not any((b.get("tbv") or 0) > 0 for b in pen):
                yok["tbv eksik"] += 1
                continue
            kv = o1.harita_kur(pen, p)
            spv = o1.yogunluk_p(kv, stop, p)
            if spv is None:
                continue
            hedef = p * 1.10
            sonuc = None
            for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, n)):
                b = d[j]
                if b["l"] <= stop:
                    sonuc = "STOP"
                    break
                if b["h"] >= hedef:
                    sonuc = "HEDEF"
                    break
            if sonuc is None:
                sonuc = "ZAMAN"
            j24 = i0 + 24
            if j24 >= n:
                continue
            gun = __import__("datetime").datetime.fromtimestamp(
                d[i0]["t"] / 1000, __import__("datetime").timezone.utc).strftime("%Y-%m-%d")
            out.append({"gun": gun, "sym": sym, "stop_p": spv,
                        "stop_atr": (p - stop) / atr, "stop_pct": sf,
                        "atr_pct": atr / p * 100.0,
                        "ham": (d[j24]["c"] / p - 1) * 100.0,
                        "sonuc": sonuc,
                        "stop_oldu": 1 if sonuc == "STOP" else 0,
                        "hedef_oldu": 1 if sonuc == "HEDEF" else 0})
        if di % 80 == 0:
            print("   ... %d/%d sembol · %s giris" % (di, len(dosyalar), "{:,}".format(len(out))))
    return out, yok


def main():
    print("=" * 106)
    print("STOP LIKIDITE — 2 YILLIK VERI (UCUNCU BAKIS) · ON_KAYIT 5a66803")
    print("t esigi %.1f · ekonomik taban %.1f puan · faz KAYDIRILDI" % (T_ESIK, TABAN_PUAN * 100))
    print("🔴 populasyon MEKANIK (skor YOK) — botun evreni DEGIL")
    print("=" * 106)
    rows, yok = uret()
    for k, v in yok.most_common(4):
        print("   elenen: %-24s %s" % (k, "{:,}".format(v)))
    gunler = sorted(set(x["gun"] for x in rows))
    print("N=%s · gun=%d · sembol=%d" % ("{:,}".format(len(rows)), len(gunler),
                                         len(set(x["sym"] for x in rows))))
    if len(rows) < 1000 or len(gunler) < 20:
        print("🔴 yetersiz -> DURDU")
        return
    ks = gunler[int(len(gunler) * KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("KESIF %s (%s..%s) · HOLDOUT %s (%s..)"
          % ("{:,}".format(len(kesif)), gunler[0], ks, "{:,}".format(len(hold)), ks))
    print()

    print("### 1) DILIM TABLOSU — HOLDOUT")
    print("   %-14s %8s %9s %9s %9s %11s %9s"
          % ("stop_p", "N", "STOP%", "HEDEF%", "ham+24s", "stop ATR", "stop%"))
    for q in o1.dilimle(hold, "stop_p"):
        if len(q) < 50:
            continue
        print("   %-14s %8s %8.1f%% %8.1f%% %+8.3f%% %10.2f %8.2f%%"
              % ("%.2f-%.2f" % (q[0]["stop_p"], q[-1]["stop_p"]), "{:,}".format(len(q)),
                 100.0 * sum(x["stop_oldu"] for x in q) / len(q),
                 100.0 * sum(x["hedef_oldu"] for x in q) / len(q),
                 stx.mean([x["ham"] for x in q]),
                 stx.mean([x["stop_atr"] for x in q]),
                 stx.mean([x["stop_pct"] for x in q])))
    print()

    kh, kk = o1.kars(hold), o1.kars(kesif)
    if kh is None or kk is None:
        print("dilim doldurulamadi -> DURDU")
        return
    fh, th, mdeh, ngh, ki, bo, nk, nb = kh
    print("### 2) HAM (katmansiz)")
    print("   HOLDOUT kume ici %.2f%% (N=%s) · bos %.2f%% (N=%s)"
          % (ki * 100, "{:,}".format(nk), bo * 100, "{:,}".format(nb)))
    print("           fark %+.4f (%.2f puan) · gun-t %+.2f (%d gun) · MDE %.4f (%.2f puan)"
          % (fh, fh * 100, th, ngh, mdeh, mdeh * 100))
    print("   KESIF   fark %+.4f (%.2f puan · t %+.2f)" % (kk[0], kk[0] * 100, kk[1]))
    print()

    print("### 3) 🔴 KATMANLI (ATR karistiricisi sabit) — U5")
    kat, nkat = o1.katmanli(hold)
    if kat is None:
        print("   katman yetersiz -> U5 DUSTU")
        kat, U5 = 0.0, False
    else:
        oran = (kat / fh) if fh else 0.0
        print("   HAM %+.4f (%.2f puan) · KATMANLI %+.4f (%.2f puan) · koruma %.0f%%"
              % (fh, fh * 100, kat, kat * 100, oran * 100))
        U5 = (oran >= o1.KORUMA)
        print("   -> %s" % ("KORUDU" if U5 else "🔴 STOP MESAFESININ KILIGI"))
    print()

    print("### 4) NEGATIF KONTROL — U6")
    for lst in (kesif, hold):
        g = collections.defaultdict(list)
        for i, x in enumerate(lst):
            g[x["gun"]].append(i)
        for _, idx in g.items():
            v = [lst[i]["stop_p"] for i in idx]
            random.shuffle(v)
            for i, val in zip(idx, v):
                lst[i]["_g"] = lst[i]["stop_p"]
                lst[i]["stop_p"] = val
    ks_ = o1.kars(hold)
    neg = bool(ks_ and ks_[0] > 0 and ks_[1] >= T_ESIK)
    if ks_:
        print("   SAHTE fark %+.4f (%.2f puan) · t %+.2f -> %s"
              % (ks_[0], ks_[0] * 100, ks_[1], "🔴 SAHTE DE ETKI URETTI" if neg else "temiz"))
    for lst in (kesif, hold):
        for x in lst:
            x["stop_p"] = x.pop("_g", x["stop_p"])
    print()

    U = {
        "U1 katmanli fark > 0": kat > 0,
        "U2 gun-kumeli t >= 2,5": th >= T_ESIK,
        "U3 |fark| > MDE": abs(fh) > mdeh,
        "U4 kesif+holdout ayni isaret": (kk[0] > 0) == (fh > 0),
        "U5 katmanli >= hamin %50si": U5,
        "U6 negatif kontrol temiz": not neg,
        "U7 katmanli >= 3,0 PUAN (ekonomik)": kat >= TABAN_PUAN,
    }
    print("=" * 106)
    print("HUKUM — ON_KAYIT bolum 7")
    print("=" * 106)
    for k, v in U.items():
        print("   %-38s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if all(U.values()):
        print("   🔑 KURAL YAZILABILIR — kumedeki stop belirgin daha cok yeniyor.")
        print("   🔴 GIRIS KAPISI DEGIL, STOP YERLESTIRME. Kod OTOMATIK degismez.")
    elif all(U[k] for k in U if not k.startswith("U7")):
        print("   GORULUR AMA ISE YARAMAZ — %.2f puan < %.1f puan ekonomik taban."
              % (kat * 100, TABAN_PUAN * 100))
        print("   Kural YAZILMAZ (on-kayit bolum 6, sonuc gorulmeden ilan edildi).")
    elif not (U["U1 katmanli fark > 0"] and U["U4 kesif+holdout ayni isaret"]):
        print("   YON YOK.")
    elif not U5:
        print("   🔴 STOP MESAFESININ KILIGI.")
    else:
        print("   HALA GUC YETERSIZ.")
    print()
    print("🔴 ON_KAYIT bolum 1: DORDUNCU BAKIS YOK. Bu hipotez KAPANDI.")
    print("Salt-okuma. Bot dosyalarina yazim: YOK · ucretli cagri: YOK")


if __name__ == "__main__":
    main()
