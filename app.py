import streamlit as st
import pandas as pd
import requests

# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------

st.set_page_config(page_title="AI Farmer Profit Predictor", layout="wide")

# Add background image
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Get unique states and districts from dataset
states = sorted(data['State Name'].unique().tolist())
states.insert(0, "")

state = st.selectbox(
    "Select State",
    states
)

# Get districts for selected state
if state:
    districts = sorted(data[data['State Name'] == state]['Dist Name'].unique().tolist())
    districts.insert(0, "")
else:
    districts = [""]

district = st.selectbox(
    "Select District",
    districts
)

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

if district != "" and state != "":

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

            st.warning("Invalid district/city name. Using default weather values.")

    except:

        st.warning("Weather API Error. Using default weather values.")

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

    # Define minimum investment requirement (same for all crops)
    min_investment_per_acre = 3000  # ₹3,000 per acre

    # Define water-intensive crops (require irrigation)
    water_intensive_crops = ["RICE", "SUGARCANE", "MAIZE", "COTTON", "GROUNDNUT", "SOYABEAN"]

    # Define drought-resistant crops (can grow with less water)
    drought_resistant_crops = ["WHEAT", "CHICKPEA", "PIGEONPEA", "PEARL MILLET", "BARLEY", "SESAMUM", "SUNFLOWER", "CASTOR", "LINSEED"]

    # ------------------------------------------------

    # Filter crops based on water availability and minimum investment
    crops_to_consider = {}
    for crop, yield_column in crop_mapping.items():
        # Check investment requirement
        min_total_investment = min_investment_per_acre * acres

        if investment >= min_total_investment:
            # Filter based on water availability
            if water == "Yes":
                # Water available - consider water-intensive crops
                if crop in water_intensive_crops:
                    crops_to_consider[crop] = yield_column
            else:
                # No water - consider drought-resistant crops
                if crop in drought_resistant_crops:
                    crops_to_consider[crop] = yield_column

    # Show warning if investment is too low for any crop
    if len(crops_to_consider) == 0:
        st.error(f"❌ Investment of ₹{investment:.2f} is too low for any crop with {acres} acres.")
        st.info(f"Minimum investment needed: ₹{min_investment_per_acre * acres:.2f} for {acres} acre(s)")
        st.stop()

    for crop, yield_column in crops_to_consider.items():

        try:

            # Get location-specific yield
            if district != "" and state != "":
                district_data = data[
                    (data['Dist Name'].str.lower() == district.lower()) &
                    (data['State Name'].str.lower() == state.lower())
                ]
                if len(district_data) > 0:
                    avg_yield = district_data[yield_column].mean()
                else:
                    state_data = data[data['State Name'].str.lower() == state.lower()]
                    if len(state_data) > 0:
                        avg_yield = state_data[yield_column].mean()
                    else:
                        avg_yield = data[yield_column].mean()
            elif state != "":
                state_data = data[data['State Name'].str.lower() == state.lower()]
                if len(state_data) > 0:
                    avg_yield = state_data[yield_column].mean()
                else:
                    avg_yield = data[yield_column].mean()
            else:
                avg_yield = data[yield_column].mean()

            # production in kg

            production_kg = avg_yield * hectares

            # ------------------------------------------------
            # WEATHER SUITABILITY
            # ------------------------------------------------

            suitability = 1

            # RICE
            if crop == "RICE":
                if humidity >= 70 and water == "Yes":
                    suitability = 1.2
                elif humidity >= 60:
                    suitability = 1.0
                else:
                    suitability = 0.7

            # WHEAT
            elif crop == "WHEAT":
                if 15 <= temperature <= 28:
                    suitability = 1.2
                elif 10 <= temperature <= 32:
                    suitability = 1.0
                else:
                    suitability = 0.6

            # MAIZE
            elif crop == "MAIZE":
                if 20 <= temperature <= 35:
                    suitability = 1.2
                elif 15 <= temperature <= 38:
                    suitability = 1.0
                else:
                    suitability = 0.7

            # SUGARCANE
            elif crop == "SUGARCANE":
                if water == "Yes" and humidity >= 60:
                    suitability = 1.1
                elif water == "Yes":
                    suitability = 0.9
                else:
                    suitability = 0.5

            # COTTON
            elif crop == "COTTON":
                if temperature >= 25 and humidity < 60:
                    suitability = 1.2
                elif temperature >= 20:
                    suitability = 1.0
                else:
                    suitability = 0.6

            # GROUNDNUT
            elif crop == "GROUNDNUT":
                if 20 <= temperature <= 30:
                    suitability = 1.2
                elif 18 <= temperature <= 32:
                    suitability = 1.0
                else:
                    suitability = 0.7

            # SESAMUM
            elif crop == "SESAMUM":
                if humidity < 50:
                    suitability = 1.2
                elif humidity < 60:
                    suitability = 1.0
                else:
                    suitability = 0.7

            # SOYABEAN
            elif crop == "SOYABEAN":
                if humidity >= 60:
                    suitability = 1.2
                elif humidity >= 50:
                    suitability = 1.0
                else:
                    suitability = 0.7

            # CHICKPEA
            elif crop == "CHICKPEA":
                if temperature < 30:
                    suitability = 1.2
                elif temperature < 35:
                    suitability = 1.0
                else:
                    suitability = 0.6

            # PIGEONPEA
            elif crop == "PIGEONPEA":
                if water == "No":
                    suitability = 1.2
                else:
                    suitability = 1.0

            # PEARL MILLET
            elif crop == "PEARL MILLET":
                if temperature >= 30:
                    suitability = 1.2
                elif temperature >= 25:
                    suitability = 1.0
                else:
                    suitability = 0.7

            # BARLEY
            elif crop == "BARLEY":
                if temperature <= 25:
                    suitability = 1.2
                elif temperature <= 28:
                    suitability = 1.0
                else:
                    suitability = 0.6

            # SUNFLOWER
            elif crop == "SUNFLOWER":
                if humidity < 60:
                    suitability = 1.2
                elif humidity < 70:
                    suitability = 1.0
                else:
                    suitability = 0.7

            # CASTOR
            elif crop == "CASTOR":
                if water == "No":
                    suitability = 1.2
                else:
                    suitability = 0.9

            # LINSEED
            elif crop == "LINSEED":
                if temperature < 28:
                    suitability = 1.2
                elif temperature < 32:
                    suitability = 1.0
                else:
                    suitability = 0.7

            else:

                suitability = 1

            # ------------------------------------------------
            # FINAL PRODUCTION
            # ------------------------------------------------

            adjusted_kg = production_kg * suitability

            # For sugarcane: kg -> tons, for others: kg -> quintals
            if crop == "SUGARCANE":
                production_units = adjusted_kg / 1000  # kg to tons
            else:
                production_units = adjusted_kg / 100  # kg to quintals

            # ------------------------------------------------
            # MARKET PRICE
            # ------------------------------------------------

            market_price = market_data.loc[
                market_data['Crop'] == crop,
                'Price'
            ].values[0]

            # ------------------------------------------------
            # PROFIT
            # ------------------------------------------------

            profit = (
                production_units * market_price
            ) - investment

            # ------------------------------------------------
            # BEST CROP
            # ------------------------------------------------

            if profit > best_profit:

                best_profit = profit

                best_crop = crop

                best_production = production_units

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

    # Show production in tons for sugarcane, quintals for others
    if best_crop == "SUGARCANE":
        st.success(
            f"Estimated Production: {best_production:.2f} tons"
        )
        st.success(
            f"Market Price: ₹ {best_market_price} per ton"
        )
    else:
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
    
    # Show all crop comparisons
    st.subheader("📈 Crop Comparison")
    
    comparison_data = []
    
    # Show only crops that meet minimum investment and water availability
    for crop, yield_column in crop_mapping.items():
        # Check investment requirement
        min_total_investment = min_investment_per_acre * acres

        if investment >= min_total_investment:
            # Filter based on water availability
            if water == "Yes":
                # Water available - consider water-intensive crops
                if crop in water_intensive_crops:
                    # Include this crop in comparison
                    try:
                        # Get location-specific yield
                        if district != "" and state != "":
                            district_data = data[
                                (data['Dist Name'].str.lower() == district.lower()) &
                                (data['State Name'].str.lower() == state.lower())
                            ]
                            if len(district_data) > 0:
                                avg_yield = district_data[yield_column].mean()
                            else:
                                state_data = data[data['State Name'].str.lower() == state.lower()]
                                if len(state_data) > 0:
                                    avg_yield = state_data[yield_column].mean()
                                else:
                                    avg_yield = data[yield_column].mean()
                        elif state != "":
                            state_data = data[data['State Name'].str.lower() == state.lower()]
                            if len(state_data) > 0:
                                avg_yield = state_data[yield_column].mean()
                            else:
                                avg_yield = data[yield_column].mean()
                        else:
                            avg_yield = data[yield_column].mean()

                        # Calculate suitability
                        suitability = 1

                        # RICE
                        if crop == "RICE":
                            if humidity >= 70 and water == "Yes":
                                suitability = 1.2
                            elif humidity >= 60:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # WHEAT
                        elif crop == "WHEAT":
                            if 15 <= temperature <= 28:
                                suitability = 1.2
                            elif 10 <= temperature <= 32:
                                suitability = 1.0
                            else:
                                suitability = 0.6

                        # MAIZE
                        elif crop == "MAIZE":
                            if 20 <= temperature <= 35:
                                suitability = 1.2
                            elif 15 <= temperature <= 38:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # SUGARCANE
                        elif crop == "SUGARCANE":
                            if water == "Yes" and humidity >= 60:
                                suitability = 1.1
                            elif water == "Yes":
                                suitability = 0.9
                            else:
                                suitability = 0.5

                        # COTTON
                        elif crop == "COTTON":
                            if temperature >= 25 and humidity < 60:
                                suitability = 1.2
                            elif temperature >= 20:
                                suitability = 1.0
                            else:
                                suitability = 0.6

                        # GROUNDNUT
                        elif crop == "GROUNDNUT":
                            if 20 <= temperature <= 30:
                                suitability = 1.2
                            elif 18 <= temperature <= 32:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # SESAMUM
                        elif crop == "SESAMUM":
                            if humidity < 50:
                                suitability = 1.2
                            elif humidity < 60:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # SOYABEAN
                        elif crop == "SOYABEAN":
                            if humidity >= 60:
                                suitability = 1.2
                            elif humidity >= 50:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # CHICKPEA
                        elif crop == "CHICKPEA":
                            if temperature < 30:
                                suitability = 1.2
                            elif temperature < 35:
                                suitability = 1.0
                            else:
                                suitability = 0.6

                        # PIGEONPEA
                        elif crop == "PIGEONPEA":
                            if water == "No":
                                suitability = 1.2
                            else:
                                suitability = 1.0

                        # PEARL MILLET
                        elif crop == "PEARL MILLET":
                            if temperature >= 30:
                                suitability = 1.2
                            elif temperature >= 25:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # BARLEY
                        elif crop == "BARLEY":
                            if temperature <= 25:
                                suitability = 1.2
                            elif temperature <= 28:
                                suitability = 1.0
                            else:
                                suitability = 0.6

                        # SUNFLOWER
                        elif crop == "SUNFLOWER":
                            if humidity < 60:
                                suitability = 1.2
                            elif humidity < 70:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # CASTOR
                        elif crop == "CASTOR":
                            if water == "No":
                                suitability = 1.2
                            else:
                                suitability = 0.9

                        # LINSEED
                        elif crop == "LINSEED":
                            if temperature < 28:
                                suitability = 1.2
                            elif temperature < 32:
                                suitability = 1.0
                            else:
                                suitability = 0.7
                        
                        # Calculate production and profit
                        production_kg = avg_yield * hectares * suitability
                        
                        # For sugarcane: kg -> tons, for others: kg -> quintals
                        if crop == "SUGARCANE":
                            production_units = production_kg / 1000  # kg to tons
                            unit_label = "tons"
                        else:
                            production_units = production_kg / 100  # kg to quintals
                            unit_label = "quintals"
                        
                        try:
                            market_price = market_data.loc[
                                market_data['Crop'] == crop,
                                'Price'
                            ].values[0]
                        except:
                            market_price = 2000  # Default price
                        
                        profit = (production_units * market_price) - investment
                        
                        comparison_data.append({
                            'Crop': crop,
                            'Yield (Kg/ha)': f"{avg_yield:.2f}",
                            'Suitability': f"{suitability:.2f}",
                            f'Production ({unit_label})': f"{production_units:.2f}",
                            'Profit (₹)': f"{profit:.2f}"
                        })
                    except:
                        pass
            else:
                # No water - consider drought-resistant crops
                if crop in drought_resistant_crops:
                    # Include this crop in comparison
                    try:
                        # Get location-specific yield
                        if district != "" and state != "":
                            district_data = data[
                                (data['Dist Name'].str.lower() == district.lower()) &
                                (data['State Name'].str.lower() == state.lower())
                            ]
                            if len(district_data) > 0:
                                avg_yield = district_data[yield_column].mean()
                            else:
                                state_data = data[data['State Name'].str.lower() == state.lower()]
                                if len(state_data) > 0:
                                    avg_yield = state_data[yield_column].mean()
                                else:
                                    avg_yield = data[yield_column].mean()
                        elif state != "":
                            state_data = data[data['State Name'].str.lower() == state.lower()]
                            if len(state_data) > 0:
                                avg_yield = state_data[yield_column].mean()
                            else:
                                avg_yield = data[yield_column].mean()
                        else:
                            avg_yield = data[yield_column].mean()

                        # Calculate suitability
                        suitability = 1

                        # RICE
                        if crop == "RICE":
                            if humidity >= 70 and water == "Yes":
                                suitability = 1.2
                            elif humidity >= 60:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # WHEAT
                        elif crop == "WHEAT":
                            if 15 <= temperature <= 28:
                                suitability = 1.2
                            elif 10 <= temperature <= 32:
                                suitability = 1.0
                            else:
                                suitability = 0.6

                        # MAIZE
                        elif crop == "MAIZE":
                            if 20 <= temperature <= 35:
                                suitability = 1.2
                            elif 15 <= temperature <= 38:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # SUGARCANE
                        elif crop == "SUGARCANE":
                            if water == "Yes" and humidity >= 60:
                                suitability = 1.1
                            elif water == "Yes":
                                suitability = 0.9
                            else:
                                suitability = 0.5

                        # COTTON
                        elif crop == "COTTON":
                            if temperature >= 25 and humidity < 60:
                                suitability = 1.2
                            elif temperature >= 20:
                                suitability = 1.0
                            else:
                                suitability = 0.6

                        # GROUNDNUT
                        elif crop == "GROUNDNUT":
                            if 20 <= temperature <= 30:
                                suitability = 1.2
                            elif 18 <= temperature <= 32:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # SESAMUM
                        elif crop == "SESAMUM":
                            if humidity < 50:
                                suitability = 1.2
                            elif humidity < 60:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # SOYABEAN
                        elif crop == "SOYABEAN":
                            if humidity >= 60:
                                suitability = 1.2
                            elif humidity >= 50:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # CHICKPEA
                        elif crop == "CHICKPEA":
                            if temperature < 30:
                                suitability = 1.2
                            elif temperature < 35:
                                suitability = 1.0
                            else:
                                suitability = 0.6

                        # PIGEONPEA
                        elif crop == "PIGEONPEA":
                            if water == "No":
                                suitability = 1.2
                            else:
                                suitability = 1.0

                        # PEARL MILLET
                        elif crop == "PEARL MILLET":
                            if temperature >= 30:
                                suitability = 1.2
                            elif temperature >= 25:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # BARLEY
                        elif crop == "BARLEY":
                            if temperature <= 25:
                                suitability = 1.2
                            elif temperature <= 28:
                                suitability = 1.0
                            else:
                                suitability = 0.6

                        # SUNFLOWER
                        elif crop == "SUNFLOWER":
                            if humidity < 60:
                                suitability = 1.2
                            elif humidity < 70:
                                suitability = 1.0
                            else:
                                suitability = 0.7

                        # CASTOR
                        elif crop == "CASTOR":
                            if water == "No":
                                suitability = 1.2
                            else:
                                suitability = 0.9

                        # LINSEED
                        elif crop == "LINSEED":
                            if temperature < 28:
                                suitability = 1.2
                            elif temperature < 32:
                                suitability = 1.0
                            else:
                                suitability = 0.7
                        
                        # Calculate production and profit
                        production_kg = avg_yield * hectares * suitability
                        
                        # For sugarcane: kg -> tons, for others: kg -> quintals
                        if crop == "SUGARCANE":
                            production_units = production_kg / 1000  # kg to tons
                            unit_label = "tons"
                        else:
                            production_units = production_kg / 100  # kg to quintals
                            unit_label = "quintals"
                        
                        try:
                            market_price = market_data.loc[
                                market_data['Crop'] == crop,
                                'Price'
                            ].values[0]
                        except:
                            market_price = 2000  # Default price
                        
                        profit = (production_units * market_price) - investment
                        
                        comparison_data.append({
                            'Crop': crop,
                            'Yield (Kg/ha)': f"{avg_yield:.2f}",
                            'Suitability': f"{suitability:.2f}",
                            f'Production ({unit_label})': f"{production_units:.2f}",
                            'Profit (₹)': f"{profit:.2f}"
                        })
                    except:
                        pass
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('Profit (₹)', ascending=False)
    st.dataframe(comparison_df, use_container_width=True)
