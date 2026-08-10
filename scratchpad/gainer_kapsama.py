#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GAINER KAPSAMA (2026-08-10) — "radar buyuk hareketleri GORUYOR mu?"

SORU (kullanici): "tum gainer'lara baktin mi? Amac onlari iceri alabilmenin yolunu
bulup botu optimize etmek. Su andaki bot kazandiran degil, AZ KAYBETTIREN."

ONCEKI OLCUMLERIN KOR NOKTASI: hepsi radar_archive uzerindeydi — yani RADARIN GORDUGU
evren. Piyasanin gercek kazandiranlari o evrende yoksa, tum sonuclar filtrelenmis bir
balonun icinde kalir. Bu script balonu disaridan olcer.

YONTEM:
  1. Binance USDT PERP evreninin TAMAMI (exchangeInfo) — radar'in listesi degil.
  2. Her sembol icin 46 gunluk pencerede 1h mumlardan:
       en_iyi_24h  : herhangi bir 24 saatlik pencerede en yuksek yukselis
       en_iyi_72h  : herhangi bir 72 saatlik pencerede en yuksek yukselis
       dip_zirve   : donem icindeki en dusuk -> sonraki en yuksek (tam hareket)
  3. En buyuk hareketler siralanir = PIYASANIN GERCEK KAZANDIRANLARI.
  4. Her biri icin: hareketin BASLADIGI ana bakilir ve sorulur —
       (a) radar_archive'da bu sembol o sirada VAR MIYDI?
       (b) varsa skoru/stage'i neydi? botun esiklerini gecer miydi?
       (c) hic yoksa: radar bu coini HIC gormemis mi, yoksa hareket disinda mi gormus?
  5. KAPSAMA ORANI: ilk 50 hareketin kaci radarda vardi, kaci esikleri gecerdi.

ON-KAYIT: "hareket basi" = 24h getirinin ilk kez +%15'i astigi bar (sabit, aranmadi).
Radar'in gormesi icin pencere: hareket basindan ONCEKI 24 saat.
"""
import json, os, sys, time, statistics as st, collections, datetime
import urllib.request

BURA = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(BURA)
CACHE = os.path.join(BURA, "klines_1h")
FAPI = "https://fapi.binance.com"
BAS_MS = 1781222400000          # 2026-06-12
HAREKET_ESIK = 15.0             # % — "hareket" tanimi (sabit, sonuca bakilmadan secildi)


def get(u, t=30):
    with urllib.request.urlopen(urllib.request.Request(
            u, headers={"User-Agent": "gainer/1.0"}), timeout=t) as r:
        return json.loads(r.read())


def tum_perpler():
    d = get(f"{FAPI}/fapi/v1/exchangeInfo")
    out = []
    for s in d["symbols"]:
        if s.get("quoteAsset") == "USDT" and s.get("status") == "TRADING" \
           and s.get("contractType") == "PERPETUAL":
            out.append(s["symbol"][:-4])
    return sorted(set(out))


def klines(sym):
    yol = os.path.join(CACHE, f"{sym}.json")
    if os.path.exists(yol):
        try:
            return json.load(open(yol))
        except Exception:
            pass
    out, bas = [], BAS_MS
    while True:
        try:
            d = get(f"{FAPI}/fapi/v1/klines?symbol={sym}USDT&interval=1h&startTime={bas}&limit=1500")
        except Exception:
            break
        if not d:
            break
        out += d
        if len(d) < 1500:
            break
        bas = d[-1][0] + 3600000
        time.sleep(0.1)
    b = [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]),
          "c": float(k[4]), "qv": float(k[7])} for k in out]
    json.dump(b, open(yol, "w"))
    time.sleep(0.06)
    return b


def hareketler(b):
    """Donem icindeki en buyuk yukselisler + hareketin BASLADIGI bar."""
    if len(b) < 100:
        return None
    en24 = en72 = 0.0
    i24 = i72 = None
    for i in range(24, len(b)):
        r = (b[i]["h"] / b[i - 24]["c"] - 1) * 100
        if r > en24:
            en24, i24 = r, i
    for i in range(72, len(b)):
        r = (b[i]["h"] / b[i - 72]["c"] - 1) * 100
        if r > en72:
            en72, i72 = r, i
    # hareketin basi: en24 zirvesinden geriye, 24h getirinin ilk kez esigi astigi bar
    bas_i = None
    if i24:
        for j in range(max(24, i24 - 48), i24 + 1):
            if (b[j]["h"] / b[j - 24]["c"] - 1) * 100 >= HAREKET_ESIK:
                bas_i = j
                break
    return {"en24": en24, "en72": en72, "zirve_i": i24, "bas_i": bas_i,
            "zirve_ts": b[i24]["t"] if i24 else None,
            "bas_ts": b[bas_i]["t"] if bas_i else None,
            # onbellekteki eski mumlarda qv yok (oruntu_analiz sadece ohlc yazmisti) -> None
            "hacim_musd": (st.median([x["qv"] for x in b[-500:]]) / 1e6
                           if len(b) >= 500 and "qv" in b[-1] else None)}


def main():
    print("Perp evreni cekiliyor...")
    perpler = tum_perpler()
    print(f"  {len(perpler)} USDT perp")

    print("Radar arsivi okunuyor...")
    radar = collections.defaultdict(list)
    with open(os.path.join(HERE, "radar_archive.jsonl"), encoding="utf-8") as f:
        for l in f:
            if l.strip():
                r = json.loads(l)
                radar[r["sym"]].append(r)
    print(f"  radar {len(radar)} sembol gormus")

    print("Mumlar + hareketler (onbellekten / indirilerek)...")
    sonuc = []
    for n, s in enumerate(perpler, 1):
        b = klines(s)
        if not b or len(b) < 200:
            continue
        h = hareketler(b)
        if h and h["en24"] > 0:
            h["sym"] = s
            sonuc.append(h)
        if n % 80 == 0:
            print(f"  {n}/{len(perpler)} ...")

    sonuc.sort(key=lambda x: -x["en24"])
    print(f"\n{len(sonuc)} sembolde hareket olculdu\n")

    def radar_gordu_mu(sym, bas_ms, saat=24):
        """Hareket basindan ONCEKI 'saat' icinde radar bu sembolu kaydetmis mi?"""
        if sym not in radar or not bas_ms:
            return None
        alt = bas_ms - saat * 3600000
        kay = []
        for r in radar[sym]:
            try:
                ms = int(datetime.datetime.strptime(r["ts"], "%Y-%m-%d %H:%M")
                         .astimezone().timestamp() * 1000)
            except Exception:
                continue
            if alt <= ms <= bas_ms:
                kay.append((ms, r))
        if not kay:
            return None
        kay.sort()
        return max((r for _, r in kay), key=lambda r: r.get("score") or 0)

    print("=" * 112)
    print(f"EN BUYUK 40 HAREKET — radar gordu mu, esikleri gecer miydi?")
    print("=" * 112)
    print(f"{'#':>3} {'coin':9}{'en iyi 24h':>11}{'en iyi 72h':>11}{'hacim M$':>10}"
          f"{'radar arsivinde':>16}{'hareket oncesi':>15}{'skor':>7}{'stage':>13}")
    print("-" * 112)
    hic, gordu, esik = 0, 0, 0
    for i, x in enumerate(sonuc[:40], 1):
        r = radar_gordu_mu(x["sym"], x["bas_ts"])
        arsivde = "VAR" if x["sym"] in radar else "YOK"
        if x["sym"] not in radar:
            hic += 1
        if r:
            gordu += 1
            if (r.get("score") or 0) >= 45:
                esik += 1
        print(f"{i:3d} {x['sym']:9}{x['en24']:10.0f}%{x['en72']:10.0f}%"
              f"{(x['hacim_musd'] or 0):10.1f}{arsivde:>16}"
              f"{('GORDU' if r else '—'):>15}"
              f"{((r.get('score') or 0) if r else 0):7.1f}{(r.get('stage') if r else '—'):>13}")
    print("-" * 112)
    ilk = sonuc[:40]
    print(f"  radar arsivinde HIC yok           : {hic}/40")
    print(f"  hareket ONCESI 24s'te kaydedilmis : {gordu}/40")
    print(f"  ...ve skor >= 45 (botun kapisi)   : {esik}/40")

    # tum evren kapsamasi
    print("\n" + "=" * 112)
    print("TUM EVREN KAPSAMASI")
    print("=" * 112)
    for esik_pct, ad in ((50, ">%50"), (30, ">%30"), (20, ">%20"), (15, ">%15")):
        alt = [x for x in sonuc if x["en24"] >= esik_pct]
        if not alt:
            continue
        v = sum(1 for x in alt if x["sym"] in radar)
        g = sum(1 for x in alt if radar_gordu_mu(x["sym"], x["bas_ts"]))
        e = sum(1 for x in alt if (radar_gordu_mu(x["sym"], x["bas_ts"]) or {}).get("score", 0) >= 45)
        print(f"  24h hareketi {ad:5} : {len(alt):4d} sembol | radar arsivinde {v:4d} (%{v/len(alt)*100:3.0f})"
              f" | hareket oncesi gordu {g:4d} (%{g/len(alt)*100:3.0f})"
              f" | skor>=45 {e:3d} (%{e/len(alt)*100:3.0f})")

    json.dump([{k: v for k, v in x.items() if k != "bas_i"} for x in sonuc[:200]],
              open(os.path.join(BURA, "gainer_listesi.json"), "w"))
    print("\n-> scratchpad/gainer_listesi.json")


if __name__ == "__main__":
    main()
