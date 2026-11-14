# Abacus system: master file

Draft as of Nov 14, 2026. Every cutoff below is a placeholder until approved.

## The three measures

| Measure | Engine | Question |
|---|---|---|
| Probability | Phase 🌙 | How likely is the outcome? |
| Edge | Gambit ♟︎ | How far is my number from the market's? |
| Value | Abacus 🧮 | Does the price pay enough for my number? |

Order of use: Probability, then Edge, then Value.

### Probability (Phase 🌙)
- Input: true probability. For now it is typed in; a model supplies it later.
- Calculates: the probability itself, and fair odds = 1 / probability.
- Ladder: 🌑 New Moon, 🌒 Waxing Crescent, 🌓 First Quarter, 🌔 Waxing Gibbous, 🌕 Full Moon, 🔴 Blood Moon.
- Draft bands, game lines (%): under 20, 20-40, 40-60, 60-80, 80-90, 90 and up.
- Draft bands, props (%): under 10, 10-20, 20-35, 35-50, 50-65, 65 and up.

### Edge (Gambit ♟︎)
- Inputs: true probability; odds on both sides from several books.
- Calculates: true probability minus the market's fair probability, in points. Fair probability is the vig-free average across books. With only one side entered, it falls back to the best price with the vig still in it.
- Ladder: ♟︎ Pawn, ♞ Knight, ♝ Bishop, ♜ Rook, ♛ Queen, ♚ King.
- Draft cutoffs (points where each tier starts): 1, 2, 3.5, 5, 7, 10.
- Cap: ♛ Queen until the play is verified.

### Value (Abacus 🧮)
- Inputs: true probability; odds at each book.
- Calculates: EV per $1 = probability x decimal odds - 1, at the best price.
- Ladder: ☠️ Poison, ⚖️ Fair, 🔪 Sharp, 🪓 Extra Sharp, 🩸 Bleeding, ⚔️ Lethal.
- Draft cutoffs (EV% where each tier starts after Poison): -2, 2, 5, 9, 14.
- Cap: 🪓 Extra Sharp until the play is verified.

## Parked: Stake (Tithe 🪙)
Units to place, sized from bankroll.
- Ladder: 🪙 💵 💰 🏦 💎 🏆, with ⛔ for no bet.
- Method: Kelly fraction = (p x d - 1) / (d - 1), played at a fraction of Kelly (quarter by default), capped per bet.
- Draft tiers: 0.25u, 0.5u, 1u, 2u, 3u, 5u. 1 unit = 1% of bankroll by default.

## Operating principles
1. Probability and value are separate measurements. A likely winner can be a terrible bet.
2. Price matters. The same selection can be Poison at one book and Sharp at another.
3. Never confuse external model consensus with Abacus's own probability.
4. Injury, lineup, starting-pitcher, goalie, weather and matchup checks are sport-specific gates.
5. No certification without a defensible probability and a verified price.
6. No invented grades, percentages or confidence.

## Verification gate
A play is verified when the price is confirmed at the book (timestamped) and the sport-specific checks are done. Until then, Edge caps at ♛ and Value caps at 🪓.

## Data sources
- Prices: The Odds API (free tier, about 40 books, REST polling). Alternatives: SportsGameOdds, SharpAPI, OddsPapi.
- Probability model inputs: nflverse (nflfastR, nflreadr, nfl_data_py) for play-by-play, injuries, schedules and lines.
- External win probabilities: sanity check only, never the Abacus probability.
- Closing line for CLV: Pinnacle closing odds, via an API that carries them.
- Not yet researched: NHL and NBA model data, weather feeds, official injury report timing.

## Linking bets to books by URL
The Odds API returns deep links when `includeLinks=true`, and `pull_odds.py` sets it. Each CSV row has `link` and `link_level`.

Link levels, deepest first:
1. `betslip`: opens the book with the bet already on the slip.
2. `market`: opens that market (moneyline, spread, total) on the book.
3. `event`: opens the game page.
4. `homepage`: fallback from the `BOOK_HOME` list in the script. The API does not supply homepages, so check each one.

Which levels you get depends on the book, so expect a mix.

Steps for each play:
1. Pick the book with the best price from the CSV (Value uses the best price).
2. Open that row's `link`.
3. Confirm the odds and line on the book's own betslip. If they differ from the CSV, the CSV price is stale: use the betslip price, or skip the bet.
4. Place the bet.
5. Log it with the book, the confirmed price, the time, and the link.

A price counts as verified only after step 3. Odds move, links can expire, and a betslip link may not fill in on some apps, so the betslip price always wins over the CSV.

Ledger columns for logged bets: date, sport, game, selection, book, line, confirmed odds, units or stake, link, Phase, Edge, Value, result, closing odds.

## Workflow
1. Run `pull_odds.py` to pull timestamped multi-book odds and links to CSV.
2. Supply a true probability per play.
3. Run Phase, then Edge, then Value across the CSV.
4. Open the best-price link and confirm the price on the betslip (verification gate).
5. Log the bet with its link and track CLV.

## Open items
- Approve or change every cutoff.
- Build the probability model (NFL first, via nflverse).
- Add props to the odds pull.
- Add a bet ledger and CLV tracking.
- Unpark Stake and settle its unit sizes.
