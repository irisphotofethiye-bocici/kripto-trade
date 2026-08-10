#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KAÇAN KAZANANLAR (2026-08-10) — "kazananlara neden giremedi?"

SORU (kullanici): "kazananlara neden giremedigini, girmesi gereken yerde girseydi ne
olurdu — kazananlardaki ortak GIRILECEK NOKTA'yi ara. Ayni sinyale sahip radarda olup
degerlendirilmemislerle karsilastir."

HUNI TERSINE KURULUYOR:
  1. 46 gunluk radar arsivindeki 7119 olayin hepsi botun gercek mekanigiyle oynatildi.
     KAZANAN = hedefe (2R) ulasan olay. KAYBEDEN = stopa giden.
  2. Her olay icin botun KAPILARI yeniden hesaplanir (arsiv alanlarindan):
     skor kapisi · pump kapisi · stage kapisi · dip-bicak kapisi · R/R kapisi
  3. "Kazananlarin kacini hangi kapi kesti" tablosu cikarilir.
  4. GIRIS NOKTASI olculeri eklenir (arsivde YOK, mumdan hesaplanir):
       stop_frac  : giristen stopa uzaklik (%) — girisin yapiya YAKINLIGI
       rr_tp1     : en yakin yapisal hedefe uzaklik / risk — botun R/R kapisinin gordugu
       uzanim     : giris fiyatinin son 20 barin tepesine uzakligi (ATR cinsinden)
       mae / mfe  : en fazla aleyhte / lehte gidis (R cinsinden) — "girecegi nokta" testi
  5. Kazananlarin bu olculerdeki ortak yani, TUM POPULASYONLA ve zaman ikiye
     bolunerek karsilastirilir (pos>=0.85 dersi: kontrolsuz ortak-yan = tesaduf).

ON-KAYIT: esik aranmayacak; bantlar dagilimin ceyreklerinden. N<25-30 = izlenim.
"""
import json, os, sys, statistics as st, collections, datetime

BURA = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(BURA)
CACHE = os.path.join(BURA, "klines_1h")
UFUK, NBAR, MALIYET = 72, 10, 0.04


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def bars_of(sym):
    p = os.path.join(CACHE, f"{sym}.json")
    return json.load(open(p)) if os.path.exists(p) else None


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


def giris_olculeri(b, gi):
    """SHORT icin: stop, hedef, rr_tp1, uzanim, mae, mfe."""
    i = gi - 1
    a = atr14(b, i)
    if a is None or a <= 0:
        return None
    ref = b[gi]["o"]
    hi, lo = swings(b, i)
    res = min([x for x in hi if x > ref], default=None)
    sup = max([x for x in lo if x < ref], default=None)
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
    if risk <= 0:
        return None
    tp1 = sup if (sup is not None and sup < ref) else ref - 2 * risk
    rr1 = (ref - tp1) / risk
    tepe20 = max(x["h"] for x in b[max(0, i - 19):i + 1])
    uzanim = (tepe20 - ref) / a           # tepeden kac ATR asagidayiz
    son = min(gi + UFUK, len(b))
    mfe = mae = 0.0
    for j in range(gi, son):
        mfe = max(mfe, (ref - b[j]["l"]) / risk)
        mae = max(mae, (b[j]["h"] - ref) / risk)
        if b[j]["h"] >= stop:
            break
    return {"stop_frac": risk / ref * 100, "rr_tp1": rr1, "uzanim": uzanim,
            "mfe": mfe, "mae": mae}


def main():
    ol = json.load(open(os.path.join(BURA, "oruntu_olaylar.json")))
    ol = [o for o in ol if o.get("R_short") is not None]
    print(f"Olay: {len(ol)} — giris olculeri hesaplaniyor...")
    idxc = {}
    ek = 0
    for o in ol:
        sym = o["sym"]
        if sym not in idxc:
            b = bars_of(sym)
            idxc[sym] = (b, {x["t"] // 3600000: i for i, x in enumerate(b)}) if b else (None, None)
        b, idx = idxc[sym]
        if not b:
            continue
        ms = int(datetime.datetime.strptime(o["ts"], "%Y-%m-%d %H:%M").astimezone().timestamp() * 1000)
        gi = idx.get(ms // 3600000 + 1)
        if gi is None or gi < 30:
            continue
        g = giris_olculeri(b, gi)
        if g:
            o.update(g)
            ek += 1
    ge = [o for o in ol if "rr_tp1" in o]
    print(f"  {ek} olayda giris olculeri hesaplandi\n")

    tsl = sorted(o["ts"] for o in ge)
    ORTA = tsl[len(tsl) // 2]

    KAZ = [o for o in ge if o["R_short"] > 1.5]      # hedefe ulasan
    KAY = [o for o in ge if o["R_short"] < -0.9]     # stopa giden
    print("=" * 100)
    print("1) KAZANAN vs KAYBEDEN — giris noktasi olculeri")
    print("=" * 100)
    print(f"  KAZANAN (2R hedefe ulasan): {len(KAZ)}  ·  KAYBEDEN (stopa giden): {len(KAY)}"
          f"  ·  toplam {len(ge)}")
    print(f"\n{'olcu':16}{'KAZANAN medyan':>17}{'KAYBEDEN medyan':>18}{'TUM medyan':>14}{'ayirt?':>10}")
    print("-" * 100)
    for alan, ad in (("stop_frac", "stop mesafesi %"), ("rr_tp1", "rr_tp1"),
                     ("uzanim", "tepeden ATR"), ("score", "skor"), ("pos", "pos"),
                     ("funding", "funding"), ("oi24", "oi24"), ("comp", "comp"),
                     ("vol_x", "vol_x"), ("chg24", "chg24")):
        k = [o[alan] for o in KAZ if o.get(alan) is not None]
        y = [o[alan] for o in KAY if o.get(alan) is not None]
        t = [o[alan] for o in ge if o.get(alan) is not None]
        if not k or not y:
            continue
        mk, my, mt = st.median(k), st.median(y), st.median(t)
        fark = "EVET" if abs(mk - my) > 0.15 * (abs(mt) + 1e-9) else "hayir"
        print(f"{ad:16}{mk:17.3f}{my:18.3f}{mt:14.3f}{fark:>10}")

    # --- 2. kapi hunisi
    print("\n" + "=" * 100)
    print("2) BOTUN KAPILARI — kazananlarin kacini hangi kapi keserdi?")
    print("=" * 100)
    KAPI = [
        ("skor < 45 (radar_short_skor)", lambda o: (o.get("score") or 0) < 45),
        ("chg24 >= 20 (pump kapisi)", lambda o: (o.get("chg24") or 0) >= 20),
        ("stage = izle (NOTR stage kapisi)", lambda o: o.get("stage") == "izle"),
        ("pos < 0.20 (AYI-SHORT tabani)", lambda o: (o.get("pos") or 0) < 0.20),
        ("chg24 <= -40 (asiri dusmus)", lambda o: (o.get("chg24") or 0) <= -40),
        ("rr_tp1 < 1.5 (R/R kapisi, YENI)", lambda o: o["rr_tp1"] < 1.5),
        ("rr_tp1 < 2.0 (R/R kapisi, ESKI)", lambda o: o["rr_tp1"] < 2.0),
    ]
    print(f"{'kapi':38}{'kazananin %':>13}{'kaybedenin %':>14}{'tum %':>9}"
          f"{'kestiginin R':>14}{'gecirdiginin R':>16}")
    print("-" * 100)
    for ad, fn in KAPI:
        kk = sum(1 for o in KAZ if fn(o)) / len(KAZ) * 100
        ky = sum(1 for o in KAY if fn(o)) / len(KAY) * 100
        kt = sum(1 for o in ge if fn(o)) / len(ge) * 100
        kes = [o["R_short"] for o in ge if fn(o)]
        gec = [o["R_short"] for o in ge if not fn(o)]
        sk = f"{st.mean(kes):14.3f}" if kes else f"{'—':>14}"
        sg = f"{st.mean(gec):16.3f}" if gec else f"{'—':>16}"
        print(f"{ad:38}{kk:12.1f}%{ky:13.1f}%{kt:8.1f}%{sk}{sg}")
    print("\nOKUMA: 'kazananin %' yuksek + 'gecirdiginin R' dusuk = kapi KAZANANLARI kesiyor.")

    # --- 3. bilesik: botun tum kapilarindan gecen vs kesilen
    print("\n" + "=" * 100)
    print("3) RADARDA VAR ama DEGERLENDIRILEMEYENLER — botun tum kapilariyla ayrim")
    print("=" * 100)

    def gecer(o, rr_esik):
        return ((o.get("score") or 0) >= 45 and (o.get("chg24") or 0) < 20
                and (o.get("pos") or 0) >= 0.20 and (o.get("chg24") or 0) > -40
                and o["rr_tp1"] >= rr_esik)

    def oz(sec):
        rs = [o["R_short"] for o in sec]
        if not rs:
            return None
        return {"n": len(rs), "ort": st.mean(rs), "hedef": sum(1 for r in rs if r > 1.5) / len(rs) * 100,
                "sh": st.pstdev(rs) / len(rs) ** 0.5 if len(rs) > 1 else 0}

    for rr_esik, ad in ((2.0, "ESKI R/R kapisi (2.0)"), (1.5, "YENI R/R kapisi (1.5)"), (0.0, "R/R kapisi YOK")):
        gecen = [o for o in ge if gecer(o, rr_esik)]
        kesilen = [o for o in ge if not gecer(o, rr_esik)]
        g, k = oz(gecen), oz(kesilen)
        print(f"\n  --- {ad} ---")
        print(f"    GECEN   : N={g['n']:5d}  ort R {g['ort']:+.3f} ±{g['sh']:.3f}  hedefe ulasan %{g['hedef']:.0f}")
        print(f"    KESILEN : N={k['n']:5d}  ort R {k['ort']:+.3f} ±{k['sh']:.3f}  hedefe ulasan %{k['hedef']:.0f}")
        kk = [o for o in KAZ if gecer(o, rr_esik)]
        print(f"    -> {len(KAZ)} kazanandan {len(kk)}'i gecerdi (%{len(kk)/len(KAZ)*100:.0f}), "
              f"{len(KAZ)-len(kk)}'i KESILIRDI")

    # --- 4. A+B kapisi ayni huniyle
    print("\n" + "=" * 100)
    print("4) A+B KAPISI ayni huniyle (funding<=-0.05 & oi24>=10)")
    print("=" * 100)
    AB = lambda o: ((o.get("funding") or 0) <= -0.05 and (o.get("oi24") or 0) >= 10)
    for ad, fn in (("A+B tek basina", AB),
                   ("A+B + rr_tp1>=1.5", lambda o: AB(o) and o["rr_tp1"] >= 1.5),
                   ("A+B + skor>=45", lambda o: AB(o) and (o.get("score") or 0) >= 45)):
        sec = [o for o in ge if fn(o)]
        a = oz(sec)
        if not a:
            continue
        kk = sum(1 for o in KAZ if fn(o))
        aa = oz([o for o in sec if o["ts"] < ORTA]); bb = oz([o for o in sec if o["ts"] >= ORTA])
        print(f"  {ad:24} N={a['n']:5d}  ort R {a['ort']:+.3f} ±{a['sh']:.3f}  "
              f"hedefe %{a['hedef']:.0f}  |  kazananlarin {kk}/{len(KAZ)}'i icinde"
              f"  |  A {aa['ort']:+.3f} B {bb['ort']:+.3f}")

    json.dump([{k: v for k, v in o.items() if k in
                ("ts", "sym", "score", "stage", "pos", "funding", "oi24", "chg24",
                 "stop_frac", "rr_tp1", "uzanim", "mfe", "mae", "R_short")} for o in ge],
              open(os.path.join(BURA, "kacan_olaylar.json"), "w"))
    print("\n-> scratchpad/kacan_olaylar.json")


if __name__ == "__main__":
    main()
