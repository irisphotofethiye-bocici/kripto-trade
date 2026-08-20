# -*- coding: utf-8 -*-
"""IZ A-2 — >%40 bandi: botun IKI YONU DE yasakladigi yer.

Ust olcumde bu bandin LONG-SHORT farki +1,863 puan cikti (en buyuk).
AMA LONG'un kendi ay-kumeli t'si +1,43 idi — anlamli degil.
Burada band ALT BANTLARA bolunur ve sans olcumu yapilir.
ESIK TARAMASI DEGIL: 40 botun mevcut esigi; ustu tarif ediliyor.
"""
import sys, os, collections, statistics as stx, datetime, random, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import olcum_ortak as oo
import ileri_rr as ir
import btcpay_rejim as bp

HEDEF, UFUK = 10.0, 72
ALT = [(40,60,"40..60"),(60,100,"60..100"),(100,1e9,">100")]
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
            if c24 < 40: continue
            ad = next((a for lo,hi,a in ALT if lo <= c24 < hi), None)
            if ad is None: continue
            gi = i+1
            if not atrs[i] or gi >= len(b): continue
            ref = b[gi]["o"]
            if ref <= 0: continue
            son = min(gi+UFUK, len(b))
            if son-gi < 4: continue
            for yon in ("SHORT","LONG"):
                if yon == "SHORT":
                    stop = ir.stop_hesapla(b,i,ref,atrs[i]); sp=(stop-ref)/ref*100; hed=ref*(1-HEDEF/100)
                else:
                    stop = bp.stop_long(b,i,ref,atrs[i]); sp=(ref-stop)/ref*100; hed=ref*(1+HEDEF/100)
                if sp <= 0 or sp < 2.0: continue
                cj=ham=None
                for j in range(gi,son):
                    vs=(b[j]["h"]>=stop) if yon=="SHORT" else (b[j]["l"]<=stop)
                    vh=(b[j]["l"]<=hed) if yon=="SHORT" else (b[j]["h"]>=hed)
                    if vs: cj,ham=j,-sp; break
                    if vh: cj,ham=j,HEDEF; break
                if cj is None:
                    cj=son-1
                    ham=((ref-b[son-1]["c"]) if yon=="SHORT" else (b[son-1]["c"]-ref))/ref*100
                f=ir.fonlama_pct(ft,fr,b[gi]["t"],b[cj]["t"])
                h[(ad,yon)].append((ham-oo.MALIYET+(f if yon=="SHORT" else -f), sym, b[gi]["t"]))
    return h

def kumeli(v, asgari=15):
    a=collections.defaultdict(list)
    for net,s,t in v: a[ay(t)].append(net)
    ok=[k for k in a if len(a[k])>=asgari]
    if len(ok)<3: return None
    m=[stx.mean(a[k]) for k in ok]
    se=stx.stdev(m)/len(m)**0.5
    return stx.mean(m),(stx.mean(m)/se if se else 0),len(ok),sum(1 for x in m if x>0),m

h=kostur()
print("IZ A-2 — >%40 bandi (bot IKI YONU DE yasakliyor)")
print("="*86)
print("%-9s %-6s %8s %10s %9s %8s %9s"%("alt bant","yon","N","ay ort %","ay-t","poz ay","sembol"))
for lo,hi,ad in ALT:
    for yon in ("SHORT","LONG"):
        v=h.get((ad,yon),[])
        if len(v)<40: print("%-9s %-6s %8d  N yetersiz"%(ad,yon,len(v))); continue
        k=kumeli(v)
        if k is None: print("%-9s %-6s %8d  ay yetersiz"%(ad,yon,len(v))); continue
        print("%-9s %-6s %8d %+10.3f %+9.2f %5d/%-3d %8d"%(ad,yon,len(v),k[0],k[1],k[3],k[2],len({z[1] for z in v})))
    print()
print("YON FARKI (ayni barlar):")
for lo,hi,ad in ALT:
    l,s=h.get((ad,"LONG"),[]),h.get((ad,"SHORT"),[])
    if len(l)<40 or len(s)<40: continue
    kl,ks=kumeli(l),kumeli(s)
    if kl and ks: print("  %-9s LONG %+7.3f  SHORT %+7.3f  ->  FARK %+7.3f"%(ad,kl[0],ks[0],kl[0]-ks[0]))

# SANS OLCUMU: >40 LONG'un ay ortalamasi sansla aciklanir mi
print()
print("SANS OLCUMU — >40 LONG (tum alt bantlar birlikte)")
tum=[z for lo,hi,ad in ALT for z in h.get((ad,"LONG"),[])]
k=kumeli(tum)
if k:
    ger=k[0]; aylar=k[4]
    random.seed(7); sahte=[]
    tumnet=[z[0] for z in tum]
    for _ in range(2000):
        random.shuffle(tumnet)
        # ayni ay boyutlariyla yeniden bol
        i=0; m=[]
        for _n in range(len(aylar)):
            b=len(tumnet)//len(aylar)
            m.append(stx.mean(tumnet[i:i+b])); i+=b
        sahte.append(stx.mean(m))
    ust=sum(1 for x in sahte if x>=ger)
    print("  gercek ay ortalamasi %+.3f · ay sayisi %d · pozitif %d"%(ger,k[2],k[3]))
    print("  karistirilmis 2000 tur: ortalama %+.3f · sapma %.3f"%(stx.mean(sahte),stx.pstdev(sahte)))
    print("  p = %.4f  -> %s"%(ust/2000,"sanstan farkli" if ust/2000<0.05 else "SANSTAN AYIRT EDILEMIYOR"))
