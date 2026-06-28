with base as (
    select * from {{ ref('stg_retail_financials') }}
),

with_lag as (
    select
        company,
        retailer_category,
        fiscal_year,
        gross_margin_pct,
        revenue,
        lag(gross_margin_pct) over (
            partition by company order by fiscal_year
        ) as prev_year_margin_pct,
        lag(revenue) over (
            partition by company order by fiscal_year
        ) as prev_year_revenue
    from base
)

select
    company,
    retailer_category,
    fiscal_year,
    gross_margin_pct,
    prev_year_margin_pct,
    round(gross_margin_pct - prev_year_margin_pct, 2) as margin_change_pp,
    round(revenue / 1e9, 2) as revenue_billions,
    round(
        (revenue - prev_year_revenue)
        / nullif(prev_year_revenue, 0) * 100,
        2
    ) as revenue_growth_pct
from with_lag