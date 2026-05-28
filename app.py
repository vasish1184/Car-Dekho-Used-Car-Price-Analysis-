import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

st.set_page_config(page_title="CarDekho Analytics Dashboard", layout="wide")
df = pd.read_csv("cardekho.csv")
df.columns = df.columns.str.lower().str.strip()

# Rename complex column
df = df.rename(columns={"mileage(km/ltr/kg)": "mileage"})

# ================= CLEAN DATA =================

# Convert text → numeric
df["mileage"] = df["mileage"].astype(str).str.extract('(\d+\.?\d*)')[0]
df["mileage"] = pd.to_numeric(df["mileage"], errors='coerce')

df["engine"] = df["engine"].astype(str).str.extract('(\d+)')[0]
df["engine"] = pd.to_numeric(df["engine"], errors='coerce')

df["max_power"] = df["max_power"].astype(str).str.extract('(\d+\.?\d*)')[0]
df["max_power"] = pd.to_numeric(df["max_power"], errors='coerce')

# ================= FILL VALUES =================

# Numerical
df["selling_price"] = df["selling_price"].fillna(df["selling_price"].mean())
df["km_driven"] = df["km_driven"].fillna(df["km_driven"].mean())
df["mileage"] = df["mileage"].fillna(df["mileage"].mean())
df["engine"] = df["engine"].fillna(df["engine"].mean())
df["max_power"] = df["max_power"].fillna(df["max_power"].mean())
df["seats"] = df["seats"].fillna(df["seats"].mode()[0])

# Categorical
df["fuel"] = df["fuel"].fillna(df["fuel"].mode()[0])
df["seller_type"] = df["seller_type"].fillna(df["seller_type"].mode()[0])
df["transmission"] = df["transmission"].fillna(df["transmission"].mode()[0])
df["owner"] = df["owner"].fillna(df["owner"].mode()[0])

# Feature
df["car_age"] = 2024 - df["year"]

# ================= SIDEBAR =================
with st.sidebar:
    selected = option_menu(
        "🚗 CarDekho Dashboard",
        ["Dataset", "Overview", "Car Analytics", "Filters", "Search"],
        icons=["table", "bar-chart", "car-front", "sliders", "search"],
        default_index=2

    )

# ================= DATASET =================
if selected == "Dataset":
    st.title("🚗 Car Dataset Explorer")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cars", len(df))
    col2.metric("Avg Price", f"₹ {df['selling_price'].mean():.2f}")
    col3.metric("Max Price", f"₹ {df['selling_price'].max():.2f}")

    st.divider()

    cols = st.multiselect("Select Columns", df.columns, default=df.columns)
    filtered_df = df[cols]
    search_col = st.selectbox("Select Column to Search", filtered_df.columns)
    column_values = filtered_df[search_col].dropna().unique()
    search_val_col = st.selectbox("Select Value", column_values)

    if search_val_col:
        filtered_df = filtered_df[
            filtered_df[search_col].astype(str).str.contains(str(search_val_col), case=False, na=False)
        ]

    search = st.text_input("🔍 Search Car")
    if search:
        filtered_df = filtered_df[
            filtered_df.astype(str).apply(
                lambda x: x.str.contains(search, case=False).any(), axis=1
            )
        ]

    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "Filtered_Cars.csv")

# ================= OVERVIEW =================
elif selected == "Overview":
    st.title("📊 Overview Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cars", len(df))
    col2.metric("Fuel Types", df["fuel"].nunique())
    col3.metric("Avg KM Driven", int(df["km_driven"].mean()))
    col4.metric("Avg Car Age", int(df["car_age"].mean()))

    st.subheader("Car Distribution (Fuel → Transmission → Owner)")

    fig = px.sunburst(
        df,
        path=["fuel", "transmission", "owner"],
        values="selling_price",
        color="owner"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 🌳 Treemap Chart
    st.subheader("Car Distribution ")

    fig = px.treemap(
        df,
        path=["fuel", "transmission", "owner"],
        values="selling_price",
        color="fuel"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Fuel Distribution
    st.subheader("Fuel Type Distribution")
    fig1 = px.pie(df, names="fuel")
    st.plotly_chart(fig1, use_container_width=True)

    # Car Age vs Price
    st.subheader("Car Age vs Price")
    fig2 = px.bar(df, x="car_age", y="selling_price", color="fuel")
    st.plotly_chart(fig2, use_container_width=True)

# ================= CAR ANALYTICS =================
elif selected == "Car Analytics":
    st.title("🚘 Car Analytics")

    # Top Cars
    st.subheader("Top 10 Expensive Cars")
    top = df.sort_values("selling_price", ascending=False).head(10)
    fig1 = px.bar(top, x="name", y="selling_price", color="name")
    st.plotly_chart(fig1, use_container_width=True)

    # KM vs Price
    st.subheader("KM Driven vs Price")
    fig2 = px.scatter(df, x="km_driven", y="selling_price", color="transmission")
    st.plotly_chart(fig2, use_container_width=True)

    # Transmission
    st.subheader("Transmission Distribution")
    fig3 = px.histogram(df,x="transmission",color="transmission")
    st.plotly_chart(fig3, use_container_width=True)

    # Fuel vs Price
    st.subheader("Fuel Type  Price")
    fig4 = px.box(df, x="fuel", y="selling_price", color="fuel")
    st.plotly_chart(fig4, use_container_width=True)

# ================= FILTERS =================
elif selected == "Filters":
    st.title("🎯 Filter Cars")

    fuel = st.selectbox("Select Fuel Type", df["fuel"].unique())
    transmission = st.selectbox("Select Transmission", df["transmission"].unique())

    price_range = st.slider(
        "Select Price Range",
        float(df["selling_price"].min()),
        float(df["selling_price"].max()),
        (float(df["selling_price"].min()), float(df["selling_price"].max()))
    )

    filtered = df[
        (df["fuel"] == fuel) &
        (df["transmission"] == transmission) &
        (df["selling_price"].between(price_range[0], price_range[1]))
    ]

    st.dataframe(filtered, use_container_width=True)

# ================= SEARCH =================
elif selected == "Search":
    st.title("🔍 Search Cars")

    car = st.text_input("Enter Car Name")

    if car:
        result = df[df["name"].str.contains(car, case=False, na=False)]

        if not result.empty:
            st.success(f"{len(result)} cars found")
            st.dataframe(result)
        else:
            st.warning("No car found")