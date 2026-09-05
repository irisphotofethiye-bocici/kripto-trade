#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PAHALI AYNASI — esik ve kapsam sayimi (2026-09-05)
Yalniz DAGILIM ve TETIK sayar. Getiri HESAPLAMAZ.
Amac: "ucuz yerine pahali olsa" sorusunun esigini UYDURMADAN belirlemek.
Orijinal kapi: fiyat <= $0,07 = dagilimin %20'lik dilimi (config notu).
Aynasi: fiyat >= %80'lik dilim. Dilim AYNI evrenden hesaplanir."""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import sys, os, json, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ileri_rr as ir

BURA = os.path.dirname(os.path.abspath(__file__))
ESKI_K, YENI_K = os.path.join(BURA, "klines_1h_uzun"), os.path.join(BURA, "taze_1h")
ISINMA, UFUK, SEYRELT = 220, 72, 24
PUMP, MIN_VOL, MA50_MESAFE = 20.0, 3_000_000, 3.72
BOGA_BAS = "2026-08-21"


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


def main():
    bas = int(dt.datetime.strptime(BOGA_BAS, "%Y-%m-%d")
              .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    fiyatlar_2y, fiyatlar_boga = [], []
    kl = {}
    for f in sorted(os.listdir(ESKI_K)):
        if not f.endswith(".json"):
            continue
        sym = f[:-5]
        b = birlestir(os.path.join(ESKI_K, f), os.path.join(YENI_K, f))
        if not b or len(b) < ISINMA + UFUK + 50:
            continue
        kl[sym] = b
        for i in range(ISINMA, len(b) - UFUK - 2, SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < MIN_VOL / 24:
                continue
            fiyatlar_2y.append(x["c"])
            if x["t"] >= bas:
                fiyatlar_boga.append(x["c"])

    def dilim(v, p):
        s = sorted(v)
        return s[int(len(s) * p)]

    print("=" * 72)
    print("PAHALI AYNASI — ESIK ve KAPSAM (getiri HESAPLANMADI)")
    print("=" * 72)
    print("sembol: %d\n" % len(kl))
    for ad, v in (("2 YIL", fiyatlar_2y), ("BOGA penceresi", fiyatlar_boga)):
        if not v:
            continue
        print("%s  N=%d" % (ad, len(v)))
        for p in (0.10, 0.20, 0.50, 0.80, 0.90):
            print("    %%%2d dilim : $%.6f" % (p * 100, dilim(v, p)))
        print()
    ucuz_2y, pahali_2y = dilim(fiyatlar_2y, 0.20), dilim(fiyatlar_2y, 0.80)
    print("ORIJINAL kapi esigi (config)     : $0,07")
    print("2 yillik %%20 dilimi (yeniden)   : $%.6f   <- config ile tutuyor mu?" % ucuz_2y)
    print("2 yillik %%80 dilimi = AYNA esigi : $%.6f" % pahali_2y)
    print()

    # BOGA penceresinde ayna kapisi kac olay verir (24s soguma)
    en_son = max(b[-1]["t"] for b in kl.values())
    kesme = en_son - UFUK * 3600000
    say = collections.Counter()
    son = {}
    gun, sem = set(), set()
    for sym, b in kl.items():
        ma50 = ir.ma_serisi(b, 50)
        for i in range(ISINMA, len(b)):
            x = b[i]
            if x["t"] < bas or x["t"] > kesme:
                continue
            if (x.get("qv") or 0) < MIN_VOL / 24:
                continue
            if i < 24 or b[i - 24]["c"] <= 0:
                continue
            if (x["c"] / b[i - 24]["c"] - 1) * 100 >= PUMP:
                continue
            if x["c"] < pahali_2y:
                continue
            if not ma50[i] or ma50[i] <= 0:
                continue
            if (x["c"] / ma50[i] - 1) * 100 < MA50_MESAFE:
                continue
            say["ham"] += 1
            s0 = son.get(sym)
            if s0 is not None and x["t"] - s0 < 24 * 3600000:
                continue
            son[sym] = x["t"]
            say["OLAY"] += 1
            gun.add(x["t"] // 86400000)
            sem.add(sym)
    print("AYNA KAPISI (fiyat >= $%.4f VE ma50_mesafe >= %%%.2f), BOGA penceresi:"
          % (pahali_2y, MA50_MESAFE))
    print("   ham tetik %d  ->  BAGIMSIZ OLAY %d   (%d gun · %d sembol)"
          % (say["ham"], say["OLAY"], len(gun), len(sem)))
    print("\n(kiyas: ucuz kapisi ayni pencerede 580 olay / 13 gun / 253 sembol)")
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
