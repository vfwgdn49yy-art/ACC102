import pathlib

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Global Inflation Explorer", layout="wide")

DATA_DIR = pathlib.Path(__file__).parent / "data"
CPI_FILE = DATA_DIR / "API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_287.csv"
COUNTRY_META_FILE = DATA_DIR / "Metadata_Country_API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_287.csv"


@st.cache_data
def load_cpi_long() -> pd.DataFrame:
    raw = pd.read_csv(CPI_FILE, skiprows=4)
    raw = raw.drop(columns=[c for c in raw.columns if c.startswith("Unnamed")], errors="ignore")
    year_cols = [c for c in raw.columns if c.isdigit()]
    base_cols = ["Country Name", "Country Code", "Indicator Name", "Indicator Code"]
    use_cols = [c for c in base_cols + year_cols if c in raw.columns]
    raw = raw[use_cols]

    long_df = raw.melt(
        id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Inflation",
    )
    long_df["Year"] = pd.to_numeric(long_df["Year"], errors="coerce").astype("Int64")
    long_df["Inflation"] = pd.to_numeric(long_df["Inflation"], errors="coerce")
    return long_df.dropna(subset=["Year"])


@st.cache_data
def load_country_meta() -> pd.DataFrame:
    meta = pd.read_csv(COUNTRY_META_FILE)
    keep_cols = ["Country Code", "Region", "IncomeGroup", "TableName"]
    keep_cols = [c for c in keep_cols if c in meta.columns]
    return meta[keep_cols]


def main() -> None:
    st.title("Global Inflation Explorer")
    st.caption(
        "Data source: World Bank WDI (Indicator FP.CPI.TOTL.ZG), download date: 2026-04-08."
    )

    cpi = load_cpi_long()
    meta = load_country_meta()
    df = cpi.merge(meta, on="Country Code", how="left")

    st.sidebar.header("Filters")
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())
    year_range = st.sidebar.slider("Year range", min_year, max_year, (2000, max_year))

    region_options = sorted([x for x in df["Region"].dropna().unique()])
    selected_regions = st.sidebar.multiselect("Region", region_options, default=region_options[:4])

    filtered = df[
        (df["Year"] >= year_range[0])
        & (df["Year"] <= year_range[1])
        & (df["Region"].isin(selected_regions) if selected_regions else True)
    ].copy()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Records", f"{len(filtered):,}")
    with col2:
        st.metric("Countries/Areas", f"{filtered['Country Code'].nunique():,}")
    with col3:
        st.metric("Missing rate", f"{filtered['Inflation'].isna().mean() * 100:.1f}%")

    st.subheader("1) Inflation Trend by Region")
    region_trend = (
        filtered.groupby(["Year", "Region"], dropna=False)["Inflation"]
        .mean()
        .reset_index()
        .dropna(subset=["Region", "Inflation"])
    )
    fig_region = px.line(region_trend, x="Year", y="Inflation", color="Region")
    fig_region.update_layout(height=420)
    st.plotly_chart(fig_region, use_container_width=True)

    st.subheader("2) Country Inflation Comparison")
    top_n = st.slider("Top N countries by latest-year inflation", min_value=5, max_value=30, value=10)
    latest_year = int(filtered["Year"].max())
    latest_df = filtered[filtered["Year"] == latest_year].dropna(subset=["Inflation"])
    top_df = latest_df.nlargest(top_n, "Inflation")[["Country Name", "Region", "Inflation"]]
    fig_top = px.bar(top_df, x="Country Name", y="Inflation", color="Region")
    fig_top.update_layout(height=420, xaxis_tickangle=-35)
    st.plotly_chart(fig_top, use_container_width=True)

    st.subheader("3) Distribution and Volatility")
    dist_year = st.slider("Distribution year", min_value=min_year, max_value=max_year, value=latest_year)
    dist_df = filtered[filtered["Year"] == dist_year].dropna(subset=["Inflation"])
    fig_hist = px.histogram(dist_df, x="Inflation", nbins=35)
    fig_hist.update_layout(height=380)
    st.plotly_chart(fig_hist, use_container_width=True)

    # Country-level volatility in the selected period (inflation std).
    vol_df = (
        filtered.groupby("Country Name")["Inflation"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={"mean": "AvgInflation", "std": "Volatility", "count": "Obs"})
    )
    vol_df = vol_df[vol_df["Obs"] >= 8].dropna(subset=["AvgInflation", "Volatility"])
    fig_scatter = px.scatter(vol_df, x="AvgInflation", y="Volatility", hover_name="Country Name")
    fig_scatter.update_layout(height=420)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("4) Key Insights")
    st.markdown(
        "- Use regional trend lines to compare inflation trajectories over time.\n"
        "- Use country comparison to identify recent inflation hotspots.\n"
        "- Use volatility analysis to find economies with high average inflation and high instability."
    )

    st.subheader("Data Preview")
    st.dataframe(filtered.head(30), use_container_width=True)


if __name__ == "__main__":
    main()
