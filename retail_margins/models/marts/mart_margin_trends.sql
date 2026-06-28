with base as (
    select * from {{ ref('stg_retail_financials') }}
)

select
    company,
    retailer_category,
    fiscal_year,
    round(revenue / 1e9, 2) as revenue_billions,
    round(gross_profit / 1e9, 2) as gross_profit_billions,
    round(cogs / 1e9, 2) as cogs_billions,
    gross_margin_pct
from base
order by company, fiscal_year