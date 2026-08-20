# -*- coding: utf-8 -*-
"""IZ B-2 — TAKIP EDEN STOP, 2 yillik sinav.  30. CIKIS VARYANTI.

NEDEN YENI: olcumler.md'deki 29 varyantin listesi -> 5 cikis kiyasi + 8 oynak
hedef + 7 kismi + 1 basabas + 8 erken mudahale. TAKIP EDEN STOP bunlarda YOK.
Ve bot onu LONG tarafinda ZATEN kullaniyor (SABIT_HEDEF_KAPILARI disinda kalan
her giris trailing ile cikiyor). Yani asimetri olculmemis bir varsayim.

ON-KAYIT (kosturmadan once yazildi, bu dosyada):
  KONTROL : sabit %10 hedef (botun bugunku SHORT cikisi, 29'un gecen tek varyanti)
  KURAL   : takip eden stop, mesafe = BASLANGIC STOP MESAFESI x 1,0
            (keyfi sayi DEGIL — pozisyonun kendi riskiyle ayni olcek)
  Duyarlilik olarak 0,5x ve 1,5x da raporlanir AMA HUKUM 1,0x uzerinden verilir.
  Ayni girisler, ayni baslangic stopu -> ESLESMIS test.
  GECME OLCUTU: (1) islem basina yuksek (2) IKI ZAMAN YARISINDA da yuksek
                (3) AY-KUMELI t > +2,0 (4) uc rejimde ters isaret yok
  BEKLENTI: kararsiz. Lehte: kutugun kendi kalibi "kotu giriste siki cikis kaybi
  keser" ve bu defterin girisleri kotu. Aleyhte: 28/28 sikilastirma kaldi.

⚠️ KARAR CIKARILMAYACAK — kullanici talimati. Yalniz olcum.
"""
import json, os, sys, collections, random, statistics as stx, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import olcum_ortak as oo
import ileri_rr as ir

HEDEF, UFUK = 10.0, 72
CARPANLAR = [0.5, 1.0, 1.5]
random.seed(41)

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

def kostur():
    sonuc = collections.defaultdict(list)   # (mod) -> [(net, sym, ts, rejim)]
    rej = ir.btc_rejim()
    islenen = 0
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
        ma50 = ir.ma_serisi(b, 50)
        islenen += 1
        faz = random.randint(0, 23)
        import bisect
        for i in range(ir.ISINMA + faz, len(b) - UFUK - 2, ir.SEYRELT):
            x = b[i]
            if (x.get("qv") or 0) < ir.MIN_VOL/24 or i < 24: continue
            if (x["c"]/b[i-24]["c"]-1)*100 >= ir.PUMP: continue     # pump kapisi (bot da uyguluyor)
            # botun SABIT HEDEF kapilari: A+B (funding) veya MA50+ucuz
            gecti = False
            if ft:
                k = bisect.bisect_right(ft, x["t"]) - 1
                if k >= 0 and fr[k]["r"]*100 <= ir.FUND_ESIK: gecti = True
            if not gecti and ma50[i] and ma50[i] > 0 and x["c"] <= ir.UCUZ_FIYAT:
                if (x["c"]/ma50[i]-1)*100 >= ir.MA50_MESAFE: gecti = True
            if not gecti: continue
            gi = i+1
            if not atrs[i] or gi >= len(b): continue
            ref = b[gi]["o"]
            if ref <= 0: continue
            stop0 = ir.stop_hesapla(b, i, ref, atrs[i])
            sp = (stop0-ref)/ref*100
            if sp <= 0 or sp < ir.ASGARI_STOP: continue
            son = min(gi+UFUK, len(b))
            if son-gi < 4: continue
            hed = ref*(1-HEDEF/100)
            r_ad = rej.get(x["t"]//3600000, "NOTR")

            def kaydet(mod, ham, cj):
                f = ir.fonlama_pct(ft, fr, b[gi]["t"], b[cj]["t"])
                sonuc[mod].append((ham - oo.MALIYET + f, sym, b[gi]["t"], r_ad))

            # KONTROL: sabit hedef
            cj = ham = None
            for j in range(gi, son):
                if b[j]["h"] >= stop0: cj, ham = j, -sp; break
                if b[j]["l"] <= hed:   cj, ham = j, HEDEF; break
            if cj is None:
                cj = son-1; ham = (ref-b[son-1]["c"])/ref*100
            kaydet("sabit", ham, cj)

            # KURAL: takip eden stop (mesafe = baslangic stop mesafesi x carpan)
            for c in CARPANLAR:
                trail = sp * c
                stop = stop0; eniyi = ref
                cj2 = ham2 = None
                for j in range(gi, son):
                    if b[j]["h"] >= stop:
                        cj2, ham2 = j, (ref-stop)/ref*100
                        break
                    eniyi = min(eniyi, b[j]["l"])
                    stop = min(stop, eniyi*(1+trail/100))
                if cj2 is None:
                    cj2 = son-1; ham2 = (ref-b[son-1]["c"])/ref*100
                kaydet("trail%.1f" % c, ham2, cj2)
    return sonuc, islenen

def kumeli(v, asgari=20):
    a = collections.defaultdict(list)
    for net, s, t, r in v: a[ay(t)].append(net)
    ok = [k for k in a if len(a[k]) >= asgari]
    if len(ok) < 3: return None
    m = [stx.mean(a[k]) for k in ok]
    se = stx.stdev(m)/len(m)**0.5
    return stx.mean(m), (stx.mean(m)/se if se else 0), len(ok), sum(1 for x in m if x > 0)

s, islenen = kostur()
print("IZ B-2 — TAKIP EDEN STOP, 2 yillik sinav (30. cikis varyanti)")
print("="*94)
print("islenen sembol: %d · giris kumesi: botun SABIT HEDEF kapilari (A+B / MA50+ucuz)"%islenen)
print("ESLESMIS test: ayni girisler, ayni baslangic stopu, FARKLI cikis\n")
kon = s["sabit"]
print("%-10s %8s %10s %10s %9s %8s"%("mod","N","islem ort","ay ort","ay-t","poz ay"))
for mod in ["sabit"] + ["trail%.1f"%c for c in CARPANLAR]:
    v = s[mod]
    if len(v) < 100: continue
    k = kumeli(v)
    nt = "  <-- KONTROL (botun bugunku hali)" if mod == "sabit" else ""
    if mod == "trail1.0": nt = "  <-- ON-KAYITLI KURAL"
    if k is None:
        print("%-10s %8d %+10.3f   ay yetersiz%s"%(mod,len(v),stx.mean([z[0] for z in v]),nt))
    else:
        print("%-10s %8d %+10.3f %+10.3f %+9.2f %5d/%-3d%s"%(mod,len(v),stx.mean([z[0] for z in v]),k[0],k[1],k[3],k[2],nt))

print("\nESLESMIS FARK (trail1.0 - sabit), ayni giris sirasi:")
a = {(z[1], z[2]): z[0] for z in kon}
b_ = {(z[1], z[2]): z[0] for z in s["trail1.0"]}
ortak_k = sorted(set(a) & set(b_))
fark = [b_[k]-a[k] for k in ortak_k]
print("  N=%d  ortalama fark %+.4f%%  medyan %+.4f%%  pozitif %d (%%%.0f)"
      % (len(fark), stx.mean(fark), stx.median(fark), sum(1 for x in fark if x > 0),
         100*sum(1 for x in fark if x > 0)/len(fark)))
af = collections.defaultdict(list)
for k, f in zip(ortak_k, fark): af[ay(k[1])].append(f)
ok = [k for k in af if len(af[k]) >= 20]
m = [stx.mean(af[k]) for k in ok]
se = stx.stdev(m)/len(m)**0.5
print("  AY-KUMELI: %d ay · ortalama %+.4f · t=%+.2f · pozitif %d/%d"
      % (len(ok), stx.mean(m), stx.mean(m)/se if se else 0, sum(1 for x in m if x > 0), len(ok)))
print("\nOLCUT 2 — IKI ZAMAN YARISI:")
yar = len(ortak_k)//2
for et, dilim in (("A yarisi", ortak_k[:yar]), ("B yarisi", ortak_k[yar:])):
    d = [b_[k]-a[k] for k in dilim]
    print("  %s: fark %+.4f%%  (N=%d)"%(et, stx.mean(d), len(d)))
print("\nOLCUT 4 — REJIM:")
rj = {(z[1], z[2]): z[3] for z in kon}
for r in ("AYI", "NOTR", "BOGA"):
    d = [b_[k]-a[k] for k in ortak_k if rj.get(k) == r]
    if len(d) >= 50: print("  %-5s fark %+.4f%%  (N=%d)"%(r, stx.mean(d), len(d)))
