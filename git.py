
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("all_rules.csv")

df = load_data()



# Load your final_rules DataFrame (must include columns: antecedents, consequents, case_count, support, confidence, lift)
# Example if saved earlier:
# final_rules = pd.read_csv("final_rules.csv")

# Convert frozensets to strings for display
all_rules["antecedents_str"] = all_rules["antecedents"].apply(lambda x: ", ".join(list(x)))
all_rules["consequents_str"] = all_rules["consequents"].apply(lambda x: ", ".join(list(x)))

st.title("Drug–Event Association Dashboard")

# Search box for antecedents
search_term = st.text_input("Search antecedents (type part of a drug name):")

if search_term:
    # Filter antecedents by search term
    filtered_options = sorted(
        [a for a in all_rules["antecedents_str"].unique() if search_term.lower() in a.lower()]
    )
else:
    filtered_options = sorted(all_rules["antecedents_str"].unique())

# Multi-select for antecedents
selected_antecedents = st.multiselect("Select antecedents (drug pairs):", filtered_options)

if selected_antecedents:
    # Filter rules by selected antecedents
    filtered = all_rules[final_rules["antecedents_str"].isin(selected_antecedents)]

    st.subheader("Relevant PTs")
    for _, row in filtered.iterrows():
        pt = row["consequents_str"]
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
    st.info("Search and select antecedents to see associated PTs.")

