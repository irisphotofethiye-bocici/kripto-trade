# -*- coding: utf-8 -*-
"""KOSUL URETICI — alanlardan 'kural parcasi' uretir. Esik TARANMAZ:
sayisal alanlar kendi TERCILINE gore ucе bolunur, kategorikler seviyeleriyle girer."""


ATLA = {"id","sym","yon","giris_ts","cikis_ts","pnl","n_kayit","kismi_var",
        "sebep_cikis","tutma_saat","giris_fiyat","cikis_fiyat","sebep_giris",
        "donem","eslesti","aday_ts","eslesme_dk","d_derinlik_giriste",
        "d_marjin","d_funding_usdt","a_price"}

def kosullar(poz, min_dolu=0.8):
    """-> [(ad, fonksiyon)] ; her kosul pozisyonu kabul/ret eder."""
    n = len(poz)
    alanlar = set()
    for p in poz: alanlar |= set(p)
    out = []
    for a in sorted(alanlar):
        if a in ATLA: continue
        v = [p.get(a) for p in poz]
        dolu = [x for x in v if x is not None]
        if len(dolu) < n*min_dolu: continue
        say = [x for x in dolu if isinstance(x,(int,float)) and not isinstance(x,bool)]
        if len(say) == len(dolu) and len(set(dolu)) > 4:
            s = sorted(say); k1, k2 = s[len(s)//3], s[2*len(s)//3]
            if k1 == k2: continue
            out.append(("%s<%.4g"%(a,k1),      lambda p,a=a,k=k1: p.get(a) is not None and p[a]< k))
            out.append(("%s %.4g-%.4g"%(a,k1,k2), lambda p,a=a,x=k1,y=k2: p.get(a) is not None and x<=p[a]<y))
            out.append(("%s>=%.4g"%(a,k2),     lambda p,a=a,k=k2: p.get(a) is not None and p[a]>=k))
        else:
            for lv in sorted(set(map(str,dolu))):
                c = sum(1 for x in dolu if str(x)==lv)
                if 3 <= c <= n-3:
                    out.append(("%s=%s"%(a,lv), lambda p,a=a,l=lv: p.get(a) is not None and str(p[a])==l))
    return out
