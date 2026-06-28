# Retailers vs Amazon: Gross Margin Resilience Analysis (CY2014-CY2024)
 
## Business Question
 
Which US retailers protected their gross margin across a decade of Amazon growth and discount retail expansion, and what does the data say about who is structurally resilient versus who just looked profitable on average?
 
## Key Findings
 
- **Discount retailers won on stability.** Walmart and Dollar General both maintained a coefficient of variation of 0.02 across the full decade, the lowest in the set. Despite operating at the thinnest average margins, they proved the most structurally resilient.
- **Margin level is not the same as margin resilience.** Macy's averaged 38.72% gross margin, the highest in the set, but also posted the highest volatility (CV 0.08) and a nearly 12 percentage point swing from peak to trough. Its margin collapsed in 2020 and only recovered when stores reopened.
- **2020 was a stress test.** The Covid disruption separated resilient from fragile business models. Department stores saw sharp margin declines, while discount retailers were barely affected.
- **Target's post-Covid inventory problem shows up clearly in the data.** A notable margin drop in 2022 reflects the period when Target was caught with excess inventory and had to discount aggressively to clear it.
- **Dollar General doubled revenue while holding margin.** Growing from $19bn to $41bn in a decade while maintaining margin stability is a significant operational achievement that the data captures clearly.
## Resilience Ratings
 
| Company | Category | Avg Gross Margin % | Volatility (CV) | 10yr Change (pp) | Rating |
|---|---|---|---|---|---|
| Walmart | Discount | 24.92 | 0.02 | +0.02 | High |
| Dollar General | Discount | 30.80 | 0.02 | -1.10 | High |
| Target | Mass Market | 28.62 | 0.05 | -1.18 | Medium |
| Nordstrom | Department Store | 33.70 | 0.05 | -0.45 | Medium |
| Macy's | Department Store | 38.72 | 0.08 | +0.28 | Low |
 
Resilience is defined by coefficient of variation (CV) of gross margin across all available years. CV measures volatility relative to the average, allowing fair comparison across companies operating at different margin levels.
 
## Stack
 
```
Data Source    SEC EDGAR API (XBRL financial data)
Ingestion      Python (requests, pandas)
Storage        DuckDB
Transformation dbt (3 mart models, 8+ passing tests)
Dashboard      Power BI Desktop
```
 
## Project Structure
 
```
retail_margins/
    seeds/
        retail_financials.csv        # Raw ingested data, 55 rows
        schema.yml
    models/
        staging/
            stg_retail_financials.sql
            _stg_retail_financials.yml
        marts/
            mart_margin_trends.sql       # Annual revenue and margin per retailer
            mart_yoy_changes.sql         # Year-on-year margin and revenue changes
            mart_resilience_scores.sql   # Aggregate resilience metrics per retailer
            _marts.yml
    exports/
        mart_margin_trends.csv
        mart_yoy_changes.csv
        mart_resilience_scores.csv
    export_to_csv.py
    RetailMarginsAnalysis.pbix
```
 
## Data Notes
 
Data was sourced from SEC EDGAR XBRL filings via the public API. All figures are in USD. Revenue is presented in billions for readability.
 
A small number of structured GrossProfit fields were unavailable directly from EDGAR and were handled as follows:
 
- Nordstrom CY2020-CY2024: backfilled using manually confirmed GAAP data
- Macy's CY2021: backfilled using manually confirmed GAAP data
All other figures are sourced directly from EDGAR XBRL tags with coalescing across multiple valid tag variants to account for inconsistencies in company reporting conventions.
 
## How to Run
 
**Requirements:** Python 3.9+, dbt-duckdb
 
```bash
# Clone the repo
git clone https://github.com/mo-mo35/Retailers-Versus-Amazon-Commercial-Project.git
cd Retailers-Versus-Amazon-Commercial-Project/retail_margins
 
# Install dbt
pip install dbt-duckdb
 
# Load seed data and run models
dbt seed
dbt run
dbt test
 
# Export to CSV for Power BI
python export_to_csv.py
```
 
Open `RetailMarginsAnalysis.pbix` in Power BI Desktop and refresh the data sources pointing to the `exports/` folder.
 
## Dashboard Pages
 
**Page 1: Revenue Under Pressure**
Revenue in USD billions per retailer from CY2014 to CY2024. Walmart and Dollar General grew throughout the decade. Macy's peaked in 2015 and has not recovered. Nordstrom was essentially flat in real terms.
 
**Page 2: Margin Resilience**
Gross margin percentage trends and year-on-year margin change per retailer. The 2020 Covid stress test is clearly visible. Discount retailers show near-zero year-on-year volatility throughout. Department stores show sharp swings.
 
**Page 3: The Verdict**
Aggregate resilience metrics with ratings. Answers the business question directly.
 
