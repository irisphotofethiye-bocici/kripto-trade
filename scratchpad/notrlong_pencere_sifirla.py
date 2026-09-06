#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""notrlong PENCERE-2 SIFIRLAMA (2026-09-06, KULLANICI KARARI)

Kullanici: 'botu sifirlamamissin, paneli'.
Belge duzeyinde sifirlama panelde gorunmuyordu; GERCEK sifirlama yapiliyor.

🔴 ON KOSUL: KriptoNotrLong gorevi DEVRE DISI ve kosan tur BITMIS olmali.
   (check-then-act tuzagi — CLAUDE.md mimari tuzaklar.)

NE YAPAR
  1) state ve defterlerin YEDEGINI alir  (SILME YOK)
  2) defterleri  *_pencere1.jsonl  olarak ARSIVLER (tasir, silmez)
  3) state'i PENCERE-2 icin kurar: kasa 10.000, zirve 10.000, ucret 0,
     baslangic_ts = simdi, sonraki_id = 1
  4) cooldown / son_giris KORUNUR (ORCA 4 saatlik bekleme hakkini kaybetmesin)
  5) ATOMIK yazar (.tmp + os.replace) — CLAUDE.md kurali
  6) yazdiktan sonra DOGRULAR

Acik pozisyon varsa CALISMAYI REDDEDER.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, shutil, io
import datetime as dt

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATEF = os.path.join(KOK, "notrlong_state.json")
DEFTERLER = ["notrlong_islemler.jsonl", "notrlong_equity.jsonl",
             "notrlong_veto.jsonl", "notrlong_elenen.jsonl"]
YENI_KASA = 10000.0


def main():
    damga = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    st = json.load(io.open(STATEF, encoding="utf-8", errors="replace"))

    print("=" * 84)
    print("notrlong PENCERE-2 SIFIRLAMA")
    print("=" * 84)
    print("ONCE:")
    print("   durum            : %s" % st.get("durum"))
    print("   equity           : %.2f" % st.get("equity", 0))
    print("   baslangic_bakiye : %.2f" % st.get("baslangic_bakiye", 0))
    print("   baslangic_ts     : %s" % st.get("baslangic_ts"))
    print("   acik pozisyon    : %d" % len(st.get("acik_pozisyonlar", [])))
    print("   sonraki_id       : %s" % st.get("sonraki_id"))

    if st.get("acik_pozisyonlar"):
        print()
        print("🔴 ACIK POZISYON VAR -> REDDEDILDI. Once pozisyonlar kapanmali.")
        return 1

    # 1) YEDEK
    yed = os.path.join(KOK, "yedek_pencere1_%s" % damga)
    os.makedirs(yed, exist_ok=True)
    shutil.copy2(STATEF, os.path.join(yed, os.path.basename(STATEF)))
    n_yedek = 1
    for f in DEFTERLER:
        p = os.path.join(KOK, f)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(yed, f))
            n_yedek += 1
    print()
    print("1) YEDEK   : %s  (%d dosya)" % (os.path.basename(yed), n_yedek))

    # 2) ARSIVLE (tasi, silme)
    print("2) ARSIVLE :")
    for f in DEFTERLER:
        p = os.path.join(KOK, f)
        if not os.path.exists(p):
            print("      %-28s (yok)" % f)
            continue
        n = sum(1 for l in io.open(p, encoding="utf-8", errors="replace") if l.strip())
        hedef = os.path.join(KOK, f.replace(".jsonl", "_pencere1.jsonl"))
        if os.path.exists(hedef):          # daha once arsivlenmisse ekle
            with io.open(hedef, "a", encoding="utf-8") as h, \
                 io.open(p, encoding="utf-8", errors="replace") as k:
                h.write(k.read())
            os.remove(p)
        else:
            os.replace(p, hedef)
        print("      %-28s -> %s  (%d satir)" % (f, os.path.basename(hedef), n))

    # 3) YENI STATE
    yeni = dict(st)
    yeni["baslangic_ts"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yeni["baslangic_bakiye"] = YENI_KASA
    yeni["equity"] = YENI_KASA
    yeni["zirve"] = YENI_KASA
    yeni["kumulatif_giris_ucret"] = 0.0
    yeni["sonraki_id"] = 1
    yeni["durum"] = "AKTIF"
    yeni["acik_pozisyonlar"] = []
    yeni["bekleyenler"] = {}
    # cooldown / son_giris / veto_cooldown KORUNUR (bekleme haklari kaybolmasin)

    tmp = STATEF + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(yeni, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATEF)                # ATOMIK
    print("3) STATE   : atomik yazildi (.tmp + os.replace)")

    # 4) DOGRULA
    k = json.load(io.open(STATEF, encoding="utf-8", errors="replace"))
    print()
    print("SONRA:")
    print("   durum            : %s" % k.get("durum"))
    print("   equity           : %.2f" % k.get("equity", 0))
    print("   baslangic_bakiye : %.2f" % k.get("baslangic_bakiye", 0))
    print("   baslangic_ts     : %s" % k.get("baslangic_ts"))
    print("   zirve            : %.2f" % k.get("zirve", 0))
    print("   giris ucreti     : %.2f" % k.get("kumulatif_giris_ucret", 0))
    print("   sonraki_id       : %s" % k.get("sonraki_id"))
    print("   cooldown korundu : %d kayit" % len(k.get("cooldown", {})))
    tamam = (abs(k.get("equity", 0) - YENI_KASA) < 1e-9
             and abs(k.get("baslangic_bakiye", 0) - YENI_KASA) < 1e-9
             and k.get("sonraki_id") == 1
             and not os.path.exists(os.path.join(KOK, "notrlong_islemler.jsonl")))
    print()
    print("DOGRULAMA: %s" % ("✔ TAMAM" if tamam else "✘ EKSIK VAR"))
    print("Yedek: %s" % yed)
    return 0 if tamam else 1


if __name__ == "__main__":
    _sys.exit(main())
