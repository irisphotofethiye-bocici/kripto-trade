#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIKET DONMESEYDI — NOTR'de kalsaydi ne olurdu? (2026-09-05)

ON-KAYIT: ON_KAYIT_etiket_karsiolgu.md, commit 8757c99 — KOSTURULMADAN ONCE.
Yapilabilirlik AYRICA dogrulandi: kayitli kararlarin %98,9'u yeniden uretildi.

UC KOL: A=GERCEK (rejim arsivden) · B=NOTR zorlanir · C=NOTR ama SHORT atilir.
karar_yon KAYNAKTAN cagrilir. Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sys, json, os, math, statistics as stx, collections, datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BURA = os.path.join(KOK, "scratchpad")
sys.path.insert(0, KOK)
sys.path.insert(0, BURA)
import testbot
import olcum_ortak as oo
import ileri_rr as ir

ARSIV = os.path.join(KOK, "testbot_aday_arsiv.jsonl")
BTCPAY = os.path.join(KOK, "btc_pay_log.jsonl")
ESKI_K, YENI_K = os.path.join(BURA, "klines_1h_uzun"), os.path.join(BURA, "taze_1h")
ESKI_F, YENI_F = os.path.join(BURA, "funding_gecmis"), os.path.join(BURA, "taze_funding")

BAS = "2026-08-21"
UFUK, HEDEF_PCT, ASGARI_STOP = 72, 10.0, 2.0
SLOT, COOLDOWN_SAAT = 8, 4
OFSET_SAAT = -3            # arsiv ts YEREL (UTC+3) -> UTC


def birlestir(a, b):
    d = {}
    for y in (a, b):
        if os.path.exists(y):
            try:
                for x in json.load(open(y, encoding="utf-8")):
                    d[int(x["t"])] = x
            except Exception:
                pass
    return [d[k] for k in sorted(d)] if d else None


def utc_ms(ts):
    d = dt.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
    return int((d + dt.timedelta(hours=OFSET_SAAT)).timestamp() * 1000)


def btc_pay_serisi():
    out = {}
    if os.path.exists(BTCPAY):
        for line in open(BTCPAY, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            ts = r.get("ts") or r.get("tarih") or ""
            if ts:
                out[ts[:10]] = r
    return out


def kararlar(kol, bp):
    """kol: 'A' | 'B' | 'C'  -> [(t_ms, sym, yon)] zaman sirali"""
    out = []
    for line in open(ARSIV, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        ts = r.get("ts") or ""
        if ts[:10] < BAS:
            continue
        rejim = r.get("rejim")
        if rejim in (None, "BILINMIYOR"):
            continue
        rj = rejim if kol == "A" else "NOTR"
        pillar = {"smart": r.get("smart"), "taker": r.get("taker"),
                  "top_ls": r.get("top_ls"), "glob_ls": r.get("glob_ls")}
        try:
            k = testbot.karar_yon(rj, r, pillar, bool(r.get("dusuk_float")),
                                  veto_out=None, para_cikis=False,
                                  btc_pay=bp.get(ts[:10]), para_durgun=False)
        except Exception:
            continue
        if not k:
            continue
        yon = k[0]
        if kol == "C" and yon == "SHORT":
            continue
        try:
            out.append((utc_ms(ts), r.get("sym"), yon))
        except Exception:
            continue
    out.sort()
    return out


def yol(b, gi, son, ref, stop, hedef, yon):
    sp = abs(stop - ref) / ref * 100
    hp = abs(hedef - ref) / ref * 100
    for j in range(gi, son):
        x = b[j]
        if yon == "SHORT":
            if x["h"] >= stop:
                return -sp, "STOP", j
            if x["l"] <= hedef:
                return hp, "HEDEF", j
        else:
            if x["l"] <= stop:
                return -sp, "STOP", j
            if x["h"] >= hedef:
                return hp, "HEDEF", j
    j = son - 1
    ham = ((ref - b[j]["c"]) if yon == "SHORT" else (b[j]["c"] - ref)) / ref * 100
    return ham, "SURE", j


def islem(b, atrs, si, ft, fr, yon):
    gi = si + 1
    if gi >= len(b) or si < 60 or not atrs[si] or atrs[si] <= 0:
        return None
    ref, a = b[gi]["o"], atrs[si]
    if ref <= 0:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    if yon == "SHORT":
        stop = ir.stop_hesapla(b, si, ref, a)
        hedef = ref * (1 - HEDEF_PCT / 100)
    else:
        # LONG icin aynalanmis A-stop (btcpay_rejim.py deseni)
        bas = max(3, si - 100)
        lo = []
        for j in range(bas, si - 2):
            w = b[j - 3:j + 4]
            if w and b[j]["l"] == min(x["l"] for x in w):
                lo.append(b[j]["l"])
        sup = max([x for x in lo if x < ref], default=None)
        ad = []
        if sup is not None and (ref - sup) <= 3 * a:
            ad.append(sup - 0.25 * a)
        nb = min(x["l"] for x in b[max(0, si - 9):si + 1])
        if nb < ref:
            ad.append(nb - 0.25 * a)
        ad.append(ref - 1.5 * a)
        gec = [s for s in ad if s < ref]
        stop = max(gec) if gec else ref - 1.5 * a
        hedef = ref * (1 + HEDEF_PCT / 100)
    sp = abs(stop - ref) / ref * 100
    if sp <= 0 or sp < ASGARI_STOP:
        return None
    ham, tip, j = yol(b, gi, son, ref, stop, hedef, yon)
    fon = ir.fonlama_pct(ft, fr, b[gi]["t"], b[j]["t"])
    fon = fon if yon == "SHORT" else -fon
    net = ham - oo.MALIYET + fon
    return {"net": net, "R": net / sp, "tip": tip, "sp": sp,
            "gir_ms": b[gi]["t"], "cik_ms": b[j]["t"], "saat": j - gi, "yon": yon}


def simule(kar, kl, fn, idx, atrs, ma_ft):
    """Slot kisitli simulasyon. -> [islem]"""
    acik = []          # (cik_ms, sym)
    son_giris = {}
    out = []
    for t, sym, yon in kar:
        acik = [x for x in acik if x[0] > t]
        if len(acik) >= SLOT:
            continue
        if any(x[1] == sym for x in acik):
            continue
        s0 = son_giris.get(sym)
        if s0 is not None and t - s0 < COOLDOWN_SAAT * 3600000:
            continue
        b = kl.get(sym)
        if not b:
            continue
        si = idx[sym].get((t // 3600000) * 3600000)
        if si is None:
            continue
        r = islem(b, atrs[sym], si, ma_ft[sym], fn.get(sym) or [], yon)
        if not r:
            continue
        son_giris[sym] = t
        acik.append((r["cik_ms"], sym))
        r["sym"] = sym
        r["gun"] = r["gir_ms"] // 86400000
        out.append(r)
    return out


def ozet(ad, ps, notional=1000.0):
    if not ps:
        print("  %-14s (islem yok)" % ad)
        return None
    net = [p["net"] for p in ps]
    usd = sum(p["net"] / 100 * notional for p in ps)
    g = collections.defaultdict(list)
    for p in ps:
        g[p["gun"]].append(p["net"])
    gv = [sum(v) / len(v) for v in g.values()]
    gm = sum(gv) / len(gv)
    yon = collections.Counter(p["yon"] for p in ps)
    print("  %-14s N=%-4d %-22s toplam %+9.2f $  islem-ort %+6.3f%%  gun-ort %+6.3f%%  gun=%d  kazanan %%%.1f"
          % (ad, len(ps), str(dict(yon)), usd, stx.mean(net), gm, len(gv),
             sum(1 for x in net if x > 0) / len(net) * 100))
    return {"ps": ps, "usd": usd, "gun": g, "gun_ort": gm}


def fark_t(a, b):
    """gun bazinda eslesmis olmayan iki kol -> iki-orneklemli gun-kumeli t"""
    ga = [sum(v) / len(v) for v in a["gun"].values()]
    gb = [sum(v) / len(v) for v in b["gun"].values()]
    if len(ga) < 3 or len(gb) < 3:
        return None, None
    ma, mb = sum(ga) / len(ga), sum(gb) / len(gb)
    se = math.sqrt(stx.variance(ga) / len(ga) + stx.variance(gb) / len(gb))
    return (ma - mb), ((ma - mb) / se if se else None)


def main():
    print("=" * 100)
    print("ETIKET DONMESEYDI — NOTR'de kalsaydi ne olurdu?")
    print("=" * 100)
    print("ON-KAYIT: ON_KAYIT_etiket_karsiolgu.md commit 8757c99 — KOSMADAN once")
    print("Yapilabilirlik: kayitli kararlarin %98,9'u yeniden uretildi (167 sapma,")
    print("  hepsi 'para_cikis' kaynakli LONG vetosu -> karsi-olgu LONG-YANLI).\n")

    bp = btc_pay_serisi()
    kl, fn, idx, atrs, ma_ft = {}, {}, {}, {}, {}
    for f in sorted(os.listdir(ESKI_K)):
        if not f.endswith(".json"):
            continue
        sym = f[:-5]
        b = birlestir(os.path.join(ESKI_K, f), os.path.join(YENI_K, f))
        if not b or len(b) < 300:
            continue
        kl[sym] = b
        fn[sym] = birlestir(os.path.join(ESKI_F, f), os.path.join(YENI_F, f)) or []
        idx[sym] = {x["t"]: i for i, x in enumerate(b)}
        atrs[sym] = ir.atr_serisi(b)
        ma_ft[sym] = [x["t"] for x in fn[sym]]
    print("fiyat serisi olan sembol: %d\n" % len(kl))

    sonuc = {}
    print("### KARARLAR ve SIMULASYON (notional $1.000 sabit, slot=%d)" % SLOT)
    for kol, ad in (("A", "A GERCEK"), ("B", "B NOTR"), ("C", "C NOTR-LONG")):
        kar = kararlar(kol, bp)
        yond = collections.Counter(y for _, _, y in kar)
        ps = simule(kar, kl, fn, idx, atrs, ma_ft)
        print("  %-12s karar=%-5d %-24s -> pozisyon=%d" % (ad, len(kar), str(dict(yond)), len(ps)))
        sonuc[kol] = ozet(ad, ps)
    print()

    if not (sonuc.get("A") and sonuc.get("B")):
        print("A ya da B olculemedi -> HUKUM YOK")
        return

    print("=" * 100)
    print("HUKUM — ON_KAYIT_etiket_karsiolgu.md bolum 6")
    print("=" * 100)
    A, B, C = sonuc["A"], sonuc["B"], sonuc.get("C")
    K1 = B["usd"] > A["usd"]
    print("K1  B toplam > A toplam : %+.2f $  vs  %+.2f $  -> %s"
          % (B["usd"], A["usd"], "GECTI" if K1 else "DUSTU"))
    f, t = fark_t(B, A)
    K2 = t is not None and abs(t) >= 2.0
    print("K2  gun-kumeli |t| >= 2,0 : fark %+.3f%%  t=%s -> %s"
          % (f if f is not None else 0, ("%.2f" % t) if t is not None else "yok",
             "GECTI" if K2 else "DUSTU"))
    # K3 iki yari
    tsler = sorted(p["gir_ms"] for p in A["ps"] + B["ps"])
    orta = tsler[len(tsler) // 2]
    isaret = []
    for ad, lo, hi in (("ilk yari", 0, orta), ("son yari", orta, 9e18)):
        a2 = sum(p["net"] / 100 * 1000 for p in A["ps"] if lo <= p["gir_ms"] < hi)
        b2 = sum(p["net"] / 100 * 1000 for p in B["ps"] if lo <= p["gir_ms"] < hi)
        isaret.append(b2 - a2)
        print("      %-9s A %+9.2f $  B %+9.2f $  fark %+9.2f $" % (ad, a2, b2, b2 - a2))
    K3 = len(isaret) == 2 and isaret[0] * isaret[1] > 0
    print("K3  iki yaride ayni isaret -> %s" % ("GECTI" if K3 else "DUSTU"))
    h = "GECTI" if (K1 and K2 and K3) else ("ZAYIF (K2 dustu)" if (K1 and K3) else "DUSTU")
    print("\nSONUC: %s" % h)

    print("\nK4 (AYRI RAPOR, OLCUT DEGIL) — C vs B:")
    if C:
        fc, tc = fark_t(C, B)
        print("      C %+.2f $  vs  B %+.2f $  fark %+.3f%%  t=%s"
              % (C["usd"], B["usd"], fc if fc is not None else 0,
                 ("%.2f" % tc) if tc is not None else "yok"))
    print("\n⚠️ SINIR: yol bagimliligi yaklasik · para_cikis yanliligi (+167 LONG) ·")
    print("   ONAY_BEKLE bir tur beklemeden alindi · kismi kar/likidasyon/fren YOK.")
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
