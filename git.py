import streamlit as st
import pandas as pd

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("drug_pairs_rules.csv")
    return df

df_rules = load_data()

st.title("Drug–Event Association Dashboard")

# -----------------------------
# Multi-select for Drug1 and Drug2
# -----------------------------
# Get unique drug names
all_drugs = sorted(set(df_rules["Drug1"]).union(set(df_rules["Drug2"])))

st.subheader("Select exactly 2 drugs as antecedents")
selected_drugs = st.multiselect(
    "Pick 2 drugs:",
    options=all_drugs,
    default=None
)

# Enforce exactly 2 drugs
if len(selected_drugs) != 2 and selected_drugs:
    st.warning("Please select exactly 2 drugs to see associated PTs.")
elif len(selected_drugs) == 2:
    drug_a, drug_b = selected_drugs
    
    # Filter rules where the two drugs appear (any order)
    filtered = df_rules[
        ((df_rules["Drug1"] == drug_a) & (df_rules["Drug2"] == drug_b)) |
        ((df_rules["Drug1"] == drug_b) & (df_rules["Drug2"] == drug_a))
    ]
    
    if filtered.empty:
        st.info("No PTs found for this drug combination.")
    else:
        st.subheader("Relevant PTs")
        for _, row in filtered.iterrows():
            pt = row["PT"]
            case_count = row["case_count"]

            # Choose background color based on case_count
            if case_count > 30:
                color = "red"
            elif 20 <= case_count <= 30:
                color = "green"
            else:
                color = "yellow"

            st.markdown(
                f"<div style='background-color:{color};padding:10px;margin:5px;border-radius:5px;'>"
                f"<b>PT:</b> {pt} | <b>Case Count:</b> {case_count} | "
                f"<b>Support:</b> {row['support']:.4f} | "
                f"<b>Confidence:</b> {row['confidence']:.2f} | "
                f"<b>Lift:</b> {row['lift']:.2f}"
                "</div>",
                unsafe_allow_html=True
            )
else:
    st.info("Select 2 drugs to see associated PTs.")

