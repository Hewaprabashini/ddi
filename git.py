import streamlit as st
import pandas as pd
from PIL import Image
import seaborn as sns
from visualize import *  # only if you have custom visualization functions

# Load CSV data
df = pd.read_csv("interaction_signals.csv")

# Configure the Streamlit page
st.set_page_config(
    page_title="Interaction Signals Dashboard",  # page title
    page_icon=":bar_chart:",                      # page icon
    layout="wide",                                # full-width layout
)

# Add page title (properly terminated string)
st.title("Interaction Signals Dashboard :bar_chart:")

# Display first few rows
