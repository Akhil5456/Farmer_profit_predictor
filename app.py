import streamlit as st
import pandas as pd
import requests

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(page_title="AI Farmer Profit Predictor")

st.title("AI Farmer Profit Prediction System")

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

data = pd.read_csv("ICRISAT-District Level Data.csv")

market_data = pd.read_csv("market_price.csv")

data = data.dropna()

# ----------------------------------------------------
# USER INPUTS
# ----------------------------------------------------

st.subheader("Enter Farmer Details")

state = st.text_input("Enter State")

district = st.text_input("Enter District")

investment = st.number_input(
    "Investment Capacity (₹)",
    value=50000.0
)

acres = st.number_input(
    "Land Area (Acres)",
    value=5.0
)

water = st.selectbox(
    "Water Availability",
    ["Yes", "No"]
)

# ----------------------------------------------------
# WEATHER API
# ----------------------------------------------------

API_KEY = "0879ca4ca202e6048f440bf91f856ccd"

temperature = 0
humidity = 0

if district != "":

    try:

        url = f"https://api.openweathermap.org/data/2.5/weather?q={district},IN&appid={API_KEY}&units=metric"

        response = requests.get(url)

        weather_data = response.json()

        if response.status_code == 200:

            temperature = weather_data['main']['temp']

            humidity = weather_data['main']['humidity']

            st.subheader("Live Weather Data")

            st.write(f"Temperature: {temperature} °C")

            st.write(f"Humidity: {humidity}%")

        else:

            st.warning("Invalid district/city")

    except:

        st.warning("Weather API Error")

# ----------------------------------------------------
# RANDOM FOREST MODEL
# ----------------------------------------------------

X = data[['Year', 'State Code', 'RICE AREA (1000 ha)']]

y = data['RICE PRODUCTION (1000 tons)']

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestRegressor()

model.fit(X_train, y_train)

# ----------------------------------------------------
# PREDICT BUTTON
# ----------------------------------------------------

if st.button("Predict Best Crop and Profit"):

    best_crop = ""
    best_profit = -999999999
    best_production = 0
    best_market_price = 0

    # ------------------------------------------------
    # LOOP THROUGH ALL CROPS
    # ------------------------------------------------

    for index, row in market_data.iterrows():

        crop = row['Crop']

        market_price = row['Price']

        # production prediction

        production = model.predict(
            [[2024, 1, acres]]
        )[0]

        # thousand tons -> tons

        production_tons = production * 1000

        # tons -> quintals

        production_quintals = production_tons * 10

        # weather effect

        weather_factor = 1

        if temperature > 35:
            weather_factor = 0.8

        elif humidity > 70:
            weather_factor = 1.1

        adjusted_production = (
            production_tons * weather_factor
        )

        # water effect

        if water == "No":

            adjusted_production *= 0.7

        # profit

        profit = (
            adjusted_production * market_price
        ) - investment

        # best crop selection

        if profit > best_profit:

            best_profit = profit

            best_crop = crop

            best_market_price = market_price

            best_production = production_quintals

    # ------------------------------------------------
    # RESULTS
    # ------------------------------------------------

    st.subheader("Prediction Results")

    st.success(
        f"Recommended Crop: {best_crop}"
    )

    st.success(
        f"Estimated Production: {best_production:.2f} quintals"
    )

    st.success(
        f"Current Market Price: ₹ {best_market_price} per ton"
    )

    st.success(
        f"Estimated Profit: ₹ {best_profit:.2f}"
    )

    # ------------------------------------------------

    if best_profit > 0:

        st.balloons()

        st.success(
            "Profitable Crop Recommendation"
        )

    else:

        st.error(
            "Low Profit. Try different inputs."
        )
