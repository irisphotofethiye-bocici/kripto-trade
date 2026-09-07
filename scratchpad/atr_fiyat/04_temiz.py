#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ATR/FIYAT — SECIM YANLILIGI GIDERILMIS (DUZELTME KOSUMU)

ON_KAYIT_atr_temiz.md · commit 55ca5a9 — KOSMADAN ONCE yazildi.
Olcutler orada sabit; burada YENIDEN TANIMLANMAZ, yalniz uygulanir.

DUZELTME: stop = 1,5xATR (asgari_stop kapisi YOK) · hedef = 4,5xATR
          -> R:R = 3,0 HER HUCREDE AYNI, payda artefakti YAPISAL OLARAK IMKANSIZ
🔴 C0 ZORUNLU SINAMA: stop/ATR ve R:R sapmasi %1'i asarsa BETIK DURUR.
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
STOP_K = 1.5          # on-kayit bolum 2 — ARANMADI
HEDEF_K = 4.5         # R:R = 3,0
ATR_TAVAN = 20.0      # on-kayit bolum 4 — bozuk mum budamasi
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
    out = []
    say = collections.Counter()
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
            atr = olcucu.atr(bars, period=14)
            if atr <= 0:
                continue
            atr_pct = atr / p * 100.0
            say["aday"] += 1
            if atr_pct > ATR_TAVAN:
                say["ATR>%20 budandi"] += 1
                continue
            # 🔴 asgari_stop KAPISI YOK — duzeltmenin ozu
            stop = p - STOP_K * atr
            hedef = p + HEDEF_K * atr
            if stop <= 0:
                say["stop<=0"] += 1
                continue
            sf = (p - stop) / p * 100.0
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
            out.append({
                "gun": dt.datetime.fromtimestamp(d[i0]["t"] / 1000,
                                                 dt.timezone.utc).strftime("%Y-%m-%d"),
                "sym": sym, "atr_pct": atr_pct, "stop_pct": sf,
                "stop_atr": sf / atr_pct, "rr": (hedef - p) / (p - stop),
                "net": net, "R": net / sf})
        if di % 150 == 0:
            print("   ... %d/%d sembol · %s giris" % (di, len(dosyalar), "{:,}".format(len(out))))
    return out, say


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
    _, t, ng = kume_fark(rows, ae, ue, metrik, "gun")
    mde = 2.8 * math.sqrt(stx.variance(ra) / len(ra) + stx.variance(ru) / len(ru))
    return fark, t, mde, ng, stx.mean(ra), stx.mean(ru), ae, ue


def main():
    print("=" * 104)
    print("ATR/FIYAT — SECIM YANLILIGI GIDERILMIS · ON_KAYIT 55ca5a9")
    print("stop %.1fxATR (kapi YOK) · hedef %.1fxATR (R:R 3,0) · ATR tavani %%%.0f"
          % (STOP_K, HEDEF_K, ATR_TAVAN))
    print("=" * 104)
    rows, say = uret()
    print("   aday %s · ATR>%%20 budandi %s (%%%.3f)"
          % ("{:,}".format(say["aday"]), "{:,}".format(say["ATR>%20 budandi"]),
             100.0 * say["ATR>%20 budandi"] / max(1, say["aday"])))
    gunler = sorted(set(x["gun"] for x in rows))
    ks = gunler[int(len(gunler) * KESIF_PAY)]
    kesif = [x for x in rows if x["gun"] < ks]
    hold = [x for x in rows if x["gun"] >= ks]
    print("N=%s · gun=%d · sembol=%d · KESIF %s · HOLDOUT %s"
          % ("{:,}".format(len(rows)), len(gunler), len(set(x["sym"] for x in rows)),
             "{:,}".format(len(kesif)), "{:,}".format(len(hold))))
    print()

    print("### 0) 🔴 C0 YAPISAL SINAMA — stop/ATR ve R:R SABIT mi?")
    sa = [stx.mean([x["stop_atr"] for x in q]) for q in dil(hold, "atr_pct")]
    rr = [stx.mean([x["rr"] for x in q]) for q in dil(hold, "atr_pct")]
    print("   stop/ATR dilimler: %s" % " · ".join("%.4f" % v for v in sa))
    print("   R:R      dilimler: %s" % " · ".join("%.4f" % v for v in rr))
    sap_s = (max(sa) - min(sa)) / stx.mean(sa) * 100
    sap_r = (max(rr) - min(rr)) / stx.mean(rr) * 100
    print("   sapma: stop/ATR %%%.4f · R:R %%%.4f  (esik %%1)" % (sap_s, sap_r))
    if sap_s > 1.0 or sap_r > 1.0:
        print("   🔴 C0 DUSTU -> BETIK CALISMAYI REDDEDIYOR")
        return
    print("   -> C0 GECTI, geometri her hucrede AYNI")
    print()

    print("### 1) DILIM TABLOSU — HOLDOUT")
    print("   %-16s %9s %10s %11s %11s %10s"
          % ("ATR% dilimi", "N", "ort ATR%", "ort R", "ham net%", "stop%"))
    for q in dil(hold, "atr_pct"):
        print("   %-16s %9s %9.2f%% %+11.4f %+10.3f%% %9.2f%%"
              % ("%.2f-%.2f" % (q[0]["atr_pct"], q[-1]["atr_pct"]), "{:,}".format(len(q)),
                 stx.mean([x["atr_pct"] for x in q]), stx.mean([x["R"] for x in q]),
                 stx.mean([x["net"] for x in q]), stx.mean([x["stop_pct"] for x in q])))
    print()

    print("### 2) 🔴 BIRINCIL — ort R (en dusuk ATR - en yuksek)")
    fh, th, mdeh, ngh, ah, uh, ae, ue = kars(hold, "R")
    fk = kars(kesif, "R")[0]
    print("   HOLDOUT dusuk %+.4f · yuksek %+.4f · fark %+.4f · gun-t %+.2f (%d gun) · MDE %.4f"
          % (ah, uh, fh, th, ngh, mdeh))
    print("   KESIF   fark %+.4f" % fk)
    print()

    print("### 3) IKINCIL — ham net%% (BETIMLEYICI, olcut DEGIL)")
    gh = kars(hold, "net")
    print("   HOLDOUT dusuk %+.3f%% · yuksek %+.3f%% · fark %+.4f%%" % (gh[4], gh[5], gh[0]))
    print("   (geometri sabitken dusuk-ATR TANIM GEREGI az yuzde hareket eder;")
    print("    ayrisma ARTEFAKT DEGIL — on-kayit bolum 3)")
    print()

    print("### 4) NEGATIF KONTROL (C5)")
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
    neg = abs(ns[1]) >= T_ESIK
    print("   SAHTE fark %+.4f · t %+.2f -> %s"
          % (ns[0], ns[1], "🔴 SAHTE DE ETKI URETTI" if neg else "temiz"))
    for lst in (kesif, hold):
        for x in lst:
            x["atr_pct"] = x.pop("_g", x["atr_pct"])
    print()

    print("### 5) SEMBOL KUMELEMESI (C6)")
    ms, ts, nsy = kume_fark(hold, ae, ue, "R", "sym")
    print("   sembol-kumeli fark %+.4f · t %+.2f (%d sembol)" % (ms, ts, nsy))
    print()

    C = {
        "C1 holdout R farki > 0": fh > 0,
        "C2 gun-kumeli t >= 2,5": th >= T_ESIK,
        "C3 |fark| > MDE": abs(fh) > mdeh,
        "C4 kesif+holdout ayni isaret": (fk > 0) == (fh > 0),
        "C5 negatif kontrol temiz": not neg,
        "C6 sembol-kumeli t >= 2,5": abs(ts) >= T_ESIK,
    }
    print("=" * 104)
    print("HUKUM — ON_KAYIT bolum 5")
    print("=" * 104)
    for k, v in C.items():
        print("   %-34s %s" % (k, "GECTI" if v else "DUSTU"))
    print()
    if all(C.values()):
        print("   🔑 YON VAR — SAKIN coin, risk birimi basina daha cok kazandiriyor.")
        print("   🔴 SIRADA: tasinabilirlik (botun evreninde). Kod OTOMATIK degismez.")
    elif (not C["C1 holdout R farki > 0"]) and abs(th) >= T_ESIK and C["C4 kesif+holdout ayni isaret"]:
        print("   🔴 TERS YON — OYNAK coin daha iyi. Bu bir BULGUDUR, 'dustu' degil.")
    elif not (C["C1 holdout R farki > 0"] or C["C4 kesif+holdout ayni isaret"]):
        print("   YON YOK.")
    else:
        print("   GOREMIYORUZ — isaret var, esik asilmadi.")
    print()
    print("🔴 Mekanik evrendeki SON ATR/fiyat olcumu (on-kayit bolum 7).")
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
