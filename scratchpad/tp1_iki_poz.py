#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TP1 EKLENSEYDI, STOP OLAN IKI POZ NE OLURDU? (ARX id=1 · TAO id=4)

Kullanici sorusu: "tp1 i ekleseydik stop olan 2 poz ne olurdu"

SALT-OKUNUR. Bot dosyalarina yazim YOK. State/defter DEGISTIRILMEZ.
N=2 -> bu bir TESHIS, kural cikarilmaz.

ZORUNLU SINAMA: yeniden kurulan 1m yol, defterdeki GERCEK sonucu
(stop fiyati + kapanis anI + sonuc_usdt) yeniden uretmiyorsa
betik CALISMAYI REDDEDER.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, datetime as dt
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

CFG = json.load(io.open(os.path.join(KOK, "kripto-config.json"), encoding="utf-8"))
MAL = CFG.get("maliyet", {})
TAKER = float(MAL.get("taker_fee_pct", 0.045)) / 100.0
SLIP = float(MAL.get("slippage_pct", 0.02)) / 100.0
KISMI_KAR_R = float(CFG.get("esikler", {}).get("kismi_kar_r", 1.5))

TZ_KAY = 3          # defter damgasi YEREL (UTC+3) — testbot.now_dt() = datetime.now()
API = "https://fapi.binance.com/fapi/v1/klines"
_MUM = {}


def klines(sym, bas_ms, bit_ms):
    """1m mumlar, [bas, bit] araligi. -> [{t,o,h,l,c}]"""
    out, cur = [], bas_ms
    while cur < bit_ms:
        u = "%s?symbol=%s&interval=1m&startTime=%d&endTime=%d&limit=1000" % (
            API, sym, cur, bit_ms)
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
        if not d:
            break
        for k in d:
            out.append({"t": int(k[0]), "o": float(k[1]), "h": float(k[2]),
                        "l": float(k[3]), "c": float(k[4])})
        if len(d) < 1000:
            break
        cur = int(d[-1][0]) + 60_000
    return out


def yerel_ms(s):
    """'YYYY-mm-dd HH:MM:SS' YEREL -> epoch ms (UTC)."""
    t = dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return int((t - dt.timedelta(hours=TZ_KAY)).replace(
        tzinfo=dt.timezone.utc).timestamp() * 1000)


def kapanis_pnl(giris, fiyat_piyasa, miktar):
    """testbot.pozisyon_kapat ile AYNI aritmetik (LONG)."""
    cikis_ef = fiyat_piyasa * (1 - SLIP)
    pnl_ham = (cikis_ef - giris) * miktar
    ucret = miktar * cikis_ef * TAKER
    return pnl_ham - ucret, cikis_ef


def simule(bars, giris, stop, tp1, miktar, babas):
    """-> (toplam_pnl, olaylar). babas=True ise TP1 sonrasi stop girise cekilir.

    Ayni mumda hem TP1 hem stop varsa STOP once sayilir (KOTUMSER).
    """
    yari = miktar / 2.0
    kalan = miktar
    st_ak = stop
    top = 0.0
    olay = []
    ayni_bar = 0
    for b in bars:
        if b["l"] <= st_ak:
            p, ce = kapanis_pnl(giris, st_ak, kalan)
            if b["h"] >= tp1 and kalan == miktar:
                ayni_bar += 1
            top += p
            olay.append(("STOP", b["t"], st_ak, kalan, p))
            return top, olay, ayni_bar
        if kalan == miktar and b["h"] >= tp1:
            p, ce = kapanis_pnl(giris, tp1, yari)
            top += p
            kalan -= yari
            olay.append(("TP1", b["t"], tp1, yari, p))
            if babas:
                st_ak = giris
    # ufuk icinde kapanmadi -> son kapanis
    p, ce = kapanis_pnl(giris, bars[-1]["c"], kalan)
    top += p
    olay.append(("ACIK_SON", bars[-1]["t"], bars[-1]["c"], kalan, p))
    return top, olay, ayni_bar


def ms_str(ms):
    return (dt.datetime.utcfromtimestamp(ms / 1000) +
            dt.timedelta(hours=TZ_KAY)).strftime("%m-%d %H:%M")


def main():
    print("=" * 100)
    print("TP1 EKLENSEYDI — STOP OLAN IKI POZ (ARX id=1 · TAO id=4)")
    print("kismi_kar_r = %.1f · taker %%%.3f · slipaj %%%.3f" %
          (KISMI_KAR_R, TAKER * 100, SLIP * 100))
    print("=" * 100)

    kayit = []
    for l in io.open(os.path.join(KOK, "notrlong_islemler.jsonl"), encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        if r.get("sebep") == "STOP" and not r.get("kismi"):
            kayit.append(r)
    print("STOP kaydi: %d\n" % len(kayit))

    ozet = []
    for r in kayit:
        sym = r["sym"] + "USDT"
        giris = r["giris"]
        cikis_ef = r["cikis"]
        stop = cikis_ef / (1 - SLIP)                 # etkin cikistan HAM stopu geri cevir
        risk = giris - stop
        miktar = r["notional"] / giris
        tp1 = giris + KISMI_KAR_R * risk             # yapisal TP1 ancak DAHA YAKIN olabilir

        kapanis_ms = yerel_ms(r["ts"])
        giris_ms = kapanis_ms - int(r["tutma_saat"] * 3600 * 1000)
        bars = klines(sym, giris_ms - 3 * 60_000, kapanis_ms + 3 * 60_000)
        # giris barindan itibaren
        bars = [b for b in bars if b["t"] >= giris_ms - 60_000]
        if not bars:
            print("  %-5s MUM YOK -> atlanir" % r["sym"])
            continue
        _MUM[r["sym"]] = bars

        print("--- %s (id=%d) ---" % (r["sym"], r["id"]))
        print("   giris %.6f · stop %.6f (%.2f%%) · %dx · notional %.2f"
              % (giris, stop, risk / giris * 100, r["kaldirac"], r["notional"]))
        print("   TP1(1,5R) %.6f  (+%.2f%%)   tutma %.1f sa · %d mum"
              % (tp1, (tp1 / giris - 1) * 100, r["tutma_saat"], len(bars)))

        # --- ZORUNLU SINAMA: gercek sonucu yeniden uretiyor muyuz?
        p_ger, _ = kapanis_pnl(giris, stop, miktar)
        sapma = abs(p_ger - r["sonuc_usdt"])
        stop_var = any(b["l"] <= stop for b in bars)
        print("   SINAMA: yeniden uretilen stop P&L %+.2f vs defter %+.2f (sapma %.2f) · "
              "yolda stop %s" % (p_ger, r["sonuc_usdt"], sapma,
                                 "VAR" if stop_var else "YOK"))
        if sapma > 1.0 or not stop_var:
            print("   🔴 SINAMA DUSTU -> bu poz icin hukum YAZILMAZ\n")
            continue

        # --- MFE: fiyat en fazla kac R lehimize gitti?
        en_yuksek = max(b["h"] for b in bars)
        mfe_r = (en_yuksek - giris) / risk
        t_yuksek = [b["t"] for b in bars if b["h"] == en_yuksek][0]
        print("   MFE  : en yuksek %.6f (%+.2f%%) = %+.2f R  ·  %s"
              % (en_yuksek, (en_yuksek / giris - 1) * 100, mfe_r, ms_str(t_yuksek)))

        a, oa, ab1 = simule(bars, giris, stop, tp1, miktar, babas=False)
        b_, ob, ab2 = simule(bars, giris, stop, tp1, miktar, babas=True)
        print("   GERCEK (TP1 yok)          : %+8.2f $" % r["sonuc_usdt"])
        print("   (a) TP1 var, stop AYNI    : %+8.2f $   fark %+.2f" % (a, a - r["sonuc_usdt"]))
        print("   (b) TP1 var, stop BASABAS : %+8.2f $   fark %+.2f" % (b_, b_ - r["sonuc_usdt"]))
        for et, ms, fy, mk, pn in oa:
            print("        (a) %-9s %s  fiyat %.6f  miktar %.1f  %+8.2f $"
                  % (et, ms_str(ms), fy, mk, pn))
        if ob != oa:
            for et, ms, fy, mk, pn in ob:
                print("        (b) %-9s %s  fiyat %.6f  miktar %.1f  %+8.2f $"
                      % (et, ms_str(ms), fy, mk, pn))
        if ab1 or ab2:
            print("        ⚠ ayni mumda hem TP1 hem stop: %d (STOP once sayildi)" % max(ab1, ab2))
        print()
        ozet.append((r["sym"], r["sonuc_usdt"], a, b_, mfe_r, tp1, en_yuksek))

    if not ozet:
        print("Hukum yazilabilecek poz YOK.")
        return
    print("=" * 100)
    print("OZET")
    print("=" * 100)
    print("   %-6s %10s %12s %12s %8s" % ("sym", "GERCEK", "(a) stop ayni", "(b) basabas", "MFE R"))
    for s, g, a, b_, m, _t, _h in ozet:
        print("   %-6s %+10.2f %+12.2f %+12.2f %8.2f" % (s, g, a, b_, m))
    tg = sum(x[1] for x in ozet)
    ta = sum(x[2] for x in ozet)
    tb = sum(x[3] for x in ozet)
    print("   %-6s %+10.2f %+12.2f %+12.2f" % ("TOPLAM", tg, ta, tb))
    print()
    print("   (a) fark: %+.2f $   (b) fark: %+.2f $" % (ta - tg, tb - tg))
    print()

    print("=" * 100)
    print("EK — TP1 MERDIVENI (bilgi icin; ESIK ARAMASI DEGIL)")
    print("=" * 100)
    print("🔴 N=2. Asagidan 'en iyi R' secmek bu projede REDDEDILMIS davranistir")
    print("   (CLAUDE.md: 'En iyi hucre secilmez'). Merdiven yalniz TP1'in NEREDE")
    print("   olmasi gerektigini gosterir — kural degil.")
    print()
    header = "   %-8s" % "TP1(R)"
    for s, _g, _a, _b, _m, _t, _h in ozet:
        header += " %20s" % (s + " (a)/(b)")
    print(header + " %12s" % "TOPLAM (a)")
    for m in (0.25, 0.50, 0.75, 1.00, 1.25, 1.50):
        sat = "   %-8.2f" % m
        top_a = 0.0
        for r in kayit:
            eslesen = [z for z in ozet if z[0] == r["sym"]]
            if not eslesen:
                continue
            giris = r["giris"]
            stop = r["cikis"] / (1 - SLIP)
            risk = giris - stop
            miktar = r["notional"] / giris
            tp1 = giris + m * risk
            bars = _MUM[r["sym"]]
            a, oa, _ = simule(bars, giris, stop, tp1, miktar, babas=False)
            b_, _ob, _ = simule(bars, giris, stop, tp1, miktar, babas=True)
            tetik = any(e[0] == "TP1" for e in oa)
            sat += " %9.2f/%-9.2f%s" % (a, b_, "*" if tetik else " ")
            top_a += a
        sat += " %12.2f" % top_a
        print(sat)
    print()
    print("   * = TP1 gercekten TETIKLENDI.  GERCEK toplam %+.2f $" % tg)
    print()
    print("N=2 — TESHIS. Kural cikarilmaz.")
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
