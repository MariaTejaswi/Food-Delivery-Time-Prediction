
import pickle
import pandas as pd
import streamlit as st
from datetime import datetime

# Load the trained model and expected columns
with open("delivery_model.pkl", "rb") as file:
    model = pickle.load(file)

with open("model_columns.pkl", "rb") as file:
    model_columns = pickle.load(file)

from pymongo import MongoClient

# Use the same working Atlas URI from your notebook
MONGO_URI = "mongodb+srv://yt:MooF7nuqTwvwc67q@project.w8jrnwg.mongodb.net/project"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
db = client["FoodDeliveryDB"]
history_collection = db["prediction_history"]

st.set_page_config(
    page_title="Food Delivery Time Predictor",
    page_icon="🍔",
    layout="centered"
)

st.title("Food Delivery Time Prediction")
st.write("Enter your order details to estimate the delivery time.")

# User inputs
distance = st.number_input(
    "Delivery distance (km)", min_value=0.1,
    max_value=100.0, value=7.5, step=0.5
)

preparation = st.number_input(
    "Preparation time (minutes)", min_value=0,
    max_value=180, value=15
)

experience = st.number_input(
    "Courier experience (years)", min_value=0,
    max_value=50, value=2
)

weather = st.selectbox(
    "Weather", ["Sunny", "Rainy", "Cloudy", "Windy", "Foggy", "Stormy"]
)

traffic = st.selectbox(
    "Traffic level", ["Low", "Medium", "High"]
)

time_of_day = st.selectbox(
    "Time of day", ["Morning", "Afternoon", "Evening", "Night"]
)

vehicle = st.selectbox(
    "Vehicle type", ["Motorcycle", "Bicycle", "Car", "Scooter"]
)


if st.button("Predict Delivery Time"):
    order = pd.DataFrame([{
        "Distance_km": distance,
        "Preparation_Time_min": preparation,
        "Courier_Experience_yrs": experience,
        "Weather": weather,
        "Traffic_Level": traffic,
        "Time_of_Day": time_of_day,
        "Vehicle_Type": vehicle
    }])

    # Prepare input for the model
    order = pd.get_dummies(order, dtype=int)
    order = order.reindex(columns=model_columns, fill_value=0)

    # 1. Predict first
    prediction = float(model.predict(order)[0])

    # 2. Save the prediction to MongoDB
    record = {
        "Distance_km": float(distance),
        "Preparation_Time_min": int(preparation),
        "Courier_Experience_yrs": int(experience),
        "Weather": weather,
        "Traffic_Level": traffic,
        "Time_of_Day": time_of_day,
        "Vehicle_Type": vehicle,
        "Predicted_Delivery_Time_min": prediction,
        "Created_At": datetime.now()
    }

    try:
        history_collection.insert_one(record)
        st.success(
            f"Estimated delivery time: {prediction:.2f} minutes"
        )
        st.caption("Prediction saved to MongoDB successfully!")

    except Exception as e:
        st.error(f"Could not save prediction to MongoDB: {e}")
        st.info(f"Your predicted delivery time is {prediction:.2f} minutes.")
