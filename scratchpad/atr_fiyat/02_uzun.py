#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ATR/FIYAT — 2 YILLIK MEKANIK BORU HATTINDA (IKINCI BAKIS)

ON_KAYIT_atr_2yil.md · commit 4474a75 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

🔴 BIRINCIL R · ZORUNLU IKIZ SINAMA: ham net% AYNI ISARETTE olmali (B5)
🔴 SPEARMAN YOK · t esigi 2,5 (ikinci bakisin bedeli)
Populasyon/faz/mekanik: stop_likidite/02_uzun.py ile BIREBIR.
SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, sys, math, random, collections, datetime as dt, statistics as stx
import importlib.util as il

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location(
    "ar", os.path.join(KOK, "scratchpad", "giris_arama", "01_arama.py"))
ar = il.module_from_spec(sp)
sp.loader.exec_module(ar)
import olcucu  # noqa: E402

KDIR = os.path.join(KOK, "scratchpad", "klines_1h_uzun")
SEYRELT = 24
DILIM = 5
T_ESIK = 2.5
KESIF_PAY = 0.60
random.seed(20260907)


def faz(sym):
    h = 0
    for c in sym:
        h = (h * 131 + ord(c)) & 0xFFFFFFFF
    return h % SEYRELT


def uret():
    """stop_likidite/02_uzun.py ile AYNI mekanik; ek alanlar: R, net%, hacim, logfiyat."""
    out = []
    yok = collections.Counter()
    dosyalar = sorted(x for x in os.listdir(KDIR) if x.endswith(".json"))
    for di, fn in enumerate(dosyalar, 1):
        sym = fn[:-5]
        try:
            d = json.load(open(os.path.join(KDIR, fn), encoding="utf-8"))
        except Exception:
            continue
        d.sort(key=lambda x: x["t"])
        n = len(d)
        if n < ar.YAPI_BAR + ar.ZAMAN_STOP + 40:
            continue
        for i0 in range(ar.YAPI_BAR + faz(sym), n - ar.ZAMAN_STOP - 1, SEYRELT):
            p = d[i0]["c"]
            if not p or p <= 0:
                continue
            bars = d[i0 - ar.YAPI_BAR:i0]
            stop = ar.stop_hesapla(bars, p)
            if stop is None:
                continue
            sf = (p - stop) / p * 100.0
            if sf < ar.ASGARI_STOP:
                yok["asgari_stop"] += 1
                continue
            atr = olcucu.atr(bars, period=14)
            if atr <= 0:
                continue
            hedef = p * 1.10
            net = None
            for j in range(i0 + 1, min(i0 + 1 + ar.ZAMAN_STOP, n)):
                b = d[j]
                if b["l"] <= stop:
                    net = (stop / p - 1) * 100.0 - ar.MALIYET
                    break
                if b["h"] >= hedef:
                    net = (hedef / p - 1) * 100.0 - ar.MALIYET
                    break
            if net is None:
                j = min(i0 + ar.ZAMAN_STOP, n - 1)
                net = (d[j]["c"] / p - 1) * 100.0 - ar.MALIYET
            hac = stx.mean([(b.get("qv") or 0.0) for b in bars[-24:]]) if bars else 0.0
            out.append({
                "gun": dt.datetime.fromtimestamp(d[i0]["t"] / 1000,
                                                 dt.timezone.utc).strftime("%Y-%m-%d"),
                "sym": sym, "atr_pct": atr / p * 100.0, "stop_pct": sf,
                "net": net, "R": net / sf,
                "logfiyat": math.log10(p) if p > 0 else 0.0,
                "loghacim": math.log10(hac) if hac > 0 else 0.0})
        if di % 120 == 0:
            print("   ... %d/%d sembol · %s giris" % (di, len(dosyalar), "{:,}".format(len(out))))
    return out, yok


def dil(rows, alan, k=DILIM):
    v = sorted(rows, key=lambda x: x[alan])
    n = len(v)
    return [v[i * n // k:(i + 1) * n // k] for i in range(k)]


def kume_fark(rows, ae, ue, metrik, anahtar):
    g = collections.defaultdict(lambda: ([], []))
    for x in rows:
        if x["atr_pct"] <= ae:
            g[x[anahtar]][0].append(x[metrik])
        elif x["atr_pct"] >= ue:
            g[x[anahtar]][1].append(x[metrik])
    v = [stx.mean(a) - stx.mean(b) for a, b in g.values()
         if len(a) >= 3 and len(b) >= 3]
    if len(v) < 5:
        return 0.0, 0.0, len(v)
    m = stx.mean(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, (m / se if se else 0.0), len(v)


def kars(rows, metrik="R"):
    p = dil(rows, "atr_pct")
    alt, ust = p[0], p[-1]
    ae, ue = alt[-1]["atr_pct"], ust[0]["atr_pct"]
    ra = [x[metrik] for x in alt]
    ru = [x[metrik] for x in ust]
    fark = stx.mean(ra) - stx.mean(ru)
    m, t, ng = kume_fark(rows, ae, ue, metrik, "gun")
    mde = 2.8 * math.sqrt(stx.variance(ra) / len(ra) + stx.variance(ru) / len(ru))
    return fark, t, mde, ng, stx.mean(ra), stx.mean(ru), ae, ue


def main():
    print("=" * 104)
    print("ATR/FIYAT — 2 YILLIK MEKANIK (IKINCI BAKIS) · ON_KAYIT 4474a75")
    print("🔴 birincil R · ZORUNLU ikiz sinama ham net%% · t esigi %.1f · Spearman YOK" % T_ESIK)
    print("=" * 104)
    rows, yok = uret()
    for k, v in yok.most_common(3):
        print("   elenen: %-18s %s" % (k, "{:,}".format(v)))
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%s · gun=%d · sembol=%d · KESIF %s · HOLDOUT %s"
          % ("{:,}".format(len(rows)), len(gunler), len(set(x["sym"] for x in rows)),
             "{:,}".format(len(kesif)), "{:,}".format(len(hold))))
    print()

    print("### 1) DILIM TABLOSU — HOLDOUT")
    print("   %-14s %8s %10s %11s %10s %10s %10s"
          % ("ATR% dilimi", "N", "ort ATR%", "ort R", "ham net%", "stop%", "log hacim"))
    for q in dil(hold, "atr_pct"):
        print("   %-14s %8s %9.2f%% %+11.4f %+9.3f%% %9.2f%% %10.2f"
              % ("%.2f-%.2f" % (q[0]["atr_pct"], q[-1]["atr_pct"]), "{:,}".format(len(q)),
                 stx.mean([x["atr_pct"] for x in q]), stx.mean([x["R"] for x in q]),
                 stx.mean([x["net"] for x in q]), stx.mean([x["stop_pct"] for x in q]),
                 stx.mean([x["loghacim"] for x in q])))
    print()

    print("### 2) 🔴 BIRINCIL — ort R (en dusuk ATR - en yuksek)")
    fh, th, mdeh, ngh, ah, uh, ae, ue = kars(hold, "R")
    fk = kars(kesif, "R")[0]
    print("   HOLDOUT dusuk %+.4f · yuksek %+.4f · fark %+.4f · gun-t %+.2f (%d gun) · MDE %.4f"
          % (ah, uh, fh, th, ngh, mdeh))
    print("   KESIF   fark %+.4f" % fk)
    print()

    print("### 3) 🔴 ZORUNLU IKIZ SINAMA — HAM net%% (B5)")
    gh = kars(hold, "net")
    gk = kars(kesif, "net")[0]
    print("   HOLDOUT dusuk %+.3f%% · yuksek %+.3f%% · fark %+.4f%% · t %+.2f"
          % (gh[4], gh[5], gh[0], gh[1]))
    print("   KESIF   fark %+.4f%%" % gk)
    B5 = (fh > 0) == (gh[0] > 0)
    print("   -> %s" % ("AYNI ISARET, artefakt belirtisi YOK" if B5
                        else "🔴 ISARETLER AYRISTI -> PAYDA ARTEFAKTI"))
    print()

    print("### 4) NEGATIF KONTROL (B6)")
    for lst in (kesif, hold):
        g = collections.defaultdict(list)
        for i, x in enumerate(lst):
            g[x["gun"]].append(i)
        for _, idx in g.items():
            v = [lst[i]["atr_pct"] for i in idx]
            random.shuffle(v)
            for i, val in zip(idx, v):
                lst[i]["_g"] = lst[i]["atr_pct"]
                lst[i]["atr_pct"] = val
    ns = kars(hold, "R")
    neg = (ns[0] > 0 and ns[1] >= T_ESIK)
    print("   SAHTE fark %+.4f · t %+.2f -> %s"
          % (ns[0], ns[1], "🔴 SAHTE DE ETKI URETTI" if neg else "temiz"))
    for lst in (kesif, hold):
        for x in lst:
            x["atr_pct"] = x.pop("_g", x["atr_pct"])
    print()

    print("### 5) SEMBOL KUMELEMESI (B7)")
    ms, ts, nsy = kume_fark(hold, ae, ue, "R", "sym")
    print("   sembol-kumeli fark %+.4f · t %+.2f (%d sembol)" % (ms, ts, nsy))
    print()

    print("### 6) 🔴 TERS KARISTIRICI — ATR baska bir seyin vekili mi (EK RAPOR)")
    print("   %-14s %10s %10s %10s" % ("ATR% dilimi", "log fiyat", "log hacim", "stop%"))
    for q in dil(hold, "atr_pct"):
        print("   %-14s %10.2f %10.2f %9.2f%%"
              % ("%.2f-%.2f" % (q[0]["atr_pct"], q[-1]["atr_pct"]),
                 stx.mean([x["logfiyat"] for x in q]),
                 stx.mean([x["loghacim"] for x in q]),
                 stx.mean([x["stop_pct"] for x in q])))
    print()

    B = {
        "B1 holdout R farki > 0": fh > 0,
        "B2 gun-kumeli t >= 2,5": th >= T_ESIK,
        "B3 |fark| > MDE": abs(fh) > mdeh,
        "B4 kesif+holdout ayni isaret": (fk > 0) == (fh > 0),
        "B5 ham net% AYNI ISARET": B5,
        "B6 negatif kontrol temiz": not neg,
        "B7 sembol-kumeli t >= 2,5": ts >= T_ESIK,
    }
    print("=" * 104)
    print("HUKUM — ON_KAYIT bolum 5")
    print("=" * 104)
    for k, v in B.items():
        print("   %-34s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if all(B.values()):
        print("   🔑 YON VAR — sakin coin, risk birimi basina daha cok kazandiriyor.")
        print("   🔴 SIRADA: tasinabilirlik (botun evreninde). Kod OTOMATIK degismez.")
    elif not B5:
        print("   🔴 PAYDA ARTEFAKTI — R gecse bile kural YAZILMAZ.")
    elif not (B["B1 holdout R farki > 0"] and B["B4 kesif+holdout ayni isaret"]):
        print("   YON YOK.")
    elif not B["B7 sembol-kumeli t >= 2,5"]:
        print("   SEMBOLE OZGU olabilir.")
    else:
        print("   GOREMIYORUZ — isaret var, esik asilmadi.")
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
