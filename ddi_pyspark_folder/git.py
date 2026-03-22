import os
import pandas as pd
import streamlit as st

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "result.csv")
    df = pd.read_csv(file_path)
    return df

df_rules = load_data()

st.title("Drug–Event Association Dashboard")

# -----------------------------
# Build Drug List
# -----------------------------
all_drugs = sorted(set(df_rules["drug_1"]).union(set(df_rules["drug_2"])))

st.subheader("Select antecedent drugs")

# First drug
first_drug = st.selectbox("Pick the first drug:", all_drugs)

# Suggest second drug
possible_seconds = sorted(
    set(df_rules[df_rules["drug_1"] == first_drug]["drug_2"]).union(
        set(df_rules[df_rules["drug_2"] == first_drug]["drug_1"])
    )
)

second_drug = st.selectbox("Pick the second drug:", possible_seconds)

# -----------------------------
# Filters
# -----------------------------
st.subheader("Filter rules by metrics")

min_case = st.slider("Minimum Case Count:", 1, 50, 1)
min_conf = st.slider("Minimum Confidence:", 0.0, 1.0, 0.0, 0.05)
min_lift = st.slider("Minimum Lift:", 0.0, 5000.0, 0.0, 50.0)

# -----------------------------
# Filter selected pair
# -----------------------------
filtered = df_rules[
    (((df_rules["drug_1"] == first_drug) & (df_rules["drug_2"] == second_drug)) |
     ((df_rules["drug_1"] == second_drug) & (df_rules["drug_2"] == first_drug)))
]

# Apply filters
filtered = filtered[
    (filtered["case_count"] >= min_case) &
    (filtered["confidence"] >= min_conf) &
    (filtered["lift"] >= min_lift)
]

# -----------------------------
# Display results
# -----------------------------
if filtered.empty:
    st.info("No PTs found for this drug combination with the selected filters.")
else:
    st.subheader("Relevant PTs (sorted by Lift)")
    filtered = filtered.sort_values(by="lift", ascending=False)

    for _, row in filtered.iterrows():
        pt = row["pt"]
        case_count = row["case_count"]
        support = row["support"]
        confidence = row["confidence"]
        lift = row["lift"]
        outcome = row["final_outcome"]

        # 🎨 Color based on OUTCOME (better clinical logic)
        if outcome == "Critical":
            color = "#ff4d4d"  # red
        elif outcome == "Serious":
            color = "#ff944d"  # orange
        elif outcome == "Moderate":
            color = "#ffd966"  # yellow
        else:
            color = "#cce5ff"  # blue

        st.markdown(
            f"<div style='background-color:{color};padding:10px;margin:6px;border-radius:8px;'>"
            f"<b>PT:</b> {pt} | "
            f"<b>Outcome:</b> {outcome} | "
            f"<b>Case Count:</b> {case_count} | "
            f"<b>Support:</b> {support:.4f} | "
            f"<b>Confidence:</b> {confidence:.2f} | "
            f"<b>Lift:</b> {lift:.2f}"
            "</div>",
            unsafe_allow_html=True
        )

# -----------------------------
# Info
# -----------------------------
st.markdown("""
**Tips:**  
- Case Count: Number of cases where this PT occurred with the drug pair  
- Support: Frequency of occurrence in dataset  
- Confidence: Likelihood of PT given drug pair  
- Lift: Strength of association  
- **Outcome-based colors (clinical severity):**  
  🔴 Critical | 🟠 Serious | 🟡 Moderate | 🔵 Mild/Other  
""")
