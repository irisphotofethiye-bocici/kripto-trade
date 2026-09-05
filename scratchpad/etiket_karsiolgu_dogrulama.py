#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIKET KARSI-OLGUSU — YAPILABILIRLIK DOGRULAMASI (2026-09-05)

Kullanici: "bot etiket dondukten sonra actigi pozlari/secimleri etiket donmemis
  gibi yapsaydi ne olurdu — NOTR calismaya devam etseydi?"

🔴 BU BETIK HENUZ KARSI-OLGUYU KOSTURMUYOR. Once tek sey sinaniyor:
   KAYITLI KARARLARI YENIDEN URETEBILIYOR MUYUM?
   Uretemezsem karsi-olgu DEGERSIZDIR ve kosturulmaz.

YONTEM: testbot.karar_yon() KAYNAKTAN cagrilir (yeniden yazilmaz). Girdiler
  testbot_aday_arsiv.jsonl'den; pillar {smart,taker,top_ls,glob_ls} arsivde var;
  btc_pay btc_pay_log.jsonl'den tarihe gore eslenir.
  EKSIK: para_cikis · para_durgun (arsivde yok) -> False varsayilir, sapma
  buradan gelirse RAPORLANIR.

Salt-okunur.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sys, json, os, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import testbot

ARSIV = os.path.join(KOK, "testbot_aday_arsiv.jsonl")
BTCPAY = os.path.join(KOK, "btc_pay_log.jsonl")
BAS = "2026-08-21"


def btc_pay_serisi():
    """gun -> btc_pay dict (bant/degisim). Son kayit kazanir."""
    out = {}
    if not os.path.exists(BTCPAY):
        return out
    for line in open(BTCPAY, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        ts = r.get("ts") or r.get("tarih") or ""
        if ts:
            out[ts[:10]] = r
    return out


def karar_metni(k):
    """karar_yon ciktisini arsivdeki 'karar' bicimine cevir."""
    if k is None:
        return "karar-yok"
    return "%s/%s" % (k[0], k[1])


def main():
    print("=" * 80)
    print("ETIKET KARSI-OLGUSU — YAPILABILIRLIK DOGRULAMASI")
    print("=" * 80)
    print("🔴 Karsi-olgu HENUZ kosturulmuyor. Tek soru: kayitli kararlari")
    print("   yeniden uretebiliyor muyum?\n")

    bp = btc_pay_serisi()
    print("btc_pay_log gun sayisi: %d" % len(bp))

    esles = collections.Counter()
    ciftler = collections.Counter()
    n = 0
    for line in open(ARSIV, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        ts = r.get("ts") or ""
        if ts[:10] < BAS:
            continue
        kayitli = r.get("karar")
        if kayitli is None:
            continue                      # karar alani yazilmamis satirlar
        rejim = r.get("rejim")
        if rejim in (None, "BILINMIYOR"):
            continue
        pillar = {"smart": r.get("smart"), "taker": r.get("taker"),
                  "top_ls": r.get("top_ls"), "glob_ls": r.get("glob_ls")}
        try:
            k = testbot.karar_yon(rejim, r, pillar, bool(r.get("dusuk_float")),
                                  veto_out=None, para_cikis=False,
                                  btc_pay=bp.get(ts[:10]), para_durgun=False)
        except Exception as e:
            esles["HATA:" + str(e)[:40]] += 1
            continue
        n += 1
        uretilen = karar_metni(k)
        # arsivdeki VETO:* kayitlari da 'karar-yok'a denk gelir (veto -> None)
        kay = kayitli
        if kay.startswith("VETO:"):
            kay_norm = "karar-yok"
        else:
            kay_norm = kay
        esles["ESLESTI" if uretilen == kay_norm else "SAPTI"] += 1
        if uretilen != kay_norm:
            ciftler["%s  ->  uretilen %s" % (kay, uretilen)] += 1

    print("\nkarsilastirilan kayit: %d" % n)
    for k, v in esles.most_common():
        print("  %-12s %6d  (%%%.1f)" % (k, v, v / n * 100 if n else 0))
    if ciftler:
        print("\nEN SIK SAPMALAR (kayitli -> uretilen):")
        for k, v in ciftler.most_common(10):
            print("  %6d  %s" % (v, k))

    ok = esles["ESLESTI"] / n * 100 if n else 0
    print("\n" + "=" * 80)
    if ok >= 95:
        print("SONUC: %%%.1f eslesme -> KARSI-OLGU KOSTURULABILIR." % ok)
    else:
        print("SONUC: %%%.1f eslesme -> YETERSIZ. Karsi-olgu KOSTURULMAZ;" % ok)
        print("       once sapmanin kaynagi bulunmali (muhtemel: para_cikis/para_durgun).")
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
