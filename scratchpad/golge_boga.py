#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GOLGE DEFTER, BOGA PENCERESI (2026-08-21 ->) — olculdugumuz araligin CANLI kontrolu

NEDEN: bugun 08-21..09-02 penceresinde bir dizi olcum yapildi (stop genisligi,
  MA50 kapisi, ucuz/pahali). Hepsi SENTETIK evrende kosuldu. Golge defter ayni
  pencerede CANLI kayit tutuyor -> bagimsiz bir capraz kontrol.

🔴 CLAUDE.md KURALLARI UYGULANIYOR:
  - Pozisyon SAYARKEN  not kismi  suzgeci uygulanir.
  - P&L TOPLARKEN suzgec UYGULANMAZ; kayitlar 'id' ile birlestirilir
    (yoksa TP1'de realize edilmis kar KAYBOLUR — olculmus hata ~4.465 $).
  - 'r' alani KISMI KARI GORMEZ -> dolar ile ters isaret verebilir; R ile dolar
    ayri ayri raporlanir.
  - golge IKI IS birden yapar: pump_long_tezi (~%68) ve reddedilen girisler
    (~%32). Kirilim ZORUNLU; tek kasa rakami yaniltir.
  - funding_usdt DILIMDIR -> id ile toplanir. null = bilinmiyor (sifir DEGIL).

Salt-okunur. Bot dosyalarina yazim: YOK.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json, os, math, statistics as stx, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFTER = os.path.join(KOK, "golge_islemler.jsonl")
BOGA_BAS = "2026-08-21"


def oku():
    out = []
    with open(DEFTER, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def poz_birlestir(kayitlar):
    """id -> pozisyon.  P&L TUM kayitlardan toplanir (kismi dahil);
    nitelikler ACILIS (kismi olmayan ya da ilk) kaydindan alinir."""
    g = collections.defaultdict(list)
    for r in kayitlar:
        g[r.get("id")].append(r)
    poz = {}
    for i, ks in g.items():
        ana = next((k for k in ks if not k.get("kismi")), ks[0])
        usd = sum(k.get("sonuc_usdt") or 0.0 for k in ks)
        fon = [k.get("funding_usdt") for k in ks if k.get("funding_usdt") is not None]
        poz[i] = {
            "id": i, "sym": ana.get("sym"), "yon": ana.get("yon"),
            "kaynak": ana.get("kaynak") or "?", "rejim": ana.get("rejim_giriste"),
            "ts": ana.get("ts"), "usd": usd,
            "fon": (sum(fon) if fon else None),
            "r": ana.get("r"), "notional": ana.get("notional") or 0.0,
            "kismi_var": any(k.get("kismi") for k in ks),
            "sebep": ana.get("sebep"), "n_kayit": len(ks),
        }
    return poz


def ozet(ad, ps):
    if not ps:
        print("  %-26s (yok)" % ad)
        return
    usd = sum(p["usd"] for p in ps)
    kaz = sum(1 for p in ps if p["usd"] > 0)
    rs = [p["r"] for p in ps if p["r"] is not None]
    fon = [p["fon"] for p in ps if p["fon"] is not None]
    print("  %-26s N=%-4d  toplam %+9.2f $  ort %+7.2f $  kazanan %%%-5.1f  R_med %+6.2f  fonlama %s"
          % (ad, len(ps), usd, usd / len(ps), kaz / len(ps) * 100,
             stx.median(rs) if rs else 0,
             ("%+8.2f $ (N=%d)" % (sum(fon), len(fon))) if fon else "bilinmiyor"))


def gun_t(ps):
    g = collections.defaultdict(list)
    for p in ps:
        g[p["ts"][:10]].append(p["usd"])
    v = [sum(x) / len(x) for x in g.values()]
    if len(v) < 3:
        return None, None, len(v)
    m = sum(v) / len(v)
    se = stx.stdev(v) / math.sqrt(len(v))
    return m, (m / se if se else None), len(v)


def main():
    print("=" * 82)
    print("GOLGE DEFTER — BOGA PENCERESI (%s ->) · olculen araligin CANLI kontrolu" % BOGA_BAS)
    print("=" * 82)
    kayitlar = oku()
    poz = poz_birlestir(kayitlar)
    hepsi = list(poz.values())
    boga = [p for p in hepsi if p["ts"] and p["ts"][:10] >= BOGA_BAS]

    print("defter: %d kayit -> %d pozisyon (id ile birlestirildi)" % (len(kayitlar), len(hepsi)))
    print("BOGA penceresi: %d pozisyon · %d gun\n"
          % (len(boga), len({p["ts"][:10] for p in boga})))
    if not boga:
        print("BOGA penceresinde golge pozisyonu YOK -> capraz kontrol yapilamiyor")
        return

    # --- CLAUDE.md: golge IKI IS yapiyor, kirilim ZORUNLU ---
    print("### KAYNAGA GORE KIRILIM (CLAUDE.md: tek kasa rakami yaniltir)")
    kay = collections.defaultdict(list)
    for p in boga:
        kay[p["kaynak"]].append(p)
    for k in sorted(kay, key=lambda x: -len(kay[x])):
        ozet(k, kay[k])
    print()
    ozet("TUMU (bilgi)", boga)
    print()

    print("### YONE GORE — bugunku olcumun ana iddiasi burada sinaniyor")
    for y in ("SHORT", "LONG"):
        ps = [p for p in boga if p["yon"] == y]
        ozet(y, ps)
        if ps:
            m, t, ng = gun_t(ps)
            print("      gun-kumeli: %d gun · gun ort %s · t %s"
                  % (ng, ("%+.2f $" % m) if m is not None else "yok",
                     ("%+.2f" % t) if t is not None else "yok"))
    print()

    print("### REJIM ETIKETI (giriste) — bot BOGA'yi ne zaman gordu")
    rj = collections.Counter(p["rejim"] for p in boga)
    print("   " + " · ".join("%s %d" % (k, v) for k, v in rj.most_common()))
    print()

    print("### MUTABAKAT — kismi kar suzgeci hatasi (CLAUDE.md olculmus tuzak)")
    dogru = sum(p["usd"] for p in boga)
    suzgecli = sum(p["usd"] for p in boga if not p["kismi_var"])
    print("   DOGRU (id ile birlestirilmis)     : %+10.2f $" % dogru)
    print("   YANLIS (kismi olanlar atilirsa)   : %+10.2f $" % suzgecli)
    print("   fark                              : %+10.2f $   (%d pozisyonda kismi var)"
          % (dogru - suzgecli, sum(1 for p in boga if p["kismi_var"])))
    print()

    print("### CAPRAZ KONTROL — sentetik olcum ne demisti?")
    sh = [p for p in boga if p["yon"] == "SHORT"]
    if sh:
        no = [p["usd"] / p["notional"] * 100 for p in sh if p["notional"]]
        print("   sentetik olcum (bugun): BOGA'da SHORT kaybettirir")
        print("     A_funding -%.3f%% · MA50 -%.3f%% · K_genis -%.3f%% (islem basi net)"
              % (0.692, 0.193, 0.771))
        if no:
            print("   GOLGE (canli, ayni pencere): SHORT islem basi %+.3f%% (notional'e gore, N=%d)"
                  % (stx.mean(no), len(no)))
            print("     -> isaret %s"
                  % ("AYNI (ikisi de negatif)" if stx.mean(no) < 0 else "AYRISIYOR"))
    else:
        print("   BOGA penceresinde golge SHORT'u YOK -> dogrudan kiyas yapilamiyor")
    print()
    print("🔴 Golge defter bir KENAR OLCUSU DEGILDIR: reddedilen girisler + hic")
    print("   denenmemis bir LONG tezi karisik. Kirilim yukarida; tek rakam okunmaz.")
    print("Bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
