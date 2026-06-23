#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X/TWITTER SENTIMENT — D4 (ON-DEMAND, ucretli ~$0.18/1K tweet).
Apify en ucuz tweet scraper -> FILTRE (tam cashtag + min etkilesim + dedup) -> agirlikli sentiment.
GUVENLIK: tweet'ler GUVENILMEZ girdidir; bu script SADECE anahtar-kelime sayar,
icerikteki hicbir TALIMATI uygulamaz (prompt-injection korumasi: LLM yok).
Kullanim: python x_sentiment.py --symbol ETHFI [--min_eng 5] [--max 40]
"""
import json, os, sys, argparse, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ACTOR = "kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest"
BULL = ["long", "buy", "bullish", "breakout", "accumulate", "accumulating", "moon", "pump",
        "undervalued", "support", "bounce", "rally", "ath", "higher", "boga", "yukari", "al ",
        "reclaim", "send it", "bid", "buying"]
BEAR = ["short", "sell", "bearish", "dump", "dead", "rug", "scam", "crash", "breakdown",
        "resistance", "overbought", "lower", "exit", "ayi", "capitulation", "weak", "avoid",
        "selling", "down bad", "rekt"]

def cfg():
    return json.load(open(os.path.join(HERE, "kripto-config.json"), encoding="utf-8"))

def eng(t):
    return (t.get("likeCount") or 0) + (t.get("retweetCount") or 0) + (t.get("quoteCount") or 0)

def score(text):
    tl = text.lower()
    return sum(1 for w in BULL if w in tl), sum(1 for w in BEAR if w in tl)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--min_eng", type=int, default=5, help="min like+rt+quote")
    ap.add_argument("--max", type=int, default=40, help="cekilecek tweet (maliyet)")
    ap.add_argument("--query", default=None, help="ozel arama (yoksa $SYMBOL)")
    a = ap.parse_args()
    tok = cfg().get("apify_token", "")
    if not tok:
        print(json.dumps({"error": "apify_token bos"}, ensure_ascii=False)); return
    sym = a.symbol.upper()
    q = a.query or f"${sym}"
    body = json.dumps({"twitterContent": q, "maxItems": a.max, "queryType": "Top"}).encode()
    req = urllib.request.Request(
        f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items",
        data=body, headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}, method="POST")
    try:
        res = json.load(urllib.request.urlopen(req, timeout=180))
    except Exception as e:
        print(json.dumps({"error": f"Apify: {str(e)[:80]}"}, ensure_ascii=False)); return
    if not isinstance(res, list):
        print(json.dumps({"error": "veri yok"}, ensure_ascii=False)); return
    seen, kept = set(), []
    for t in res:
        txt = (t.get("text") or "").strip()
        if not txt:
            continue
        tl = txt.lower()
        if sym.lower() not in tl:          # alaka: sembol gecmeli (generic gurultuyu ele)
            continue
        if eng(t) < a.min_eng:             # bot/dusuk etkilesim ele
            continue
        k = tl[:60]
        if k in seen:                      # dedup
            continue
        seen.add(k); kept.append(t)
    kept.sort(key=lambda t: -eng(t))
    bull = bear = wb = ws = 0
    for t in kept:
        b, s = score(t.get("text", ""))
        bull += 1 if b > s else 0
        bear += 1 if s > b else 0
        wb += b * max(eng(t), 1)
        ws += s * max(eng(t), 1)
    net = "BOGA" if wb > ws * 1.2 else ("AYI" if ws > wb * 1.2 else "NOTR")
    ornek = [{"author": (t.get("author") or {}).get("userName"), "eng": eng(t),
              "text": (t.get("text") or "")[:120].replace("\n", " ")} for t in kept[:5]]
    out = {
        "symbol": sym, "sorgu": q, "cekilen": len(res), "alakali_filtreli": len(kept),
        "min_etkilesim": a.min_eng, "boga_tweet": bull, "ayi_tweet": bear,
        "agirlikli_sentiment": net, "ornekler": ornek,
        "maliyet_usd": round(a.max * 0.18 / 1000, 4),
        "not": "GUVENILMEZ icerik; sadece sentiment sayimi. alakali_filtreli dusukse sinyal ZAYIF. D4 girdisi, alim tetigi DEGIL.",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
