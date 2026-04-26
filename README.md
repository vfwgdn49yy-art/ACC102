Global Inflation Data Analysis Product

1) Project Objective

This project builds an interactive, reproducible, and substantive data analysis product based on World Bank inflation data.

· Analysis Question: How do inflation levels across different countries and regions change over time?
· Target Users: Investors, policy analysts, and the general public interested in macroeconomics.
· Data Source: World Bank WDI, indicator FP.CPI.TOTL.ZG.
· Retrieval Date: 2026-04-08.

2) Directory Structure

```text
Iflation/
  data/
    API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_287.csv
    Metadata_Country_API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_287.csv
    Metadata_Indicator_API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_287.csv
  app.py
  inflation_analysis.ipynb
  reflection_report.md
  requirements.txt
  README.md
```

3) Product Operation (Local)

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the Streamlit product:

```bash
streamlit run app.py
```

Main page features:

· Filter data by year and region.
· Display regional inflation trend changes.
· Display country inflation comparison for the latest year.
· Display distribution and volatility analysis.

4) Python Notebook

Notebook file: inflation_analysis.ipynb

Notebook contents:

· Data loading and cleaning
· Data transformation (wide format to long format)
· Descriptive statistics
· Visualization and conclusion extraction