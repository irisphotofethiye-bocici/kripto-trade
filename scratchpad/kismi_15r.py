#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESKI 1.5R KISMI KURALI LEHIMIZE MI? — 2 yillik sinav (2026-08-12)
On-kayit: fikir-defteri.md (KOSTURULMADAN once commit edildi)

BULUNAN CELISKI (2026-08-12, acik pozisyon incelemesi):
  Kullanici kismi kar seviyesini "hedefin %40'i" olarak ayarladi (kismi_pay=0.40 ->
  %10 hedefte -%4). Ama testbot.py:902 HER TURDA sunu yapiyor:
      tp1 = tp1_efektif_hesapla(giris, stop_orijinal, tp1, yon)
      -> yapisal TP1 ile 1.5xRISK'ten HANGISI DAHA YAKINSA o.
  Yani stop DARSA (1.5 x stop% < 4%  <=>  stop% < %2.67) eski 1.5R kurali yeni
  %40 ayarini SESSIZCE EZIYOR. Canli ornek: UMA stop %0.96 -> TP1 %4 yerine %1.43,
  yarisini -%1.4'te satti (+46$).

SORU (kullanici): "eski 1.5R kurali lehimize mi degil mi?"

SINANAN 4 KURAL (hepsi ayni girislerde, ayni stop, ayni maliyet):
  A) kismi YOK                          — hedefe kadar tek parca
  B) sabit %40  (= -%4)                 — kullanicinin NIYET ETTIGI kural
  C) MEVCUT FIILI = yakin olan{%4, 1.5R} — botun BUGUN yaptigi
  D) saf 1.5R                            — eski kural tek basina
  (ayrica sekil icin 1.0R / 2.0R / 3.0R)

KRITIK ALT KIRILIM: iki kural YALNIZCA stop < %2.67 olan islemlerde ayrisir.
  Karar o alt kumede verilir; genel ortalama farki SULANDIRIR.

MEKANIK canlinin aynisi: A-stop (yapisal/10-bar/1.5ATR en yakini) · Wilder ATR ·
  sabit %10 hedef · 72 saat · maliyet %0.13 · giris sonraki barin acilisi ·
  pump kapisi (chg24 < %20) · hacim tabani $3M/24s · seyreltme 24 bar ·
  kismi sonrasi stop BASABASA CEKILMEZ (canli davranis, cikis_modu=sabit_hedef).
Kapilar: A+B'nin funding bacagi (<= -0.05) + MA50+ucuz (fiyat<=0.07 & ma50>=%3.72).
Veri: klines_1h_uzun (566 sembol, 2 yil — GERCEK BOGA VE GERCEK AYI icerir).

Salt-okunur. Bota dokunmaz.
"""
import json, os, sys, statistics as stx, collections, bisect, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olcum_ortak as oo

BURA = os.path.dirname(os.path.abspath(__file__))
KLINE = os.path.join(BURA, "klines_1h_uzun")
FUND = os.path.join(BURA, "funding_gecmis")
HEDEF_PCT, UFUK = 10.0, 72
STOP_NBAR = 10
RISK_PCT, MARJIN_PCT, KALD_MAX = 0.015, 0.10, 10
ISINMA, SEYRELT = 220, 24
FUND_ESIK, PUMP, MIN_VOL = -0.05, 20.0, 3_000_000
MA50_ESIK, UCUZ = 3.72, 0.07
KISMI_PAY = 0.40
AYRISMA_STOP = HEDEF_PCT * KISMI_PAY / 1.5     # = %2.67


def atr_serisi(b, n=14):
    out, tr = [None] * len(b), [None] * len(b)
    for i in range(1, len(b)):
        pc = b[i - 1]["c"]
        tr[i] = max(b[i]["h"] - b[i]["l"], abs(b[i]["h"] - pc), abs(pc - b[i]["l"]))
    if len(b) <= n:
        return out
    a = sum(tr[1:n + 1]) / n
    out[n] = a
    for i in range(n + 1, len(b)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def stop_hesapla(b, si, ref, a):
    bas = max(3, si - 100)
    hi = []
    for j in range(bas, si - 2):
        w = b[j - 3:j + 4]
        if w and b[j]["h"] == max(x["h"] for x in w):
            hi.append(b[j]["h"])
    res = min([x for x in hi if x > ref], default=None)
    ad = []
    if res is not None and (res - ref) <= 3 * a:
        ad.append(res + 0.25 * a)
    nb = max(x["h"] for x in b[max(0, si - STOP_NBAR + 1):si + 1])
    if nb > ref:
        ad.append(nb + 0.25 * a)
    ad.append(ref + 1.5 * a)
    gec = [s for s in ad if s > ref]
    return min(gec) if gec else ref + 1.5 * a


def ma(v, n):
    out, s = [None] * len(v), 0.0
    for i, x in enumerate(v):
        s += x
        if i >= n:
            s -= v[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def btc_rejim():
    b = json.load(open(os.path.join(KLINE, "BTC.json"), encoding="utf-8"))
    c = [x["c"] for x in b]
    pen, out = 720, {}
    for i in range(pen, len(b)):
        g = (c[i] / c[i - pen] - 1) * 100
        out[b[i]["t"] // 3600000] = "BOGA" if g >= 15 else ("AYI" if g <= -15 else "NOTR")
    return out


def kismi_seviye(kural, sp):
    """SHORT icin kismi kar seviyesi, GIRISTEN yuzde olarak. None -> kismi yok."""
    if kural == "YOK":
        return None
    sabit = HEDEF_PCT * KISMI_PAY
    if kural == "SABIT40":
        return sabit
    if kural == "MEVCUT":
        return min(sabit, 1.5 * sp)          # "yakin olan" — testbot.py:902
    if kural.endswith("R"):
        return float(kural[:-1]) * sp
    raise ValueError(kural)


def calis(b, atrs, si, kural):
    """Doner: (net_fiyat_yuzdesi, tip, stop%). Kismi sonrasi stop AYNI kalir (canli)."""
    gi = si + 1
    if si < ISINMA or gi >= len(b) or not atrs[si]:
        return None
    ref = b[gi]["o"]
    if ref <= 0:
        return None
    stop = stop_hesapla(b, si, ref, atrs[si])
    sp = (stop - ref) / ref * 100
    if sp <= 0:
        return None
    son = min(gi + UFUK, len(b))
    if son - gi < 4:
        return None
    hedef = ref * (1 - HEDEF_PCT / 100)
    kp = kismi_seviye(kural, sp)
    # kismi seviye hedefin otesindeyse anlamsiz -> kismi yok say
    if kp is not None and kp >= HEDEF_PCT:
        kp = None
    kf = ref * (1 - kp / 100) if kp else None
    alindi, kar = False, 0.0
    for j in range(gi, son):
        x = b[j]
        if x["h"] >= stop:                                   # stop once mu?
            z = -sp
            return ((0.5 * kar + 0.5 * z if alindi else z) - oo.MALIYET,
                    "KISMI+STOP" if alindi else "STOP", sp)
        if kf and not alindi and x["l"] <= kf:
            alindi, kar = True, kp
        if x["l"] <= hedef:
            return ((0.5 * kar + 0.5 * HEDEF_PCT if alindi else HEDEF_PCT) - oo.MALIYET,
                    "KISMI+HEDEF" if alindi else "HEDEF", sp)
    g = (ref - b[son - 1]["c"]) / ref * 100
    return ((0.5 * kar + 0.5 * g if alindi else g) - oo.MALIYET,
            "KISMI+SURE" if alindi else "SURE", sp)


def olaylari_topla(rej):
    olay = []
    dosyalar = sorted(f for f in os.listdir(KLINE) if f.endswith(".json"))
    for n, f in enumerate(dosyalar, 1):
        if f == "BTC.json":
            continue
        sym = f[:-5]
        try:
            b = json.load(open(os.path.join(KLINE, f), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ISINMA + UFUK + 5:
            continue
        c = [x["c"] for x in b]
        qv = [x.get("qv", 0.0) for x in b]
        m50 = ma(c, 50)
        atrs = atr_serisi(b)
        fy = os.path.join(FUND, sym + ".json")
        fr = json.load(open(fy, encoding="utf-8")) if os.path.exists(fy) else []
        ft = [x["t"] for x in fr]
        son = -10 ** 9
        for i in range(ISINMA, len(b) - UFUK - 2):
            if not atrs[i] or c[i - 24] <= 0 or sum(qv[i - 23:i + 1]) < MIN_VOL:
                continue
            if (c[i] / c[i - 24] - 1) * 100 >= PUMP or i - son < SEYRELT:
                continue
            kapi = None
            if fr:
                k = bisect.bisect_right(ft, b[i]["t"]) - 1
                if k >= 0 and fr[k]["r"] <= FUND_ESIK:
                    kapi = "A+B"
            if kapi is None and m50[i] and c[i] <= UCUZ \
                    and (c[i] / m50[i] - 1) * 100 >= MA50_ESIK:
                kapi = "MA50"
            if not kapi:
                continue
            son = i
            olay.append({"sym": sym, "b": b, "atrs": atrs, "i": i, "t": b[i]["t"],
                         "kapi": kapi, "rej": rej.get(b[i]["t"] // 3600000)})
        if n % 150 == 0:
            print(f"  {n}/{len(dosyalar)} ...", flush=True)
    return olay


KURALLAR = [("A) kismi YOK", "YOK"),
            ("B) sabit %40 (niyet)", "SABIT40"),
            ("C) MEVCUT: yakin olan", "MEVCUT"),
            ("D) saf 1.5R (eski)", "1.5R"),
            ("   saf 1.0R", "1.0R"),
            ("   saf 2.0R", "2.0R"),
            ("   saf 3.0R", "3.0R")]


def main():
    print("Olaylar toplaniyor (2 yil, 566 sembol)...", flush=True)
    rej = btc_rejim()
    olay = olaylari_topla(rej)
    if not olay:
        print("OLAY YOK"); return
    tl = sorted(o["t"] for o in olay)
    ORTA = tl[len(tl) // 2]

    # her olay icin stop% bir kez — alt kirilim ve boyut icin
    for o in olay:
        r = calis(o["b"], o["atrs"], o["i"], "YOK")
        o["_sp"] = r[2] if r else None
    olay = [o for o in olay if o["_sp"]]

    print("\n" + "=" * 118)
    print("ESKI 1.5R KISMI KURALI LEHIMIZE MI? — 2 yillik sinav")
    print("=" * 118)
    print(f"N={len(olay)} · {len(set(o['sym'] for o in olay))} ayri sembol · "
          f"hedef %{HEDEF_PCT} · {UFUK}s · maliyet %{oo.MALIYET}")
    print(f"Kapi dagilimi: {dict(collections.Counter(o['kapi'] for o in olay))}")
    print(f"stop medyani %{stx.median([o['_sp'] for o in olay]):.2f} · "
          f"AYRISMA SINIRI %{AYRISMA_STOP:.2f} (altinda 1.5R kurali %40'i EZER)")
    dar = [o for o in olay if o["_sp"] < AYRISMA_STOP]
    print(f"  -> stop DAR  (<%{AYRISMA_STOP:.2f}) : {len(dar):5d} olay "
          f"(%{len(dar)/len(olay)*100:.0f}) — IKI KURAL BURADA AYRISIR")
    print(f"  -> stop GENIS (>=%{AYRISMA_STOP:.2f}): {len(olay)-len(dar):5d} olay "
          f"— iki kural AYNI seyi yapar\n")

    def olc(sec, kural):
        kay, sem = [], []
        for o in sec:
            r = calis(o["b"], o["atrs"], o["i"], kural)
            if r:
                boy = min(RISK_PCT / (r[2] / 100.0), MARJIN_PCT * KALD_MAX)
                kay.append((r[0] * boy, r[1], o["t"])); sem.append(o["sym"])
        if len(kay) < 40:
            return None
        g = [k[0] for k in kay]
        n = len(g); k_ = len(set(sem))
        t = stx.mean(g) / (stx.stdev(g) / math.sqrt(n)) if n > 1 else 0
        return {"n": n, "serm": stx.mean(g), "sem": k_, "t": t,
                "t_kume": t * math.sqrt(k_ / n),
                "kismi": sum(1 for k in kay if k[1].startswith("KISMI")) / n * 100,
                "hedef": sum(1 for k in kay if k[1].endswith("HEDEF")) / n * 100,
                "A": stx.mean([k[0] for k in kay if k[2] < ORTA] or [0]),
                "B": stx.mean([k[0] for k in kay if k[2] >= ORTA] or [0])}

    def tablo(baslik, sec):
        print("=" * 118)
        print(f"{baslik}   (N={len(sec)})")
        print("=" * 118)
        print(f"{'kural':26}{'N':>6}{'SERMAYE/islem':>15}{'kismi degdi':>13}"
              f"{'hedefe vardi':>14}{'A yari':>9}{'B yari':>9}{'t':>7}{'t_kume':>8}")
        print("-" * 118)
        taban = None
        for ad, k in KURALLAR:
            r = olc(sec, k)
            if not r:
                continue
            if taban is None:
                taban = r["serm"]
            im = ""
            if k != "YOK":
                im = f"  {r['serm']-taban:+.3f}"
            print(f"{ad:26}{r['n']:6d}{r['serm']:+15.3f}{r['kismi']:12.0f}%"
                  f"{r['hedef']:13.0f}%{r['A']:+9.3f}{r['B']:+9.3f}"
                  f"{r['t']:+7.2f}{r['t_kume']:+8.2f}{im}")
        print()

    tablo("### 1) TUM OLAYLAR", olay)
    tablo("### 2) ASIL TEST — stop DAR olanlar (iki kural burada ayrisir)", dar)
    tablo("### 3) KIYAS — stop GENIS olanlar (iki kural ayni, fark cikmamali)",
          [o for o in olay if o["_sp"] >= AYRISMA_STOP])

    print("=" * 118)
    print("### 4) REJIME GORE — dar-stop alt kumesi")
    print("=" * 118)
    print(f"{'rejim':8}{'N':>6}", end="")
    for ad, _ in KURALLAR[:4]:
        print(f"{ad.split(')')[0]:>12}", end="")
    print()
    print("-" * 118)
    for rr in ("BOGA", "NOTR", "AYI"):
        sec = [o for o in dar if o["rej"] == rr]
        if len(sec) < 60:
            continue
        print(f"{rr:8}{len(sec):6d}", end="")
        for _, k in KURALLAR[:4]:
            r = olc(sec, k)
            print(f"{(r['serm'] if r else float('nan')):+12.3f}", end="")
        print()

    print("\n" + "=" * 118)
    print("### 5) KAPIYA GORE — dar-stop alt kumesi")
    print("=" * 118)
    for kp in ("A+B", "MA50"):
        sec = [o for o in dar if o["kapi"] == kp]
        if len(sec) < 60:
            continue
        print(f"{kp:8}{len(sec):6d}", end="")
        for _, k in KURALLAR[:4]:
            r = olc(sec, k)
            print(f"{(r['serm'] if r else float('nan')):+12.3f}", end="")
        print()

    print("\nOKUMA: 'SERMAYE/islem' = risk-onceli boyutlandirma dahil, ASIL KARAR SUTUNU.")
    print("Saga yazilan +/- sayi, o satirin 'kismi YOK'a gore farkidir.")


if __name__ == "__main__":
    main()
