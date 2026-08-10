#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A+B ÇIKIŞ TESTİ (2026-08-10) — botun fiili cikisi A+B edge'inin ne kadarini aliyor?

BULGU: A+B kapisinin edge'i hedef buyudukce ARTIYOR (SHORT net %):
  hedef %1.5 -> +0.14 | %2.0 -> +0.22 | %2.5 -> +0.47 | %3 -> +0.72
        %5   -> +1.33 | %7.5 -> +1.63 | %10  -> +2.19 | %15 -> +2.36 (isabet cokuyor)
Botun FIILI cikisi: kismi kar 1.5R'de (stop medyani %1.35 -> ~%2 hedef) + trailing.
Yani mevcut cikis, masadaki +2.19%'un ~+0.22%'sini aliyor gibi gorunuyor.

BU SCRIPT botun GERCEK cikis mekanigini birebir simule eder ve alternatiflerle karsilastirir:
  C1 MEVCUT   : %50 kismi 1.5R'de · kalan trailing (1R'de aktif, 2xATR; 2R'de 1.5x; 3R'de 1x)
                · breakeven tabani · 48s zaman stopu
  C2 KISMI YOK: sadece trailing (ayni parametreler)
  C3 SABIT %10: kismi yok, hedef %10, trailing yok
  C4 KARMA    : %50 kismi %5'te, kalan %10 hedefe (trailing yok)
  C5 GENIS TRAIL: kismi 1.5R'de ama trailing 3xATR sabit (daralmiyor)
Hepsi ayni girislerde (A+B olaylari), 1 saatlik mumla, fitil bazli, maliyet %0.09.

NOT: bot 1 DAKIKALIK mumla yonetiyor; burada 1 SAATLIK mum var -> trailing daha KABA,
gercek sonuc bundan biraz farkli olur. Siralamayi degistirmesi beklenmez.
"""
import json, os, statistics as st, datetime

BURA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BURA, "klines_1h")
NBAR, MALIYET = 10, 0.09
UFUK = 48


def atr14(b, i):
    if i < 14:
        return None
    tr = []
    for j in range(i - 13, i + 1):
        p = b[j - 1]["c"]
        tr.append(max(b[j]["h"] - b[j]["l"], abs(b[j]["h"] - p), abs(p - b[j]["l"])))
    return st.mean(tr)


def swings(b, i, left=3, right=3, geri=100):
    bas = max(left, i - geri)
    hi, lo = [], []
    for j in range(bas, i - right + 1):
        w = b[j - left:j + right + 1]
        if not w:
            continue
        if b[j]["h"] == max(x["h"] for x in w):
            hi.append(b[j]["h"])
        if b[j]["l"] == min(x["l"] for x in w):
            lo.append(b[j]["l"])
    return hi, lo


def kurulum(b, gi):
    """SHORT icin giris/stop/atr."""
    i = gi - 1
    a = atr14(b, i)
    if not a or a <= 0 or gi >= len(b):
        return None
    ref = b[gi]["o"]
    hi, _ = swings(b, i)
    res = min([x for x in hi if x > ref], default=None)
    ad = []
    if res is not None and (res - ref) <= 3 * a:
        ad.append(res + 0.25 * a)
    nb = max(x["h"] for x in b[max(0, i - NBAR + 1):i + 1])
    if nb > ref:
        ad.append(nb + 0.25 * a)
    ad.append(ref + 1.5 * a)
    gec = [s for s in ad if s > ref]
    stop = min(gec) if gec else ref + 1.5 * a
    risk = stop - ref
    return (ref, stop, risk, a) if risk > 0 else None


def cikis(b, gi, mod):
    """SHORT. -> net getiri % | None"""
    k = kurulum(b, gi)
    if not k:
        return None
    ref, stop0, risk, a = k
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    kalan, kar = 1.0, 0.0
    stop = stop0
    kismi_alindi = False
    trail_aktif = False
    en_iyi = ref
    if mod == "C3":
        hedef = ref * 0.90
    elif mod == "C4":
        kismi_h, hedef = ref * 0.95, ref * 0.90
    for j in range(gi, son):
        x = b[j]
        # --- trailing guncelle (fitil bazli, kaba)
        en_iyi = min(en_iyi, x["l"])
        if mod in ("C1", "C2", "C5"):
            kar_r = (ref - en_iyi) / risk
            if kar_r >= 1.0:
                trail_aktif = True
            if trail_aktif:
                kat = 3.0 if mod == "C5" else (1.0 if kar_r >= 3 else (1.5 if kar_r >= 2 else 2.0))
                yeni = en_iyi + kat * a
                be = ref * (1 - 0.0015)
                yeni = min(yeni, be)
                stop = min(stop, yeni)
        # --- stop
        if x["h"] >= stop:
            kar += kalan * (ref - stop) / ref * 100
            return kar - MALIYET
        # --- kismi / hedef
        if mod == "C1" and not kismi_alindi and x["l"] <= ref - 1.5 * risk:
            kar += 0.5 * (1.5 * risk) / ref * 100
            kalan = 0.5
            kismi_alindi = True
        if mod == "C3" and x["l"] <= hedef:
            kar += kalan * 10.0
            return kar - MALIYET
        if mod == "C4":
            if not kismi_alindi and x["l"] <= kismi_h:
                kar += 0.5 * 5.0
                kalan = 0.5
                kismi_alindi = True
            if x["l"] <= hedef:
                kar += kalan * 10.0
                return kar - MALIYET
    c = b[son - 1]["c"]
    kar += kalan * (ref - c) / ref * 100
    return kar - MALIYET


def oz(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {"n": len(v), "ort": st.mean(v), "sh": st.pstdev(v) / len(v) ** 0.5 if len(v) > 1 else 0,
            "poz": sum(1 for x in v if x > 0) / len(v) * 100}


def main():
    ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
    AB = lambda o: ((o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10)
    bc, idxc, sec = {}, {}, []
    for o in ol:
        if not AB(o):
            continue
        s = o["sym"]
        if s not in bc:
            p = os.path.join(CACHE, f"{s}.json")
            bc[s] = json.load(open(p)) if os.path.exists(p) else None
            if bc[s]:
                idxc[s] = {x["t"] // 3600000: i for i, x in enumerate(bc[s])}
        if not bc[s]:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        gi = idxc[s].get(ms // 3600000 + 1)
        if gi is not None:
            o["_b"], o["_gi"] = bc[s], gi
            sec.append(o)
    tsl = sorted(o["ts"] for o in sec)
    ORTA = tsl[len(tsl) // 2]
    print("=" * 100)
    print(f"A+B ÇIKIŞ TESTİ — {len(sec)} A+B olayi · ayni girisler · SHORT · 1h mum, 48s ufuk")
    print("=" * 100)
    MOD = [("C1", "MEVCUT (kismi 1.5R + trailing)"), ("C2", "kismi YOK, sadece trailing"),
           ("C3", "sabit %10 hedef, trailing yok"), ("C4", "kismi %5 + hedef %10"),
           ("C5", "kismi 1.5R + GENIS trail (3xATR)")]
    print(f"{'cikis kurali':38}{'N':>6}{'net %':>10}{'kazanan':>10}{'A yari':>10}{'B yari':>10}")
    print("-" * 100)
    for m, ad in MOD:
        v = [cikis(o["_b"], o["_gi"], m) for o in sec]
        a = oz(v)
        A = oz([cikis(o["_b"], o["_gi"], m) for o in sec if o["ts"] < ORTA])
        B = oz([cikis(o["_b"], o["_gi"], m) for o in sec if o["ts"] >= ORTA])
        if a:
            print(f"{ad:38}{a['n']:6d}{a['ort']:+10.2f}{a['poz']:9.1f}%"
                  f"{(A['ort'] if A else 0):+10.2f}{(B['ort'] if B else 0):+10.2f}")
    print("\nNOT: bot 1 DAKIKALIK mumla yonetiyor, burada 1 SAATLIK -> trailing kaba.")
    print("Siralamanin degismesi beklenmez ama mutlak degerler farkli olur.")


if __name__ == "__main__":
    main()
