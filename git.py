import streamlit as st
from PIL import Image
import seaborn as sns

from visualize import *

# load data
df = sns.load_dataset('iris')
# get column and species names
attributes = df.columns[:-1].tolist()
species = df['species'].unique().tolist()

# streamlit page config
st.set_page_config(
    page_title="Iris Dashboard",  # the page title shown in the browser tab
    page_icon=":bar_chart:",  # the page favicon shown in the browser tab
    layout="wide",  # page layout : use the entire screen
)

# add page title
st.title("My Iris Dataset Dashboard :bar_chart::hibiscus:")
