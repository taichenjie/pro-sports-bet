# Pro Sports Bet — Design Doc

Exported from the Claude Docs design doc on 20 Oct 2026. The Claude Docs version is the source of truth; re-export after changes.

## Overview

An analysis tool that scores 10–20 metrics per match to estimate the probability of specific bet outcomes, then outputs 0–3 picks per day from Singapore Pools markets.

- **Not an xG model.** xG is one input among many; no single metric drives the output.
- **Metrics → features → probability.** Metrics tagged to League, Match, Team or Player become continuous features; the models turn features into P. No vetoes, no pass/fail signals (see Model structure).
- **Edge over conviction.** A pick needs a high model probability AND a price that pays more than that probability implies.
- **Codify CJ's process.** CJ's signals are encoded as features (see CJ's signals → features), so their weight is tested against results instead of memory.

This doc is the single source of truth: decisions, verified facts and open questions are updated here as the project moves.

## Decision log

40 decisions agreed as of 20 Oct 2026, newest first. Superseded decisions stay listed and are marked.

| # | Date | Decision | Rationale |
| --- | --- | --- | --- |
| D40 | 20 Oct 2026 | Infra v1: ap-southeast-1; Lambda + Fargate; EventBridge Scheduler with per-match pre-kick-off schedules; S3 + Parquet + DuckDB (no RDS); Telegram bot for picks; private repo, public later without odds data or weights; single prod environment plus local dev | Lowest cost and ops load; avoids a NAT gateway; instant alerts for withdrawals |
| D39 | 20 Oct 2026 | Pick log records whether CJ placed each pick, with a note; CJ's own manual picks are logged in the same table, flagged by source | Separates model results from CJ's results; compares CJ vs model over the season |
| D38 | 20 Oct 2026 | Flat 1-unit stakes in v1; Kelly-based staking after v1, once calibration is proven. Kelly fraction set at that point | Kelly amplifies probability errors, so it needs a calibrated model first |
| D37 | 20 Oct 2026 | Evaluation: log loss, Brier score and calibration; chronological testing with no leakage; results per league and market; closing-line value and ROI per market | Judge probabilities, not hit rates; prove edge against the market |
| D36 | 20 Oct 2026 | Lineup strength (L3–L5) weights position groups by learned importance instead of summing player ratings equally | A player's impact depends on position, not just rating |
| D35 | 20 Oct 2026 | Refinements from the ChatGPT review: non-penalty xG in F5; new F7 shot quality; set-piece xG in A5; GK goals prevented in A1; margin-free odds and Pinnacle closing odds as benchmark in A3; player minutes load and extra-time exposure in R2/L7 | Cleaner, more stable versions of existing features; all free |
| D34 | 20 Oct 2026 | Remaining features G1–G4, U1–U3, R1–R4, M1–M3 agreed: upsets measured against the strength rating, rest days capped at 10, fixture load across all competitions, new-manager window of 5 matches | Completes the definitions for CJ's original metrics |
| D33 | 20 Oct 2026 | Claude's 9 additional metrics (A1–A9) accepted as candidate features, built after the core features and kept only if the backtest gives them weight | Covers gaps in the original brief: finishing luck, goal timing, market benchmark |
| D32 | 20 Oct 2026 | Picks published the day before from the expected XI; re-scored on confirmed lineups \~1 hour before kick-off; a pick is withdrawn if its edge falls below the threshold | Fits CJ's schedule while still using confirmed lineups |
| D31 | 20 Oct 2026 | Lineup strength = L1–L7. Player quality from FotMob ratings blended with G/A and defensive actions per 90, compared within position; separate attack and defence strength feeding goals-for and goals-against rates; new signings use Transfermarkt market value until 5 appearances | Sub quality decides the impact of an absence; a missing striker and a missing centre-back affect different goal rates |
| D30 | 20 Oct 2026 | Form = F1–F6 (points, capped margin, Elo-style rating, performance vs expectation, dominance, venue split); recent matches weighted more; league matches only (all-competition form separate); ratings carried over at season start | Continuous form that accounts for opponent strength |
| D29 | 20 Oct 2026 | Training window = several seasons, recent seasons weighted more; feature windows stay short (D10); backtest tests how many seasons work best | One season is too few matches to learn reliable weights; old seasons never describe a current team |
| D28 | 20 Oct 2026 | Core features built first: form, lineup strength, opponent form | CJ's top three inputs |
| D27 | 20 Oct 2026 | Transparent Poisson regression with named interactions and regularisation; gradient boosting as challenger. Backtest decides, even against CJ's expectations | Interpretable first; data, not belief, sets weights |
| D26 | 20 Oct 2026 | Every team metric paired for both sides plus the difference | Form only matters relative to the opponent |
| D25 | 20 Oct 2026 | No binary signals or vetoes: all metrics enter the model as continuous, weighted features; only bet rules are yes/no | CJ: always a combination of metrics, never one signal |
| D24 | 20 Oct 2026 | Team to Score First (FT and HT) is a 3-way market incl. No Goal (verified by CJ); the model prices all three outcomes | No Goal is a real selection, especially at HT |
| D23 | 20 Oct 2026 | First-goal model: v1 derived from score-model rates; v2 timing layer is a challenger, adopted only if it beats v1 in backtest | Start simple; prove CJ's timing signals add accuracy |
| D22 | 20 Oct 2026 | Score model with separate 1H and FT rates (Poisson + Dixon-Coles) covers AH, HT AH, 1X2, HT 1X2, O/U, HT O/U, BTTS | One grid keeps all markets consistent; 1H is its own market |
| D21 | 20 Oct 2026 | v1 is pre-match only; no live betting | Live needs real-time feeds: a separate project |
| D20 | 20 Oct 2026 | 1.50 minimum applies to the whole bet; a double's legs may each be below 1.50 | CJ's rule |
| D19 | 20 Oct 2026 | Singapore Pools offers HT markets for Serie A (verified by CJ) | All 6 primary markets are in play for both leagues |
| D18 | 20 Oct 2026 | Shrinkage on all HT and first-goal team metrics, toward the team's tier average; strength k fitted per metric by backtest. FT metrics only if the backtest shows benefit | HT samples are small; tier baseline avoids penalising genuinely strong teams |
| D17 | 20 Oct 2026 | Vision League (Feb–Jun 2026) results count for H2H and player data; excluded from table tiers and upset % | Regional group format, no relegation: not a normal table |
| D16 | 20 Oct 2026 | J1 winter break: windows count matches, not days; windows spanning the break are flagged, and season-to-date gets extra weight for the first 3 matches after it | Form can reset over a \~2-month break |
| D15 | 20 Oct 2026 | ~~Player importance = 50% minutes share + 50% G/A share~~ **Superseded by D31.** GK flag kept as L6 | Replaced by lineup strength, which measures the sub's quality |
| D14 | 20 Oct 2026 | Derby/rivalry list: 25 fixtures across 5 leagues; the 10 in J1 and Serie A are active | CJ-supplied; other leagues stored for future scope |
| D13 | 20 Oct 2026 | Home and away kept as separate features; the backtest sets their weights. Every pick logs whether it backs the home side | CJ gains conviction on home picks; the log tests whether that holds |
| D12 | 20 Oct 2026 | H2H upset history and derby/rivalry flags are features whose effect depends on other metrics (D25) | CJ uses H2H to spot volatile fixtures; form outweighs H2H |
| D11 | 20 Oct 2026 | Table tiers (20 teams): top 3 / 4–9 / 10–16 / 17–20 | Clearer quality divide than thirds |
| D10 | 20 Oct 2026 | Feature windows: last 5, last 10 and season-to-date for every form-type metric | Short-term form plus a stable baseline |
| D9 | 20 Oct 2026 | Design before build: every design decision is agreed before code | CJ owns bet-selection expertise; the model encodes it |
| D8 | 20 Oct 2026 | Model is a multi-metric analysis tool, not xG-led | Matches how CJ evaluates bets |
| D7 | 20 Oct 2026 | Markets: 6 primary (AH, HT AH, Team to Score First, HT Team to Score First, HT 1X2, HT O/U), 3 secondary (1X2, O/U, BTTS) | HT and first-goal markets are CJ's core edge area |
| D6 | 20 Oct 2026 | 0–3 picks per day, ranked by edge; no forced picks | Forcing volume adds negative-EV bets |
| D5 | 20 Oct 2026 | Infra: AWS + Terraform + GitHub from day one | Production-grade pipeline; doubles as a Platform Engineering portfolio project |
| D4 | 20 Oct 2026 | Free data sources only | Cost control while the edge is unproven |
| D3 | 20 Oct 2026 | Leagues: J1 League and Serie A. EPL excluded | EPL is the most efficient market, so mispricing is rarest there |
| D2 | 20 Oct 2026 | Bet types: singles or doubles (2 legs), minimum odds 1.50 (see D20) | Original brief |
| D1 | 20 Oct 2026 | Odds and selections come from Singapore Pools | Only legal operator in Singapore |

## Scope

Two leagues and nine markets. HT markets dominate the primary list, so half-time data is a first-class requirement, not an add-on.

| League | Season in play | HT markets on Singapore Pools |
| --- | --- | --- |
| J1 League | 2026–27 (Aug 2026 – Jun 2027) | Yes (verified by CJ). Not offered for J2/J3 |
| Serie A | 2026–27 | Yes (verified by CJ) |

| Tier | Market | Data it depends on |
| --- | --- | --- |
| Primary | Asian Handicap (incl. quarter lines) | FT goal margin distribution |
| Primary | HT Asian Handicap | HT goal margin distribution |
| Primary | Team to Score First | First-goal team, minute of first goal |
| Primary | HT Team to Score First | First-goal team and whether it falls in 1H |
| Primary | HT 1X2 | HT result |
| Primary | HT Over/Under | 1H total goals |
| Secondary | 1X2 | FT result |
| Secondary | Over/Under | FT total goals |
| Secondary | BTTS | Each team's scoring / clean-sheet rates |

## Verified facts

Facts the design depends on, with who verified them. Unverified items live in Open questions.

| Fact | Impact on design | Verified by |
| --- | --- | --- |
| Singapore Pools AH includes quarter lines (±0.25, ±0.75 etc.) | Settlement logic must handle half-win / half-loss | CJ, 20 Oct 2026 |
| Singapore Pools offers HT markets for J1 and Serie A, not J2/J3 | All primary markets are in play for both leagues | CJ, 20 Oct 2026 |
| Team to Score First (FT and HT) includes a No Goal option | First-goal model prices three outcomes | CJ, 20 Oct 2026 |
| Singapore Pools 1X2 margin cited around 13% ([SingSaver](https://www.singsaver.com.sg/page/blog/soccer-betting-singapore-guide)) | Edge must clear a high margin; measure per market ourselves | Third-party guide, to re-measure |
| J1 moved to autumn–spring: 2026–27 runs 7 Aug 2026 – 6 Jun 2027 ([Wikipedia](https://en.wikipedia.org/wiki/2026%E2%80%9327_J1_League)) | Season-to-date windows are short now; prior J1 seasons were calendar-year | Claude, 20 Oct 2026 |
| J1 has a winter break, roughly mid-Dec to late Feb ([guide](https://guidetofootball.com/competitions/j1-league/)) | Handled by D16 | Claude, 20 Oct 2026 |
| Feb–Jun 2026 was the one-off J1 100 Year Vision League, regional group format, no relegation ([sortitoutsi](https://sortitoutsi.net/content/76075/fm26-a-new-era-for-japanese-football)) | Handled by D17 | Claude, 20 Oct 2026 |
| FBref lost all Opta advanced data in Jan 2026; basic stats remain ([Sports Reference](https://www.sports-reference.com/blog/category/statgeekery/)) | FBref is a basic-stats source only | Claude, 20 Oct 2026 |
| Understat covers Serie A, not J1; FotMob shows J1 xG | J1 xG comes from FotMob | Claude, 20 Oct 2026 |

## Bet selection rules

These are the only yes/no rules in the system (D25). A pick must pass rules 1–5; survivors are ranked by edge and the top 0–3 are output.

1. **Probability:** the models estimate P(outcome) from features (see Model structure).
2. **Edge:** edge = P × decimal odds − 1. Minimum edge threshold: TBD from backtest.
3. **Conviction floor:** P above a market-specific minimum (TBD), so we avoid long-shot value bets that CJ would not back.
4. **Odds floor:** 1.50 minimum on the whole bet (D20). A double's legs may each be below 1.50, e.g. 1.30 × 1.25 = 1.63.
5. **Doubles:** two legs from different matches, each passing rules 1–3 on its own; the whole bet passes rule 4. Combined edge = P1 × P2 × O1 × O2 − 1.
6. **Cap:** 0–3 picks per day. A day with no qualifying pick outputs nothing.
7. **Timing (D32):** picks are published the day before; \~1 hour before kick-off they are re-scored on confirmed lineups and withdrawn if edge falls below the threshold.

Every pick also lists the top 5 features that pushed its P up or down. This is an explanation, not a filter.

**Note on stacking low odds.** A double of two 1.30 favourites reaches 1.69, but it only adds value if each leg is already underpriced. Otherwise it multiplies Singapore Pools' margin twice. Rule 5 enforces this.

**AH settlement:** quarter lines settle as two half-stakes (e.g. −0.75 = half on −0.5, half on −1.0). Expected value is computed per half, then summed.

## CJ's signals → features

Every signal CJ uses maps to one or more continuous features, so its weight is tested against results. Two signals are not model inputs: they are checked through edge and the pick log.

| CJ signal | Feature(s) | Defined in |
| --- | --- | --- |
| Top 3 vs bottom of table | Table tier gap; strength rating gap (F3) | D11, D30 |
| Winning the past N games, and by how many | Points form (F1); capped margin form (F2) | D30 |
| How good the opponents were | Strength rating (F3); performance vs expectation (F4) | D30 |
| xG, did they dominate | Dominance (F5): shots share, xG difference (Understat for Serie A, FotMob for J1) | D30 |
| Led at HT | HT points form (F1, HT version); % games leading at HT, shrunk | D30, D18 |
| Who scores first | % scoring first, % conceding first, average minute of first goal | D23 (first-goal v2) |
| Scoring in the 1H (e.g. Sanfrecce) | % games with a 1H goal; 1H goals for and against | D18 |
| Attacking, open style → Overs | Goals for and against per game (FT and 1H); % games over the line; BTTS rate | D22 |
| Overpowers weaker teams | Interaction: strength gap × form | D27 |
| Main G/A player playing; injuries; suspensions | Lineup strength L1–L7, incl. attack strength (L4) | D31 |
| Home side | Home flag; venue form (F6) | D13, D30 |
| Fixture load, fatigue | Rest days; matches in last 14 days; difference vs opponent | To define |
| League vs continental form | League form (F1–F6) and all-competition form as separate features | D30 |
| Morale, manager pressure | Losing streak; manager change flag; manager tenure | To define |
| H2H upsets, derbies | H2H features, upset-history flag, derby flag | D12, D14 |
| Big-name team priced generously against | Not a feature: shows up as edge when model P exceeds the market's implied P | Bet rules |
| Favourite teams over the season | Not a feature: the pick log reports hit rate by team | Pick log |

**Two cautions.** Favourite teams are a strength only if the hit rate holds on logged picks. The Barcelona, Dortmund and Man Utd examples are outside our two leagues; the patterns transfer, the teams do not.

## Metrics catalogue v1

The same metrics grouped by the question each market asks. A metric can serve several questions.

| Market question | Markets | Metric families |
| --- | --- | --- |
| Who is stronger overall? | AH, 1X2 | Form F1–F6, table tier gap, lineup strength, home flag |
| Who starts faster? | HT AH, HT 1X2, Team to Score First, HT Team to Score First | HT form, % leading at HT, 1H goals for/against, % scoring first, average minute of first goal, % games with a 1H goal |
| How open will it be? | O/U, HT O/U, BTTS | Goals per game (FT and 1H), % over line, clean-sheet rate, failed-to-score rate, BTTS rate, attack and defence strength (L4, L5) |
| What changes this match? | All | Lineup strength and certainty, rest days, fixture load vs opponent, continental fixtures, manager change, match stakes |
| What is the league baseline? | All | League home win %, draw rate, 1H share of goals, upset rate |

**Sample-size warning.** 1H events are rarer than FT events, so HT team metrics over 10 games are noisy. Expect longer windows plus shrinkage for HT metrics.

### CJ's original metrics (all retained)

All 16 metrics from the original brief stay in; the backtest sets each one's weight. Sources are in the Source map.

| Metric | Level | Now defined as | Status |
| --- | --- | --- | --- |
| % of upsets | League | % of matches where the lower-tier team wins or draws (FT and HT); blended with prior season until \~matchday 8; Vision League excluded (D17) | Draft |
| H2H | Match | Last 5 meetings within 3 seasons (results, goals, HT result, first scorer) plus upset-history and derby flags | Draft (D12) |
| Sentiment analysis | Match | Deferred to v2; proxies until then: losing streak, manager change | Deferred |
| Injuries | Team | Lineup strength L1–L7 | Agreed (D31) |
| Form last N | Team | Points form F1, margin form F2, venue form F6 | Agreed (D30) |
| Form vs opponent strength | Team | Strength rating F3, performance vs expectation F4 | Agreed (D30) |
| Goals scored last N | Team | Goals for per game, FT and 1H, home/away split | Draft |
| xG last N | Team | Part of dominance F5 | Agreed (D30) |
| Goals conceded last N | Team | Goals against per game, FT and 1H, home/away split | Draft |
| xGA last N | Team | Part of dominance F5 | Agreed (D30) |
| Rotation chance | Team | Feeds lineup certainty L7: continental or cup match within 3–4 days, starters' minutes load, dead-rubber flag | Draft |
| Player form | Player | Feeds player quality L2 | Agreed (D31) |
| Rating last N | Player | FotMob rating, last 10 appearances, within L2 | Agreed (D31) |
| Attacking influence (G/A) | Player | G/A per 90, within L2 and attack strength L4 | Agreed (D31) |
| Defensive influence | Player | Tackles + interceptions + clearances per 90, within L2 and defence strength L5. “Big chances prevented” not available free | Agreed (D31) |
| Win rate with / without | Player | Team PPG with vs without the player; min 5 games each side, shrunk. May overlap with lineup strength | Draft; backtest decides |

**How player metrics reach the model.** Player metrics roll up into team features through lineup strength (D31). The model sees team- and match-level features only.

### Additional metrics (agreed as candidates, D33)

Nine metrics not in the original brief, ranked by expected value. All are free to source. They enter as candidates: built after the core features (D28), kept only if the backtest gives them weight.

| # | Metric | Definition | Markets it helps most | Source | Expected value |
| --- | --- | --- | --- | --- | --- |
| A1 | Finishing and keeping luck | Goals minus non-penalty xG (attack); goalkeeper goals prevented (D35); last 10. Large gaps tend to shrink back | All, esp. AH, O/U | Understat / FotMob | High |
| A2 | Goal timing profile | Share of a team's goals scored and conceded in 0–15, 16–30, 31–45 and 2nd half, season-to-date, shrunk (D18) | HT markets, first-goal | Understat, FBref goal logs | High |
| A3 | Market benchmark and line movement | Singapore Pools implied probability with margin removed; change between the day-before and pre-kick-off scrapes (D32); Pinnacle closing odds as a sharper benchmark for Serie A (D35) | All | Our own scrape | High as a benchmark; tested as a feature |
| A4 | Game-state behaviour | HT lead conversion rate; points won from losing positions; points dropped from winning positions | AH, 1X2, HT/FT consistency | Results with goal minutes | Medium |
| A5 | Set-piece threat and weakness | Set-piece xG for and against per game (D35), set-piece goal share where xG is unavailable; corners for/against per game | O/U, BTTS, first-goal | Understat (Serie A), FotMob (J1) | Medium |
| A6 | Squad value ratio | Squad market value vs opponent; promoted-team flag | All, esp. early season | Transfermarkt | Medium early season, low later |
| A7 | Match stakes | Points gap to title, continental, relegation places vs games left; dead-rubber flag | AH, 1X2 | Table | Medium in the last third of the season |
| A8 | Kick-off weather | Temperature and humidity at kick-off | O/U, HT O/U (J1 summer heat; northern J1 winter games) | Free weather API | Medium for J1, low for Serie A |
| A9 | Travel distance | Away team's travel distance; long trip after a midweek away game | AH, 1X2 (J1) | Stadium coordinates | Low to medium |

**On A3:** the market price already contains a lot of information, so feeding it in can make the model copy the market and find no edge. It is used first as a benchmark (is our P better calibrated than Singapore Pools' implied P?) and tested as a feature separately.

**Considered and left out for now:** referee tendencies (weak, hard to source for J1), kick-off time slot, international-break effects, tactical event metrics such as PPDA, field tilt and xT (no free J1 source; v2), and a separate upset model (the score model already gives upset probabilities, D22).

## Data sources

All free. The biggest gap is historical odds for HT markets, especially J1.

| Source | Serie A | J1 | Provides | Caveat |
| --- | --- | --- | --- | --- |
| Singapore Pools website | ✅ | ✅ | Live selections and odds | Check ToS; scrape a few times a day; never automate betting |
| [football-data.co.uk](https://www.football-data.co.uk/) | ✅ | ⚠️ | Results, HT scores, historical odds incl. closing (Serie A) | J1 believed to be FT + 1X2 odds only; to verify |
| [Understat](https://understat.com/) | ✅ | ❌ | Shot-level data with minutes and xG → HT goals, first goal | No J1 coverage |
| [J.League Data Site](https://data.j-league.or.jp/) | — | ✅ | Official results, goal minutes, lineups since 1992 | Japanese-language site |
| [FBref](https://fbref.com/) | ✅ | ✅ | Basic stats, match reports | Advanced data removed Jan 2026 |
| [StatsBomb free J1 2024](https://www.hudl.com/blog/j1-league-free-data-statsbomb) | — | ✅ | Full event data, one season | Good for building features, too small to backtest |
| FotMob / Sofascore | ✅ | ✅ | Per-half stats, ratings, lineups, injuries | Unofficial endpoints; ToS grey area |
| Transfermarkt | ✅ | ✅ | Injuries, suspensions, squad values | Scrape gently |
| OddsPortal | ✅ | ✅ | Historical odds incl. some 1H markets | ToS; coverage of HT markets to check |

**Plan for the odds gap:** start scraping Singapore Pools early to build our own odds history; until enough history exists, evaluate the model on probability accuracy (calibration, Brier score) rather than ROI.

### Source map (feasibility check, 20 Oct 2026)

Every data need has at least one candidate source; the J1 xG gap is closed by FotMob. Two items still need a test scrape, and J1 historical odds remain unconfirmed.

| Data need | Serie A | J1 | Status |
| --- | --- | --- | --- |
| Results, HT scores | football-data.co.uk | FBref match reports, J.League Data Site | Serie A confirmed; J1 to test-scrape |
| Goal minutes (first goal, 1H goals) | Understat shot data | FBref goal logs list the minute of each J1 goal ([example](https://aws.fbref.com/en/players/1f0205cc/goallogs/dom_lg)) | Confirmed |
| xG / xGA | Understat ([top European leagues](https://understat.com/)) | FotMob shows team and player xG, xGOT and xA for the J. League ([FC Tokyo stats](https://www.fotmob.com/nb/teams/4399/stats)) | Confirmed; FotMob is unofficial, so endpoint risk |
| Per-half shots, possession | FotMob | FotMob | To test-scrape on one match page |
| Player shots, G/A rankings | FBref basic, FotMob | Official J.League stats pages ([shots ranking](https://www.jleague.jp/stats/j1/player/2024/all/shoot/?mode=pc)) | Confirmed |
| Player ratings | FotMob | FotMob (J. League player ratings shown) | Confirmed |
| Injuries, suspensions | Transfermarkt, FotMob | Transfermarkt, FotMob | Not yet checked |
| Historical odds (FT) | football-data.co.uk incl. closing | football-data.co.uk Japan page | J1 unconfirmed: site rate-limited the check |
| Historical odds (HT markets) | OddsPortal | OddsPortal | Not yet checked; fallback is our own Singapore Pools scrape |
| Ready-made J1 match and 1H datasets | FootyStats | [FootyStats](https://footystats.org/japan/j1-league/datasets) offers J1 CSVs and 1st-half tables | Likely paid; excluded under D4 unless a free tier covers it |

**Net change:** J1 xG moves from “gap” to “available via FotMob”. The real remaining gap is historical HT odds for J1.

## Probability models

Two models turn metrics into probabilities: a score model covers 7 markets, and a first-goal model covers the 2 first-goal markets (D22, D23).

| Market | Model | How the probability is read |
| --- | --- | --- |
| AH (incl. quarter lines) | Score, FT rates | Sum of grid cells by goal margin; quarter lines split into two half-stakes |
| HT AH | Score, 1H rates | Same, on the 1H grid |
| 1X2 | Score, FT rates | Home win / draw / away win cells |
| HT 1X2 | Score, 1H rates | Same, on the 1H grid |
| O/U | Score, FT rates | Cells above / below the line |
| HT O/U | Score, 1H rates | Same, on the 1H grid |
| BTTS | Score, FT rates | Cells where both teams score ≥ 1 |
| Team to Score First | First-goal | Home first / away first / no goal |
| HT Team to Score First | First-goal | Same, within the 1st half |

**Score model.** Features produce four expected-goal rates per match: home and away, for the 1st half and for full time. Each rate becomes a goal distribution (Poisson, with a Dixon-Coles correction for low scores); the two teams' distributions form a scoreline grid. Weights linking features to rates are learned in the backtest.

**First-goal model.** v1 is derived from the score model:

```latex
P(\text{home first}) = \frac{\lambda_H}{\lambda_H + \lambda_A} \left(1 - e^{-(\lambda_H + \lambda_A)}\right), \qquad P(\text{no goal}) = e^{-(\lambda_H + \lambda_A)}
```

v2 adds a timing layer from CJ's first-goal signals (% scoring first, average minute of first goal, % games with a 1H goal). v2 replaces v1 only if it predicts first goals better in the backtest.

**Worked example** (illustrative rates: home 1.6, away 0.9 FT; 1H = 40% of FT). FT: 1X2 53.8% / 25.0% / 21.2%, Over 2.5 45.6%. 1H: HT 1X2 36.5% / 45.8% / 17.7%, HT Over 0.5 63.2%. HT Team to Score First: home 40.5%, away 22.8%, no goal 36.8%.

**Known limits:** goals are treated as independent within a half (game-state effects are only partly captured by the 1H/FT split); the 1H share of goals is set per team with tier shrinkage (D18).

## Model structure

No binary signals or vetoes: metrics become continuous features, the models turn features into P, and the only yes/no decisions are the bet rules (D25).

| Layer | What it holds |
| --- | --- |
| 1. Metrics | Raw numbers per league, match, team and player |
| 2. Features | Metrics after shrinkage, paired for both teams with differences, composites, named interactions |
| 3. Models | Score model and first-goal model; feature weights are learned here |
| 4. Bet rules | Edge threshold, 1.50 odds floor, 0–3 picks per day |
| 5. Explanation | Top 5 features that pushed each pick's P up or down, with values |

**Feature design**

- **Paired:** every team metric is computed for both sides, plus the difference (D26). “Good form” only means something against the opponent's form.
- **Lineup strength (composite):** expected XI quality vs full-strength XI, using the replacements' own quality (D31). A good sub means a small drop.
- **Named interactions:** combinations CJ reasons with, built as their own features, e.g. H2H upset flag × opponent form; lineup strength drop × opponent strength.
- **Natural yes/no inputs** (home, derby flag) enter as 0/1 features, never as gates.

**Core features first (D28):** form, lineup strength and opponent form are built and validated before anything else.

**Model approach (D27):** transparent Poisson regression with the named interactions and regularisation (penalties that shrink weak weights toward zero), plus gradient boosting as a challenger. The backtest decides which wins and what the weights are, including weights that contradict CJ's expectations.

**Two different data windows**

| Window | Meaning | Length | Why |
| --- | --- | --- | --- |
| Feature window | How far back a team's metrics look | Short: last 5, last 10, season-to-date (D10) | Teams change; old performance says little about the current side |
| Training window | Which past matches teach the model the weights | Several seasons, recent seasons weighted more | Learns how much form, lineup and opponent form matter in general; one season (\~380 matches) is too few to learn reliable weights |

Old seasons never describe a current team: they only show the model how much recent form has mattered historically. Agreed as D29.

## Core feature definitions

### Form (agreed, D30)

Form is a family of continuous features, computed for both teams and as a difference (D26), over last 5, last 10 and season-to-date (D10).

| # | Feature | Definition | FT / HT |
| --- | --- | --- | --- |
| F1 | Points form | Points per game | FT; HT version = points as if the match ended at HT |
| F2 | Margin form | Goal difference per game, each match capped at ±3 | FT and 1H |
| F3 | Strength rating | Elo-style rating updated after every match; a win over a strong side gains more than a win over a weak one | FT |
| F4 | Performance vs expectation | Points won minus points expected from both teams' ratings and venue. Positive = overperforming | FT and HT |
| F5 | Dominance | Shots share; non-penalty xG difference per game (D35) | FT and 1H |
| F6 | Venue form | F1–F2 split into home-only and away-only | FT and HT |
| F7 | Shot quality | xG per shot; % of shots inside the box, for and against (D35) | FT and 1H |

F3 and F4 answer CJ's “how good was the opponent” check directly. Table tier stays as a separate, simpler feature.

**Choices (agreed)**

- [x] Cap margin at ±3 per match
- [x] Opponent strength from Elo-style rating; table tier kept as a separate feature
- [x] Recent matches weighted more inside each window (e.g. last game 1.0, five games ago 0.6; decay tuned by backtest)
- [x] League matches only for form; all-competition form as a separate feature
- [x] Season start: last season's rating carried in, shrunk toward the tier average, until \~5 matches are played

**Decisions:** D29 — training window is several seasons, recent seasons weighted more; feature windows stay short (D10); the backtest tests how many seasons work best. D30 — form = F1–F6 with the five choices above.

### Lineup strength (agreed, D31)

Lineup strength measures how much of a team's normal quality is on the pitch, split by where on the pitch it is missing.

| # | Feature | Definition |
| --- | --- | --- |
| L1 | Expected XI | Predicted from the last 3 league lineups minus injured and suspended players; replaced by the confirmed XI \~1 hour before kick-off |
| L2 | Player quality | Each player's average rating over his last 10 appearances, compared only with players in the same position; low-minute players shrunk toward the team average |
| L3 | Overall lineup strength | Expected XI quality ÷ full-strength XI quality (most-used XI), with position groups weighted by learned importance (D36). 1.00 = full strength |
| L4 | Attack strength | L3 for forwards and attacking midfielders only. Feeds the team's goals-for rate |
| L5 | Defence strength | L3 for defenders and goalkeeper only. Feeds the team's goals-against rate |
| L6 | First-choice GK out | 0/1 feature (D15) |
| L7 | Lineup certainty | How confident the expected XI is: rotation risk, late fitness doubts, starters' minutes over the last 7 and 14 days (D35). 1.00 once the XI is confirmed |

The sub's quality is built in: if a striker is out and his replacement rates almost as well, L4 barely moves.

**Choices (agreed)**

- [x] Player quality from FotMob ratings, blended with G/A and defensive actions per 90, compared within position
- [x] Separate attack (L4) and defence (L5) strength, feeding the goals-for and goals-against rates
- [x] New signings: Transfermarkt market value as a stand-in until 5 appearances
- [x] Timing: picks published the day before, re-scored on confirmed lineups \~1 hour before kick-off, withdrawn if edge drops below threshold (D32)

### Opponent form (agreed, D26 + D30)

Opponent form is F1–F6 and L1–L7 computed for the opponent, plus the difference between the two teams. No separate definition is needed.

### Remaining features (agreed, D34)

Four metric groups from the original brief still need definitions. All are paired for both teams (D26), use the D10 windows and D30 recency weighting unless stated.

**Goals for and against**

| # | Feature | Definition |
| --- | --- | --- |
| G1 | Goals for | Per game, FT and 1H, home/away split, shrunk toward tier average |
| G2 | Goals against | Same, conceded |
| G3 | Clean-sheet and failed-to-score rates | % of games, FT and 1H |
| G4 | Over-line rates | % of games over 0.5 / 1.5 / 2.5 / 3.5 (FT) and over 0.5 / 1.5 (1H) |

G1–G2 overlap with xG (F5); the backtest decides how the weight splits.

**% of upsets (league level)**

| # | Feature | Definition |
| --- | --- | --- |
| U1 | League upset rate | % of matches where the weaker side (lower Elo-style rating, F3) avoids defeat; season-to-date, blended with prior season until \~matchday 8 |
| U2 | Upset rate by gap | U1 split by rating gap band (small / medium / large) |
| U3 | HT upset rate | % where the weaker side is level or leading at HT |

**Fixture load**

| # | Feature | Definition |
| --- | --- | --- |
| R1 | Rest days | Days since last match, all competitions, capped at 10 |
| R2 | Recent load | Matches played in the last 14 days, all competitions, plus extra-time matches (D35) |
| R3 | Load gap | R1 and R2 minus the opponent's |
| R4 | Next-match pull | Continental or cup match within the next 4 days (also feeds lineup certainty L7) |

**Morale and manager**

| # | Feature | Definition |
| --- | --- | --- |
| M1 | Current run | League games since last win (negative) or since last loss (positive) |
| M2 | New manager | Matches since a manager change, if within the last 5 |
| M3 | Manager tenure | League matches under the current manager |

Under- or over-performance itself is already measured by F4 (performance vs expectation).

**Open choices**

- [x] Upsets measured against the Elo-style rating (F3), not table position
- [x] Rest days capped at 10
- [x] Fixture load counts all competitions; form stays league-only (D30)
- [x] New-manager effect window of 5 matches

## Evaluation (D37)

The model is judged on probability quality first, then on betting results against the market.

| Check | Measure |
| --- | --- |
| Probability accuracy | Log loss and Brier score, per league and per market |
| Calibration | Events given \~60% happen \~60% of the time |
| Testing method | Chronological walk-forward; no future data in any feature |
| Betting value | Closing-line value vs Singapore Pools and Pinnacle; ROI per market |

## Pick log (agreed, D38–D39)

Three tables. Every priced selection is logged, not only the picks, so calibration (D37) is measured without selection bias.

| Table | One row per | Purpose |
| --- | --- | --- |
| odds\_snapshots | Selection per scrape | Raw Singapore Pools odds over time; source of line movement (A3) and closing odds |
| predictions | Selection per scoring run (publish, pre-kick-off) | Model P vs market for every selection; feeds calibration and log loss |
| picks | Bet leg that passed the bet rules | What was published, what happened, what it earned |

**picks fields**

| Group | Fields |
| --- | --- |
| Identity | pick\_id, match\_id, league, kick-off time, home team, away team, model\_version |
| Bet | bet\_type (single/double), double\_id and leg number, market, selection (e.g. home, over, no goal), line (e.g. −0.75, 2.5) |
| Probability | p\_model; p\_market (Singapore Pools, margin removed); p\_pinnacle (Serie A) |
| Odds | odds at publish; odds at pre-kick-off re-score; closing odds (last scrape before kick-off) |
| Lifecycle (D32) | status (published / confirmed / withdrawn), withdraw reason, edge at publish, edge at re-score, lineup certainty at each run |
| Context | backs home side (D13), derby flag, top 5 features with values and contributions |
| Outcome | HT score, FT score, first-goal team, settlement (win / half win / push / half loss / loss / void), profit in units, closing-line value |
| CJ | source (model / CJ manual), placed by CJ (yes/no), CJ note, stake in units |

**Open choices**

- [x] Staking: flat 1 unit per pick for v1; Kelly-based staking after v1 (D38)
- [x] Track whether CJ placed each pick, plus a note (D39)
- [x] CJ's own manual picks logged in the same table, flagged by source (D39)

## Architecture (draft)

Serverless and scheduled: nothing runs between jobs. D32 needs two scoring runs per match day: a day-before run that publishes picks, and a run \~1 hour before each kick-off that re-scores on confirmed lineups. Service choices are placeholders until build.

```text
Sources -> Scrapers (Lambda on schedule) -> Raw data (S3) -> Metrics engine
        -> Metrics store (S3 Parquet + DuckDB) -> Model -> Selection rules -> Daily picks + pick log (Telegram)
Terraform + GitHub Actions provision and deploy all of it.
```

Raw data is kept separate from metrics, so a metric definition can change and be recomputed over history without re-scraping.

**Components (draft for CJ review)**

| Component | Proposed choice |
| --- | --- |
| Region | ap-southeast-1 (Singapore) |
| Scrapers and scoring | Lambda, packaged as container images in ECR (Python 3.12) |
| Training and backtests | ECS Fargate task, run on demand |
| Scheduling | EventBridge Scheduler: one daily publish run; that run creates a one-off schedule at kick-off − 60 min for each match (D32) |
| Storage | S3: raw scrapes, then metrics, features, predictions and picks as Parquet, queried with DuckDB (Athena for ad hoc) |
| Secrets | SSM Parameter Store |
| Monitoring | CloudWatch logs; alarm on any failed scrape or run, sent to CJ |
| Pick delivery | Telegram bot (D40); bot token in SSM |
| Terraform state | S3 backend with native lock file |
| CI/CD | GitHub Actions; AWS access via OIDC role, no stored keys; terraform plan on pull request, apply on merge to main |

**Repo layout**

```text
pro-sports-bet/
  infra/
    bootstrap/        state bucket, GitHub OIDC role
    modules/          storage, ecr, scraper, scoring, scheduler, monitoring
    envs/prod/
  src/
    scrapers/         sgpools, understat, fotmob, fbref, jleague, transfermarkt, football_data
    metrics/          raw metrics per level
    features/         shrinkage, pairing, composites (F, L, G, U, R, M, A)
    models/           score_model, first_goal
    rules/            bet rules, AH settlement
    picklog/
  backtest/
  tests/
  .github/workflows/  ci, terraform, deploy
```

**Open choices**

- [x] Storage: S3 + Parquet + DuckDB for v1, no RDS (D40)
- [x] Pick delivery: Telegram bot (D40)
- [x] Repo private now; public later as a portfolio piece without odds data or model weights (D40)
- [x] One environment (prod) plus local development (D40)

## Feature lifecycle

Metric definitions are frozen for v1. Their parameters (decay rates, shrinkage strength k, weights) are tuned in the backtest, because they can only be set from data. New metrics can be added at any time:

1. CJ or Claude proposes it; it is defined here with a source.
2. It is computed over history from the raw data in S3 (no re-scraping).
3. The backtest compares the model with and without it.
4. It stays only if it improves log loss out of sample (D37); either way the result is recorded here.

## Build plan

1. **Bootstrap:** GitHub repo, Terraform state bucket, OIDC role, CI pipeline.
2. **Data:** scrapers for each source; resolves the data checks in Open questions. Singapore Pools odds scraping starts here, so odds history builds up from day one.
3. **Metrics and features:** core features first (form, lineup strength, opponent form, D28), then the rest.
4. **Models and backtest:** score model and first-goal model, walk-forward backtest, evaluation per D37.
5. **Paper trading:** scheduled runs and Telegram picks, no real money, for at least 6–8 weeks.
6. **Live:** real stakes, flat 1 unit (D38), only if paper trading shows positive closing-line value.

## Derby / rivalry list

Fixtures that set the derby flag (D12, D14). The flag fires only when the fixture is scheduled in a league we bet on, so clubs outside the top flight this season cost nothing. Order within a pair does not matter.

| League | Fixture | Status |
| --- | --- | --- |
| J1 League | Urawa Reds vs RB Omiya Ardija | Active |
| J1 League | FC Tokyo vs Kawasaki Frontale | Active |
| J1 League | Kashima Antlers vs Yokohama F. Marinos | Active |
| J1 League | Gamba Osaka vs Cerezo Osaka | Active |
| J1 League | Kashiwa Reysol vs JEF United Chiba | Active |
| Serie A | Inter vs AC Milan | Active |
| Serie A | Roma vs Lazio | Active |
| Serie A | Juventus vs Inter | Active |
| Serie A | Juventus vs Torino | Active |
| Serie A | Napoli vs Roma | Active |
| EPL | Liverpool vs Manchester United | Stored |
| EPL | Arsenal vs Tottenham Hotspur | Stored |
| EPL | Manchester United vs Manchester City | Stored |
| EPL | Chelsea vs Arsenal | Stored |
| EPL | Newcastle United vs Sunderland | Stored |
| La Liga | Barcelona vs Real Madrid | Stored |
| La Liga | Real Madrid vs Atlético Madrid | Stored |
| La Liga | Sevilla vs Real Betis | Stored |
| La Liga | Barcelona vs Espanyol | Stored |
| La Liga | Athletic Club vs Real Sociedad | Stored |
| Bundesliga | Borussia Dortmund vs Bayern Munich | Stored |
| Bundesliga | Borussia Dortmund vs Schalke 04 | Stored |
| Bundesliga | Werder Bremen vs Hamburger SV | Stored |
| Bundesliga | Union Berlin vs Hertha Berlin | Stored |
| Bundesliga | Bayern Munich vs 1860 Munich | Stored |

## Open questions and risks

**Open questions**

- [ ] Test-scrape J1 results, HT scores and per-half stats (J.League Data Site, FBref, FotMob)
- [ ] Confirm football-data.co.uk J1 coverage (FT odds, closing odds); first check was rate-limited
- [ ] Check OddsPortal coverage of historical HT-market odds for J1 and Serie A
- [ ] Check injury and suspension coverage (Transfermarkt, FotMob) for J1
- [ ] Read Singapore Pools website terms on automated access
- [ ] Confirm confirmed-lineup data appears \~1 hour before kick-off on a scrapeable source for both leagues (D32)
- [ ] Measure Singapore Pools margin per market from scraped odds
- [ ] Define remaining features: fixture load, morale/manager, % upsets, goals for/against
- [x] Pick log schema. Done (D38–D39)

**Risks**

| Risk | Mitigation |
| --- | --- |
| Singapore Pools margin wipes out edge | Measure margin per market; bet only above edge threshold |
| No historical HT odds for J1 → can't backtest ROI | Scrape our own odds from now; judge calibration first |
| Small HT samples → noisy metrics | Longer windows, shrinkage to tier average (D18) |
| Too many features for the data → model memorises noise | Composite features, regularisation, walk-forward testing (D27, D29) |
| J1 season-format change breaks form history | Winter break and Vision League handled explicitly (D16, D17) |
| Unofficial endpoints (FotMob) change or block | Source abstraction layer; fallbacks per metric |
| Confirmed lineups arrive late or not at all | Day-before pick stands only if its edge held on the expected XI; otherwise withdrawn |
| Model encodes CJ's biases | Backtest sets weights (D27); pick log reviews hit rate by feature, market and team |

## Changelog

| Date | Change |
| --- | --- |
| 20 Oct 2026 | D40: infra agreed. Feature lifecycle and build plan added |
| 20 Oct 2026 | D38–D39: pick log agreed (odds\_snapshots, predictions, picks); flat staking for v1, Kelly after; CJ placement and manual picks tracked |
| 20 Oct 2026 | D34–D37: remaining features agreed; ChatGPT review refinements folded into F5, F7, A1, A3, A5, R2, L3, L7; Evaluation section added |
| 20 Oct 2026 | D33: 9 additional metrics (A1–A9) accepted as candidates. Remaining features (goals, upsets, fixture load, morale) drafted |
| 20 Oct 2026 | Cleanup: removed stale signal/veto wording, rewrote signals and original-metrics tables to point at agreed features, cleared resolved open questions, marked D15 superseded |
| 20 Oct 2026 | D31–D32: lineup strength agreed; picks published day before and re-scored on confirmed lineups |
| 20 Oct 2026 | D29–D30: training window; form definition F1–F6 |
| 20 Oct 2026 | D25–D28: signal-agreement draft replaced by Model structure (continuous features, no vetoes, paired metrics, lineup strength, core features first). D12 revised |
| 20 Oct 2026 | D22–D24: score model and first-goal model; Probability models section added |
| 20 Oct 2026 | D19–D21: Serie A HT markets confirmed, 1.50 floor on whole bet, pre-match only. Source map added; J1 xG found on FotMob |
| 20 Oct 2026 | D18: shrinkage of HT and first-goal metrics toward tier average |
| 20 Oct 2026 | D15–D17: player importance weight, J1 winter break handling, Vision League handling |
| 20 Oct 2026 | D13–D14: home/away weighting from backtest with home-pick logging; derby/rivalry list added (25 fixtures, 10 active) |
| 20 Oct 2026 | D10–D12: windows, 4 table tiers, H2H as caution signal (later revised by D25) |
| 20 Oct 2026 | Added CJ's 16 original metrics with draft definitions, HT variants and sources |
| 20 Oct 2026 | Doc created. Decisions D1–D9 logged; CJ's signals mapped to metrics; data sources and J1 calendar change recorded |
