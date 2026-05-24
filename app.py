import streamlit as st
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.title("Crop Prediction System")

data = pd.read_csv("ICRISAT-District Level Data.csv")

data = data.dropna()

st.write(data.head())

# Example columns
X = data[['Area', 'Production']]

y = data['Crop']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier()

model.fit(X_train, y_train)

area = st.number_input("Enter Area")

production = st.number_input("Enter Production")

if st.button("Predict Crop"):

    prediction = model.predict([[area, production]])

    st.success(f"Predicted Crop: {prediction[0]}")
