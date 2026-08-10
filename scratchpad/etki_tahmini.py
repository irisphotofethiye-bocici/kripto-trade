#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETKI TAHMINI (2026-08-10) — 08-10 degisiklikleri son 7 gunde kac giris URETIRDI?

NE: testbot_aday_arsiv.jsonl'deki GERCEK adaylara ESKI ve YENI karar_yon uygulanir.
    Amac "kar ne olurdu" DEGIL (o golge defterin isi) — yalnizca BANT GENISLIGI:
    kac karar cikardi, hangi daldan, hangi yonde.

SINIR (dursturluk):
  - Arsiv, kisa listeye (top-10) girmis adaylari tasir. HAZIRLANIYOR sira bonusu
    listeye GIRME sansini artirir; bu etki burada GORULEMEZ (arsivde olmayan aday
    simule edilemez) -> gercek artis buradaki tahminden BUYUK olacak.
  - R/R kapisi (rr_kapisi_r) giris ANINDA olcucu ile bakilir; arsivde o veri yok.
    Yani asagidaki sayilar "karar_yon'dan cikan" sayilardir, acilan islem degil.
  - Tum kayitlar rejim=NOTR; AYI/BOGA dallari bu pencerede test edilmedi.
"""
import json, os, sys, collections

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import evren  # noqa: E402


def karar(r, yeni):
    """NOTR dali — eski/yeni karar_yon'un ilgili kismi. Donus: (yon, sebep) | None"""
    skor = r.get("score") or 0
    stage = r.get("stage")
    smart = r.get("smart")
    taker = r.get("taker")
    pos = r.get("pos", 0.5)
    chg24 = r.get("chg24") or 0.0
    oi24 = r.get("oi24") or 0.0
    dip_yakit = r.get("dip_yakit")
    dusuk_float = bool(r.get("dusuk_float"))

    esik_uzun = 45.0                      # radar_alert_skor(40) + 5
    asiri_yuk = chg24 >= 40.0
    asiri_dus = chg24 <= -40.0
    pumplamis = chg24 >= 20.0
    short_riskli_dip = bool(dip_yakit and dusuk_float)
    long_veto = (pos < 0.25 or asiri_dus or (chg24 < 0 and oi24 >= 15.0))

    esik = (40.0 if (yeni and stage == "HAZIRLANIYOR") else esik_uzun)
    stage_ok = stage in ("BASLIYOR", "HAZIRLANIYOR")
    # C varyanti: fade dali stage sarti ARAMAZ (fade'in ihtiyaci "hareket" degil UC NOKTA).
    # 'izle' hucresi OTOPSI-3'te +0.07R (BASLIYOR -0.09'dan iyi) ve havuzun %89'u orada.
    izle_fade = (yeni == "C" and stage == "izle" and skor >= 40.0)
    if not (stage_ok and skor >= esik) and not izle_fade:
        return None

    if smart == "LONG" and stage_ok:
        if asiri_yuk or long_veto or (taker or 0) < 1.0:
            return None
        return ("LONG", "notr_long_acik")
    if smart == "SHORT" and stage_ok and not short_riskli_dip and not asiri_dus:
        if yeni and pumplamis:
            return None                    # YENI: pump kapisi NOTR-SHORT'a da
        return ("SHORT", "smart-SHORT")
    if yeni and smart in (None, "NOTR"):    # YENI: iki yonlu fade dali
        if pos >= 0.75 and not short_riskli_dip and not asiri_dus and not pumplamis:
            return ("SHORT", "NOTR-fade")
        if pos <= 0.40 and not asiri_yuk and not long_veto and (taker or 0) >= 1.0:
            return ("LONG", "NOTR-fade")
    return None


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "testbot_aday_arsiv.jsonl"),
                                        encoding="utf-8") if l.strip()]
    g = [r for r in rows if (r.get("ts") or "") >= "2026-08-03"]
    print(f"Pencere: 2026-08-03 -> simdi | aday kaydi: {len(g)} | ayri tur: {len({r['ts'] for r in g})}")

    for ad, yeni in (("A: ESKI kural", False), ("B: YENI (uygulanan)", True),
                 ("C: YENI + fade izle-hucresinde de calissin", "C")):
        say = collections.Counter()
        semboller = collections.defaultdict(set)
        for r in g:
            k = karar(r, yeni)
            if k:
                say[f"{k[0]} / {k[1]}"] += 1
                semboller[k[1]].add(r["sym"])
        toplam = sum(say.values())
        print(f"\n--- {ad}: {toplam} karar ({len({r['ts'] for r in g})} turda) ---")
        for k, v in say.most_common():
            print(f"   {k:26} {v:5d}")
        for dal, ss in semboller.items():
            print(f"   [{dal}] ayri sembol: {len(ss)} -> {', '.join(sorted(ss)[:12])}")


if __name__ == "__main__":
    main()
