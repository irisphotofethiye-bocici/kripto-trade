# -*- coding: utf-8 -*-
"""IZ F — TEK AYAKTA KALAN BULGU MEKANIKTEN BAGIMSIZ MI?

KULLANICI ITIRAZI (hakli): "bu olcumlerin dogruluguna guvenmemi gerektiren sebep ne?"
Kanit: ayni 117 islem, benim replay mekanigimle -2.400 $, botun gercek sonucu -489 $.
Yani 2 yillik olcumlerim BASKA BIR SISTEMI tarif ediyor.

CLAUDE.md acikca soyluyor:
  "SINYAL, MEKANIKTEN ARINIK OLCULUR — ham ileri getiri -> ticaret mekanigi -> portfoy"
BEN BU SIRAYI ATLADIM. 0..20 LONG bulgusu A-stop + %10 hedefle olculdu.

BU BETIK: ayni bantlari UC farkli sekilde olcer.
  1. HAM ileri getiri (stop YOK, hedef YOK, maliyet YOK) — sinyalin kendisi
  2. A-stop + %10 hedef (ilk olcumdeki mekanik)
  3. Takip eden stop
Bulgu UCUNDE DE ayni yonde ise sinyal gercek; yalniz birinde varsa MEKANIK ESERIDIR.
"""
import json, os, sys, collections, random, statistics as stx, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import olcum_ortak as oo
import ileri_rr as ir
import btcpay_rejim as bp

UFUK = 72
BANTLAR = [(-40, 0, "-40..0"), (0, 20, "0..20"), (20, 40, "20..40"), (40, 1e9, ">40")]
random.seed(41)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

def kostur():
    h = collections.defaultdict(list)
    for fn in sorted(os.listdir(ir.KLINE)):
        if not fn.endswith(".json"): continue
        sym = fn[:-5]
        try: b = json.load(open(os.path.join(ir.KLINE, fn), encoding="utf-8"))
        except Exception: continue
        if len(b) < ir.ISINMA + UFUK + 50: continue
        fp = os.path.join(ir.FUND, fn); fr = []
        if os.path.exists(fp):
            try: fr = json.load(open(fp, encoding="utf-8"))
            except Exception: fr = []
        ft = [x["t"] for x in fr]
        atrs = ir.atr_serisi(b)
        faz = random.randint(0, 23)
        for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24 or b[i-24]["c"] <= 0: continue
            c24 = (x["c"]/b[i-24]["c"]-1)*100
            ad = next((a for lo, hi, a in BANTLAR if lo <= c24 < hi), None)
            if ad is None: continue
            gi = i+1
            if not atrs[i] or gi >= len(b): continue
            ref = b[gi]["o"]
            if ref <= 0: continue
            son = min(gi+UFUK, len(b))
            if son-gi < 4: continue
            t0 = b[gi]["t"]
            # --- 1) HAM ileri getiri: stop yok, hedef yok, maliyet yok ---
            ham_l = (b[son-1]["c"]-ref)/ref*100
            h[(ad, "LONG", "ham")].append((ham_l, sym, t0))
            h[(ad, "SHORT", "ham")].append((-ham_l, sym, t0))
            # --- 2) A-stop + %10 hedef (ilk olcumdeki mekanik) ---
            for yon in ("LONG", "SHORT"):
                if yon == "SHORT":
                    stop = ir.stop_hesapla(b, i, ref, atrs[i]); sp = (stop-ref)/ref*100; hed = ref*0.90
                else:
                    stop = bp.stop_long(b, i, ref, atrs[i]); sp = (ref-stop)/ref*100; hed = ref*1.10
                if sp <= 0 or sp < 2.0: continue
                cj = hm = None
                for j in range(gi, son):
                    vs = (b[j]["h"] >= stop) if yon == "SHORT" else (b[j]["l"] <= stop)
                    vh = (b[j]["l"] <= hed) if yon == "SHORT" else (b[j]["h"] >= hed)
                    if vs: cj, hm = j, -sp; break
                    if vh: cj, hm = j, 10.0; break
                if cj is None:
                    cj = son-1
                    hm = ((ref-b[son-1]["c"]) if yon == "SHORT" else (b[son-1]["c"]-ref))/ref*100
                f = ir.fonlama_pct(ft, fr, t0, b[cj]["t"])
                h[(ad, yon, "mekanik")].append((hm-oo.MALIYET+(f if yon == "SHORT" else -f), sym, t0))
                # --- 3) takip eden stop (mesafe = baslangic stopu) ---
                st2 = stop; en = ref; cj2 = hm2 = None
                for j in range(gi, son):
                    if (b[j]["h"] >= st2) if yon == "SHORT" else (b[j]["l"] <= st2):
                        hm2 = ((ref-st2) if yon == "SHORT" else (st2-ref))/ref*100
                        cj2 = j; break
                    en = min(en, b[j]["l"]) if yon == "SHORT" else max(en, b[j]["h"])
                    yeni = en*(1+sp/100) if yon == "SHORT" else en*(1-sp/100)
                    st2 = min(st2, yeni) if yon == "SHORT" else max(st2, yeni)
                if cj2 is None:
                    cj2 = son-1
                    hm2 = ((ref-b[son-1]["c"]) if yon == "SHORT" else (b[son-1]["c"]-ref))/ref*100
                f2 = ir.fonlama_pct(ft, fr, t0, b[cj2]["t"])
                h[(ad, yon, "trail")].append((hm2-oo.MALIYET+(f2 if yon == "SHORT" else -f2), sym, t0))
    return h

def kumeli(v):
    a = collections.defaultdict(list)
    for net, s, t in v: a[ay(t)].append(net)
    ok = [k for k in a if len(a[k]) >= 20]
    if len(ok) < 3: return None
    m = [stx.mean(a[k]) for k in ok]
    se = stx.stdev(m)/len(m)**0.5
    return stx.mean(m), (stx.mean(m)/se if se else 0), len(ok), sum(1 for x in m if x > 0)

h = kostur()
print("IZ F — 0..20 LONG BULGUSU MEKANIKTEN BAGIMSIZ MI?")
print("=" * 96)
print("CLAUDE.md sirasi: HAM ileri getiri -> ticaret mekanigi. Ilk olcum ham'i ATLAMISTI.\n")
for yon in ("LONG", "SHORT"):
    print("### %s" % yon)
    print("%-9s %-9s %8s %10s %9s %9s" % ("bant", "olcum", "N", "ay ort", "ay-t", "poz ay"))
    for lo, hi, ad in BANTLAR:
        for mod, etiket in (("ham", "HAM getiri"), ("mekanik", "A-stop+%10"), ("trail", "trailing")):
            v = h.get((ad, yon, mod), [])
            if len(v) < 100:
                print("%-9s %-9s %8d  N yetersiz" % (ad, etiket, len(v))); continue
            k = kumeli(v)
            if k is None:
                print("%-9s %-9s %8d  ay yetersiz" % (ad, etiket, len(v))); continue
            print("%-9s %-9s %8d %+10.3f %+9.2f %5d/%-3d" % (ad, etiket, len(v), k[0], k[1], k[3], k[2]))
        print()
