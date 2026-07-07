#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F&G — Fear & Greed endeksi (D4, deterministik; 2026-07-02, B-eksik #2 duzeltmesi).
Kaynak: alternative.me ucretsiz API (anahtarsiz). Eskiden web_search ile aliniyordu.
SKILL D4 kurali: >75 dagitim | 50-75 normal | 25-50 birikim | <25 guclu dip. VETO: F&G>80 -> long girme.
Kullanim: python fng.py [--gun 30]
"""
import json, os, sys, argparse, urllib.request, statistics

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def etiket(v):
    if v > 80: return "VETO_BOLGESI (>80: long girme)"
    if v > 75: return "DAGITIM (>75)"
    if v >= 50: return "NORMAL (50-75)"
    if v >= 25: return "BIRIKIM (25-50)"
    if v >= 15: return "GUCLU_DIP (<25)"
    return "ASIRI_KORKU (<15: DCA hizlandirici esigi)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gun", type=int, default=30)
    a = ap.parse_args()
    try:
        req = urllib.request.Request(f"https://api.alternative.me/fng/?limit={a.gun}&format=json",
                                     headers={"User-Agent": "fng/1.0"})
        d = json.load(urllib.request.urlopen(req, timeout=15)).get("data", [])
    except Exception as e:
        print(json.dumps({"error": f"alternative.me erisilemedi: {str(e)[:80]} -> web_search yedegine dus"},
                         ensure_ascii=False))
        sys.exit(1)
    if not d:
        print(json.dumps({"error": "veri yok"}, ensure_ascii=False)); sys.exit(1)
    vals = [int(x["value"]) for x in d]
    simdi = vals[0]
    out = {
        "fng": simdi,
        "siniflama_kaynak": d[0].get("value_classification"),
        "skill_etiketi": etiket(simdi),
        "dun": vals[1] if len(vals) > 1 else None,
        "ort_7g": round(statistics.mean(vals[:7]), 1) if len(vals) >= 7 else None,
        "ort_30g": round(statistics.mean(vals[:30]), 1) if len(vals) >= 30 else None,
        "min_30g": min(vals), "max_30g": max(vals),
        "kaynak": "alternative.me (ucretsiz, anahtarsiz)",
        "not": "D4 girdisi. VETO: >80 long girme. <15 = DCA hizlandirici esigi (dip-alim kurali).",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
