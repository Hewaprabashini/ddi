import os
import pandas as pd
import streamlit as st

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "result.csv")
    return pd.read_csv(file_path)

df_rules = load_data()

st.title("Drug–Event Association Dashboard")

# =============================
# MODE SWITCH
# =============================
mode = st.radio(
    "Select Analysis Mode:",
    ["Drug Pair → PTs", "PT → Drug Pairs"]
)

# =============================
# MODE 1 — Drug Pair → PTs
# =============================
if mode == "Drug Pair → PTs":

    st.subheader("Select Drug Pair")

    all_drugs = sorted(set(df_rules["drug_1"]).union(set(df_rules["drug_2"])))

    first_drug = st.selectbox("Pick first drug:", all_drugs)

    possible_seconds = sorted(
        set(df_rules[df_rules["drug_1"] == first_drug]["drug_2"]).union(
            set(df_rules[df_rules["drug_2"] == first_drug]["drug_1"])
        )
    )

    second_drug = st.selectbox("Pick second drug:", possible_seconds)

    filtered = df_rules[
        (((df_rules["drug_1"] == first_drug) & (df_rules["drug_2"] == second_drug)) |
         ((df_rules["drug_1"] == second_drug) & (df_rules["drug_2"] == first_drug)))
    ]

# =============================
# MODE 2 — PT → Drug Pairs
# =============================
else:

    st.subheader("Select Adverse Event (PT)")

    all_pts = sorted(df_rules["pt"].unique())
    selected_pt = st.selectbox("Choose PT:", all_pts)

    filtered = df_rules[df_rules["pt"] == selected_pt]

# =============================
# COMMON FILTERS
# =============================
st.subheader("Filter rules")

min_case = st.slider("Minimum Case Count:", 1, 50, 1)
min_conf = st.slider("Minimum Confidence:", 0.0, 1.0, 0.0, 0.05)
min_lift = st.slider("Minimum Lift:", 0.0, 5000.0, 0.0, 50.0)

filtered = filtered[
    (filtered["case_count"] >= min_case) &
    (filtered["confidence"] >= min_conf) &
    (filtered["lift"] >= min_lift)
]

# =============================
# DISPLAY
# =============================
if filtered.empty:
    st.info("No results found.")
else:
    st.subheader("Results (sorted by Lift)")
    filtered = filtered.sort_values(by="lift", ascending=False)

    for _, row in filtered.iterrows():

        drug1 = row["drug_1"]
        drug2 = row["drug_2"]
        pt = row["pt"]
        case_count = row["case_count"]
        confidence = row["confidence"]
        lift = row["lift"]
        outcome = row["final_outcome"]

        if outcome == "Critical":
            color = "#ff4d4d"
        elif outcome == "Serious":
            color = "#ff944d"
        elif outcome == "Moderate":
            color = "#ffd966"
        else:
            color = "#cce5ff"

        st.markdown(
            f"<div style='background-color:{color};padding:10px;margin:6px;border-radius:8px;'>"
            f"<b>Drug Pair:</b> {drug1} + {drug2} | "
            f"<b>PT:</b> {pt} | "
            f"<b>Outcome:</b> {outcome} | "
            f"<b>Case Count:</b> {case_count} | "
            f"<b>Confidence:</b> {confidence:.2f} | "
            f"<b>Lift:</b> {lift:.2f}"
            "</div>",
            unsafe_allow_html=True
        )
