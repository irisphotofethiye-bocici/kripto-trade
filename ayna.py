#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AYNA DEFTERI — dorduncu kasa (2026-08-12, kullanici karari).

SORDUGU SORU: "Botun girdigi pozisyonlari BEN karda gordugum yerde kapatsam,
    daha iyi olur muydum?"  Kullanicinin gercek hayatta yapmayi dusundugu sey bu.

NASIL CALISIR: bot bir pozisyon actiginda AYNISI buraya kopyalanir — ayni fiyat,
    ayni an, ayni boyut, ayni stop/TP. Sonra BOTUN KENDI KURALLARIYLA yonetilir.
    Yani sen dokunmadikca ayna, botun BIREBIR AYNISINI yapar.
    Tek yetkin: panelden "kapatirdim" demek.

    -> Fark yalnizca SENIN MUDAHALENDEN gelir. Kontrol grubu bedava gelir.

NEDEN AYRI KASA (dorduncusu):
    testbot : botun kendi kararlari ne yapiyor
    golge   : botun REDDETTIGI girisler ne yapardi
    benim   : BENIM SECTIGIM girisler ne yapiyor        (fark = GIRIS karari)
    ayna    : botun girislerinde BENIM CIKISIM ne yapardi (fark = CIKIS karari)
    Dordu de ayni cikis motorunu kullanir; her biri TEK degiskende ayrisir.
    benim.py'ye eklenemezdi: onun kurulus sarti "cikislar AYNI kalsin, fark yalniz
    giristen gelsin" — bu deney tam tersini yapiyor, ikisi tek defterde ayrilamaz.

RISK: YOK. Ayri kasa, ayri dosyalar, ayri equity. testbot'un state'ine dokunmaz.
    Tum cagrilar cagiran tarafta try/except icinde — ayna coker ise BOT ETKILENMEZ.
    Bildirim GONDERMEZ (golge ile ayni gerekce: olcum katmani insana aksiyon
    egilimi bulastirmamali).

BASLANGIC: ilk calistirmada botun O ANKI durumunun tam kopyasi alinir (equity +
    acik pozisyonlar + id'ler). Boylece iki defter AYNI NOKTADAN baslar ve
    equity egrileri dogrudan kiyaslanabilir; her ayrisma senin karariniddir.

Kullanim:  python ayna.py --durum
           python ayna.py --kur       (ilk kurulum: bottan anlik kopya)
           python ayna.py --kapat SYM (elle kapatma; normalde panelden)
"""
import json, os, sys, argparse, copy

import testbot

HERE = os.path.dirname(os.path.abspath(__file__))
STATEF = os.path.join(HERE, "ayna_state.json")
ISLEMLERF = os.path.join(HERE, "ayna_islemler.jsonl")
EQUITYF = os.path.join(HERE, "ayna_equity.jsonl")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def yukle():
    try:
        return json.load(open(STATEF, encoding="utf-8"))
    except Exception:
        return None


def kaydet(st):
    """ATOMIK yazma. [DERS 2026-08-12] golge.py duz json.dump kullaniyordu; bir tur
    kayitlari deftere yazdi ama durumu kaydedemedi -> ayni pozisyon iki kez kapandi
    ve defter 314$ sapti. Bu defter ilk gunden atomik."""
    gecici = STATEF + ".tmp"
    with open(gecici, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=2)
        fh.flush(); os.fsync(fh.fileno())
    os.replace(gecici, STATEF)


def _sessiz(*a, **kw):
    """Ayna defteri Telegram/toast GONDERMEZ — bunlar gercek karar degil, olcum."""
    return None


def _defterde(fn, *a, **kw):
    """testbot fonksiyonunu AYNA defterine yazacak + SESSIZ calistir.
    finally ile MUTLAKA geri alinir; yoksa botun kapanislari aynaya duser."""
    eski_defter = testbot._DEFTER
    eski_tg, eski_toast = testbot.telegram_gonder, testbot.toast_gonder
    testbot._DEFTER = ISLEMLERF
    testbot.telegram_gonder = _sessiz
    testbot.toast_gonder = _sessiz
    try:
        return fn(*a, **kw)
    finally:
        testbot._DEFTER = eski_defter
        testbot.telegram_gonder = eski_tg
        testbot.toast_gonder = eski_toast


def kur(zorla=False):
    """Botun O ANKI durumunun tam kopyasini alir. Iki defter ayni noktadan baslar."""
    var = yukle()
    if var and not zorla:
        return False, "Ayna defteri zaten kurulu (yeniden kurmak icin --kur --zorla)."
    bst = testbot._load_state()
    if not bst:
        return False, "Bot durumu okunamadi."
    st = {
        "baslangic_ts": testbot.now_iso(),
        "baslangic_bakiye": round(bst["equity"], 2),
        "equity": bst["equity"],
        "durum": "AKTIF",
        "acik_pozisyonlar": copy.deepcopy(bst["acik_pozisyonlar"]),
        "sonraki_id": bst["sonraki_id"],
        "cooldown": {}, "bekleyenler": {},
        "son_cycle_ts": None,
        "kumulatif_giris_ucret": 0.0, "kumulatif_funding": 0.0,
        "kaynak_not": ("Bottan anlik kopya. Kopyalanan acik pozisyonlarin gecmisi "
                       "(TP1 kismileri) botun defterinde; buradaki equity o karlari "
                       "ZATEN icerir cunku botun gerceklesmis equity'sinden baslandi."),
    }
    for p in st["acik_pozisyonlar"]:
        p["ayna_kaynak"] = "kurulum_kopyasi"
    kaydet(st)
    equity_yaz(st)
    return True, (f"Ayna kuruldu — equity ${st['equity']:.2f}, "
                  f"{len(st['acik_pozisyonlar'])} pozisyon kopyalandi.")


def aynala(bot_pos):
    """testbot bir GIRIS actiginda cagrilir. Pozisyonun BIREBIR kopyasini aynaya koyar.
    Fiyat/boyut/stop/TP yeniden HESAPLANMAZ — kopyalanir; yoksa 'ayni islem' olmaz."""
    st = yukle()
    if not st or st.get("durum") != "AKTIF":
        return False
    if any(p["sym"] == bot_pos["sym"] for p in st["acik_pozisyonlar"]):
        return False
    p = copy.deepcopy(bot_pos)
    p["ayna_kaynak"] = "bot_girisi"
    st["acik_pozisyonlar"].append(p)
    st["sonraki_id"] = max(st.get("sonraki_id", 1), bot_pos["id"] + 1)
    kaydet(st)
    equity_yaz(st)
    return True


def kapat(sym):
    """Kullanicinin TEK yetkisi: 'ben burada kapatirdim'. Piyasa fiyatindan kapatir.
    Bot ETKILENMEZ — botun ayni pozisyonu kendi kaderini yasamaya devam eder."""
    sym = str(sym).upper().strip()
    st = yukle()
    if not st:
        return False, "Ayna defteri kurulu degil."
    pos = next((p for p in st["acik_pozisyonlar"] if p["sym"] == sym), None)
    if not pos:
        return False, f"Aynada {sym} adinda acik pozisyon yok."
    px = testbot.fiyat_fapi(sym)
    if not px:
        return False, "Anlik fiyat alinamadi, kapatma yapilmadi."
    kayit = _defterde(testbot.pozisyon_kapat, st, pos, px, "ELLE_KAPAT")
    st["acik_pozisyonlar"] = [p for p in st["acik_pozisyonlar"] if p["sym"] != sym]
    kaydet(st)
    equity_yaz(st)
    pnl = kayit["sonuc_usdt"] if kayit else 0.0
    return True, f"{sym} aynada kapatildi ({pnl:+.2f}$). Botun pozisyonu devam ediyor."


def tur():
    """testbot.cycle() sonunda cagrilir. Acik ayna pozisyonlarini BOTLA AYNI
    kurallarla yonetir. Yeni giris ARAMAZ — girisler yalnizca aynala()'dan gelir."""
    st = yukle()
    if not st:
        return
    if st["acik_pozisyonlar"]:
        _defterde(testbot.yonet_acik_pozisyonlar, st)
    st["son_cycle_ts"] = testbot.now_iso()
    kaydet(st)
    equity_yaz(st)


def equity_yaz(st):
    try:
        testbot._append_jsonl(EQUITYF, {
            "ts": testbot.now_iso(), "equity": round(st["equity"], 2),
            "acik_pnl": round(testbot.acik_pnl_toplam(st), 2),
            "acik_sayisi": len(st["acik_pozisyonlar"])})
    except Exception:
        pass


def karne():
    """Ayna vs bot, id uzerinden eslestirerek.

    [EKSIK VE ONARIMI 2026-08-12] Eskiden yalnizca IKISINDE DE KAPANMIS islemler
    donuyordu; kullanici 5 karar verdiyse ve bunlarin 3'u BOTTA HALA ACIKSA panelde
    yalnizca 2 satir gorunuyordu ("aynada kapatilmis 2 poz goruyorum"). Verilen karar
    kaybolmus gibi duruyordu. Artik ucu de donuyor:
      kesin   : ikisinde de kapandi -> fark GERCEKLESTI
      bekleyen: aynada kapandi, botta ACIK -> fark henuz belirsiz (canli PnL panelde)
    'elle_fark' YALNIZ kesinlesenleri toplar; bekleyenler karari kirletmez."""
    try:
        ay = [json.loads(l) for l in open(ISLEMLERF, encoding="utf-8") if l.strip()]
        bo = [json.loads(l) for l in open(testbot.ISLEMLERF, encoding="utf-8") if l.strip()]
    except Exception:
        return None
    bst = testbot._load_state() or {}
    bot_acik = {p["id"]: p for p in (bst.get("acik_pozisyonlar") or [])}
    ay = [k for k in ay if not k.get("kismi")]
    bo_kapali = {k["id"]: k for k in bo if not k.get("kismi")}

    kesin, bekleyen = [], []
    for k in ay:
        ortak = {"id": k["id"], "sym": k["sym"], "yon": k["yon"],
                 "ayna_sebep": k["sebep"], "ayna": k["sonuc_usdt"], "ayna_ts": k["ts"]}
        b = bo_kapali.get(k["id"])
        if b and b["sym"] == k["sym"]:
            kesin.append({**ortak, "bot_sebep": b["sebep"], "bot": b["sonuc_usdt"],
                          "fark": round(k["sonuc_usdt"] - b["sonuc_usdt"], 2),
                          "bot_ts": b["ts"], "durum": "kesin"})
        elif k["id"] in bot_acik and bot_acik[k["id"]]["sym"] == k["sym"]:
            p = bot_acik[k["id"]]
            bekleyen.append({**ortak, "durum": "bekliyor", "bot_sebep": "ACIK",
                             "bot_giris": p["giris"], "bot_miktar": p["miktar"],
                             "bot_tp2": p.get("tp2"), "bot_stop": p.get("stop")})
        else:
            # botta ne acik ne kapali (orn. kurulum oncesi kapanmis) -> eslesemez
            bekleyen.append({**ortak, "durum": "eslesmedi", "bot_sebep": "?"})

    elle_kesin = [e for e in kesin if e["ayna_sebep"] == "ELLE_KAPAT"]
    return {"esli": kesin, "elle": elle_kesin, "bekleyen": bekleyen,
            "elle_fark": round(sum(e["fark"] for e in elle_kesin), 2),
            "tum_fark": round(sum(e["fark"] for e in kesin), 2),
            "kazandiran": sum(1 for e in elle_kesin if e["fark"] > 0),
            "kaybettiren": sum(1 for e in elle_kesin if e["fark"] < 0),
            "karar_sayisi": sum(1 for k in ay if k["sebep"] == "ELLE_KAPAT")}


def durum():
    st = yukle()
    if not st:
        print("AYNA DEFTERI kurulu degil.  Kurmak icin: python ayna.py --kur")
        return
    bst = testbot._load_state() or {}

    def _acik_pnl(s):
        t = 0.0
        for p in (s.get("acik_pozisyonlar") or []):
            px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
            t += (px - p["giris"]) * p["miktar"] * (1 if p["yon"] == "LONG" else -1)
        return t

    print("=== AYNA DEFTERI — botun girislerinde BENIM CIKISIM ===")
    print(f"Baslangic {st['baslangic_ts']}  |  ${st['baslangic_bakiye']:.2f} -> ${st['equity']:.2f}")
    if bst:
        # [ONARIM 2026-08-12] Eskiden GERCEKLESMIS equity'ler kiyaslaniyordu; ayna
        # kapatinca kari bankaya yazdigi, botunki hala acik oldugu icin bu YANILTICIYDI
        # (isaret bile ters donuyordu: +220$ gorunurken gercek -210$). Efektif kiyas.
        ae, be = st["equity"] + _acik_pnl(st), bst.get("equity", 0) + _acik_pnl(bst)
        print(f"EFEKTIF (acik K/Z dahil)  ayna ${ae:.2f}  vs  bot ${be:.2f}   "
              f"fark {ae - be:+.2f}$")
        print("  (gerceklesmis equity'leri dogrudan kiyaslamak yanlis olur — ayna kapattigi")
        print("   anda kari yazar, botun ayni pozisyonu hala acik. Karne KESINLESENDEN okunur.)")
    print(f"Acik ayna pozisyonu: {len(st['acik_pozisyonlar'])}")
    for p in st["acik_pozisyonlar"]:
        print(f"   {p['sym']:10} {p['yon']:5} giris {p['giris']:<12} "
              f"stop {p['stop']:<12} tp2 {p.get('tp2')}  [{p.get('ayna_kaynak','')}]")
    k = karne()
    if not k or not (k["esli"] or k["bekleyen"]):
        print("\nHenuz karar verilmedi.")
        return
    print(f"\nVERDIGIN KARAR: {k['karar_sayisi']}  |  kesinlesen: {len(k['elle'])}  "
          f"|  bekleyen: {len(k['bekleyen'])}")
    print(f"{'id':>4} {'coin':10}{'AYNA':>22}{'BOT':>22}{'FARK':>10}")
    print("-" * 72)
    for e in k["esli"]:
        print(f"{e['id']:>4} {e['sym']:10}{e['ayna_sebep']:>12}{e['ayna']:+10.2f}"
              f"{e['bot_sebep']:>12}{e['bot']:+10.2f}{e['fark']:+10.2f}")
    for e in k["bekleyen"]:
        canli = ""
        if e["durum"] == "bekliyor":
            px = testbot.fiyat_fapi(e["sym"])
            if px:
                isaret = 1 if e["yon"] == "LONG" else -1
                canli = f"{(px - e['bot_giris']) * e['bot_miktar'] * isaret:+10.2f}"
        print(f"{e['id']:>4} {e['sym']:10}{e['ayna_sebep']:>12}{e['ayna']:+10.2f}"
              f"{e['bot_sebep']:>12}{canli:>10}{'   (bekliyor)' if e['durum']=='bekliyor' else '   (eslesmedi)'}")
    print("-" * 72)
    print(f"KESINLESEN net fark: {k['elle_fark']:+.2f}$   "
          f"({k['kazandiran']} kazandirdi / {k['kaybettiren']} kaybettirdi)")
    print("  (+) = elle kapatmak DAHA IYIYDI   (-) = botu birakmak daha iyiydi")
    if k["bekleyen"]:
        print("  Bekleyenler bot kapanana kadar karneye GIRMEZ (canli sayilar gerceklesmedi).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--durum", action="store_true")
    ap.add_argument("--kur", action="store_true")
    ap.add_argument("--zorla", action="store_true")
    ap.add_argument("--tur", action="store_true")
    ap.add_argument("--kapat", metavar="SYM")
    a = ap.parse_args()
    if a.kur:
        print(kur(a.zorla)[1])
    elif a.kapat:
        print(kapat(a.kapat)[1])
    elif a.tur:
        tur(); print("ayna turu tamam")
    else:
        durum()


if __name__ == "__main__":
    main()
