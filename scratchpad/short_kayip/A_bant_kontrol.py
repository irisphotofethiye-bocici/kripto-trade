# -*- coding: utf-8 -*-
"""IZ A — KARISTIRICI KONTROLU: 0..20 LONG bulgusu rejimden mi geliyor?

Ust olcum: 0..20 bandinda LONG ay-kumeli -0,406% (t=-4,11, 4/25 ay pozitif).
SORU: bu "LONG genel olarak kotu" mu, yoksa BANDA OZGU mu?
Kontrol: her rejim icinde bantlar yan yana; ve LONG-SHORT FARKI (ayni barlar).
"""
import sys, os, collections, statistics as stx, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import A_bant as A
import ileri_rr as ir

def ay(ms):
    return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m")

hucre, _ = A.kostur()
rej = ir.btc_rejim()

def kumeli(v):
    a = collections.defaultdict(list)
    for net, sym, t in v: a[ay(t)].append(net)
    ok = [k for k in a if len(a[k]) >= 15]
    if len(ok) < 3: return None
    m = [stx.mean(a[k]) for k in ok]
    se = stx.stdev(m)/len(m)**0.5
    return stx.mean(m), (stx.mean(m)/se if se else 0.0), len(ok), sum(1 for x in m if x > 0)

print("KONTROL 1 — REJIM ICINDE bantlar (rejim karistiricisi sabitlenir)")
print("="*88)
print("%-9s %-6s %8s %10s %8s %8s"%("bant","rejim","N","ay ort %","ay-t","poz ay"))
for lo,hi,ad in A.BANTLAR:
    v = hucre.get((ad,"LONG"), [])
    if len(v) < 100: continue
    for r in ("AYI","NOTR","BOGA"):
        vv = [z for z in v if rej.get(z[2]//3600000,"NOTR")==r]
        if len(vv) < 100: 
            print("%-9s %-6s %8d   N yetersiz"%(ad,r,len(vv))); continue
        k = kumeli(vv)
        if k is None: print("%-9s %-6s %8d   ay yetersiz"%(ad,r,len(vv))); continue
        print("%-9s %-6s %8d %+10.3f %+8.2f %5d/%-3d"%(ad,r,len(vv),k[0],k[1],k[3],k[2]))
    print()

print()
print("KONTROL 2 — LONG eksi SHORT (AYNI barlar, yon farki)")
print("="*88)
print("Ayni giris anlarinda iki yonun farki: 'bu bantta yon secimi onemli mi'")
print("%-9s %10s %10s %10s"%("bant","LONG ay","SHORT ay","FARK"))
for lo,hi,ad in A.BANTLAR:
    l = hucre.get((ad,"LONG"), []); s = hucre.get((ad,"SHORT"), [])
    if len(l) < 100 or len(s) < 100: continue
    kl, ks = kumeli(l), kumeli(s)
    if not kl or not ks: continue
    print("%-9s %+10.3f %+10.3f %+10.3f"%(ad,kl[0],ks[0],kl[0]-ks[0]))
