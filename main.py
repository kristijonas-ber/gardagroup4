import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

def process_group_1_macro():
    """Extracts latest macro data for US, Europe, Japan and standardizes it."""
    us = pd.read_csv("group1_macro/US.csv")
    eu = pd.read_csv("group1_macro/Europe.csv")
    jp = pd.read_csv("group1_macro/Japan.csv")
    
    # Get the latest row of data
    us_latest = us.iloc[-1]
    eu_latest = eu.iloc[-1]
    jp_latest = jp.iloc[-1]
    
    # Helper function to clean strings to floats
    def to_float(val):
        try:
            return float(str(val).replace(',', '').strip())
        except ValueError:
            return np.nan
            
    # Note: We invert Core CPI and Unemployment (multiply by -1) 
    # so that lower inflation/unemployment yields a higher (better) score
    macro_data = {
        'Region': ['US', 'Europe', 'Japan'],
        'GDP_Growth': [to_float(us_latest['GDP YoY % Change']), to_float(eu_latest['GDP Growth']), to_float(jp_latest['GDP YoY % Change'])],
        'Core_CPI_Inv': [-to_float(us_latest['Core CPI']), -to_float(eu_latest['Core HICP']), -to_float(jp_latest['Core CPI'])],
        'Unemp_Inv': [-to_float(us_latest['Unemployment Levels %']), -to_float(eu_latest['Unemployment']), -to_float(jp_latest['Unemployment Levels %'])]
    }
    df_macro = pd.DataFrame(macro_data)
    
    # Cross-sectional Z-score for the 3 sub-metrics
    for col in ['GDP_Growth', 'Core_CPI_Inv', 'Unemp_Inv']:
        df_macro[f'{col}_Z'] = (df_macro[col] - df_macro[col].mean()) / df_macro[col].std(ddof=0)
        
    df_macro['Macro_Score'] = df_macro[['GDP_Growth_Z', 'Core_CPI_Inv_Z', 'Unemp_Inv_Z']].mean(axis=1)
    return df_macro[['Region', 'Macro_Score']]

def process_group_2_policy():
    """Averages Central Bank Sentiment into a Policy Score by Region."""
    df_bank = pd.read_csv("group2_policy/outputs/2_daily_macro_scores_by_bank.csv")
    
    bank_to_region = {
        'US Federal Reserve': 'US',
        'European Central Bank': 'Europe',
        'Bank of Japan': 'Japan',
        'Bank of England': 'UK'
    }
    df_bank['Region'] = df_bank['Source_Bank'].map(bank_to_region)
    df_bank = df_bank.dropna(subset=['Region'])
    
    df_policy = df_bank.groupby('Region')['Daily_Macro_Score'].mean().reset_index()
    df_policy.rename(columns={'Daily_Macro_Score': 'Policy_Score'}, inplace=True)
    return df_policy

def process_group_3_earnings_ai():
    """Combines Earnings and AI Scores and maps regions to standard names."""
    df_earn = pd.read_csv("group3_earnings/output/regional_earnings_scores.csv")
    df_ai = pd.read_csv("group3_earnings/output/regional_ai_scores.csv")
    
    df_g3 = pd.merge(df_earn, df_ai, on='region', how='outer')
    
    # Map G3 broader regions to G1/G2 specific regions
    region_map = {
        'North_America': 'US',
        'Asia_Pacific': 'Japan',
        'Latin_America': 'LatAm' 
    }
    df_g3['Region'] = df_g3['region'].map(region_map).fillna(df_g3['region'])
    df_g3.rename(columns={'earnings_composite': 'Earnings_Score', 'ai_labor_score': 'AI_Score'}, inplace=True)
    
    return df_g3[['Region', 'Earnings_Score', 'AI_Score']]

def main():
    os.makedirs("outputs", exist_ok=True)

    # 1. Pull processed group data
    df_macro = process_group_1_macro()
    df_policy = process_group_2_policy()
    df_g3 = process_group_3_earnings_ai()

    # 2. Outer Merge all data
    df = pd.merge(df_policy, df_macro, on='Region', how='outer')
    df = pd.merge(df, df_g3, on='Region', how='outer')

    # 3. Standardize raw scores across regions
    score_cols = ['Policy_Score', 'Macro_Score', 'Earnings_Score', 'AI_Score']
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[f'{col}_Z'] = (df[col] - df[col].mean()) / df[col].std(ddof=0)
        # Fill missing data (e.g., LatAm missing Macro) with 0 -> "Neutral"
        df[f'{col}_Z'] = df[f'{col}_Z'].fillna(0)

    # 4. Calculate Final Composite
    df['Composite_Score'] = df[[f'{col}_Z' for col in score_cols]].mean(axis=1)

    # 5. Rank and Trade Generation
    df = df.sort_values(by='Composite_Score', ascending=False).reset_index(drop=True)
    df['Rank'] = df.index + 1
    
    df['Trade_Action'] = 'Neutral'
    if not df.empty:
        df.loc[0, 'Trade_Action'] = 'Long'
        df.loc[len(df)-1, 'Trade_Action'] = 'Short'

    long_region = df[df['Trade_Action'] == 'Long']['Region'].values[0] if len(df) > 0 else "N/A"
    short_region = df[df['Trade_Action'] == 'Short']['Region'].values[0] if len(df) > 0 else "N/A"

    # Export to CSV
    df.to_csv("outputs/final_composite_score_table.csv", index=False)
    
    # 6. Generate Text Report (Console + File)
    report_text = f"""====================================================
GROUP 4: INTEGRATION & PORTFOLIO OUTPUT - FINAL REPORT
====================================================

PIPELINE EXECUTION EXPLANATION:
--------------------------------
1. Macro Data (Group 1): Extracted the most recent row of data for GDP YoY, Core CPI, and Unemployment. Core CPI and Unemployment were inverted so that lower values yield a positive impact. These three metrics were Z-scored and averaged to create the 'Macro_Score'.
2. Policy Data (Group 2): Mapped central bank sources to our standard regions (e.g., 'Bank of England' to 'UK'). Averaged the NLP-derived daily macro sentiment scores into a single 'Policy_Score'.
3. Earnings & AI Data (Group 3): Merged regional earnings and AI scores. Mapped regions for cross-group consistency ('North_America' -> 'US', 'Asia_Pacific' -> 'Japan').
4. Integration & Standardization: Outer merged all datasets. Any missing signals (e.g., LatAm lacks Macro data, UK lacks Earnings data) were standardized to a Z-score of 0.0. This ensures a missing signal is treated as strictly "neutral" relative to the peer group rather than dropping the region entirely.
5. Composite Generation: Averaged the standardized Z-scores across all four pillars (Macro, Policy, Earnings, AI) to create the 'Composite_Score'.
6. Trade Logic: Ranked regions from highest to lowest composite score. The top-ranked region is mapped to 'Long', the bottom-ranked to 'Short', and the rest to 'Neutral'.

--- FINAL GLOBAL MACRO COMPOSITE RANKINGS ---
{df[['Rank', 'Region', 'Composite_Score', 'Trade_Action']].to_string(index=False)}

--- TRADE IDEAS ---
1. Cross-Asset Relative Value: Go Long {long_region} Equities/FX vs. Short {short_region} Equities/FX

Note: As LatAm ranked #1 entirely due to outsized positive signals in Group 3 (with Group 1 and 2 defaulting to 0), a discretionary portfolio manager should investigate LatAm earnings strength before executing.
====================================================
"""
    
    # Print to console
    print(report_text)
    
    # Save to file
    with open("outputs/summary_report.txt", "w") as f:
        f.write(report_text)
    print("Report saved to outputs/summary_report.txt")

    # 7. Generate Visualization
    plt.figure(figsize=(10, 6))
    colors = df['Trade_Action'].map({'Long': '#2ca02c', 'Short': '#d62728', 'Neutral': '#7f7f7f'})
    sns.barplot(x='Composite_Score', y='Region', data=df, palette=colors.tolist())
    
    plt.title('Global Macro Composite Scores by Region', fontsize=16, fontweight='bold')
    plt.xlabel('Standardized Composite Score (Z-Score)', fontsize=12)
    plt.ylabel('Region', fontsize=12)
    plt.axvline(0, color='black', linewidth=1.2, linestyle='--')
    plt.tight_layout()
    plt.savefig("outputs/composite_scores_chart.png", dpi=300)
    print("Chart saved to outputs/composite_scores_chart.png")

if __name__ == "__main__":
    main()