# -*- coding: utf-8 -*-
"""Ayna defteri temizligi — mukerrer kayitlarin silinmesi (2026-08-18).

VARSAYILAN: KURU KOSU. Hicbir sey silinmez. Yazmak icin acikca --uygula gerekir.

[NEDEN] ayna.py'de kilit yoktu; check-then-act ve lost-update yuzunden UC kayit
deftere yazildi ama equity etkileri GERI SARILDI. Defter bu yuzden equity'yi
+177,84 $ asiyor. Kok neden 2026-08-18'de kapatildi (ayna kilidi); bu betik
GECMIS veriyi duzeltir.

[SILME KURALI] "ikincisini sil" DEGIL -> "EQUITY ETKISI SILINEN kaydi sil".
Her biri equity logundan tek tek belirlendi (asagida kanit satirlariyla).

[GUVENLIK]
  - varsayilan kuru kosu, --uygula olmadan dosyaya dokunulmaz
  - once yedek alinir (.yedek-<damga>)
  - atomik yazim (.tmp + os.replace)
  - ONCE/SONRA mutabakat farki yazdirilir; SONRA ~0 degilse UYGULAMA IPTAL edilir
    (liste yanlissa yazmaktansa durmak yeglenir)
"""
import sys, os, json, shutil, datetime, argparse

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATEF = os.path.join(KOK, "ayna_state.json")
ISLEMLERF = os.path.join(KOK, "ayna_islemler.jsonl")

# (ts, sym, sonuc_usdt) — birebir eslesme; kanit equity logundan
SILINECEK = [
    ("2026-08-14 14:51:41", "BAS", 104.83,
     "cift kapanis — 14:51:54'te geri sarildi: 9.664,47 - 104,83 = 9.559,64, acik 6->7"),
    ("2026-08-14 19:44:34", "EDEN", -2.31,
     "cift kapanis — 19:44:36'da bayat yazim sildi: 9.665,65 + 45,83 (BICO) = 9.711,48"),
    ("2026-08-15 15:40:50", "MOVE", 75.33,
     "lost update — 15:40:52'de bayat taban: 9.991,32 - 76,99 (PLUME) = 9.914,33"),
]

# DOKUNULMAYACAK (kayda geciyor ki sonradan "atlanmis" sanilmasin)
DOKUNMA = [
    ("PLUME", "MUKERRER DEGIL. Defterde iki kez var ama FARKLI id (56 / 78). "
              "Kayip guncellemenin FAILI, kurbani degil."),
    ("BLESS", "+184,81 — mutabakat farkindan AYRI bir EKSIK GOZLEM. Golge sizintisi "
              "yuzunden botun gercek BLESS pozisyonu aynaya HIC dusmedi (ayna_state "
              "kayip_veri_notu). Kullanici o pozisyon icin karar VERMEDI, veri geri "
              "uretilemez. Eslesmis ayna-bot kiyasi tasarlanirken hesaba katilacak; "
              "defterden SILINECEK bir sey degil, EKLENEMEYECEK bir sey."),
]


def oku():
    return [json.loads(l) for l in open(ISLEMLERF, encoding="utf-8") if l.strip()]


def mutabakat(kayitlar):
    s = json.load(open(STATEF, encoding="utf-8"))
    defter = sum(r["sonuc_usdt"] for r in kayitlar)
    bek = (s["baslangic_bakiye"] + defter + s.get("kumulatif_funding", 0.0)
           - s.get("kumulatif_giris_ucret", 0.0))
    return s["equity"] - bek, defter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uygula", action="store_true", help="GERCEKTEN sil (varsayilan: kuru kosu)")
    a = ap.parse_args()

    kayitlar = oku()
    once, defter_once = mutabakat(kayitlar)
    print("=" * 72)
    print(f"ayna_islemler.jsonl : {len(kayitlar)} kayit")
    print(f"defter P&L toplami  : {defter_once:+.2f}")
    print(f"MUTABAKAT FARKI     : {once:+.2f}  (0'a inmeli)")
    print()

    print("SILINECEK (equity etkisi geri sarilmis olanlar):")
    kalan, silinen, bulunamayan = [], [], []
    hedef = {(t, s, round(v, 2)) for t, s, v, _ in SILINECEK}
    for r in kayitlar:
        anahtar = (r["ts"], r["sym"], round(r["sonuc_usdt"], 2))
        if anahtar in hedef and anahtar not in {(x["ts"], x["sym"], round(x["sonuc_usdt"], 2)) for x in silinen}:
            silinen.append(r)
        else:
            kalan.append(r)
    for t, s, v, nk in SILINECEK:
        var = any(x["ts"] == t and x["sym"] == s for x in silinen)
        print(f"  [{'BULUNDU' if var else 'YOK':>8}] {t}  {s:<6} {v:+8.2f}")
        print(f"             {nk}")
        if not var:
            bulunamayan.append((t, s))
    print(f"\n  toplam silinecek: {len(silinen)} kayit, "
          f"{sum(x['sonuc_usdt'] for x in silinen):+.2f} $")
    print()
    print("DOKUNULMAYACAK:")
    for sym, nk in DOKUNMA:
        print(f"  {sym:<6} {nk}")
    print()

    sonra, defter_sonra = mutabakat(kalan)
    print("=" * 72)
    print(f"ONCE  mutabakat farki : {once:+.2f}")
    print(f"SONRA mutabakat farki : {sonra:+.2f}   <- KONTROL")
    print(f"kalinti               : {sonra:+.2f}")
    tamam = abs(sonra) <= 0.05
    print(f"KONTROL: {'GECTI — liste dogru' if tamam else 'KALDI — LISTE YANLIS, uygulama iptal'}")

    if bulunamayan:
        print(f"\nUYARI: su kayitlar bulunamadi: {bulunamayan}")
        tamam = False

    if not a.uygula:
        print("\n[KURU KOSU] Hicbir sey silinmedi. Uygulamak icin: --uygula")
        return 0 if tamam else 1
    if not tamam:
        print("\n[IPTAL] Kontrol gecmedi -> dosyaya DOKUNULMADI.")
        return 1

    # [KILIT] Yazarken ayna turu araya girerse eszamanli bir ekleme KAYBOLUR
    #   (oku -> suz -> yaz deseninin ta kendisi). Ayni kilidi aliyoruz.
    sys.path.insert(0, KOK)
    import ayna
    if not ayna._kilit_al():
        print("\n[IPTAL] Ayna defteri mesgul (kilit alinamadi) — dosyaya DOKUNULMADI. "
              "Birkac saniye sonra tekrar dene.")
        return 1
    try:
        # kilit altinda YENIDEN oku: kuru kosudan bu yana kayit eklenmis olabilir
        taze = oku()
        if len(taze) != len(kayitlar):
            print(f"\n  NOT: kuru kosudan bu yana defter degisti "
                  f"({len(kayitlar)} -> {len(taze)} kayit). Kilit altindaki taze "
                  f"haliyle yeniden hesaplaniyor.")
            kalan = [r for r in taze
                     if (r["ts"], r["sym"], round(r["sonuc_usdt"], 2)) not in hedef]
            sonra2, _ = mutabakat(kalan)
            print(f"  taze mutabakat SONRA: {sonra2:+.2f}")
            if abs(sonra2) > 0.05:
                print("  [IPTAL] Taze kontrol gecmedi -> dosyaya DOKUNULMADI.")
                return 1
        damga = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        yedek = f"{ISLEMLERF}.yedek-{damga}"
        shutil.copy2(ISLEMLERF, yedek)
        gecici = ISLEMLERF + ".tmp"
        with open(gecici, "w", encoding="utf-8") as fh:
            for r in kalan:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            fh.flush(); os.fsync(fh.fileno())
        os.replace(gecici, ISLEMLERF)
        dogrula, _ = mutabakat(oku())
    finally:
        ayna._kilit_birak()
    print(f"\n[UYGULANDI] yedek: {os.path.basename(yedek)}")
    print(f"            diskten yeniden okundu, mutabakat farki: {dogrula:+.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
