import os
import pandas as pd
import streamlit as st

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__),result.csv")
    df = pd.read_csv(file_path)
    return df

df_rules = load_data()

st.title("Drug–Event Association Dashboard")

# -----------------------------
# Build Drug List
# -----------------------------
all_drugs = sorted(set(df_rules["Drug1"]).union(set(df_rules["Drug2"])))

st.subheader("Select antecedent drugs")

# 🔎 First drug selection
first_drug = st.selectbox("Pick the first drug:", all_drugs)

# 🔎 Suggest second drug based on first drug
possible_seconds = sorted(
    set(df_rules[df_rules["Drug1"] == first_drug]["Drug2"]).union(
        set(df_rules[df_rules["Drug2"] == first_drug]["Drug1"])
    )
)

second_drug = st.selectbox("Pick the second drug:", possible_seconds)

# -----------------------------
# Filters for metrics
# -----------------------------
st.subheader("Filter rules by metrics")
min_case = st.slider("Minimum Case Count:", min_value=1, max_value=50, value=1)
min_conf = st.slider("Minimum Confidence:", 0.0, 1.0, 0.0, 0.05)
min_lift = st.slider("Minimum Lift:", 0.0, 5000.0, 0.0, 50.0)

# -----------------------------
# Filter rules for selected pair
# -----------------------------
filtered = df_rules[
    (((df_rules["Drug1"] == first_drug) & (df_rules["Drug2"] == second_drug)) |
     ((df_rules["Drug1"] == second_drug) & (df_rules["Drug2"] == first_drug)))
]

# Apply filters
filtered = filtered[
    (filtered["case_count"] >= min_case) &
    (filtered["confidence"] >= min_conf) &
    (filtered["lift"] >= min_lift)
]

if filtered.empty:
    st.info("No PTs found for this drug combination with the selected filters.")
else:
    st.subheader("Relevant PTs (sorted by Lift)")

    # Sort by Lift descending
    filtered = filtered.sort_values(by="lift", ascending=False)

    for _, row in filtered.iterrows():
        pt = row["PT"]
        case_count = row["case_count"]
        support = row["support"]
        confidence = row["confidence"]
        lift = row["lift"]

        # 🎨 Color logic based on your description
        if case_count < 5 and lift > 1000:
            color = "#ff6666"  # very high risk
        elif lift >= 50 and case_count > 5:
            color = "#ffcc66"  # moderate
        else:
            color = "#cce5ff"  # mild / low

        st.markdown(
            f"<div style='background-color:{color};padding:10px;margin:6px;border-radius:8px;'>"
            f"<b>PT:</b> {pt} | "
            f"<b>Case Count:</b> {case_count} | "
            f"<b>Support:</b> {support:.4f} | "
            f"<b>Confidence:</b> {confidence:.2f} | "
            f"<b>Lift:</b> {lift:.2f}"
            "</div>",
            unsafe_allow_html=True
        )

# -----------------------------
# Info / Tips
# -----------------------------
st.markdown("""
**Tips:**  
- Case Count: Number of cases where this PT occurred with the drug pair.  
- Support: Proportion of all cases where this PT occurred.  
- Confidence: Probability that PT occurs given this drug pair.  
- Lift: How much more likely the PT occurs than by chance.  
- Color codes indicate severity: red = high risk, yellow = moderate, blue = mild.
""")
