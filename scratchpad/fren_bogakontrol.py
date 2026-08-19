# -*- coding: utf-8 -*-
"""BOGA bulgusunun KARISTIRICI KONTROLU — POST-HOC, on-kayitta YOKTU.

CLAUDE.md: "monotonluk/isaret tek basina YETMEZ". Ust hukum yazildiktan
SONRA, hukmu DEGISTIRMEMEK sartiyla saglamlik sorulur:
  (a) BOGA x UST hucresi takvimde kumeleniyor mu? (ay ay kirilim)
  (b) lift kac ayda pozitif? (tek bir doneme mi dayaniyor)
"""
import sys, os, collections, statistics as stx, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import btcpay_fren_rejim as F
import btcpay_rejim as bp

hucre, _ = F.kostur()
p = hucre.get(("BOGA", "UST"), [])
d = hucre.get(("BOGA", "diger"), [])


def ay(ts):
    return datetime.datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m")


ap = collections.defaultdict(list)
ad = collections.defaultdict(list)
for n, s, t in p:
    ap[ay(t)].append(n)
for n, s, t in d:
    ad[ay(t)].append(n)

print("BOGA hucresi — AY AY kirilim (post-hoc saglamlik, hukum DEGISMEZ)")
print("=" * 72)
print("%-9s %7s %9s %7s %9s %9s" % ("ay", "N_UST", "UST%", "N_dig", "diger%", "lift"))
poz = neg = 0
for k in sorted(set(ap) | set(ad)):
    a, b = ap.get(k, []), ad.get(k, [])
    if len(a) < 20 or len(b) < 20:
        print("%-9s %7d %9s %7d %9s      (N az)" % (k, len(a), "-", len(b), "-"))
        continue
    li = stx.mean(a) - stx.mean(b)
    poz += li > 0
    neg += li < 0
    print("%-9s %7d %+8.3f %7d %+8.3f %+9.3f %s"
          % (k, len(a), stx.mean(a), len(b), stx.mean(b), li, "<--" if li < 0 else ""))
print()
print("lift POZITIF ay: %d · NEGATIF ay: %d" % (poz, neg))
print("BOGA x UST toplam N=%d, %d ayrik ay, %d ayri sembol"
      % (len(p), len(ap), len(set(s for _, s, _ in p))))
en = max(ap.items(), key=lambda kv: len(kv[1]))
print("EN BUYUK ay: %s -> N=%d (%%%.1f)  <-- tek ay hakimiyeti kontrolu"
      % (en[0], len(en[1]), 100 * len(en[1]) / len(p)))

# en buyuk ay ATILDIGINDA lift ne oluyor
qa = [n for k, v in ap.items() if k != en[0] for n in v]
qb = [n for k, v in ad.items() if k != en[0] for n in v]
if len(qa) >= 40 and len(qb) >= 40:
    f, t = bp.iki_ornek(qa, qb)
    print("EN BUYUK ay ATILINCA: lift %+.3f%%  iki-ornekli t=%+.2f  (N %d vs %d)"
          % (f, t, len(qa), len(qb)))


# --- EK: BASKIN ay (lifte en cok katkiyi veren) atilinca ne oluyor ---
print()
print("=" * 72)
print("BASKIN AY testi — en cok N'li ay degil, LIFTE en cok katkiyi veren ay")
kat = {}
for k in set(ap) & set(ad):
    a, b = ap[k], ad[k]
    if len(a) >= 20 and len(b) >= 20:
        kat[k] = (stx.mean(a) - stx.mean(b)) * len(a)      # agirlikli katki
for k, v in sorted(kat.items(), key=lambda kv: -kv[1]):
    print("   %s katki %+9.1f  (lift %+.3f x N %d)" % (k, v, v / len(ap[k]), len(ap[k])))
bas = max(kat, key=lambda k: kat[k])
qa = [n for k, v in ap.items() if k != bas for n in v]
qb = [n for k, v in ad.items() if k != bas for n in v]
f, t = bp.iki_ornek(qa, qb)
print("\n%s ATILINCA: lift %+.3f%%  iki-ornekli t=%+.2f  (N %d vs %d)"
      % (bas, f, t, len(qa), len(qb)))
print("ON-KAYITLI ust hukum: lift +0.817%%, t=+6.07 -> 'fren BOGA'da ZARARLI'")
print("TEK AY cikinca hukum %s" % ("AYAKTA" if f > 0 and t > 2.0 else "COKUYOR"))

# --- AY duzeyinde kumelenmis bakis: bagimsiz birim SEMBOL degil AY/EPIZOT ---
li = [stx.mean(ap[k]) - stx.mean(ad[k]) for k in sorted(kat)]
print("\nAY duzeyinde lift dizisi: %s" % ", ".join("%+.3f" % x for x in li))
print("ay sayisi %d · ortalama %+.3f · medyan %+.3f · pozitif %d/%d"
      % (len(li), stx.mean(li), stx.median(li), sum(1 for x in li if x > 0), len(li)))
if len(li) > 1:
    se = stx.stdev(li) / len(li) ** 0.5
    print("AY-KUMELI t = %+.2f   <-- bagimsiz birim AY alinirsa" % (stx.mean(li) / se))
