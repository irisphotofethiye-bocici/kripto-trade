#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOLGE DEFTER — botun REDDETTIGI girislerin sanal karnesi (2026-08-10, kullanici karari:
"bot girmedigi surece olcemeyiz, bu durumu coz").

PROBLEM: bot 7 gunde 1141 tur kostu, 234 kez yon karari/veto uretti ve 3 GUNDUR hic
  islem acmadi. Kapilar (rr_veto / blowoff / taker_soguma / long_veto / btc_pay_freni /
  onay_bekle) calisiyor ama HICBIRININ HAKLI OLUP OLMADIGI OLCULEMIYOR — cunku olcum
  yalnizca ACILAN islemlerden geliyordu. Bir kapinin degeri "neyi engelledigi" ile
  olculur; engelledigi sey kaydedilmezse kapi sorgulanamaz hale gelir.

COZUM: her RED bir olcum olayina cevrilir. Bot bir girisi reddettiginde ayni giris
  BURADA sanal olarak acilir (olcucu'nun AYNI giris/stop/tp1/tp2 seviyeleriyle, botun
  AYNI cikis kurallariyla, AYNI risk-once boyutlandirmasiyla) ve sonuna kadar takip
  edilir. Birkac hafta sonra kapi bazinda karne cikar:
      "rr_veto'nun reddettigi 40 islem ortalama -0.6R getirdi"  -> kapi HAKLI, dokunma
      "rr_veto'nun reddettigi 40 islem ortalama +0.5R getirdi"  -> kapi PARA YAKIYOR

NEDEN KAPI GEVSETMEK DEGIL DE BU: gerceklestirilmemis girisin sonucu OLCULEBILIR bir
  seydir; olculebilen seyi tahmin etmek yerine olcmek gerekir. Kapiyi once gevsetip
  sonra bakmak, gercek (sanal da olsa) sermayeyi hipoteze yatirmaktir; bu defterde
  ise hipotez BEDAVA test edilir. Karar kapilarinda HICBIR DEGISIKLIK YAPILMADI.

RISK: YOK. Ayri kasa, ayri dosyalar, ayri equity. testbot'un state'ine dokunmaz.
  Tum cagrilar cagiran tarafta try/except icinde — golge coker ise BOT ETKILENMEZ.

TASARIM (benim.py deseni): yonetim mantigi KOPYALANMAZ, testbot'un kendi fonksiyonlari
  cagrilir; yalnizca defter yolu ve bildirim fonksiyonlari gecici olarak degistirilir
  (finally ile geri alinir). Cikis kurallari birebir ayni olsun ki fark YALNIZCA
  "kapi acti mi kapatti mi" sorusundan gelsin.

Kullanim:  python golge.py --durum     (kapi bazinda karne)
           python golge.py --acik      (acik golge pozisyonlar)
"""
import json, os, sys, argparse

import testbot

HERE = os.path.dirname(os.path.abspath(__file__))
STATEF = os.path.join(HERE, "golge_state.json")
ISLEMLERF = os.path.join(HERE, "golge_islemler.jsonl")
EQUITYF = os.path.join(HERE, "golge_equity.jsonl")

# Ayni kurulumu tekrar tekrar kaydetme (08-08'de KMNO 90 dakikada 19 kez ayni redi aldi;
# 19 kayit = 1 olayin 19 kez sayilmasi = sahte N). Sembol basina bu kadar saat gecmeden
# yeni golge acilmaz — botun kendi 4 saatlik cooldown'u ile ayni buyukluk.
TEKRAR_SAAT = 4.0
MAKS_ACIK = 20          # botun 4'lu limiti burada gecerli degil: amac olcum, sermaye degil


def yeni_state():
    return {"baslangic_ts": testbot.now_iso(), "baslangic_bakiye": 10000.0,
            "equity": 10000.0, "durum": "AKTIF", "acik_pozisyonlar": [],
            "sonraki_id": 1, "cooldown": {}, "bekleyenler": {}, "son_golge": {},
            "son_cycle_ts": None}


def yukle():
    try:
        return json.load(open(STATEF, encoding="utf-8"))
    except Exception:
        return None


def kaydet(st):
    json.dump(st, open(STATEF, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _sessiz(*a, **kw):
    """Golge girisleri/cikislari Telegram/toast GONDERMEZ — bunlar gercek karar degil,
    olcum. Bildirim maliyeti dursturlugu (Karmasiklik Butcesi md.4): alarm insana
    aksiyon egilimi bulastirir; golge defterin tamami sessiz olmali."""
    return None


def _defterde(fn, *a, **kw):
    """testbot fonksiyonunu GOLGE defterine yazacak + SESSIZ calistir.
    finally ile MUTLAKA geri alinir; yoksa botun kapanislari golgeye duser."""
    eski_defter, eski_tg, eski_toast = testbot._DEFTER, testbot.telegram_gonder, testbot.toast_gonder
    testbot._DEFTER = ISLEMLERF
    testbot.telegram_gonder = _sessiz
    testbot.toast_gonder = _sessiz
    try:
        return fn(*a, **kw)
    finally:
        testbot._DEFTER = eski_defter
        testbot.telegram_gonder = eski_tg
        testbot.toast_gonder = eski_toast


def _tekrar_var_mi(st, sym):
    son = (st.get("son_golge") or {}).get(sym)
    if not son:
        return False
    try:
        return (testbot.now_dt() - testbot.parse_iso(son)).total_seconds() / 3600 < TEKRAR_SAAT
    except Exception:
        return False


# [DENETIM DUZELTMESI 2026-08-11, Bulgu 6] Golge TUM tezleri zorla=True ile aciyordu; bu
#   rr kapisini, asgari_stop_pct'yi (bugun eklenen %2 tabani) ve guvenli-kaldirac kontrolunu
#   atlar. Iki farkli tez turu var ve ikisi ayni muameleyi GORMEMELI:
#     VETO-CALISMASI  ("kapi olmasaydi ne olurdu") -> kapilar BILEREK atlanir  [zorla=True]
#     CANLI ADAYI     ("bu kural canliya alinsin mi") -> canli kurallara UYMALI [zorla=False]
#   Aksi halde on-kayitli karar olcutu, canliya alinacak olandan FARKLI bir kurali olcer
#   ve sonuc tasinamaz. (Olcum: bugune kadar golge LONG'larin stopu hep >=%2,19 oldugu icin
#   pratikte henuz isirmamisti — ama kural ilerde ayrisabilirdi.)
CANLI_ADAYI = {"pump_long_tezi"}          # canli kurallara uyacak tezler


def ac(sym, yon, r, pillar, kapi, detay="", rejim_ad=None, olc_override=None):
    """Golgede giris AC. Donus: True/False (acildi mi).

    kapi CANLI_ADAYI icindeyse zorla=False -> canlinin tum kapilari (rr, asgari stop,
    guvenli kaldirac) aynen gecerli; olcut sonucu dogrudan canliya tasinabilir.
    Diger tezlerde zorla=True -> 'kapi olmasaydi ne olurdu' olculur."""
    if not yon or yon not in ("LONG", "SHORT"):
        return False
    st = yukle() or yeni_state()
    if any(p["sym"] == sym for p in st["acik_pozisyonlar"]):
        return False
    if len(st["acik_pozisyonlar"]) >= MAKS_ACIK or _tekrar_var_mi(st, sym):
        return False

    _zorla = kapi not in CANLI_ADAYI       # canli adayi tezleri kapilara UYAR
    ok = _defterde(testbot.yeni_giris_ac, st, sym, yon, r, pillar,
                   f"GOLGE[{kapi}] {detay}"[:160], zorla=_zorla, rejim_ad=rejim_ad,
                   olc_override=olc_override, kaynak=f"golge:{kapi}")
    if not ok:
        # golge bile acamadi (olcum hatasi / stop gecersiz) -> sessizce gec, olay kaybedilir
        return False
    pos = st["acik_pozisyonlar"][-1]
    pos["kapi"] = kapi                 # karne bunun uzerinden gruplanir
    pos["kapi_detay"] = detay[:160]
    st.setdefault("son_golge", {})[sym] = testbot.now_iso()
    kaydet(st)
    equity_yaz(st)
    return True


def tur():
    """testbot.cycle() sonunda cagrilir. Acik golge pozisyonlarini BOTLA AYNI kurallarla
    yonetir (stop/TP1/iz-suren/zaman-stopu/fonlama). Yeni giris ARAMAZ."""
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
            "acik_sayisi": len(st["acik_pozisyonlar"])})
    except Exception:
        pass


# ---------------------------------------------------------------------------
def _islemler():
    try:
        return [json.loads(l) for l in open(ISLEMLERF, encoding="utf-8")
                .read().splitlines() if l.strip()]
    except Exception:
        return []


def karne():
    """Kapi bazinda karne. R = islem sonucu / giriste hedeflenen risk (yon-notr olcu)."""
    tam = [t for t in _islemler() if not t.get("kismi") and t.get("r") is not None]
    gruplar = {}
    for t in tam:
        kapi = (t.get("kaynak") or "golge:?").split(":", 1)[-1]
        gruplar.setdefault(kapi, []).append(t)
    out = []
    for kapi, ts in sorted(gruplar.items(), key=lambda x: -len(x[1])):
        rler = [t["r"] for t in ts]
        kaz = [x for x in rler if x > 0]
        out.append({"kapi": kapi, "n": len(ts), "kazanan": len(kaz),
                    "win_rate": round(len(kaz) / len(ts) * 100, 1),
                    "ort_r": round(sum(rler) / len(rler), 3),
                    "toplam_r": round(sum(rler), 2),
                    "pnl": round(sum(t["sonuc_usdt"] for t in ts), 2)})
    return out


def durum():
    st = yukle()
    if not st:
        print("GOLGE DEFTER: henuz bir red kaydedilmedi (bot bir girisi reddedince olusur).")
        return
    print("=== GOLGE DEFTER — botun REDDETTIGI girislerin karnesi ===")
    print(f"Baslangic: {st.get('baslangic_ts')} | equity: ${st['baslangic_bakiye']:.0f} -> ${st['equity']:.2f}")
    print(f"Acik golge pozisyon: {len(st['acik_pozisyonlar'])}")
    k = karne()
    if not k:
        print("\nHenuz KAPANMIS golge islemi yok (acilanlar sonuclanmayi bekliyor).")
        return
    print(f"\n{'KAPI':22} {'N':>4} {'kazanma':>8} {'ort R':>8} {'toplam R':>9} {'PnL$':>10}")
    print("-" * 66)
    toplam_n = 0
    for g in k:
        toplam_n += g["n"]
        print(f"{g['kapi']:22} {g['n']:4d} {g['win_rate']:7.0f}% {g['ort_r']:+8.3f} "
              f"{g['toplam_r']:+9.2f} {g['pnl']:+10.2f}")
    print("-" * 66)
    print(f"{'TOPLAM':22} {toplam_n:4d}")
    print("\nOKUMA: ort R NEGATIF -> o kapi HAKLI (zarardan korudu, dokunma).")
    print("       ort R POZITIF  -> o kapi para yakiyor OLABILIR -> once N>=25-30 + coklu rejim.")
    print("N<25-30 = IZLENIM, karar degil. Tek pencereye gore esik oynatmak bu projede 18 kez yanilttti.")


def acik_yazdir():
    st = yukle()
    if not st or not st["acik_pozisyonlar"]:
        print("Acik golge pozisyon yok.")
        return
    for p in st["acik_pozisyonlar"]:
        px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
        yi = 1 if p["yon"] == "LONG" else -1
        pnl = (px - p["giris"]) * p["miktar"] * yi
        print(f"  {p['sym']:8s} {p['yon']:5s} [{p.get('kapi','?'):16s}] {p['kaldirac']}x "
              f"giris={p['giris']:.6g} anlik={px:.6g} PnL={pnl:+.2f}$ stop={p['stop']:.6g}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--durum", action="store_true")
    ap.add_argument("--acik", action="store_true")
    a = ap.parse_args()
    if a.acik:
        acik_yazdir()
    else:
        durum()
