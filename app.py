import streamlit as st
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

st.title("Farmer Profit Prediction System")

# Load dataset
data = pd.read_csv("ICRISAT-District Level Data.csv")

data = data.dropna()

# Features
X = data[['Year', 'State Code', 'RICE AREA (1000 ha)']]

# Target
y = data['RICE PRODUCTION (1000 tons)']

# Train model
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor()

model.fit(X_train, y_train)

st.subheader("Enter Details")

year = st.number_input("Year", value=2020)

state_code = st.number_input("State Code", value=1)

rice_area = st.number_input("Rice Area (1000 ha)", value=100.0)

market_price = st.number_input("Market Price per ton", value=2500.0)

cost = st.number_input("Total Cultivation Cost", value=100000.0)

if st.button("Predict Profit"):

    production = model.predict([[year, state_code, rice_area]])[0]

    profit = (production * market_price) - cost

    st.success(f"Predicted Production: {production:.2f} thousand tons")

    st.success(f"Estimated Profit: ₹ {profit:.2f}")
