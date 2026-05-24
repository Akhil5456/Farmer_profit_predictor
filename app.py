import streamlit as st
import pandas as pd
import requests

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ----------------------------------------------------
# PAGE TITLE
# ----------------------------------------------------

st.set_page_config(page_title="Farmer Profit Predictor")

st.title("AI Farmer Profit Prediction System")

# ----------------------------------------------------
# LOAD DATASETS
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

            st.warning("Invalid district/city name")

    except:

        st.warning("Weather API Error")

# ----------------------------------------------------
# CROP RECOMMENDATION LOGIC
# ----------------------------------------------------

if water == "Yes" and humidity >= 60:

    best_crop = "RICE"

elif temperature >= 30:

    best_crop = "MAIZE"

elif investment >= 100000:

    best_crop = "COTTON"

elif water == "No":

    best_crop = "WHEAT"

else:

    best_crop = "GROUNDNUT"

# ----------------------------------------------------
# MARKET PRICE FETCH
# ----------------------------------------------------

try:

    market_price = market_data.loc[
        market_data['Crop'] == best_crop,
        'Price'
    ].values[0]

except:

    market_price = 2000

# ----------------------------------------------------
# MACHINE LEARNING MODEL
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
# PREDICTION
# ----------------------------------------------------

if st.button("Predict Crop and Profit"):

    # Production Prediction

    production = model.predict(
        [[2024, 1, acres]]
    )[0]

    # Convert thousand tons to tons

    production_tons = production * 1000

    # Profit Calculation

    profit = (
        production_tons * market_price
    ) - investment

    # ------------------------------------------------

    st.subheader("Prediction Results")

    st.success(
        f"Recommended Crop: {best_crop}"
    )

    st.success(
        f"Estimated Production: {production_tons:.2f} tons"
    )

    st.success(
        f"Current Market Price: ₹ {market_price} per ton"
    )

    st.success(
        f"Estimated Profit: ₹ {profit:.2f}"
    )

    # ------------------------------------------------

    if profit > 0:

        st.balloons()

        st.success(
            "Profitable Crop Recommendation"
        )

    else:

        st.error(
            "Low Profit. Try different inputs."
        )
