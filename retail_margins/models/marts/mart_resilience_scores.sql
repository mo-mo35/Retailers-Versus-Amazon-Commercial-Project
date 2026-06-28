with base as (
    select * from {{ ref('stg_retail_financials') }}
),

stats as (
    select
        company,
        retailer_category,
        count(*) as years_of_data,
        round(avg(gross_margin_pct), 2) as avg_gross_margin_pct,
        round(min(gross_margin_pct), 2) as min_gross_margin_pct,
        round(max(gross_margin_pct), 2) as max_gross_margin_pct,
        round(stddev(gross_margin_pct), 2) as margin_std_dev,
        round(
            stddev(gross_margin_pct) / nullif(avg(gross_margin_pct), 0),
            4
        ) as margin_cv,
        max(case when fiscal_year = 2014 then gross_margin_pct end) as margin_cy2014,
        max(case when fiscal_year = 2024 then gross_margin_pct end) as margin_cy2024
    from base
    group by company, retailer_category
),

final as (
    select
        *,
        round(max_gross_margin_pct - min_gross_margin_pct, 2) as margin_range_pp,
        round(margin_cy2024 - margin_cy2014, 2) as margin_change_10yr_pp,
        case
            when margin_cv <= 0.025 then 'High'
            when margin_cv <= 0.07  then 'Medium'
            else 'Low'
        end as resilience_rating
    from stats
)

select * from final
order by avg_gross_margin_pct desc