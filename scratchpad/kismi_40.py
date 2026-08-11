#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KISMI KAR: HEDEFIN %40'INDA YARIYA INDIR — olcum (2026-08-11)

KULLANICI ONERISI: "kaldiracsiz miktarin %40'ina gelince pozisyonu yariya kucultsun."
  Hedef fiyat %10 -> %4 fiyat hareketinde YARISINI sat, kalan yari %10'a kadar devam.

NEDEN AYRI OLCUM: bu kapilarda kismi kar BILEREK kapatilmisti, ama olculen sey
  FARKLI bir kurulumdu: "1.5R'de kismi + IZ-SUREN stop" (+1.24%) vs "sabit %10" (+2.01%).
  Buradaki oneri (hedefin %40'inda kismi) hic olculmedi. Ustelik iz-suren yok.

KRITIK AYRIM — kismi sonrasi STOP ne olacak:
  (a) stop AYNI kalir        -> kalan yari orijinal stopa kadar nefes alir
  (b) stop BASABASA cekilir  -> botun mevcut pozisyon_kismi_tp1 davranisi budur
  Ikisi COK farkli sonuc verir; ikisi de olculur.

MALIYET NOTU: pozisyonun tamami yine kapaniyor, sadece iki parcada. Giris ucreti tam,
  cikis ucreti iki yarida yarim yarim -> toplam maliyet DEGISMEZ (%0.13).

Salt-okunur; bota dokunmaz.
"""
import json, os, sys, statistics as stx, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yon_avi
import yon_dogrula as yd
import olcum_ortak as oo

HEDEF, UFUK = 10.0, 72
RISK_PCT, MARJIN_PCT, KALD_MAX = 0.015, 0.10, 10


def kurulum(b, si):
    """giris, stop, stop% — botun A-stopu, Wilder ATR."""
    gi, i = si, si - 1
    if i < 200 or gi >= len(b):
        return None
    a = oo.atr(b, i)
    if not a or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, _ = yd.swings2(b, i)
    res = min([x for x in hi if x > ref], default=None)
    ad = []
    if res is not None and (res - ref) <= 3 * a:
        ad.append(res + 0.25 * a)
    nb = max(x["h"] for x in b[max(0, i - 9):i + 1])
    if nb > ref:
        ad.append(nb + 0.25 * a)
    ad.append(ref + 1.5 * a)
    gec = [s for s in ad if s > ref]
    stop = min(gec) if gec else ref + 1.5 * a
    sp = (stop - ref) / ref * 100
    return (ref, stop, sp) if sp > 0 else None


def calis(b, si, pay, basabasa_cek):
    """pay=None -> kismi YOK (bugunku hal). pay=0.4 -> hedefin %40'inda yariyi sat.
    Doner: (net_fiyat_yuzdesi, tip, stop%)"""
    k = kurulum(b, si)
    if not k:
        return None
    ref, stop, sp = k
    gi = si
    hedef = ref * (1 - HEDEF / 100)
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    kismi_fiyat = ref * (1 - HEDEF * pay / 100) if pay else None
    kismi_alindi, kismi_kar = False, 0.0
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:
            zarar = -(stop - ref) / ref * 100
            if kismi_alindi:
                return 0.5 * kismi_kar + 0.5 * zarar - oo.MALIYET, "KISMI+STOP", sp
            return zarar - oo.MALIYET, "STOP", sp
        if kismi_fiyat and not kismi_alindi and x["l"] <= kismi_fiyat:
            kismi_alindi = True
            kismi_kar = HEDEF * pay
            if basabasa_cek:
                stop = ref
        if x["l"] <= hedef:
            if kismi_alindi:
                return 0.5 * kismi_kar + 0.5 * HEDEF - oo.MALIYET, "KISMI+HEDEF", sp
            return HEDEF - oo.MALIYET, "HEDEF", sp
    c = b[son - 1]["c"]
    g = (ref - c) / ref * 100
    if kismi_alindi:
        return 0.5 * kismi_kar + 0.5 * g - oo.MALIYET, "KISMI+SURE", sp
    return g - oo.MALIYET, "SURE", sp


def main():
    ge = yon_avi.yukle()
    bc, idxc = {}, {}
    for o in ge:
        s = o["sym"]
        if s not in bc:
            p = os.path.join(yd.CACHE, f"{s}.json")
            bc[s] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M")
                 .astimezone().timestamp() * 1000)
        o["_b"], o["_gi"] = bc[s], idxc[s].get(ms // 3600000)

    def ab(o):
        return (o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10

    def ma50(o):
        px = 10 ** o["fiyat_log"] if o.get("fiyat_log") is not None else None
        return px is not None and px <= 0.07 and (o.get("ma50_mesafe") or -99) >= 3.72

    sec = [o for o in ge if o.get("_gi") is not None
           and (ab(o) or ma50(o)) and (o.get("chg24") or 0) < 20]
    tsl = sorted(o["ts"] for o in sec)
    ORTA = tsl[len(tsl) // 2]

    print("=" * 112)
    print("KISMI KAR: HEDEFIN BIR PAYINDA YARIYA INDIR — canli iki kapinin olaylari")
    print("=" * 112)
    print(f"N={len(sec)} · hedef %{HEDEF} · ufuk {UFUK}s · maliyet %{oo.MALIYET} · Wilder ATR\n")

    def olc(pay, bb):
        kayit, sem = [], []
        for o in sec:
            r = calis(o["_b"], o["_gi"] + 1, pay, bb)
            if r:
                kayit.append((o["ts"], r)); sem.append(o["sym"])
        if len(kayit) < 60:
            return None
        g = [x[1][0] for x in kayit]
        A = [x[1][0] for x in kayit if x[0] < ORTA]
        B = [x[1][0] for x in kayit if x[0] >= ORTA]
        tam = sum(1 for x in kayit if x[1][1] == "HEDEF") / len(kayit) * 100
        km = sum(1 for x in kayit if x[1][1].startswith("KISMI")) / len(kayit) * 100
        boy = [min(RISK_PCT / (x[1][2] / 100.0), MARJIN_PCT * KALD_MAX) for x in kayit]
        serm = stx.mean([x[1][0] * b for x, b in zip(kayit, boy)])
        return {"n": len(g), "ort": stx.mean(g), "A": stx.mean(A), "B": stx.mean(B),
                "tam": tam, "kismi": km, "serm": serm, "sem": len(set(sem)),
                "top": sum(g)}

    for bb, baslik in ((False, "(a) kismi sonrasi STOP AYNI KALIR"),
                       (True, "(b) kismi sonrasi STOP BASABASA CEKILIR  <- botun mevcut TP1 davranisi")):
        print(f"### {baslik}")
        print(f"{'kural':32}{'N':>6}{'net %':>9}{'kismi %':>9}{'tam hedef':>11}"
              f"{'A yari':>9}{'B yari':>9}{'sermaye/islem':>15}")
        print("-" * 112)
        taban = olc(None, bb)
        print(f"{'BUGUNKU: kismi YOK':32}{taban['n']:6d}{taban['ort']:+9.2f}"
              f"{0:8.0f}%{taban['tam']:10.1f}%{taban['A']:+9.2f}{taban['B']:+9.2f}"
              f"{taban['serm']:+15.3f}")
        for pay in (0.3, 0.4, 0.5, 0.6):
            r = olc(pay, bb)
            if not r:
                continue
            im = " *" if r["serm"] > taban["serm"] else ""
            ad = f"hedefin %{pay*100:.0f}'inda yariya in"
            print(f"{ad:32}{r['n']:6d}{r['ort']:+9.2f}{r['kismi']:8.0f}%{r['tam']:10.1f}%"
                  f"{r['A']:+9.2f}{r['B']:+9.2f}{r['serm']:+15.3f}{im}")
        print()

    print("=" * 112)
    print("OKUMA")
    print("=" * 112)
    print("  'kismi %'    : islemlerin yuzde kaci kismi seviyeye DEGDI")
    print("  'tam hedef'  : yuzde kaci %10 hedefe ULASTI")
    print("  'sermaye/islem': kaldirac ve pozisyon boyutu dahil, ASIL KARAR SUTUNU")
    print(f"  Ayri sembol sayisi: {taban['sem']} (N={taban['n']}) — kumelenme dusuk")


if __name__ == "__main__":
    main()
