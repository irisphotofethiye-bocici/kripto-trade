#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BENIM HESABIM — bagimsiz ikinci sanal kasa (2026-08-05, kullanici karari).

NE: Karar vericinin INSAN oldugu, botun DANISMAN oldugu hibrit sistem.
    Girisler yalnizca panelden gelir (bu modul KENDILIGINDEN ASLA GIRIS ARAMAZ).
    Acik pozisyonlar botun turuyla, BOTLA AYNI kurallarla yonetilir.

NEDEN AYRI KASA: bu projedeki tum olcumler (skor otopsisi, stop otopsisi, rejim
    dogrulamasi, BTC-payi katmani) botun KENDI kararlarinin karnesine dayaniyor.
    Elle acilan islemler ayni deftere karisirsa o olcumlerin hicbiri bir daha
    temiz yapilamaz ve karisan veri geriye donuk AYRILAMAZ.

NEDEN AYNI CIKIS KURALLARI: iki sistem arasindaki fark yalnizca GIRIS KARARINDAN
    gelsin diye. Cikis kurallari da ayrisirsa "fark nereden geldi" sorusu
    cevaplanamaz hale gelir.

Yonetim mantigi KOPYALANMAZ — testbot'un kendi fonksiyonlari cagrilir; yalnizca
defter yolu testbot._DEFTER ile gecici olarak degistirilir (finally ile geri alinir).

Kullanim:  python benim.py --durum
           python benim.py --tur          (elle yonetim turu; normalde testbot.cycle cagirir)
"""
import json, os, sys, argparse

import testbot
import radar
import evren

HERE = os.path.dirname(os.path.abspath(__file__))
STATEF = os.path.join(HERE, "benim_state.json")
ISLEMLERF = os.path.join(HERE, "benim_islemler.jsonl")
EQUITYF = os.path.join(HERE, "benim_equity.jsonl")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def _c(ad, varsayilan):
    """Ayarlar: once 'benim' blogu, yoksa testbot'unki (ayni cikis kurallari icin)."""
    try:
        b = evren.cfg().get("benim") or {}
        if ad in b:
            return b[ad]
    except Exception:
        pass
    return testbot._c(ad, varsayilan)


def yeni_state():
    bakiye = float(_c("baslangic_bakiye", 10000.0))
    return {"baslangic_ts": testbot.now_iso(), "baslangic_bakiye": bakiye,
            "equity": bakiye, "durum": "AKTIF", "acik_pozisyonlar": [],
            "sonraki_id": 1, "cooldown": {}, "bekleyenler": {}, "son_cycle_ts": None}


def yukle():
    try:
        return json.load(open(STATEF, encoding="utf-8"))
    except Exception:
        return None


def kaydet(st):
    json.dump(st, open(STATEF, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _defterde(fn, *a, **kw):
    """testbot'un fonksiyonunu BENIM defterime yazacak sekilde calistir.
    finally ile MUTLAKA geri alinir — yoksa botun kapanislari benim defterime duser."""
    eski = testbot._DEFTER
    testbot._DEFTER = ISLEMLERF
    try:
        return fn(*a, **kw)
    finally:
        testbot._DEFTER = eski


# ---------------------------------------------------------------------------
def bot_gorusu(sym, yon):
    """Bot SU AN bu coine baksaydi ne derdi? KURU CALISTIRMA — hicbir sey acmaz.
    Donus: (gorus_sozlugu, r, pillar, rejim_ad) — r/pillar giriste yeniden kullanilir."""
    r = radar.analyze(sym)
    if not r:
        return None, None, None, None
    pillar = radar.pillar_d(sym)
    rejim = evren.btc_rejim()
    rejim_ad = rejim.get("rejim")
    try:
        pr = evren.para_rejim()
    except Exception:
        pr = None
    try:
        bp = evren.btc_pay_akisi()
    except Exception:
        bp = None
    vlist = []
    karar = testbot.karar_yon(rejim_ad, r, pillar, False, veto_out=vlist,
                              para_cikis=bool(pr and pr.get("rejim") == "PARA CIKIYOR"),
                              btc_pay=bp,
                              para_durgun=bool(pr and pr.get("rejim") == "PARA DURGUN"))
    gorus = {
        "karar": (f"{karar[0]}/{karar[1]}" if karar else None),
        "ayni_yonde": bool(karar and karar[0] == yon),
        "vetolar": [{"kategori": v.get("kategori"), "detay": v.get("detay"),
                     "olurdu_yon": v.get("olurdu_yon")} for v in vlist],
        "skor": r.get("score"), "stage": r.get("stage"),
        "rejim": rejim_ad, "f10": rejim.get("f10"),
        "btc_pay_bant": (bp or {}).get("bant"),
        "btc_pay_degisim": (bp or {}).get("degisim"),
        "para_rejim": (pr or {}).get("rejim"),
    }
    return gorus, r, pillar, rejim_ad


def giris_ac(sym, yon, tez="", stop=None, tp1=None, tp2=None):
    """Panelden SANAL giris. Botun kapilari SOYLENIR ama ENGELLEMEZ (kullanici karari).
    -> (ok, mesaj, ayrinti)"""
    sym = str(sym).upper().strip()
    yon = "LONG" if str(yon).upper().startswith("L") else "SHORT"
    st = yukle() or yeni_state()
    if any(p["sym"] == sym for p in st["acik_pozisyonlar"]):
        return False, f"{sym} zaten açık — önce onu kapat.", None
    maks = int(_c("maks_pozisyon", 4))
    if len(st["acik_pozisyonlar"]) >= maks:
        return False, f"Aynı anda en fazla {maks} pozisyon açabilirsin.", None

    gorus, r, pillar, rejim_ad = bot_gorusu(sym, yon)
    if not r:
        return False, f"{sym} için veri alınamadı (sembol yanlış veya yeni listelenmiş).", None

    override = None
    if any(x is not None for x in (stop, tp1, tp2)):
        override = {"stop": stop, "tp1": tp1, "tp2": tp2}

    ok = _defterde(testbot.yeni_giris_ac, st, sym, yon, r, pillar,
                   f"BEN: {tez[:120]}" if tez else "BEN: (tez yazılmadı)",
                   zorla=True, rejim_ad=rejim_ad, olc_override=override, kaynak="elle")
    if not ok:
        return False, "Açılamadı — ölçücü giriş/stop üretemedi ya da kaldıraç güvenlik kırpması reddetti.", None

    pos = st["acik_pozisyonlar"][-1]
    pos["tez"] = tez
    pos["bot_gorusu"] = gorus
    kaydet(st)
    equity_yaz(st)
    return True, (f"{sym} {yon} açıldı — {pos['kaldirac']}x, teminat ${pos['marjin']:.0f}, "
                  f"risk ${pos['risk_usdt']:.0f}"), pos


def kapat(sym):
    """Panelden elle kapatma (piyasa fiyatindan)."""
    sym = str(sym).upper().strip()
    st = yukle()
    if not st:
        return False, "Hesap henüz açılmamış."
    pos = next((p for p in st["acik_pozisyonlar"] if p["sym"] == sym), None)
    if not pos:
        return False, f"{sym} adında açık pozisyon yok."
    px = testbot.fiyat_fapi(sym)
    if not px:
        return False, "Anlık fiyat alınamadı, kapatma yapılmadı."
    _defterde(testbot.pozisyon_kapat, st, pos, px, "ELLE_KAPAT")
    st["acik_pozisyonlar"] = [p for p in st["acik_pozisyonlar"] if p["sym"] != sym]
    kaydet(st)
    equity_yaz(st)
    return True, f"{sym} kapatıldı."


def equity_yaz(st):
    try:
        testbot._append_jsonl(EQUITYF, {
            "ts": testbot.now_iso(), "equity": round(st["equity"], 2),
            "acik_pnl": round(testbot.acik_pnl_toplam(st), 2),
            "acik_sayisi": len(st["acik_pozisyonlar"]), "durum": st["durum"]})
    except Exception:
        pass


def tur():
    """testbot.cycle() sonunda cagrilir. Acik pozisyonlari BOTLA AYNI kurallarla yonetir.
    YENI GIRIS ARAMAZ. Hesap yoksa hicbir sey yapmaz (dosya olusturmaz)."""
    st = yukle()
    if not st:
        return
    if st["acik_pozisyonlar"]:
        _defterde(testbot.yonet_acik_pozisyonlar, st)
    st["son_cycle_ts"] = testbot.now_iso()
    kaydet(st)
    equity_yaz(st)


def durum():
    st = yukle()
    if not st:
        print("BENIM HESABIM: henuz acilmadi (panelden ilk islemi acinca olusur).")
        return
    try:
        islemler = [json.loads(l) for l in open(ISLEMLERF, encoding="utf-8")
                    .read().splitlines() if l.strip()]
    except Exception:
        islemler = []
    tam = [t for t in islemler if not t.get("kismi")]
    kz = [t for t in tam if t["sonuc_usdt"] > 0]
    rler = [t["r"] for t in tam if t.get("r") is not None]
    print("=== BENIM HESABIM (sanal, bottan bagimsiz) ===")
    print(f"Durum: {st['durum']} | Bakiye: ${st['baslangic_bakiye']:.0f} -> ${st['equity']:.2f}")
    print(f"Acik pozisyon: {len(st['acik_pozisyonlar'])}")
    for p in st["acik_pozisyonlar"]:
        px = testbot.fiyat_fapi(p["sym"]) or p["giris"]
        yi = 1 if p["yon"] == "LONG" else -1
        pnl = (px - p["giris"]) * p["miktar"] * yi
        print(f"  {p['sym']:8s} {p['yon']:5s} {p['kaldirac']}x giris={p['giris']:.6g} "
              f"anlik={px:.6g} PnL={pnl:+.2f}$ stop={p['stop']:.6g}")
        if p.get("tez"):
            print(f"      tez: {p['tez'][:100]}")
    print(f"Kapanan islem: {len(tam)} | Kazanan: {len(kz)}"
          f"{f' (%{len(kz)/len(tam)*100:.0f})' if tam else ''}")
    if tam:
        print(f"Toplam PnL: {sum(t['sonuc_usdt'] for t in islemler):+.2f}$ | "
              f"Ort R: {sum(rler)/len(rler):+.2f}" if rler else "")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--durum", action="store_true")
    ap.add_argument("--tur", action="store_true")
    a = ap.parse_args()
    if a.tur:
        tur(); print("tur tamam")
    else:
        durum()
