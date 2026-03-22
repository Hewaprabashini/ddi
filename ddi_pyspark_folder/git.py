import os
import pandas as pd
import streamlit as st

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "drug_pairs_rules.csv")
    
    # Debug (optional)
    # st.write("Reading from:", file_path)

    df = pd.read_csv(file_path)
    return df

# ✅ IMPORTANT: call the function
df_rules = load_data()

st.title("Drug–Event Association Dashboard")

# -----------------------------
# Build Drug List
# -----------------------------
all_drugs = sorted(set(df_rules["Drug1"]).union(set(df_rules["Drug2"])))

st.subheader("Select exactly 2 drugs as antecedents")

# 🔎 Search box
search_term = st.text_input("Type a drug name to filter the list:")

if search_term:
    filtered_drugs = [d for d in all_drugs if search_term.lower() in d.lower()]
else:
    filtered_drugs = all_drugs

# Multi-select (restricted to 2)
selected_drugs = st.multiselect(
    "Pick 2 drugs:",
    options=filtered_drugs,
    max_selections=2
)

# -----------------------------
# Validation
# -----------------------------
if len(selected_drugs) == 2:
    drug_a, drug_b = selected_drugs

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

            # 🎨 Color logic
            if case_count > 30:
                color = "#ff4d4d"
            elif 20 <= case_count <= 30:
                color = "#4CAF50"
            else:
                color = "#FFD966"

            st.markdown(
                f"<div style='background-color:{color};padding:10px;"
                f"margin:6px;border-radius:8px;'>"
                f"<b>PT:</b> {pt} | "
                f"<b>Case Count:</b> {case_count} | "
                f"<b>Support:</b> {row['support']:.4f} | "
                f"<b>Confidence:</b> {row['confidence']:.2f} | "
                f"<b>Lift:</b> {row['lift']:.2f}"
                "</div>",
                unsafe_allow_html=True
            )

elif len(selected_drugs) == 1:
    st.warning("Please select one more drug to complete the pair.")

else:
    st.info("Select 2 drugs to see associated PTs.")
