import requests
import pandas as pd


# Identifiers for companies in SEC EDGAR
retailers_CIK = {
    'Walmart': '0000104169',
    'Target': '0000027419',
    "Macy's": '0000794367',
    'Nordstrom': '0000072333',
    'Dollar General': '0000029534'
}

headers = {'User-Agent': 'Mohamed moeshazly25@gmail.com'}

# Relevant tags from the 5 companies to be used in the analysis
tags = [
    'Revenues',
    'SalesRevenueNet',
    'SalesRevenueGoodsNet',
    'NetSales',
    'RevenueFromContractWithCustomerExcludingAssessedTax',
    'GrossProfit',
    'GrossProfitLoss',
    'CostOfSales',
    'CostOfRevenue',
    'CostOfGoodsAndServicesSold'
]


# Calendar parser to map retail fiscal ending months to year_range definitions
date_to_frame_map = {
    2015: 'CY2014', 2016: 'CY2015', 2017: 'CY2016', 2018: 'CY2017',
    2019: 'CY2018', 2020: 'CY2019', 2021: 'CY2020', 2022: 'CY2021',
    2023: 'CY2022', 2024: 'CY2023', 2025: 'CY2024'
}

all_data = []

for company, cik in retailers_CIK.items():
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    api_call = requests.get(url, headers=headers)
    facts = api_call.json()['facts']['us-gaap']
    
    for tag in tags:
        tag_data = facts.get(tag)
        if tag_data is None:
            continue
        entries = tag_data['units']['USD']
        
        for entry in entries:
            start = entry.get('start')
            end = entry.get('end')
            if not start or not end:
                continue
            if entry.get('form') != '10-K':
                continue    
            # Filter purely based on duration spans to capture full-year data
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
            duration_days = (end_dt - start_dt).days
            if duration_days < 350 or duration_days > 380:
                continue 
                
            # Map the exact end year to your original 'CYXXXX' string layout
            target_frame = date_to_frame_map.get(end_dt.year)
            if target_frame not in date_to_frame_map.values():
                continue

            all_data.append({
                'company': company,
                'tag': tag,
                'year': target_frame, # Retains your 'CYXXXX' formatting layout
                'value': entry.get('val')
            })

df = pd.DataFrame(all_data)

# Remove duplicates before computing pivots
df = df.drop_duplicates(subset=['company', 'tag', 'year', 'value'])

df_pivot = df.pivot_table(
    index=['company', 'year'],
    columns='tag',
    values='value',
    aggfunc='first'
).reset_index()
df_pivot.columns.name = None

# --- Coalesce Revenue (Your original layout logic) ---
rev_cols = [c for c in [
    'Revenues', 'SalesRevenueNet', 'SalesRevenueGoodsNet',
    'NetSales', 'RevenueFromContractWithCustomerExcludingAssessedTax'
] if c in df_pivot.columns]
df_pivot['Revenue'] = df_pivot[rev_cols].bfill(axis=1).iloc[:, 0]

# --- Coalesce Gross Profit ---
gp_cols = [c for c in ['GrossProfit', 'GrossProfitLoss'] if c in df_pivot.columns]
df_pivot['GrossProfit_direct'] = df_pivot[gp_cols].bfill(axis=1).iloc[:, 0] if gp_cols else None

# --- Coalesce COGS ---
cogs_cols = [c for c in ['CostOfSales', 'CostOfRevenue', 'CostOfGoodsAndServicesSold'] if c in df_pivot.columns]
df_pivot['COGS'] = df_pivot[cogs_cols].bfill(axis=1).iloc[:, 0] if cogs_cols else None

# --- Rebuild direct missing components mathematically ---
df_pivot['GrossProfit'] = df_pivot['GrossProfit_direct'].combine_first(df_pivot['Revenue'] - df_pivot['COGS'])

df_final = df_pivot[['company', 'year', 'Revenue', 'GrossProfit', 'COGS']].copy()

# --- Integrated Manual Backfill matching your 'CYXXXX' indexing layout ---
manual_backfill = {
    ('Nordstrom', 'CY2020'): {'revenue': 10715000000, 'gross_profit': 3041000000},
    ('Nordstrom', 'CY2021'): {'revenue': 14789000000, 'gross_profit': 5159000000},
    ('Nordstrom', 'CY2022'): {'revenue': 15530000000, 'gross_profit': 5345000000},
    ('Nordstrom', 'CY2023'): {'revenue': 14693000000, 'gross_profit': 5054000000},
    ('Nordstrom', 'CY2024'): {'revenue': 15016000000, 'gross_profit': 5163000000},
    ("Macy's", 'CY2021'):    {'revenue': 25399000000, 'gross_profit': 10059000000},
}

for (company, year), vals in manual_backfill.items():
    mask = (df_final['company'] == company) & (df_final['year'] == year)
    if mask.any():
        if pd.isna(df_final.loc[mask, 'GrossProfit']).all():
            df_final.loc[mask, 'GrossProfit'] = vals['gross_profit']
        if pd.isna(df_final.loc[mask, 'Revenue']).all():
            df_final.loc[mask, 'Revenue'] = vals['revenue']
    else:
        new_row = pd.DataFrame([{
            'company': company,
            'year': year,
            'Revenue': vals['revenue'],
            'GrossProfit': vals['gross_profit'],
            'COGS': vals['revenue'] - vals['gross_profit']
        }])
        df_final = pd.concat([df_final, new_row], ignore_index=True)

# Final complete self-healing calculation block
df_final['COGS'] = df_final['Revenue'] - df_final['GrossProfit']
df_final['GrossMargin'] = df_final['GrossProfit'] / df_final['Revenue']

df_final = df_final.sort_values(['company', 'year']).reset_index(drop=True)

# --- Original Output Print Commands ---
print(df_final)
print(f"\nShape: {df_final.shape}")
print(f"\nNull counts:\n{df_final.isnull().sum()}")

df_final.to_csv('retail_margins/seeds/retail_financials.csv', index=False)
print(f"\nComplete rows (no nulls): {df_final.dropna().shape[0]} of {df_final.shape[0]}")
