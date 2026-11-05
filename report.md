# Unemployment in India: Covid-19 impact, trends and policy insights

Data: CMIE-style monthly estimates. Dataset A covers May 2019 to Jun 2020 (28 states, rural and urban rows). Dataset B covers Jan to Oct 2020 (27 states, state level, with macro-region). National figures are labour-force weighted (sum of unemployed divided by sum of labour force), not simple averages of state rates.

## Data cleaning
- Dataset A: 768 raw rows, 28 were fully blank, leaving 740 usable rows. No other missing values or duplicates.
- Dataset B: 267 rows, no missing values. Column names had stray spaces. The file has two "Region" columns; the second is a macro-region (North, South, East, West, Northeast) and was renamed "Zone". The `longitude` and `latitude` columns are swapped in the source and were not used.
- Dates parsed from dd-mm-yyyy. Frequency labels harmonised ("M" and "Monthly").
- Gaps in B: Jammu & Kashmir has no April 2020 row, and Sikkim has no Jan or Feb 2020 row. Chandigarh appears in A only. These slightly affect national totals for those months.

## Key findings

### 1. Covid-19 caused a sharp, short-lived spike
| Period | National unemployment rate | Mean labour participation |
|---|---|---|
| Pre-Covid (Jan to Mar 2020) | 7.9% | 44.2% |
| Lockdown (Apr to May 2020) | 22.8% | 37.5% |
| Recovery (Jun to Oct 2020) | 7.9% | 41.9% |

- Monthly peak was April 2020 at about 24%, versus 8.8% in March.
- Employment in the states covered fell about 30% from March to April 2020 (392.5M to 274.8M; slightly overstated because J&K is missing in April).
- By July 2020 the unemployment rate was back near pre-Covid levels (7.4%), but labour participation stayed about 3 points below its January level (41.4% in October vs 44.6% in January). So the headline rate recovered faster than the share of people actually working or seeking work.

### 2. Impact was very uneven across states
Largest rise in unemployment (lockdown average vs Jan to Mar average): Puducherry (+66 pp), Jharkhand (+43), Tamil Nadu (+38), Bihar (+34), Karnataka (+22). Employment fell by more than half in Puducherry, Jharkhand and Tamil Nadu. Several northern and hill states (Himachal Pradesh, Uttarakhand, Chhattisgarh, J&K) showed little or no rise in April to May, and some of these already had high baseline unemployment. Pre-lockdown averages for Sikkim rest on a single month (March), so its change should be read with care.

By zone, April 2020 rates were highest in the East (32.5%) and South (28.6%), and lowest in the West (16.5%) and Northeast (15.5%). By October 2020 the South (3.1%) had recovered most, while the North (11.5%) was still the highest.

### 3. Rural and urban were hit about equally
In April 2020, urban unemployment reached 25.5% and rural 23.6%. Before Covid, urban rates were consistently higher (about 8 to 10% vs 6 to 8%). Both fell to roughly 11 to 12% in June 2020 (rural 10.6%, urban 12.1%).

### 4. Seasonality: limited evidence
The data does not contain two full years, so true seasonal patterns cannot be estimated. What can be said:
- From May 2019 to Feb 2020 the national rate stayed in a narrow band of 7.0 to 8.1% (std about 0.4 pp), with no clear seasonal swing.
- Only May and June overlap across years: May 2019 was 7.0% vs 23.6% in May 2020, and June 2019 was 7.9% vs 11.0% in June 2020.
- Structural, state-specific differences were much larger than any monthly pattern. Before Covid, Tripura (about 29%), Haryana (about 23%) and Himachal Pradesh (about 19%) had the highest mean rates, while Tamil Nadu, Karnataka and Puducherry were below 3.5%.
- Several states (Haryana, Rajasthan, Tripura, Jammu & Kashmir) stayed at double-digit rates throughout 2020, which points to chronic rather than Covid-driven unemployment.

### 5. Unemployment rate vs participation
Across state-months in 2020 the correlation between the two is weak (-0.07). A low unemployment rate can coexist with low participation (people who stop looking are not counted as unemployed), so both indicators need to be tracked.

## Policy implications
1. **Target support at the hardest-hit, high-informal-employment states** (Jharkhand, Bihar, Tamil Nadu, Puducherry) with fast-acting income support and employment guarantees, since employment dropped more than 50% in some of them.
2. **Watch participation, not just the rate.** Participation was still about 3 points below January 2020 in October, which signals discouraged or displaced workers who need re-skilling and job-matching help.
3. **Do not neglect chronic hotspots.** Haryana, Tripura, Himachal Pradesh and J&K had high unemployment well before Covid, so they need structural job creation, not only crisis relief.
4. **Urban safety nets matter as much as rural ones.** Urban unemployment was higher before and during the lockdown, but rural schemes are far more established.
5. **Improve data coverage.** Gaps for some states and the lack of multi-year monthly history limit seasonal and policy evaluation.

## Caveats
- Survey-based estimates; month-to-month swings in small states (Puducherry, Sikkim, Goa) are noisy.
- Dataset A and B overlap Jan to Jun 2020 and agree closely at the national level (for example 8.67% vs 8.76% in March, 24.2% vs 24.0% in April), so combining them is reasonable.
- Associations here are descriptive and do not isolate Covid from other causes.

## Files
- `unemployment_analysis.py`: full pipeline (cleaning, analysis, charts)
- Charts: `01_national_trend.png`, `02_state_covid_impact.png`, `03_state_heatmap.png`, `04_zone_trend.png`, `05_rural_urban.png`, `06_pre_covid_monthly.png`, `07_lpr_vs_unemp.png`
- Tables: `state_covid_impact.csv`, `national_monthly_*.csv`, `zone_monthly_2020.csv`, `rural_urban_monthly.csv`, cleaned datasets
