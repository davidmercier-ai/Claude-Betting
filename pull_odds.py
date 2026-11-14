#!/usr/bin/env python3
"""Pull game-line odds from The Odds API into a timestamped CSV.

Setup:
    pip install requests
    export ODDS_API_KEY=your_key_here        (Windows: set ODDS_API_KEY=your_key_here)

Run:
    python pull_odds.py                       NFL, NHL, NBA, next 36 hours
    python pull_odds.py --sports nfl          NFL only
    python pull_odds.py --hours 72            wider window

Output: odds_YYYYMMDD_HHMMSS.csv, one row per book, market and selection.
Every row carries pulled_at_utc and last_update, so each price is timestamped.
Each row also carries a link to the book (link) and how deep it goes (link_level):
betslip, market, event or homepage. Open the link, confirm the price on the book's
own betslip, then log the bet with that link.
Upload the CSV to Claude to run Phase, Edge and Value on it.
"""
import argparse
import csv
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

BASE = "https://api.the-odds-api.com/v4"
SPORTS = {
    "nfl": "americanfootball_nfl",
    "nhl": "icehockey_nhl",
    "nba": "basketball_nba",
}
# Edit this list to the books you can bet at in Ohio.
# Check each key against the API's own bookmaker list before trusting it.
BOOKS = ["draftkings", "fanduel", "betmgm", "williamhill_us", "betrivers", "espnbet", "fanatics"]
FIELDS = [
    "pulled_at_utc", "sport", "event_id", "commence_time", "home", "away",
    "book", "market", "selection", "point", "american_odds", "last_update",
    "link", "link_level",
]

# The API does not return book homepages, so these are the fallback.
# Check each one yourself and fill in any book you add.
BOOK_HOME = {
    "draftkings": "https://sportsbook.draftkings.com",
    "fanduel": "https://sportsbook.fanduel.com",
    "betmgm": "https://sports.betmgm.com",
    "williamhill_us": "https://sportsbook.caesars.com",
    "betrivers": "https://oh.betrivers.com",
    "fanatics": "https://sportsbook.fanatics.com",
}


def best_link(book, event_link, market_link, outcome_link):
    """Deepest link the book provides, falling back to a shallower one."""
    if outcome_link:
        return outcome_link, "betslip"
    if market_link:
        return market_link, "market"
    if event_link:
        return event_link, "event"
    return BOOK_HOME.get(book, ""), "homepage"


def pull(sport_key, markets, books, hours, key):
    now = datetime.now(timezone.utc)
    params = {
        "apiKey": key,
        "bookmakers": ",".join(books),
        "markets": ",".join(markets),
        "oddsFormat": "american",
        "dateFormat": "iso",
        "includeLinks": "true",
        "commenceTimeFrom": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commenceTimeTo": (now + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    r = requests.get(f"{BASE}/sports/{sport_key}/odds", params=params, timeout=30)
    if r.status_code != 200:
        sys.exit(f"{sport_key}: HTTP {r.status_code}: {r.text[:300]}")
    return r.json(), r.headers.get("x-requests-remaining"), r.headers.get("x-requests-used")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sports", nargs="+", default=["nfl", "nhl", "nba"], choices=list(SPORTS))
    ap.add_argument("--markets", nargs="+", default=["h2h", "spreads", "totals"])
    ap.add_argument("--hours", type=int, default=36)
    ap.add_argument("--books", nargs="+", default=BOOKS)
    args = ap.parse_args()

    key = os.environ.get("ODDS_API_KEY")
    if not key:
        sys.exit("Set ODDS_API_KEY first.")

    pulled_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for s in args.sports:
        events, remaining, used = pull(SPORTS[s], args.markets, args.books, args.hours, key)
        for ev in events:
            for bk in ev.get("bookmakers", []):
                for mk in bk.get("markets", []):
                    for o in mk.get("outcomes", []):
                        link, level = best_link(bk["key"], bk.get("link"), mk.get("link"), o.get("link"))
                        rows.append({
                            "pulled_at_utc": pulled_at,
                            "sport": s,
                            "event_id": ev["id"],
                            "commence_time": ev["commence_time"],
                            "home": ev["home_team"],
                            "away": ev["away_team"],
                            "book": bk["key"],
                            "market": mk["key"],
                            "selection": o["name"],
                            "point": o.get("point", ""),
                            "american_odds": o["price"],
                            "last_update": mk.get("last_update", bk.get("last_update", "")),
                            "link": link,
                            "link_level": level,
                        })
        print(f"{s}: {len(events)} games. Credits used {used}, remaining {remaining}.")

    if not rows:
        sys.exit("No odds returned. Check the sport is in season, the time window, and the book keys.")

    out = datetime.now().strftime("odds_%Y%m%d_%H%M%S.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
