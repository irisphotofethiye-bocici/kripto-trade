#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FONLAMA OKUYUCU — birim karismasini ARACLA kapatir.

NEDEN VAR (2026-08-21/24 hatasi):
   Projede fonlama IKI ayri onbellekte, AYNI alan adiyla, FARKLI birimde:
      scratchpad/funding_gecmis/        r = YUZDE    (funding_indir.py:67 zaten *100)
      scratchpad/short_kayip/fonlama/   r = ONDALIK  (short_kayip/ortak.py:82 ham)
   Alan adi (`r`) birimi TASIMIYOR. 14 betik funding_gecmis'i okuyup bir kez daha
   *100 uyguladi -> fonlama 100 KAT sisti. py_compile ve pyflakes gormez:
   sozdizimi dogru, isim tanimli, sadece SAYI yanlis.
   Yakalayan sey buyukluk mantigi oldu; bu modul o mantigi ZORUNLU kilar.

KULLANIM:
   import fonlama_oku
   ft, fr = fonlama_oku.yukle("BTC")        # fr YUZDE cinsinden, dogrulanmis
   pct    = fonlama_oku.dilim(ft, fr, t0, t1, "SHORT")

⚠️ DONEN DEGER ZATEN YUZDEDIR. Uzerine *100 UYGULAMA.
"""
# [2026-08-25] cp1254 TUZAGI — kalici kapatma.
#   Windows konsolu cp1254; print() icindeki emoji/varyasyon secici CIKTI
#   YONLENDIRILDIGINDE UnicodeEncodeError firlatiyor ve betik COKUYOR.
#   Bu sinif bu projede BES kez isirdi. Emoji ayiklamak yerine stdout
#   guvenli hale getirilir; hata sinifi disiplinle degil ARACLA kapanir.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, json, bisect, statistics as sx

HERE = os.path.dirname(os.path.abspath(__file__))
FON_DIR = os.path.join(HERE, "funding_gecmis")

# Binance fonlama orani tavani cogu sembolde %+-2, bazilarinda %+-0,3 / %+-0,75.
# YUZDE cinsinden medyan mutlak deger her zaman bunun cok altindadir (~0,005).
# ONDALIK olsaydi medyan ~0,00005 olurdu; 100 KAT SISIRILMIS olsaydi ~0,5.
# ESIKLER — 567 sembolde OLCULDU: sifir-olmayan medyan |r| araligi 0,005..0,010 (yuzde).
#   100 KAT sisirilmis olsaydi  -> 0,5 .. 1,0
#   ONDALIK birakilmis olsaydi  -> 0,00005 .. 0,0001
#   Esikler iki tarafa da ~10 kat pay birakacak sekilde ORTAYA konuldu.
# ⚠️ ILK SURUMDE ESIKLER SINIRDAYDI (0,5 ve 0,00002) ve sentetik bozuk veriyi
#   YAKALAMADI: 0,5 > 0,5 yanlis, 0,00005 < 0,00002 yanlis. Kendi sinamasi yakaladi.
MEDYAN_UST = 0.15     # bunun ustu -> 100 kat sisirilmis
MEDYAN_ALT = 0.0005   # bunun alti -> ondalik birakilmis (yuzdeye cevrilmemis)
MUTLAK_TAVAN = 10.0   # tek bir oran bunu asamaz (tavan %2, pay birakildi)


class BirimHatasi(ValueError):
    """Fonlama verisi beklenen BIRIMDE degil."""


def dogrula(oranlar, kaynak=""):
    """oranlar YUZDE cinsinden mi? Degilse BirimHatasi firlatir.

    ⚠️ MEDYAN SIFIR OLANLAR: tokenize hisseler (ASTS · INTC ...) fonlama
       ODEMIYOR, kayitlarin cogu tam 0. Ham medyan alinirsa 0 cikar ve
       "ondalik birakilmis" sanilir — ilk surumde bu YANLIS POZITIF uretti
       (3/40 sembol). Bu yuzden medyan SIFIR OLMAYAN degerler uzerinden alinir."""
    v = [abs(x) for x in oranlar if isinstance(x, (int, float))]
    if len(v) < 20:
        return                      # ornek yetersiz, sessizce gec
    enb = max(v)
    sifirsiz = [x for x in v if x > 0]
    if len(sifirsiz) < 20:
        # neredeyse tamami sifir -> birim cikarilamaz, yalniz TAVAN kontrolu
        if enb > MUTLAK_TAVAN:
            raise BirimHatasi("%s: tek oran fonlama tavanini asiyor (max |r| = %.4f > %.1f)."
                              % (kaynak, enb, MUTLAK_TAVAN))
        return
    med = sx.median(sifirsiz)
    if med > MEDYAN_UST:
        raise BirimHatasi(
            "%s: fonlama SISIRILMIS gorunuyor (medyan |r| = %.6f > %.2f). "
            "funding_gecmis ZATEN yuzde -> fazladan *100 uygulanmis olabilir."
            % (kaynak, med, MEDYAN_UST))
    if med < MEDYAN_ALT:
        raise BirimHatasi(
            "%s: fonlama ONDALIK gorunuyor (medyan |r| = %.8f < %.5f). "
            "Yuzdeye cevrilmemis." % (kaynak, med, MEDYAN_ALT))
    if enb > MUTLAK_TAVAN:
        raise BirimHatasi(
            "%s: tek oran fonlama tavanini asiyor (max |r| = %.4f > %.1f)."
            % (kaynak, enb, MUTLAK_TAVAN))


_ONBELLEK = {}


def yukle(sym):
    """-> (ts_listesi_ms, oran_listesi_YUZDE). Dosya yoksa ([], [])."""
    if sym in _ONBELLEK:
        return _ONBELLEK[sym]
    yol = os.path.join(FON_DIR, "%s.json" % sym)
    ft, fr = [], []
    if os.path.exists(yol):
        try:
            with open(yol, encoding="utf-8") as f:
                d = json.load(f)
            ft = [int(x["t"]) for x in d]
            fr = [float(x["r"]) for x in d]          # ZATEN YUZDE — *100 YOK
            dogrula(fr, kaynak="funding_gecmis/%s.json" % sym)
        except BirimHatasi:
            raise
        except Exception:
            ft, fr = [], []
    _ONBELLEK[sym] = (ft, fr)
    return ft, fr


def dilim(ft, fr, t0_ms, t1_ms, yon):
    """[t0,t1] arasinda kesilen fonlamanin POZISYON LEHINE isaretli toplami (yuzde).

    SHORT: oran pozitifse short TAHSIL eder (+).  LONG: oran pozitifse LONG ODER (-)."""
    if not ft:
        return 0.0
    i = bisect.bisect_right(ft, t0_ms)
    j = bisect.bisect_right(ft, t1_ms)
    s = sum(fr[k] for k in range(i, j))
    return s if yon == "SHORT" else -s


if __name__ == "__main__":
    import random
    d = sorted(f[:-5] for f in os.listdir(FON_DIR) if f.endswith(".json"))
    print("funding_gecmis: %d sembol" % len(d))
    random.seed(3)
    hata = 0
    for s in random.sample(d, min(40, len(d))):
        try:
            ft, fr = yukle(s)
            if fr:
                print("  %-12s n=%5d  medyan |r| = %.6f%%  max |r| = %.4f%%"
                      % (s, len(fr), sx.median(abs(x) for x in fr), max(abs(x) for x in fr)))
        except BirimHatasi as e:
            hata += 1
            print("  %-12s BIRIM HATASI: %s" % (s, e))
    print("\nbirim hatasi: %d / 40" % hata)
