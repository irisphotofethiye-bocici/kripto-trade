# -*- coding: utf-8 -*-
"""IZ A-3 — DOGRU sans olcumu: AY ICINDE bant etiketleri karistirilir.

Onceki denemem hataliydi: net degerleri karistirip aylari esit boyuta boluyordu.
O, "ay-agirlikli ortalama vs boyut-agirlikli ortalama" farkini olcuyordu, NULL degil.

DOGRU NULL: "bant etiketi bilgi tasimiyor" hipotezi. Ayni AY icindeki tum
gozlemlerin bant etiketleri karistirilir; ay yapisi ve piyasa kosullari korunur.
"""
import sys, os, collections, statistics as stx, datetime, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import A_bant as A

def ay(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

hucre, _ = A.kostur()

def ay_ort(kayit):
    a=collections.defaultdict(list)
    for net,t in kayit: a[ay(t)].append(net)
    ok=[k for k in a if len(a[k])>=15]
    if len(ok)<3: return None,None,None
    m=[stx.mean(a[k]) for k in ok]
    se=stx.stdev(m)/len(m)**0.5
    return stx.mean(m),(stx.mean(m)/se if se else 0),len(ok)

for yon in ("LONG","SHORT"):
    print("\n" + "="*84)
    print("%s — AY ICI bant karistirma testi (2000 tur)"%yon)
    print("="*84)
    # ayni ay icindeki TUM gozlemleri topla, bant etiketiyle
    hepsi=[]
    for lo,hi,ad in A.BANTLAR:
        for net,sym,t in hucre.get((ad,yon),[]):
            hepsi.append((ay(t),ad,net))
    aygrup=collections.defaultdict(list)
    for a_,ad,net in hepsi: aygrup[a_].append((ad,net))
    print("%-9s %8s %10s %9s %10s %8s"%("bant","N","gercek","sahte ort","sahte sd","p"))
    for lo,hi,ad in A.BANTLAR:
        ger=[(net,t) for net,sym,t in hucre.get((ad,yon),[])]
        if len(ger)<100: 
            print("%-9s %8d  N yetersiz"%(ad,len(ger))); continue
        g,gt,nay=ay_ort(ger)
        if g is None:
            print("%-9s %8d  ay yetersiz"%(ad,len(ger))); continue
        random.seed(41); sahte=[]
        for _ in range(2000):
            m=[]
            for a_,lst in aygrup.items():
                etk=[e for e,_n in lst]; net=[n for _e,n in lst]
                random.shuffle(etk)
                sec=[n for e,n in zip(etk,net) if e==ad]
                if len(sec)>=15: m.append(stx.mean(sec))
            if len(m)>=3: sahte.append(stx.mean(m))
        if not sahte: print("%-9s  sahte uretilemedi"%ad); continue
        if g>=0: p=sum(1 for x in sahte if x>=g)/len(sahte)
        else:    p=sum(1 for x in sahte if x<=g)/len(sahte)
        print("%-9s %8d %+10.3f %+10.3f %9.3f %8.4f %s"%(ad,len(ger),g,stx.mean(sahte),stx.pstdev(sahte),p,
              "<-- SANSTAN FARKLI" if p<0.05 else ""))
