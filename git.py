import streamlit as st
import pandas as pd
import plotly.express as px


# Page configuration
st.set_page_config(
    page_title="Drug–Drug Interaction Dashboard",
    layout="wide"
)


# Load data
@st.cache_data
def load_data():
    return pd.read_csv("interaction_signals.csv")

df = load_data()


# Title
st.title("Drug–Drug Interaction Signal Dashboard")
st.markdown(
    "Analysis of adverse drug reactions using association rule metrics "
    "(Lift and Support)."
)


# Sidebar filters
st.sidebar.header("Filters")

drug_a = st.sidebar.multiselect(
    "Select Drug A",
    options=sorted(df["DrugA"].unique())
)

drug_b = st.sidebar.multiselect(
    "Select Drug B",
    options=sorted(df["DrugB"].unique())
)

severity = st.sidebar.multiselect(
    "Select Severity",
    options=sorted(df["Severity"].unique())
)

min_lift = st.sidebar.slider(
    "Minimum Lift (2 Drugs)",
    float(df["Lift_2Drugs"].min()),
    float(df["Lift_2Drugs"].max()),
    float(df["Lift_2Drugs"].min())
)


# Apply filters
filtered_df = df.copy()

if drug_a:
    filtered_df = filtered_df[filtered_df["DrugA"].isin(drug_a)]

if drug_b:
    filtered_df = filtered_df[filtered_df["DrugB"].isin(drug_b)]

if severity:
    filtered_df = filtered_df[filtered_df["Severity"].isin(severity)]

filtered_df = filtered_df[
    filtered_df["Lift_2Drugs"] >= min_lift
]


# Key metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Interactions", len(filtered_df))
col2.metric("Unique Drug A", filtered_df["DrugA"].nunique())
col3.metric("Unique Drug B", filtered_df["DrugB"].nunique())
col4.metric("Unique ADRs", filtered_df["ADR"].nunique())


# Tabs
tab1, tab2, tab3 = st.tabs(
    ["Interaction Table", "Lift Analysis", "Severity Overview"]
)


# Tab 1: Data Table
with tab1:
    st.subheader("Filtered Drug–ADR Interactions")
    st.dataframe(
        filtered_df.sort_values("Lift_2Drugs", ascending=False),
        use_container_width=True
    )


# Tab 2: Lift analysis
with tab2:
    st.subheader("Lift vs Support")

    fig = px.scatter(
        filtered_df,
        x="Support_3Itemset",
        y="Lift_2Drugs",
        color="Severity",
        hover_data=["DrugA", "DrugB", "ADR"],
        title="Lift vs Support for Drug Pairs"
    )

    st.plotly_chart(fig, use_container_width=True)


# Tab 3: Severity distribution
with tab3:
    st.subheader("Severity Distribution")

    severity_counts = (
        filtered_df["Severity"]
        .value_counts()
        .reset_index()
    )

    severity_counts.columns = ["Severity", "Count"]

    fig = px.bar(
        severity_counts,
        x="Severity",
        y="Count",
        title="ADR Severity Levels"
    )

    st.plotly_chart(fig, use_container_width=True)


# Footer
st.markdown("---")
st.caption("Data source: FAERS | Association Rule Mining Results")
