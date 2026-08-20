#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IZ A — %20-40 BANDI: botun kor noktasi.  2 yillik sinav.

BOTUN DAVRANISI (testbot.py):
  chg24 >= 20  -> SHORT YASAK (pump kapisi, 2 yillik olcumle kuruldu, N=258)
  chg24 >= 40  -> LONG da yasak (blowoff)
  20 <= chg24 < 40 -> SADECE LONG acilabilir

SORU: o bandin LONG tarafi HIC OLCULMEDI. Ve 40 esiginin neden 40 oldugu da.
Bu betik bandi iki yonde de olcer. ESIK TARAMASI YOK — 20 ve 40 botun
mevcut esikleri, band sabit; yalniz 20-30 / 30-40 diye ikiye bolunur
(kenarin neresinde oldugunu gormek icin).

DISIPLIN: faz kaydirma (SEYRELT=24 faz kilidi) · AY-KUMELI istatistik
(bu oturumun dersi: bagimsiz birim gozlem degil takvim donemi) · maliyet+fonlama.

SALT OKUMA.
"""
import json, os, sys, collections, random, statistics as stx, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE)))
import olcum_ortak as oo
import ileri_rr as ir
import btcpay_rejim as bp          # stop_long (aynalanmis A-stop)

HEDEF_PCT, UFUK = 10.0, 72
BANTLAR = [(-1e9, -40, "<-40"), (-40, 0, "-40..0"), (0, 20, "0..20"),
           (20, 30, "20..30"), (30, 40, "30..40"), (40, 1e9, ">40")]
random.seed(41)


def ay(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%Y-%m")


def kostur():
    hucre = collections.defaultdict(list)
    islenen = 0
    for fn in sorted(os.listdir(ir.KLINE)):
        if not fn.endswith(".json"):
            continue
        sym = fn[:-5]
        try:
            b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
        except Exception:
            continue
        if len(b) < ir.ISINMA + UFUK + 50:
            continue
        fp = os.path.join(ir.FUND, fn)
        fr = []
        if os.path.exists(fp):
            try:
                fr = json.load(open(fp, encoding="utf-8"))
            except Exception:
                fr = []
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        islenen += 1
        faz = random.randint(0, 23)
        for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < ir.MIN_VOL / 24 or i < 24:
                continue
            if b[i - 24]["c"] <= 0:
                continue
            chg24 = (x["c"] / b[i - 24]["c"] - 1) * 100
            bant = next((ad for lo, hi, ad in BANTLAR if lo <= chg24 < hi), None)
            if bant is None:
                continue
            gi = i + 1
            if not atrs[i] or gi >= len(b):
                continue
            ref = b[gi]["o"]
            if ref <= 0:
                continue
            son = min(gi + UFUK, len(b))
            if son - gi < 4:
                continue
            for yon in ("SHORT", "LONG"):
                if yon == "SHORT":
                    stop = ir.stop_hesapla(b, i, ref, atrs[i])
                    sp = (stop - ref) / ref * 100
                    hedef = ref * (1 - HEDEF_PCT / 100)
                else:
                    stop = bp.stop_long(b, i, ref, atrs[i])
                    sp = (ref - stop) / ref * 100
                    hedef = ref * (1 + HEDEF_PCT / 100)
                if sp <= 0 or sp < 2.0:
                    continue
                cj, ham = None, None
                for j in range(gi, son):
                    vs = (b[j]["h"] >= stop) if yon == "SHORT" else (b[j]["l"] <= stop)
                    vh = (b[j]["l"] <= hedef) if yon == "SHORT" else (b[j]["h"] >= hedef)
                    if vs:
                        cj, ham = j, -sp
                        break
                    if vh:
                        cj, ham = j, HEDEF_PCT
                        break
                if cj is None:
                    cj = son - 1
                    ham = ((ref - b[son - 1]["c"]) if yon == "SHORT"
                           else (b[son - 1]["c"] - ref)) / ref * 100
                f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
                fon = f if yon == "SHORT" else -f
                net = ham - oo.MALIYET + fon
                hucre[(bant, yon)].append((net, sym, b[gi]["t"]))
    return hucre, islenen


def kumeli(v):
    """AY-KUMELI ozet -> (n, ort, ay_ort, ay_t, ay_sayisi, pozitif_ay)"""
    a = collections.defaultdict(list)
    for net, sym, t in v:
        a[ay(t)].append(net)
    ok = [k for k in a if len(a[k]) >= 20]
    if len(ok) < 3:
        return len(v), stx.mean([z[0] for z in v]), None, None, len(ok), None
    m = [stx.mean(a[k]) for k in ok]
    se = stx.stdev(m) / len(m) ** 0.5
    return (len(v), stx.mean([z[0] for z in v]), stx.mean(m),
            (stx.mean(m) / se if se else 0.0), len(ok), sum(1 for x in m if x > 0))


def rapor():
    print("IZ A — %20-40 BANDI, 2 yillik sinav (botun kor noktasi)")
    print("=" * 96)
    print("Bot: chg24>=20 -> SHORT yasak · chg24>=40 -> LONG da yasak")
    print("     20-40 arasi SADECE LONG acilabiliyor. O bandin LONG tarafi hic olculmedi.")
    print("Mekanik: A-stop · hedef %s%% · %ss · maliyet+FONLAMA · faz kaydirmali\n" % (HEDEF_PCT, UFUK))
    hucre, islenen = kostur()
    print("islenen sembol: %d\n" % islenen)
    print("%-9s %-6s %8s %9s %9s %8s %9s  %s"
          % ("bant", "yon", "N", "ort %", "ay ort %", "ay-t", "ay poz", "botun davranisi"))
    for lo, hi, ad in BANTLAR:
        for yon in ("SHORT", "LONG"):
            v = hucre.get((ad, yon), [])
            if len(v) < 40:
                print("%-9s %-6s %8d   N yetersiz" % (ad, yon, len(v)))
                continue
            n, ort, ayo, ayt, nay, poz = kumeli(v)
            bot = ""
            if ad in ("20..30", "30..40"):
                bot = "SHORT YASAK" if yon == "SHORT" else "acik"
            elif ad == ">40":
                bot = "yasak"
            elif yon == "SHORT":
                bot = "acik"
            else:
                bot = "acik (filtreli)"
            if ayt is None:
                print("%-9s %-6s %8d %+9.3f    ay kirilimi yok           %s" % (ad, yon, n, ort, bot))
            else:
                print("%-9s %-6s %8d %+9.3f %+9.3f %+8.2f %5d/%-3d  %s"
                      % (ad, yon, n, ort, ayo, ayt, poz, nay, bot))
    return hucre


if __name__ == "__main__":
    rapor()
