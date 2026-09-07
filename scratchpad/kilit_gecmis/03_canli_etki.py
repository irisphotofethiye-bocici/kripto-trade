#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAR KILIDININ CANLI ETKISI — notrlong PENCERE-3'un kapanmis pozisyonlari

Soru: kilit OLMASAYDI bu 9 pozisyon ne olurdu?
Onceki karsi-olgular (01/02) botun ESKI defterindeydi ve kaybedene yanliydi.
Burada kilit GERCEKTEN acikti; olculen sey onun GERCEK etkisi.

ZORUNLU SINAMA: kilitli yeniden kurulum defterdeki GERCEK toplami
uretmiyorsa o pozisyon DISLANIR.

SALT-OKUNUR. Bot dosyalarina yazim YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, io, os, sys, collections, statistics as stx
import importlib.util as il

BURA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURA))
sys.path.insert(0, KOK)
sp = il.spec_from_file_location("olc", os.path.join(BURA, "01_olcum.py"))
olc = il.module_from_spec(sp)
sp.loader.exec_module(olc)

HEDEF_PCT = 10.0
TOL = 0.03          # %3 — kilitli yol iki kez maliyet oduyor, birebir olmaz


def main():
    print("=" * 100)
    print("KAR KILIDININ CANLI ETKISI — notrlong PENCERE-3")
    print("=" * 100)

    g = collections.defaultdict(list)
    for l in io.open(os.path.join(KOK, "notrlong_islemler.jsonl"), encoding="utf-8"):
        l = l.strip()
        if l:
            r = json.loads(l)
            g[r["id"]].append(r)

    sonuc, dis = [], collections.Counter()
    for i in sorted(g):
        v = sorted(g[i], key=lambda z: z["ts"])
        ilk, son = v[0], v[-1]
        giris, k, yon = ilk["giris"], ilk["kaldirac"], ilk["yon"]
        yi = 1 if yon == "LONG" else -1
        # notional: kilit oncesi TAM pozisyon
        notional = ilk["notional"] / (ilk["kilit_pay"] if ilk.get("kilit_pay") else 1.0) \
            if ilk.get("sebep") == "KAR_KILIDI" else ilk["notional"]
        miktar = notional / giris
        ger = sum(x.get("sonuc_usdt") or 0 for x in v)

        # --- ORIJINAL stop
        if son["sebep"] == "STOP" and son.get("r"):
            net_pct = (son["cikis"] / giris - 1) * 100.0 * yi
            risk_pct = net_pct / son["r"]
        elif son.get("r"):
            net_pct = (son["cikis"] / giris - 1) * 100.0 * yi
            risk_pct = net_pct / son["r"]
        else:
            dis["r yok"] += 1
            continue
        if risk_pct <= 0:
            dis["risk<=0"] += 1
            continue
        stop = giris * (1 - yi * risk_pct / 100.0)
        hedef = giris * (1 + yi * HEDEF_PCT / 100.0)

        kap_ms = olc.yerel_ms(son["ts"])
        gir_ms = olc.yerel_ms(ilk["ts"]) - int((ilk.get("tutma_saat") or 0) * 3600000)
        bars = olc.mum_getir(ilk["sym"], gir_ms - 5 * 60000, kap_ms + 30 * 60000)
        if not bars or len(bars) < 5:
            dis["mum yok"] += 1
            continue
        olc.K["k"] = k
        # --- SINAMA: kilitli yol GERCEGI uretmeli
        n1, s1, m1, o1 = olc.yol_kos(bars, giris, stop, hedef, miktar, yon, True)
        if abs(n1 - ger) > max(abs(ger) * TOL, 3.0):
            dis["sinama dustu (%s: %.2f vs %.2f)" % (ilk["sym"], n1, ger)] += 1
            continue
        # --- KARSI-OLGU: kilit YOK
        n0, s0, m0, _ = olc.yol_kos(bars, giris, stop, hedef, miktar, yon, False)
        sonuc.append({"id": i, "sym": ilk["sym"], "k": k, "ger": ger,
                      "kilitli": n1, "kilitsiz": n0, "s0": s0, "s1": s1,
                      "tetik": any(o[0] == "KILIT" for o in o1),
                      "stop": stop, "risk_pct": risk_pct})

    print("kapanan pozisyon %d · yeniden kuruldu %d · dislanan %d"
          % (len(g), len(sonuc), sum(dis.values())))
    for s, c in dis.most_common():
        print("   dislanan: %s x%d" % (s, c))
    if not sonuc:
        print("Yeniden kurulabilen pozisyon YOK.")
        return
    print()

    print("### KILIT VAR vs KILIT YOK")
    print("   %-4s %-6s %-4s %10s %11s %11s %11s  %-12s %-12s"
          % ("id", "sym", "kald", "GERCEK", "kilitli", "KILITSIZ", "FARK", "kilitli cik", "kilitsiz cik"))
    for x in sonuc:
        print("   %-4s %-6s %-4s %+10.2f %+11.2f %+11.2f %+11.2f  %-12s %-12s"
              % (x["id"], x["sym"], "%dx" % x["k"], x["ger"], x["kilitli"],
                 x["kilitsiz"], x["kilitli"] - x["kilitsiz"], x["s1"], x["s0"]))
    tg = sum(x["ger"] for x in sonuc)
    t1 = sum(x["kilitli"] for x in sonuc)
    t0 = sum(x["kilitsiz"] for x in sonuc)
    print("   %-17s %+10.2f %+11.2f %+11.2f %+11.2f" % ("TOPLAM", tg, t1, t0, t1 - t0))
    print()

    tet = [x for x in sonuc if x["tetik"]]
    print("### OKUMA")
    print("   kilit tetikleyen : %d / %d  (%%%.0f)"
          % (len(tet), len(sonuc), 100.0 * len(tet) / len(sonuc)))
    print("   kilidin NET etkisi: %+.2f $" % (t1 - t0))
    if tet:
        iy = [x for x in tet if x["kilitli"] > x["kilitsiz"]]
        ko = [x for x in tet if x["kilitli"] < x["kilitsiz"]]
        print("   tetikleyenlerde: iyilesen %d (%+.2f $) · kotulesen %d (%+.2f $)"
              % (len(iy), sum(x["kilitli"] - x["kilitsiz"] for x in iy),
                 len(ko), sum(x["kilitli"] - x["kilitsiz"] for x in ko)))
    print()
    print("   ⚠️ N=%d. Bu bir HUKUM DEGIL — pencere olcutu 80 kapanmis pozisyon."
          % len(sonuc))
    print()
    print("Salt-okuma. Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
