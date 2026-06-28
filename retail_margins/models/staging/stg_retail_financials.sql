with source as (
    select * from {{ ref('retail_financials') }}
),

cleaned as (
    select
        company,
        cast(replace(year, 'CY', '') as integer)     as fiscal_year,
        cast(Revenue as double)                       as revenue,
        cast(GrossProfit as double)                   as gross_profit,
        cast(COGS as double)                          as cogs,
        round(cast(GrossMargin as double) * 100, 2)   as gross_margin_pct,
        case
            when company in ('Walmart', 'Dollar General') then 'Discount'
            when company in ('Macy''s', 'Nordstrom')      then 'Department Store'
            when company = 'Target'                        then 'Mass Market'
        end as retailer_category
    from source
)

select * from cleaned