#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pos'a GORE KOSULLU MEKANIK — kenar alinabilir mi?
On-kayit: ON_KAYIT_pos_kosullu_mekanik.md (commit bd92dab, KOSUMDAN ONCE). SABIT.

ASAMA 1: teshis (mudahalenin YONU) — betimleyici
ASAMA 2: dort varyant (V1..V4), ESLESMIS kiyas + KOSULSUZ KONTROL (K3)

🔑 seviyeler()/oynat() KAYNAKTAN cagrilir (stop_mu_sure_mu.py), kopyalanmaz.
   oynat() parametreli degil -> V1/V2 icin ayni mantik yeniden kurulmaz;
   KAYNAKTAKI oynat AYNEN kullanilir ve varyantlar onun CIKTISINDAN degil,
   kendi kontrollu sarmalayicisindan uretilir (asagida acikca isaretli).
🔴 BIRIM = SEMBOL-GUN · ESLESMIS fark (ayni satir, farkli cikis).
SALT OKUMA.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, io, json, math, datetime, statistics, collections

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARSIV = os.path.join(PROJE, "testbot_aday_arsiv.jsonl")
MUM = os.path.join(PROJE, "scratchpad", "aday_pencere_1h")
KAYNAK = os.path.join(PROJE, "scratchpad", "stop_mu_sure_mu.py")
BAS = "2026-08-21"
SAAT_MS = 3600 * 1000
T_ESIK = 2.5          # on-kayit: 4 varyant -> +2,0 degil +2,5
FARK_ESIK = 0.5


def mekanik_yukle():
    src = open(KAYNAK, encoding="utf-8").read()
    k = src.index('return kar, j - i, "ZAMAN_STOP"')
    k = src.index("\n", k) + 1
    ns = {"__name__": "_mek", "__file__": KAYNAK}
    tut = _sys.stdout
    _sys.stdout = io.StringIO()
    try:
        exec(compile(src[:k], KAYNAK, "exec"), ns)
    finally:
        _sys.stdout = tut
    for f in ("seviyeler", "oynat"):
        if f not in ns:
            raise SystemExit("MEKANIK YUKLENEMEDI — betik REDDEDIYOR")
    return ns


M = mekanik_yukle()
seviyeler, oynat = M["seviyeler"], M["oynat"]
MALIYET, ASGARI, YAPI, ZS = M["MALIYET"], M["ASGARI_STOP"], M["YAPI_BAR"], M["ZAMAN_STOP"]
KISMI_R, KISMI_PAY = M["KISMI_R"], M["KISMI_PAY"]
TR_KAT, TR_2R, TR_3R = M["TR_KAT"], M["TR_2R"], M["TR_3R"]


def oynat_varyant(h, l, c, i, sl, tp1, tp2, risk, a, zaman_stop=None, tp1_tam=False):
    """KAYNAKTAKI oynat() ile AYNI mantik; yalniz iki parametre acildi:
         zaman_stop : varsayilan ZS (48) yerine kisaltilabilir   -> V1
         tp1_tam    : TP1'de %100 cikis (varsayilan %40)         -> V2
    Diger her sey (iz-suren kademeleri, TP2, bar-ici sira) AYNEN korunur.
    ⚠️ Bu bir YENIDEN YAZIM DEGIL, kontrollu parametrelestirmedir; V1/V2 disinda
       davranis kaynaktakiyle BIREBIR ayni olmali — asagidaki sinama bunu dogrular.
    """
    zs = ZS if zaman_stop is None else zaman_stop
    ref = c[i]
    stop, kalan, kar = sl, 1.0, 0.0
    kismi = False
    en_iyi_R = 0.0
    for j in range(i + 1, min(i + 1 + zs, len(c))):
        if l[j] <= stop:
            kar += kalan * (stop - ref) / ref * 100.0
            return kar, j - i, ("STOP" if not kismi else "STOP_TP1SONRASI")
        if h[j] >= tp2:
            kar += kalan * (tp2 - ref) / ref * 100.0
            return kar, j - i, "TP2"
        if not kismi:
            hr = ref + KISMI_R * risk
            if h[j] >= hr:
                pay = 1.0 if tp1_tam else KISMI_PAY
                kar += pay * (hr - ref) / ref * 100.0
                kalan -= pay
                kismi = True
                if kalan <= 1e-9:
                    return kar, j - i, "TP1_TAM"
        uc = h[j]
        en_iyi_R = max(en_iyi_R, (uc - ref) / risk)
        kat = TR_KAT if en_iyi_R < 2 else (TR_2R if en_iyi_R < 3 else TR_3R)
        stop = max(stop, uc - kat * a)
    j = min(i + zs, len(c) - 1)
    kar += kalan * (c[j] - ref) / ref * 100.0
    return kar, j - i, "ZAMAN_STOP"


def utc_ts(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M") - datetime.timedelta(hours=3)
    return int((d - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def sg_gun(w, alan):
    g = collections.defaultdict(list)
    for x in w:
        if x.get(alan) is not None:
            g[(x["sym"], x["_gun"])].append(x[alan])
    sgo = {k: sum(v) / len(v) for k, v in g.items()}
    gun = collections.defaultdict(list)
    for (s, d), v in sgo.items():
        gun[d].append(v)
    return sgo, [sum(v) / len(v) for v in gun.values()]


def esli_t(w, a_alan, b_alan):
    """ESLESMIS fark: ayni sembol-gun, iki cikis kurali."""
    ga, _ = sg_gun(w, a_alan)
    gb, _ = sg_gun(w, b_alan)
    ort = set(ga) & set(gb)
    if len(ort) < 5:
        return None, None, 0, None
    fark = collections.defaultdict(list)
    for k in ort:
        fark[k[1]].append(ga[k] - gb[k])
    gv = [sum(v) / len(v) for v in fark.values()]
    if len(gv) < 3:
        return (sum(gv) / len(gv)), None, len(ort), None
    m, sd = sum(gv) / len(gv), statistics.stdev(gv)
    se = sd / math.sqrt(len(gv))
    return m, (m / se if se else None), len(ort), (2.0 * se if se else None)


def main():
    print("pos'a GORE KOSULLU MEKANIK")
    print("on-kayit ON_KAYIT_pos_kosullu_mekanik.md (bd92dab) · olcutler SABIT")
    print("=" * 108)

    seri = {}
    for fn in os.listdir(MUM):
        if not fn.endswith(".json"):
            continue
        try:
            b = json.load(open(os.path.join(MUM, fn)))
        except Exception:
            continue
        if len(b) < YAPI + 5:
            continue
        b.sort(key=lambda z: z[0])
        seri[fn[:-5]] = {"h": [x[1] for x in b], "l": [x[2] for x in b],
                         "c": [x[3] for x in b],
                         "ix": {x[0]: j for j, x in enumerate(b)}}

    # ---------------------------------------------------- sinama: sarmalayici == kaynak
    R = []
    for l in open(ARSIV, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        ts = str(r.get("ts") or "")
        if ts[:10] < BAS or not str(r.get("rejim") or "").upper().startswith("BOGA"):
            continue
        s = r.get("sym")
        if not s or s not in seri or r.get("pos") is None:
            continue
        S = seri[s]
        t0 = utc_ts(ts)
        i = S["ix"].get(t0 - (t0 % SAAT_MS))
        if i is None or i < YAPI:
            continue
        sv = seviyeler(S["h"], S["l"], S["c"], i, "LONG")
        if not sv:
            continue
        sl, tp1, tp2, risk, a = sv
        ref = S["c"][i]
        if abs(ref - sl) / ref * 100.0 < ASGARI:
            continue
        r["_S"], r["_i"], r["_sv"], r["_ref"] = S, i, sv, ref
        r["_gun"] = ts[:10]
        R.append(r)

    # sarmalayici dogrulamasi — V-parametresiz hali kaynakla BIREBIR olmali
    hata = 0
    for x in R[:400]:
        S, i = x["_S"], x["_i"]
        sl, tp1, tp2, risk, a = x["_sv"]
        k1 = oynat(S["h"], S["l"], S["c"], i, "LONG", sl, tp1, tp2, risk, a)
        k2 = oynat_varyant(S["h"], S["l"], S["c"], i, sl, tp1, tp2, risk, a)
        if abs(k1[0] - k2[0]) > 1e-9 or k1[1] != k2[1] or k1[2] != k2[2]:
            hata += 1
    print("SARMALAYICI SINAMASI: 400 satirda kaynak ile fark = %d" % hata)
    if hata:
        print("  🔴 SARMALAYICI KAYNAKTAN SAPIYOR — betik REDDEDIYOR")
        raise SystemExit(1)
    print("  -> GECTI (V-parametresiz hal kaynakla birebir)")
    print("\nolculen satir: %d · pos<0.25: %d" % (len(R), sum(1 for x in R if x["pos"] < 0.25)))

    # ---------------------------------------------------- TABAN + varyantlar
    def calistir(x, **kw):
        S, i = x["_S"], x["_i"]
        sl, tp1, tp2, risk, a = x["_sv"]
        ref = x["_ref"]
        if kw.pop("genis_stop", False):
            sl = ref - 2.5 * a
            risk = ref - sl
            tp1 = ref + 2 * risk
            tp2 = tp1 + 1.5 * risk
        return oynat_varyant(S["h"], S["l"], S["c"], i, sl, tp1, tp2, risk, a, **kw)

    VAR = [("TABAN", {}),
           ("V1 zaman stopu 6 saat", {"zaman_stop": 6}),
           ("V2 TP1'de %100 cikis", {"tp1_tam": True}),
           ("V3 V1+V2", {"zaman_stop": 6, "tp1_tam": True}),
           ("V4 stop 2,5xATR", {"genis_stop": True})]

    for ad, kw in VAR:
        for x in R:
            kar, sure, seb = calistir(x, **dict(kw))
            k = ad.split()[0]
            x["net_" + k] = kar - MALIYET
            x["sure_" + k] = sure
            x["seb_" + k] = seb

    A = [x for x in R if x["pos"] < 0.25]
    B = [x for x in R if x["pos"] >= 0.25]

    # ---------------------------------------------------- ASAMA 1 TESHIS
    print("\n" + "=" * 108)
    print("ASAMA 1) TESHIS — mudahalenin YONU (betimleyici)")
    print("-" * 108)
    st = [x["sure_TABAN"] for x in A if str(x["seb_TABAN"]).startswith("STOP")]
    print("  pos<0.25, mevcut mekanik · stop olan %d pozisyon" % len(st))
    if st:
        c = collections.Counter(min(s, 13) for s in st)
        print("  stop tetiklenme saati (13+ birlestirildi):")
        for s in sorted(c):
            print("    %2d. saat %s %d (%%%.0f)"
                  % (s, "#" * int(40.0 * c[s] / max(c.values())), c[s], 100.0 * c[s] / len(st)))
        ilk4 = sum(1 for s in st if s <= 4)
        print("  -> ilk 4 saatte stop olan: %d (%%%.0f)  ·  4. saatten SONRA: %d (%%%.0f)"
              % (ilk4, 100.0 * ilk4 / len(st), len(st) - ilk4, 100.0 * (len(st) - ilk4) / len(st)))
        if ilk4 / len(st) > 0.5:
            print("     TESHIS: stoplarin cogu SEKMENIN ICINDE -> 'stop cok dar' yonu")
        else:
            print("     TESHIS: stoplarin cogu 4. saatten SONRA -> 'cikis cok gec' yonu")

    # MFE
    print("\n  MFE (azami lehte hareket) ve zirvesinin saati — pos<0.25:")
    mfe, zir, hic = [], [], 0
    for x in A:
        S, i = x["_S"], x["_i"]
        ref = x["_ref"]
        en, ens = 0.0, 0
        for j in range(i + 1, min(i + 1 + 24, len(S["c"]))):
            v = (S["h"][j] - ref) / ref * 100.0
            if v > en:
                en, ens = v, j - i
        mfe.append(en)
        if en > 0:
            zir.append(ens)
        else:
            hic += 1
    if mfe:
        print("    MFE medyan %+.2f%% · %%25 %+.2f%% · %%75 %+.2f%%"
              % (statistics.median(mfe), sorted(mfe)[len(mfe) // 4], sorted(mfe)[3 * len(mfe) // 4]))
        print("    hic artiya gecmeyen: %d (%%%.0f)" % (hic, 100.0 * hic / len(A)))
        if zir:
            print("    MFE zirvesinin saati: medyan %d · ilk 4 saatte olan %%%.0f"
                  % (statistics.median(zir), 100.0 * sum(1 for z in zir if z <= 4) / len(zir)))
    tp1u = sum(1 for x in A if x["seb_TABAN"] in ("TP2", "STOP_TP1SONRASI"))
    tp2u = sum(1 for x in A if x["seb_TABAN"] == "TP2")
    print("\n  TP1'e ulasan %d · bunlarin TP2'ye gideni %d (%%%.0f)"
          % (tp1u, tp2u, 100.0 * tp2u / tp1u if tp1u else 0))

    # ---------------------------------------------------- ASAMA 2 VARYANTLAR
    print("\n" + "=" * 108)
    print("ASAMA 2) VARYANTLAR — ESLESMIS kiyas (ayni satirlar, farkli cikis)")
    print("-" * 108)
    print("  %-24s %10s %11s %9s %9s %10s %9s"
          % ("varyant", "sem-gun", "pos<0.25 %", "fark", "esli t", "med sure", "stop%"))
    tb, _ = sg_gun(A, "net_TABAN")
    tb_ort = sum(tb.values()) / len(tb)
    print("  %-24s %10d %+10.3f%% %9s %9s %9.1f %8.0f%%"
          % ("TABAN (mevcut)", len(tb), tb_ort, "-", "-",
             statistics.median([x["sure_TABAN"] for x in A]),
             100.0 * sum(1 for x in A if str(x["seb_TABAN"]).startswith("STOP")) / len(A)))
    sonuc = []
    for ad, kw in VAR[1:]:
        k = ad.split()[0]
        g, _ = sg_gun(A, "net_" + k)
        m, t, n, mde = esli_t(A, "net_" + k, "net_TABAN")
        ort = sum(g.values()) / len(g)
        sonuc.append((m if m else -9, t, ad, k, mde))
        print("  %-24s %10d %+10.3f%% %+8.3f%% %8s %9.1f %8.0f%%"
              % (ad, len(g), ort, m if m else 0, ("%+.2f" % t) if t else "-",
                 statistics.median([x["sure_" + k] for x in A]),
                 100.0 * sum(1 for x in A if str(x["seb_" + k]).startswith("STOP")) / len(A)))

    sonuc.sort(reverse=True)
    m0, t0v, ad0, k0, mde0 = sonuc[0]

    # ---------------------------------------------------- K2 bolunmus yari
    print("\n  K2 — bolunmus yari (en iyi varyant: %s)" % ad0)
    gunler = sorted({x["_gun"] for x in A})
    orta = gunler[len(gunler) // 2]
    yariler = []
    for et, sec in (("A", lambda x: x["_gun"] < orta), ("B", lambda x: x["_gun"] >= orta)):
        w = [x for x in A if sec(x)]
        m, t, n, _ = esli_t(w, "net_" + k0, "net_TABAN")
        yariler.append(m if m else 0)
        print("    %s yari: fark %s · t %s · sembol-gun %d"
              % (et, ("%+.3f%%" % m) if m is not None else "-",
                 ("%+.2f" % t) if t else "-", n))

    # ---------------------------------------------------- K3 KOSULSUZ KONTROL
    print("\n  🔴 K3 — KOSULSUZ KONTROL: ayni varyant TUM satirlara uygulansaydi?")
    m_all, t_all, n_all, _ = esli_t(R, "net_" + k0, "net_TABAN")
    m_b, t_b, n_b, _ = esli_t(B, "net_" + k0, "net_TABAN")
    print("    pos<0.25 dilimi : %+.3f%% (t %s)" % (m0, ("%+.2f" % t0v) if t0v else "-"))
    print("    pos>=0.25 dilimi: %+.3f%% (t %s)" % (m_b if m_b else 0, ("%+.2f" % t_b) if t_b else "-"))
    print("    TUM satirlar    : %+.3f%% (t %s)" % (m_all if m_all else 0, ("%+.2f" % t_all) if t_all else "-"))
    k3 = (m_b is None) or (m0 > 0 and m_b is not None and m0 > 2 * abs(m_b))
    print("    -> K3: %s" % ("GECTI (kazanc pos<0.25'e OZGU)" if k3
                             else "DUSTU (kazanc kosulsuz da var -> 31. varyant)"))

    # ---------------------------------------------------- HUKUM
    print("\n" + "=" * 108)
    print("BIRINCIL HUKUM — en iyi varyant: %s" % ad0)
    print("=" * 108)
    k1 = m0 > 0 and t0v is not None and t0v >= T_ESIK
    k2 = yariler[0] > 0 and yariler[1] > 0
    k4 = m0 >= FARK_ESIK
    print("  K1  fark>0 ve esli t >= +%.1f : %-6s (%.3f / %s)"
          % (T_ESIK, "GECTI" if k1 else "DUSTU", m0, ("%+.2f" % t0v) if t0v else "-"))
    print("  K2  iki yarida da > 0        : %-6s (A %+.3f · B %+.3f)"
          % ("GECTI" if k2 else "DUSTU", yariler[0], yariler[1]))
    print("  K3  kosulsuz kontrol         : %-6s" % ("GECTI" if k3 else "DUSTU"))
    print("  K4  fark >= %%%.1f            : %-6s (%.3f)" % (FARK_ESIK, "GECTI" if k4 else "DUSTU", m0))
    print()
    if k1 and k2 and k3 and k4:
        h = "GECTI"
    elif k1 and k2 and not k3:
        h = "ZAYIF — kazanc var ama pos'a OZGU DEGIL (31. varyant riski)"
    elif k1 and k2:
        h = "ZAYIF"
    else:
        h = "DUSTU"
    print("  HUKUM: %s" % h)
    if mde0:
        print("  GUC: MDE %.3f · |fark| %.3f -> %s"
              % (mde0, abs(m0), "gorulebilir" if abs(m0) > mde0 else "GOREMIYORUZ"))

    print("\n  cikis sebebi dagilimi (pos<0.25):")
    for ad, kw in VAR:
        k = ad.split()[0]
        c = collections.Counter(x["seb_" + k] for x in A)
        tp = sum(c.values())
        print("    %-24s %s" % (ad, {a: "%.0f%%" % (100.0 * b / tp) for a, b in c.most_common()}))

    print("\n" + "=" * 108)
    print("⚠️ Gecse bile KOD DEGISMEZ: portfoy asamasi + ikinci BOGA epizodu.")
    print("bot dosyalarina yazim: YOK")


if __name__ == "__main__":
    main()
