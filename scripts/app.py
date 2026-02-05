
# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

import minmax

st.set_page_config(page_title="Starter App", page_icon="🚀", layout="wide")

# --- 

import streamlit as st
import pandas as pd
from config import LOC_INTERMEDIATE

st.set_page_config(page_title="Linked multi-selects", page_icon="🧩", layout="wide")

# Example data
df_route = pd.read_csv(LOC_INTERMEDIATE/"depot-min-max-enriched.csv")
df_depot = pd.read_csv(LOC_INTERMEDIATE/"depot_location.csv")

st.title("🧩 Learning Driver Preferences")

# depot
depot_options = sorted(df_route["depot"].dropna().unique())
depots = st.selectbox(label = "Depots", options = depot_options, index = 0)

# route
df_r = df_route[df_route["depot"] == depots] if depots else df_route.iloc[0:0] # empty if none

route_options = sorted(df_r["route"].dropna().unique())
routes = st.selectbox(label = "Routes", options = route_options, index = 0)

# date
df_d = df_r[df_r["route"] == routes] if routes else df_route.iloc[0:0]

date_options = sorted(df_d["date"].dropna().unique())
dates = st.selectbox(label = "Date", options = date_options, index = 0)

df_final_route = df_d[df_d["date"] == dates] if dates else df_route.iloc[0:0]
df_final_route_T = df_final_route.transpose()

df_min = minmax.read_route(df_final_route_T.loc["min_path"].iloc[0], df_final_route_T.loc["min_resp_path"].iloc[0])
df_min_lat_lon = df_min[["latitude","longitude"]]
# st.dataframe(df_min_lat_lon)
df_max = minmax.read_route(df_final_route_T.loc["max_path"].iloc[0], df_final_route_T.loc["max_resp_path"].iloc[0])
df_max_lat_lon = df_max[["latitude","longitude"]]

df_min_with_depot = pd.concat([df_depot, df_min_lat_lon, df_depot])
df_max_with_depot = pd.concat([df_depot, df_max_lat_lon, df_depot])

# st.markdown("### 🔎 Filtered result")
# st.dataframe(df_final_route_T, use_container_width=True)
# st.caption(f"Rows: {len(df_final_route)}")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df_min_with_depot["latitude"], y=df_min_with_depot["longitude"],
    mode="lines+markers", name="First Simulation",
    line=dict(color="rgba(255,0,0,0.7)", width=3, dash="solid"),  # hex, width, dash
    marker=dict(color="rgba(255,0,0,0.7)", size=10)
))
fig1.add_trace(go.Scatter(
    x=df_max_with_depot["latitude"], y=df_max_with_depot["longitude"],
    mode="lines+markers", name="Last Simulation",
    line=dict(color="rgba(0,255,0,0.7)", width=3, dash="solid"),  # hex, width, dash
    marker=dict(color="rgba(0,255,0,0.7)", size=10)
))

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df_min_lat_lon["latitude"], y=df_min_lat_lon["longitude"],
    mode="lines+markers", name="First Simulation",
    line=dict(color="rgba(255,0,0,0.7)", width=3, dash="solid"),  # hex, width, dash
    marker=dict(color="rgba(255,0,0,0.7)", size=10)
))

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=df_max_lat_lon["latitude"], y=df_max_lat_lon["longitude"],
    mode="lines+markers", name="Last Simulation",
    line=dict(color="rgba(0,255,0,0.7)", width=3, dash="solid"),  # hex, width, dash
    marker=dict(color="rgba(0,255,0,0.7)", size=10)
))

# fig4 = go.Figure()
# fig4.add_trace(go.Scatter(
#     x=df_max_lat_lon
# ))


c1, c2, c3 = st.columns([1,1,1])
with c1:
    st.plotly_chart(fig1, use_container_width=True)
    # st.metric("Rows - min", len(df_min_lat_lon))
    # st.metric("Rows - max", len(df_max_lat_lon))
with c2:
    st.plotly_chart(fig2, use_container_width=True)
with c3:
    st.plotly_chart(fig3, use_container_width=True)

# c4, c5, c6 = st.columns([1,1,1])
# with c4:
#     st.plotly_chart(fig4, use_container_width=True)

# --- Sidebar ---
# st.sidebar.header("Controls")
# n = st.sidebar.slider("Number of points", 100, 5000, 1000, step=100)
# seed = st.sidebar.number_input("Random seed", value=42, step=1)
# show_table = st.sidebar.checkbox("Show data table", value=True)

# --- Main ---
# st.title("🚀 Streamlit Quick Starter")
# st.caption(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# @st.cache_data(show_spinner=False)
# def make_data(n: int, seed: int):
#     rng = np.random.default_rng(seed)
#     df = pd.DataFrame({
#         "x": rng.normal(size=n),
#         "y": rng.normal(size=n),
#         "group": rng.integers(1, 4, size=n).astype(str),
#     })
#     return df

# df = make_data(n, seed)

# c1, c2 = st.columns([1,2])
# with c1:
#     st.metric("Rows", len(df))
#     st.metric("Groups", df["group"].nunique())
# with c2:
#     st.scatter_chart(df, x="x", y="y", color="group", use_container_width=True)

# if show_table:
#     st.dataframe(df.head(20), use_container_width=True)

# with st.expander("Submit feedback"):
#     with st.form("feedback"):
#         email = st.text_input("Email (optional)", "")
#         msg = st.text_area("Your message")
#         submitted = st.form_submit_button("Send")
#         if submitted:
#             st.success("Thanks! Feedback captured.")
#             st.json({"email": email, "message": msg})
