import streamlit as st
import pandas as pd

st.title("Crop Prediction System")

data = pd.read_csv("ICRISAT-District Level Data.csv")

st.write(data.columns)
