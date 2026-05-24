import streamlit as st
import pandas as pd
import requests

# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------

st.set_page_config(page_title="AI Farmer Profit Predictor")

st.title("🌾 AI Farmer Profit Prediction System")

# ---------------------------------------------------
# LOAD DATASETS
# ---------------------------------------------------

data = pd.read_csv("ICRISAT-District Level Data.csv")

market_data = pd.read_csv("market_price.csv")

data = data.dropna()

# ---------------------------------------------------
# USER INPUTS
# ---------------------------------------------------

st.subheader("Enter Farmer Details")

state = st.text_input("Enter State")

district = st.text_input("Enter District")

investment = st.number_input(
    "Investment Capacity (₹)",
    value=50000.0
)

acres = st.number_input(
    "Land Area (Acres)",
    value=1.0
)

water = st.selectbox(
    "Water Availability",
    ["Yes", "No"]
)

# ---------------------------------------------------
# WEATHER API
# ---------------------------------------------------

API_KEY = "0879ca4ca202e6048f440bf91f856ccd"

temperature = 30
humidity = 60

if district != "":

    try:

        url = f"https://api.openweathermap.org/data/2.5/weather?q={district},IN&appid={API_KEY}&units=metric"

        response = requests.get(url)

        weather_data = response.json()

        if response.status_code == 200:

            temperature = weather_data['main']['temp']

            humidity = weather_data['main']['humidity']

            st.subheader("🌦 Live Weather Data")

            st.write(f"Temperature: {temperature} °C")

            st.write(f"Humidity: {humidity}%")

        else:

            st.warning("Invalid district/city name")

    except:

        st.warning("Weather API Error")

# ---------------------------------------------------
# CROP YIELD COLUMNS
# ---------------------------------------------------

crop_mapping = {

    "RICE": "RICE YIELD (Kg per ha)",

    "WHEAT": "WHEAT YIELD (Kg per ha)",

    "MAIZE": "MAIZE YIELD (Kg per ha)",

    "GROUNDNUT": "GROUNDNUT YIELD (Kg per ha)",

    "SESAMUM": "SESAMUM YIELD (Kg per ha)",

    "SUGARCANE": "SUGARCANE YIELD (Kg per ha)",

    "COTTON": "COTTON YIELD (Kg per ha)",

    "SOYABEAN": "SOYABEAN YIELD (Kg per ha)",

    "CHICKPEA": "CHICKPEA YIELD (Kg per ha)",

    "PIGEONPEA": "PIGEONPEA YIELD (Kg per ha)",

    "PEARL MILLET": "PEARL MILLET YIELD (Kg per ha)",

    "BARLEY": "BARLEY YIELD (Kg per ha)",

    "SUNFLOWER": "SUNFLOWER YIELD (Kg per ha)",

    "CASTOR": "CASTOR YIELD (Kg per ha)",

    "LINSEED": "LINSEED YIELD (Kg per ha)"
}

# ---------------------------------------------------
# PREDICTION BUTTON
# ---------------------------------------------------

if st.button("Predict Best Crop and Profit"):

    best_crop = ""
    best_profit = -999999999
    best_production = 0
    best_market_price = 0

    # acre to hectare conversion

    hectares = acres * 0.4047

    # -----------------------------------------------

    for crop, yield_column in crop_mapping.items():

        try:

            # average yield from dataset

            avg_yield = data[yield_column].mean()

            # kg production

            production_kg = avg_yield * hectares

            # weather adjustment

            weather_factor = 1

            if temperature > 38:

                weather_factor = 0.75

            elif temperature > 32:

                weather_factor = 0.85

            elif humidity > 75:

                weather_factor = 1.10

            elif humidity < 30:

                weather_factor = 0.80

            # water availability effect

            if water == "No":

                weather_factor *= 0.70

            adjusted_kg = production_kg * weather_factor

            # kg to quintals

            production_quintals = adjusted_kg / 100

            # get market price

            market_price = market_data.loc[
                market_data['Crop'] == crop,
                'Price'
            ].values[0]

            # profit calculation

            profit = (
                production_quintals * market_price
            ) - investment

            # best crop selection

            if profit > best_profit:

                best_profit = profit

                best_crop = crop

                best_production = production_quintals

                best_market_price = market_price

        except:

            pass

    # ------------------------------------------------
    # RESULTS
    # ------------------------------------------------

    st.subheader("📊 Prediction Results")

    st.success(
        f"Recommended Crop: {best_crop}"
    )

    st.success(
        f"Estimated Production: {best_production:.2f} quintals"
    )

    st.success(
        f"Market Price: ₹ {best_market_price} per quintal"
    )

    st.success(
        f"Estimated Profit: ₹ {best_profit:.2f}"
    )

    # ------------------------------------------------

    if best_profit > 0:

        st.balloons()

        st.success(
            "✅ Profitable Crop Recommendation"
        )

    else:

        st.error(
            "❌ Low Profit. Try different inputs."
        )
