import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt

# --------------------------
# Load & preprocess dataset
# --------------------------
@st.cache_data
def load_and_train():
    df = pd.read_csv("Pune house data.csv")

    # Extract BHK from "size"
    df["bhk"] = df["size"].str.extract("(\d+)").astype(float)

    # Convert total_sqft (handle ranges like "1200-1500")
    def convert_sqft(x):
        try:
            if "-" in str(x):
                nums = list(map(float, x.split("-")))
                return (nums[0] + nums[1]) / 2
            return float(x)
        except:
            return np.nan

    df["total_sqft"] = df["total_sqft"].apply(convert_sqft)

    # Drop rows with missing target/location
    df = df.dropna(subset=["price", "site_location"])

    # Features & target
    X = df[["total_sqft", "bhk", "bath", "balcony", "site_location"]]
    y = df["price"]

    # Impute missing numeric values
    num_cols = ["total_sqft", "bhk", "bath", "balcony"]
    imp = SimpleImputer(strategy="median")
    X[num_cols] = imp.fit_transform(X[num_cols])

    # Preprocess location & build model
    ct = ColumnTransformer(
        [("encoder", OneHotEncoder(handle_unknown="ignore"), ["site_location"])],
        remainder="passthrough"
    )
    model = Pipeline(steps=[("ct", ct), ("lr", LinearRegression())])
    model.fit(X, y)

    return df, model

# Load dataset & train model
df, model = load_and_train()

# --------------------------
# Streamlit UI
# --------------------------
st.title("🏡 Pune House Price Prediction App")
st.write("Enter details to predict house price in Pune (in Lakhs).")

# User inputs
size_sqft = st.number_input("Enter Size (sq.ft)", min_value=300, max_value=10000, value=1200)
bhk = st.number_input("Number of BHK", min_value=1, max_value=10, value=2)
bath = st.number_input("Number of Bathrooms", min_value=1, max_value=5, value=2)
balcony = st.number_input("Number of Balconies", min_value=0, max_value=5, value=1)

# Select location(s)
location = st.selectbox("Select Location for Single Prediction", sorted(df["site_location"].unique()))
compare_locations = st.multiselect("Compare with Multiple Locations (optional)", sorted(df["site_location"].unique()))

# Predict Button
if st.button("Predict Price"):
    # Single location prediction
    input_data = pd.DataFrame({
        "total_sqft": [size_sqft],
        "bhk": [bhk],
        "bath": [bath],
        "balcony": [balcony],
        "site_location": [location]
    })
    predicted_price = model.predict(input_data)[0]
    st.success(f"🏠 Estimated Price in {location}: ₹ {predicted_price:.2f} Lakhs")

    # Show distribution of actual prices in that location
    st.subheader(f"📊 Price distribution in {location}")
    loc_prices = df[df["site_location"] == location]["price"]

    fig, ax = plt.subplots()
    ax.hist(loc_prices, bins=20, color="skyblue", edgecolor="black")
    ax.axvline(predicted_price, color="red", linestyle="--", label="Predicted Price")
    ax.set_xlabel("Price (Lakhs)")
    ax.set_ylabel("Count of Houses")
    ax.legend()
    st.pyplot(fig)

    # Multiple location comparison
    if compare_locations:
        st.subheader("📌 Comparison Across Multiple Locations")
        comparison_results = {}
        for loc in compare_locations:
            input_data = pd.DataFrame({
                "total_sqft": [size_sqft],
                "bhk": [bhk],
                "bath": [bath],
                "balcony": [balcony],
                "site_location": [loc]
            })
            price = model.predict(input_data)[0]
            comparison_results[loc] = price

        # Show table
        comp_df = pd.DataFrame(list(comparison_results.items()), columns=["Location", "Predicted Price (Lakhs)"])
        st.table(comp_df)

        # Bar chart
        fig2, ax2 = plt.subplots()
        ax2.bar(comp_df["Location"], comp_df["Predicted Price (Lakhs)"], color="orange")
        ax2.set_ylabel("Predicted Price (Lakhs)")
        ax2.set_xlabel("Location")
        ax2.set_title("Predicted Price Comparison Across Locations")
        plt.xticks(rotation=45)
        st.pyplot(fig2)
