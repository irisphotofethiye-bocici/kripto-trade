#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOBETCI — firsat/pozisyon alarmi (2026-07-03). "PC acikken 15dk'da bir tarar ama
kimse gormezse firsat kacar" sorununu cozer: radar/defter/rejimi izler, tetik olunca
Telegram + Windows toast + nobetci_alarm.log'a yazar (Monitor bu log'u izleyip Claude'u uyandirir).

Tetikler:
  (a) radar_active.json yeni aktif sinyal (skor>=esikler.radar_alert_skor, dedup+cooldown)
  (b) acik tahminde (kripto_portfoy.json->tahminler, sonuc_durum=ACIK) fiyat giris/stop/tp1 kesti
  (c) kripto-config.json->ekstra_alarmlar seviyesi kesildi (elle konan seviye, orn ADA gecersizlik)
  (d) BTC rejim flip (evren.btc_rejim(), onceki rejim state'te tutulur)

Anti-spam: nobetci_state.json'da tetik-basina cooldown (varsayilan 60dk) + alarm log 300 satirla sinirli.
LLM YOK, deftere YAZMAZ. Kullanim: python nobetci.py [--cooldown_dk 60] [--test]
"""
import json, os, sys, argparse, datetime, urllib.request, urllib.parse

import evren
from katip import fiyat, f as _f

HERE = os.path.dirname(os.path.abspath(__file__))
STATEF = os.path.join(HERE, "nobetci_state.json")
LOGF = os.path.join(HERE, "nobetci_alarm.log")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")


def _load_state():
    try:
        return json.load(open(STATEF, encoding="utf-8"))
    except Exception:
        return {"son_tetik": {}, "rejim": None}


def _save_state(st):
    json.dump(st, open(STATEF, "w", encoding="utf-8"), ensure_ascii=False)


def _cooldown_gecti(st, anahtar, cooldown_dk):
    son = st.get("son_tetik", {}).get(anahtar)
    if not son:
        return True
    try:
        dt = datetime.datetime.strptime(son, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return True
    return (datetime.datetime.now() - dt).total_seconds() / 60 >= cooldown_dk


def telegram_gonder(msg):
    """kripto-config.json -> telegram_bot_token/telegram_chat_id. Yoksa sessizce atla."""
    cfg = evren.cfg()
    tok, chat = cfg.get("telegram_bot_token", ""), cfg.get("telegram_chat_id", "")
    if not tok or not chat:
        return False
    try:
        url = f"https://api.telegram.org/bot{tok}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat, "text": msg}).encode()
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15)
        return True
    except Exception:
        return False


def toast_gonder(baslik, msg):
    """Windows toast, best-effort (WinRT). PowerShell yoksa/hata verirse sessizce gecilir."""
    try:
        import subprocess
        ps = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] > $null;"
            "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType=WindowsRuntime] > $null;"
            f"$t = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent(0);"
            f"$texts = $t.GetElementsByTagName('text');"
            f"$texts.Item(0).AppendChild($t.CreateTextNode('{baslik}')) > $null;"
            f"$texts.Item(1).AppendChild($t.CreateTextNode('{msg}')) > $null;"
            "$toast = [Windows.UI.Notifications.ToastNotification]::new($t);"
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Nobetci').Show($toast)"
        )
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       timeout=10, capture_output=True)
        return True
    except Exception:
        return False


def alarm_yaz(tur, sym, detay):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rec = {"ts": ts, "tur": tur, "sym": sym, "detay": detay}
    with open(LOGF, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    try:
        if os.path.exists(LOGF):
            ln = open(LOGF, encoding="utf-8").read().splitlines()
            if len(ln) > 300:
                open(LOGF, "w", encoding="utf-8").write("\n".join(ln[-300:]) + "\n")
    except Exception:
        pass
    msg = f"[NOBETCI] {tur} {sym}: {detay}"
    telegram_gonder(msg)
    toast_gonder(f"Nobetci: {sym}", detay[:120])
    return msg


def kontrol_radar(st, cooldown_dk, esik_skor):
    tetikler = []
    try:
        ra = json.load(open(os.path.join(HERE, "radar_active.json"), encoding="utf-8"))
    except Exception:
        return tetikler
    for s in ra.get("aktif_sinyaller", []):
        sym, skor, stage = s.get("sym"), s.get("score", 0), s.get("stage")
        if skor < esik_skor:
            continue
        anahtar = f"radar:{sym}"
        if not _cooldown_gecti(st, anahtar, cooldown_dk):
            continue
        detay = (f"skor={skor} stage={stage} smart={s.get('smart')} "
                 f"fund={s.get('funding')} dusuk_float={s.get('dusuk_float')} rejim={ra.get('rejim', {}).get('rejim')}")
        tetikler.append(("RADAR", sym, detay, anahtar))
    return tetikler


def kontrol_tahminler(st, cooldown_dk):
    tetikler = []
    try:
        defter = json.load(open(os.path.join(HERE, "kripto_portfoy.json"), encoding="utf-8"))
    except Exception:
        return tetikler
    for t in defter.get("tahminler", []):
        if t.get("sonuc_durum", "ACIK") != "ACIK":
            continue
        sym, yon = t.get("token"), (t.get("yon") or "?")[:1].upper()
        giris, stop, tp1 = _f(t.get("giris")), _f(t.get("stop")), _f(t.get("tp1"))
        if not sym or giris is None:
            continue
        px = fiyat(sym)
        if px is None:
            continue
        if stop is not None:
            ihlal = (px <= stop) if yon == "L" else (px >= stop)
            if ihlal:
                anahtar = f"stop:{sym}:{t.get('no')}"
                if _cooldown_gecti(st, anahtar, cooldown_dk):
                    tetikler.append(("STOP_IHLAL", sym, f"#{t.get('no')} yon={t.get('yon')} anlik={px} stop={stop}", anahtar))
        if tp1 is not None:
            ulasti = (px >= tp1) if yon == "L" else (px <= tp1)
            if ulasti:
                anahtar = f"tp1:{sym}:{t.get('no')}"
                if _cooldown_gecti(st, anahtar, cooldown_dk):
                    tetikler.append(("TP1_ULASTI", sym, f"#{t.get('no')} yon={t.get('yon')} anlik={px} tp1={tp1}", anahtar))
        # emir dolum tetigi (limit giris fiyati kesildi ama henuz aktif_futures'a tasinmadi)
        emir = str(t.get("emir_durumu") or "")
        if "BEKLEMEDE" in emir.upper() and giris is not None:
            dolmus = (px <= giris) if yon == "L" else (px >= giris)
            if dolmus:
                anahtar = f"dolum:{sym}:{t.get('no')}"
                if _cooldown_gecti(st, anahtar, cooldown_dk):
                    tetikler.append(("EMIR_DOLUM_OLASI", sym, f"#{t.get('no')} anlik={px} giris={giris} -> Binance'ten teyit et", anahtar))
    return tetikler


def kontrol_ekstra(st, cooldown_dk):
    tetikler = []
    ops = {"<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b}
    for a in evren.cfg().get("ekstra_alarmlar", []):
        sym, op, seviye = a.get("sym"), a.get("op"), _f(a.get("seviye"))
        if not sym or op not in ops or seviye is None:
            continue
        px = fiyat(sym)
        if px is None:
            continue
        if ops[op](px, seviye):
            anahtar = f"ekstra:{sym}:{op}:{seviye}"
            if _cooldown_gecti(st, anahtar, cooldown_dk):
                tetikler.append(("EKSTRA_ALARM", sym, f"anlik={px} {op} {seviye} -> {a.get('not', '')}", anahtar))
    return tetikler


def kontrol_rejim(st):
    tetikler = []
    rej = evren.btc_rejim().get("rejim")
    onceki = st.get("rejim")
    # BILINMIYOR = gecici API/veri hatasi (2026-07-03 kaniti: BILINMIYOR->AYI hemen ardindan geldi,
    # gercek rejim hic degismemisti) -> ne tetik sayilir ne state'e yazilir (son BILINEN rejim korunur)
    if rej and rej != "BILINMIYOR":
        if onceki and onceki != "BILINMIYOR" and rej != onceki:
            tetikler.append(("REJIM_FLIP", "BTC", f"{onceki} -> {rej}", "rejim"))
        st["rejim"] = rej
    return tetikler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cooldown_dk", type=float, default=60.0)
    ap.add_argument("--test", action="store_true", help="sahte alarm gonder (Telegram+toast+log ucuca test)")
    a = ap.parse_args()

    if a.test:
        msg = alarm_yaz("TEST", "BTC", "nobetci --test: uctan uca kontrol")
        print(msg)
        return

    st = _load_state()
    esik_skor = evren.esik("radar_alert_skor", 40.0)
    tumu = []
    tumu += kontrol_radar(st, a.cooldown_dk, esik_skor)
    tumu += kontrol_tahminler(st, a.cooldown_dk)
    tumu += kontrol_ekstra(st, a.cooldown_dk)
    tumu += kontrol_rejim(st)

    ts_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for tur, sym, detay, anahtar in tumu:
        alarm_yaz(tur, sym, detay)
        st.setdefault("son_tetik", {})[anahtar] = ts_now
        print(f"ALARM {tur} {sym}: {detay}")
    if not tumu:
        print(f"[{ts_now}] tetik yok")
    _save_state(st)


if __name__ == "__main__":
    main()
