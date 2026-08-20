# -*- coding: utf-8 -*-
"""IZ B — SABIT HEDEF mi, TAKIP EDEN STOP mu? Yonler arasi asimetri.

BULGU (yoklama): SABIT_HEDEF_KAPILARI = ("A+B","MA50+ucuz") -> SHORT'lar sabit
%10 hedef aliyor; LONG'lar (NOTR-belirsiz) yalniz trailing. Sonuc:
SHORT 29/103 hedefe ulasti, LONG 0/14. LONG kar etti, SHORT etmedi.

⚠️ ON-KAYIT NOTU: sabit %10 hedef, denenen 29 cikis varyantindan GECEN TEK
varyant (olcumler.md). Ters cikarsa bu gerilim RAPORLANIR, kural onerilmez.

TEST: ayni girisler, dort cikis mekanigi:
  1. sabit hedef %10 (SHORT'un bugunku hali)
  2. takip eden stop (LONG'un bugunku hali)
  3. sabit hedef + TP1'de yari (botun gercek hali)
  4. takip eden + sabit hedef birlikte
5dk mum · maliyet+fonlama · risk sabit.
"""
import sys, os, statistics as stx
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak

RISK = 75.0
STOP_PCT = 3.0          # tum varyantlarda AYNI baslangic stopu -> adil kiyas
HEDEF = 10.0
UFUK = 72
TRAIL_PCT = 3.0         # takip eden stop, en iyi fiyattan bu kadar geri


def oynat(p, mod):
    yon = p["yon"]
    g0 = ortak.dt(p["giris_ts"])
    b = ortak.mumlar(p["sym"])
    t0 = int(g0.timestamp() * 1000)
    ic = [x for x in b if x["t"] >= t0][:UFUK * 12]
    if len(ic) < 3: return None
    ref = ic[0]["o"]
    if ref <= 0: return None
    isS = yon == "SHORT"
    stop = ref * (1 + STOP_PCT/100) if isS else ref * (1 - STOP_PCT/100)
    hed = ref * (1 - HEDEF/100) if isS else ref * (1 + HEDEF/100)
    eniyi = ref
    yari_alindi = False
    kar = 0.0
    cj, ham = ic[-1], None
    for x in ic:
        # stop kontrolu (trailing dahil)
        if (x["h"] >= stop) if isS else (x["l"] <= stop):
            sp = ((stop - ref) if isS else (ref - stop)) / ref * 100
            ham = -sp if not yari_alindi else (-sp * 0.5 + kar)
            cj = x; break
        # hedef
        if mod in ("sabit", "sabit_tp1", "ikisi"):
            if (x["l"] <= hed) if isS else (x["h"] >= hed):
                if mod == "sabit_tp1" and not yari_alindi:
                    pass   # tam hedefe geldi, TP1 zaten gecilmis olurdu
                ham = HEDEF if not yari_alindi else (HEDEF*0.5 + kar)
                cj = x; break
        # TP1: hedefin yarisinda yarisini al, stopu basabasa cek
        if mod == "sabit_tp1" and not yari_alindi:
            tp1 = ref * (1 - HEDEF/200) if isS else ref * (1 + HEDEF/200)
            if (x["l"] <= tp1) if isS else (x["h"] >= tp1):
                yari_alindi = True
                kar = (HEDEF/2) * 0.5
                stop = ref
        # trailing
        if mod in ("trail", "ikisi"):
            eniyi = min(eniyi, x["l"]) if isS else max(eniyi, x["h"])
            yeni = eniyi * (1 + TRAIL_PCT/100) if isS else eniyi * (1 - TRAIL_PCT/100)
            stop = min(stop, yeni) if isS else max(stop, yeni)
    if ham is None:
        c = cj["c"]
        h2 = ((ref - c) if isS else (c - ref)) / ref * 100
        ham = h2 if not yari_alindi else (h2*0.5 + kar)
    fon = ortak.fonlama_pct(ortak.fonlama(p["sym"]), t0, cj["t"], yon)
    return ham - ortak.MALIYET_PCT + fon


def dolar(v): return v * (RISK / (STOP_PCT/100)) / 100


MODLAR = [("sabit hedef %10", "sabit"),
          ("takip eden stop %3", "trail"),
          ("sabit + TP1'de yari", "sabit_tp1"),
          ("ikisi birden", "ikisi")]

poz = ortak.poz_yukle("muhasebe_11agu")
print("IZ B — CIKIS MEKANIGI (ayni girisler, ayni %3 baslangic stopu)")
print("=" * 92)
print("UYARI: sabit hedef 29 cikis varyantindan gecen TEK varyant (olcumler.md).")
print("Bu test onu sorguluyor; ters cikarsa GERILIM raporlanir, kural onerilmez.\n")
for yon in ("SHORT", "LONG"):
    for dn, ad in ((None, "TUM"), ("oncesi", "sicrama ONCESI"), ("sonrasi", "sicrama SONRASI")):
        g = [p for p in poz if p["yon"] == yon and (dn is None or p["donem"] == dn)]
        if len(g) < 5: continue
        print("--- %s %s (N=%d, gercek %+.2f $)" % (yon, ad, len(g), sum(p["pnl"] for p in g)))
        for etiket, mod in MODLAR:
            v = [oynat(p, mod) for p in g]
            v = [x for x in v if x is not None]
            if not v: continue
            kz = sum(1 for x in v if x > 0)
            print("    %-22s %+9.2f $  islem basi %+6.3f%%  kazanan %2d/%2d (%%%.0f)"
                  % (etiket, sum(dolar(x) for x in v), stx.mean(v), kz, len(v), 100*kz/len(v)))
        print()
print("bot dosyalarina yazim: YOK")
