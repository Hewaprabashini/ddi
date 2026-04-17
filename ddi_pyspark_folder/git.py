import os
import pandas as pd
import streamlit as st


# Load data
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "result.csv")
    return pd.read_csv(file_path)

df_rules = load_data()


# Page Title
st.title("Drug Safety & Interaction Explorer💊💊💊💊💊💊💊💊💊💊💊")

st.write(
    "This dashboard helps you explore relationships between drug combinations and adverse reactions . "
    "You can type the two type of nurological drugs that are need to explore or else you can enter the reaction(PT) to find the impacting drugs ."
)


# Color function (used everywhere)
def get_color(outcome):
    if outcome == "Critical":
        return "#ff4d4d"   # red
    elif outcome == "Serious":
        return "#ff944d"   # orange
    elif outcome == "Moderate":
        return "#ffd966"   # yellow
    else:
        return "#cce5ff"   # blue



# MODE SELECTION
mode = st.radio(
    "Choose what you want to explore:",
    ["🔍 Drug Pair → Adverse Reaction", "⚠️ Adverse Reaction → Drug Pairs"]
)


# MODE 1 — Drug → PT
if mode == "🔍 Drug Pair → Adverse Reaction":

    st.subheader("Select two drugs")

    all_drugs = sorted(set(df_rules["drug_1"]).union(set(df_rules["drug_2"])))

    drug_a = st.selectbox("Select first drug", all_drugs)

    possible_b = sorted(
        set(df_rules[df_rules["drug_1"] == drug_a]["drug_2"]).union(
            set(df_rules[df_rules["drug_2"] == drug_a]["drug_1"])
        )
    )

    drug_b = st.selectbox("Select second drug", possible_b)

    filtered = df_rules[
        ((df_rules["drug_1"] == drug_a) & (df_rules["drug_2"] == drug_b)) |
        ((df_rules["drug_1"] == drug_b) & (df_rules["drug_2"] == drug_a))
    ]


# MODE 2 — PT → Drug
else:

    st.subheader("Select an adverse reaction ")

    all_pts = sorted(df_rules["pt"].unique())
    selected_pt = st.selectbox("Choose reaction", all_pts)

    filtered = df_rules[df_rules["pt"] == selected_pt]

# Filters
st.subheader("Refine results ")

min_case = st.slider("Minimum number of cases", 1, 50, 1)
min_conf = st.slider("Minimum confidence (strength)", 0.0, 1.0, 0.0, 0.05)
min_lift = st.slider("Minimum lift (importance)", 0.0, 50.0, 0.0, 0.5)

filtered = filtered[
    (filtered["case_count"] >= min_case) &
    (filtered["confidence"] >= min_conf) &
    (filtered["lift"] >= min_lift)
]

# Display Results
if filtered.empty:
    st.info("No matching results found. Try adjusting filters.")
else:

    st.subheader("Results")

    filtered = filtered.sort_values(by="lift", ascending=False)

    for _, row in filtered.iterrows():

        drug1 = row["drug_1"]
        drug2 = row["drug_2"]
        pt = row["pt"]
        outcome = row["final_outcome"]
        case_count = row["case_count"]
        confidence = row["confidence"]
        lift = row["lift"]

        color = get_color(outcome)

        st.markdown(
            f"""
            <div style="background-color:{color};padding:12px;margin:8px;border-radius:10px;">
                <b>Drug Pair:</b> {drug1} + {drug2}<br>
                <b>Adverse Reaction (PT):</b> {pt}<br>
                <b>Severity:</b> {outcome}<br>
                <b>Number of Cases:</b> {case_count}<br>
                <b>Confidence:</b> {confidence:.2f}<br>
                <b>Lift:</b> {lift:.2f}
            </div>
            """,
            unsafe_allow_html=True
        )

# Help Section
st.markdown("""
---

### 📘 What these results mean

- **Drug Pair** → two medicines used together  
- **Adverse Reaction (PT)** → possible side effect or medical event  
- **Number of Cases** → how often this was observed  
- **Confidence** → how likely the reaction happens when drugs are used together  
- **Lift** → how strongly the drugs are linked to the reaction  
- **Severity Color**:
  - 🔴 Critical (very serious)
  - 🟠 Serious
  - 🟡 Moderate
  - 🔵 Mild / Other
""")
