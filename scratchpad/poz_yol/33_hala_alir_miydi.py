#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOT BU POZU SIMDI DE ACAR MIYDI? — kendi karar fonksiyonuyla, her 5 dk.

KULLANICI (2026-08-21): "acik pozlarda bot anlik veriyle o pozu iceri alir
miydi? ne zaman almamaya baslardi?"

FIKIR: cikis kurali olarak "GIRIS SARTLARI ARTIK SAGLANMIYOR"u kullan.
Tetik aramak yerine botun KENDI mantigini tersine cevir.

NASIL: pozisyon_izleme.jsonl'deki her 5 dk anlik goruntusu, karar_yon'un
okudugu TUM alanlari iceriyor:
   r      : score · stage · chg24 · pos · funding · oi24 · price · ma50_mesafe
            · dip_yakit · smart · taker
   pillar : smart · taker
karar_yon SAF (disk/ag yok, dogrulandi) -> her goruntude yeniden calistirilabilir.

⚠️ DONMUS ALAN UYARISI TERSINE CALISIYOR: oi24/top_ls/glob_ls/taker/smart/pos
   radar temposunda tazeleniyor. Ama BOTUN KENDISI de girerken radar verisini
   okuyor -> bu replay botun gercekten gorecegi seye SADIK.

⚠️ evren.para_rejim STUB'LANIR (ag cagrisi olabilir) -> para_cikis=False sabit.
   Bu, long_veto'yu GEVSETIR yonde; sonuc bu notla okunur.

OLCUM: "artik almazdi" anindan itibaren cikilsaydi ne olurdu — ve bunun
   RASTGELE cikistan (olculdu: +1,789 puan) farki var mi?

HUKUM YAZILMAZ. SALT OKUMA.
"""
import os, sys, statistics as sx, collections, random

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
PROJE = os.path.dirname(SCRATCH)
sys.path.insert(0, HERE)
sys.path.insert(0, PROJE)
import ortak                                                    # noqa: E402
import testbot                                                  # noqa: E402
import evren                                                    # noqa: E402

random.seed(13)

# --- STUB: ag cagrisi olmasin ---
evren.para_rejim = lambda *a, **k: {"durum": "NOTR"}
testbot.telegram_gonder = lambda *a, **k: None
testbot.toast_gonder = lambda *a, **k: None
testbot._append_jsonl = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("DISKE YAZIM DENENDI"))
testbot._save_state = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("DISKE YAZIM DENENDI"))


def r_kur(g):
    return {"score": g.get("score"), "stage": g.get("stage"), "chg24": g.get("chg24"),
            "pos": g.get("pos"), "funding": g.get("funding"), "oi24": g.get("oi24"),
            "price": g.get("fiyat"), "ma50_mesafe": g.get("ma50_mesafe"),
            "dip_yakit": g.get("dip_yakit"), "smart": g.get("smart"),
            "taker": g.get("taker"), "top_ls": g.get("top_ls"), "glob_ls": g.get("glob_ls"),
            "oi3": g.get("oi3"), "vol_x": g.get("vol_x"), "rel3": g.get("rel3"),
            "comp": g.get("comp"), "last1": g.get("last1"), "last3": g.get("last3"),
            "ayrisma": g.get("ayrisma"), "float_oran": g.get("float_oran"),
            "dusuk_float": g.get("dusuk_float"), "mcap": g.get("mcap")}


def karar(g, rejim):
    r = r_kur(g)
    if r["score"] is None or r["stage"] is None:
        return None, None
    pillar = {"smart": g.get("smart"), "taker": g.get("taker"),
              "top_ls": g.get("top_ls"), "glob_ls": g.get("glob_ls")}
    veto = []
    try:
        k = testbot.karar_yon(rejim, r, pillar, False, veto_out=veto,
                              para_cikis=False, btc_pay=None, para_durgun=False)
    except Exception as e:
        return None, "HATA:%s" % str(e)[:30]
    if k is None:
        return None, (veto[0]["kategori"] if veto else "karar-yok")
    return k[0], k[1]


def hazirla():
    out = []
    for p in ortak.pozisyonlar(en_az_goruntu=12, zengin=False):
        s = p["seri"]
        pnl = [g.get("pnl_pct") for g in s]
        if any(x is None for x in pnl):
            continue
        rej = (p["sonuc"] or {}).get("rejim_giriste") or "NOTR"
        out.append({"sym": p["sym"], "yon": p["yon"], "seri": s, "pnl": pnl,
                    "rejim": rej, "sonuc": p["sonuc"]})
    return out


if __name__ == "__main__":
    P = hazirla()
    print("BOT BU POZU HALA ACAR MIYDI? — %d pozisyon" % len(P))
    print("(karar_yon her 5 dk yeniden calistirildi; rejim = GIRISTEKI rejim)\n")

    ayni, kayip, hicbir = 0, [], 0
    sebepler = collections.Counter()
    ilk_hayir, cikis_farki, rast_farki = [], [], []
    for p in P:
        s, pnl, yon = p["seri"], p["pnl"], p["yon"]
        seri_karar = []
        for g in s:
            k, sb = karar(g, p["rejim"])
            seri_karar.append(k)
            if k != yon:
                sebepler[sb or "digeryon:%s" % k] += 1
        if seri_karar[0] == yon:
            ayni += 1
        # ILK "artik bu yonde almazdi" ani (girisin ilk 2 barindan sonra)
        bul = None
        for i in range(2, len(seri_karar)):
            if seri_karar[i] != yon:
                bul = i
                break
        if bul is None:
            hicbir += 1
            continue
        ilk_hayir.append(bul)
        cikis_farki.append(pnl[bul] - pnl[-1])
        aday = list(range(2, len(pnl) - 1))
        if aday:
            rast_farki.append(pnl[random.choice(aday)] - pnl[-1])

    print("GIRIS ANINDA ayni yonu soyleyen : %d / %d" % (ayni, len(P)))
    print("Omru boyunca HIC 'hayir' demeyen: %d" % hicbir)
    print("'artik almazdi' ani bulunan     : %d" % len(ilk_hayir))
    if ilk_hayir:
        print("\nILK 'ARTIK ALMAZDI' ANI:")
        print("   medyan %d. bar (%d dk) · %%25 %d. bar · %%75 %d. bar"
              % (sx.median(ilk_hayir), sx.median(ilk_hayir) * 5,
                 sorted(ilk_hayir)[len(ilk_hayir) // 4],
                 sorted(ilk_hayir)[3 * len(ilk_hayir) // 4]))
        print("\nO ANDA CIKSAYDIK (pozisyonun gercek sonuna gore, puan):")
        print("   kural  : medyan %+.3f   (N=%d)" % (sx.median(cikis_farki), len(cikis_farki)))
        print("   RASTGELE: medyan %+.3f   (ayni pozisyonlar, ayni sayida)"
              % sx.median(rast_farki))
        print("   FARK   : %+.3f" % (sx.median(cikis_farki) - sx.median(rast_farki)))
    print("\n'HAYIR' SEBEPLERI (en sik 10):")
    for k, n in sebepler.most_common(10):
        print("   %-28s %d" % (k, n))
    print("\nHUKUM YAZILMADI. diske yazim: YOK (stub'li)")
