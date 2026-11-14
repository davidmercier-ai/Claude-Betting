# Project brief: Abacus betting system

You are building a sports betting prediction, line-shopping, and value-evaluation pipeline for one user (David, bets from Ohio, Ohio-legal books only).

Read `abacus_system.md` first. It is the source of truth for the three measures, ladders, draft cutoffs, principles, verification gate, data sources and workflow. `pull_odds.py` is a working draft of the odds pull.

## Hard rules
1. Never place bets, log into sportsbooks, or automate any book's site. The user opens each link and places bets personally.
2. Never invent grades, percentages, or confidence. All cutoffs live in one config file and are labeled draft until the user approves them.
3. External win probabilities (providers, sites) are never the system's own probability. Keep them in a separate column and label them external.
4. A price is verified only after the user confirms it on the book's betslip. The pipeline can mark a price "stale" by age, but never "verified."
5. Keep the API key in an environment variable. Never write it into a file, log, or commit.
6. Do not claim a model beats the market. Report calibration and closing-line results as they are, including bad ones.
7. If a book key, endpoint or field is uncertain, check the API's own docs or response before relying on it. Say what you could not confirm.

## Target layout
```
abacus/
  config.yaml        cutoffs, book keys, Kelly settings, paths (all drafts)
  pull_odds.py       odds + deep links to timestamped CSV
  measures.py        Phase, Edge, Value classifiers + odds math (de-vig, EV, fair odds)
  model/nfl.py       NFL probability model from nflverse data
  grade_slate.py     reads odds CSV + probabilities, outputs a graded slate
  ledger.py          bet log (SQLite or CSV) and CLV tracking
  tests/             unit tests for the math and classifiers
```

## Build order
1. **Measures and tests.** Implement `measures.py`: American/decimal conversion, proportional de-vig, vig-free market consensus, EV per $1, edge in points, fair odds. Classify Phase (separate bands for game lines and props), Edge and Value from `config.yaml`. Apply the verification caps (Edge caps at Queen, Value caps at Extra Sharp until verified). Unit-test every function with hand-checked examples.
2. **Odds pull.** Run `pull_odds.py` against the live API with a free key. Confirm the Ohio book keys against the API's bookmaker list, fix the list, confirm which link levels each book returns, and add retries and a clear message when credits run low.
3. **Grade a slate.** `grade_slate.py` joins the odds CSV with a probabilities file (game, selection, true probability, source). It outputs, per play: Phase, Edge, Value, best book, best price, link, price age, and verified status (always "unverified" until the user confirms).
4. **NFL model.** Use nflverse (nfl_data_py or nflreadr) for play-by-play, injuries, schedules and lines. Build a baseline win-probability model first. Backtest on past seasons with a time split, no leakage, and report Brier score and a calibration table. Compare against the closing line where available.
5. **Ledger and CLV.** Log each bet: date, sport, game, selection, book, line, confirmed odds, stake or units, link, Phase, Edge, Value, result, closing odds. Compute CLV and results by Phase, Edge and Value tier so the tiers can be tested against outcomes.
6. **Extend.** Props (anytime TD, goalscorer) via the per-event odds endpoint, then NHL and NBA models. Watch the credit cost before adding markets.
7. **Parked.** Stake (Tithe) for bankroll and units. Do not build until asked.

## Working style
- Short plan first, then build step by step. Ask before spending API credits on anything beyond the default pull.
- After each step, run the tests and show the results.
- Keep outputs mobile-friendly: the user reads results on a phone, so graded slates should print as short lists.
- Record decisions and open questions in `DECISIONS.md`.

## Definitions at a glance
- Probability (Phase 🌙): 🌑 🌒 🌓 🌔 🌕 🔴
- Edge (Gambit ♟︎): ♟︎ ♞ ♝ ♜ ♛ ♚
- Value (Abacus 🧮): ☠️ ⚖️ 🔪 🪓 🩸 ⚔️
- Stake (Tithe 🪙), parked: 🪙 💵 💰 🏦 💎 🏆, ⛔ for no bet
