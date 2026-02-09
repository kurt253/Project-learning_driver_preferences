
# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

import minmax

st.set_page_config(page_title="Starter App", page_icon="🚀", layout="wide")

# --- 

import streamlit as st
import pandas as pd
from config import LOC_INTERMEDIATE

st.set_page_config(page_title="Learning Driver Preferences", page_icon="🧩", layout="wide")

# Example data
df_route = pd.read_csv(LOC_INTERMEDIATE/"depot-min-max-enriched.csv")
df_depot = pd.read_csv(LOC_INTERMEDIATE/"depot_location.csv")

st.title("🧩 Learning Driver Preferences")

# global overview
# ###############
# depot
glb_depot_options = sorted(df_route["depot"].dropna().unique())
glb_depots = st.selectbox(label = "Depots", options = glb_depot_options, index = 0, key="glb_depot")

# date
glb_date_df = df_route[df_route["depot"] == glb_depots] if glb_depots else glb_depots.iloc[0:0]

glb_date_options = sorted(glb_date_df["date"].dropna().unique())
glb_dates = st.selectbox(label = "Dates", options = glb_date_options, index = 0, key="glb_date")

glb_first_fig = go.Figure()
glb_final_fig = go.Figure()

routes_df = df_route[(df_route["depot"] == glb_depots) & (df_route["date"] == glb_dates)]
routes_lst = routes_df.route.tolist()
for route in routes_lst:
    route_df = routes_df[(routes_df["route"] == route)][["min_path","min_resp_path","max_path","max_resp_path"]]
    min_route_df = minmax.read_route(route_df["min_path"].iloc[0], route_df["min_resp_path"].iloc[0])
    max_route_df = minmax.read_route(route_df["max_path"].iloc[0], route_df["max_resp_path"].iloc[0])
    # route_clr = tuple(np.random.rand(3))
    route_clr = tuple(np.random.randint(0, 256, size=3))
    glb_first_fig.add_trace(go.Scatter(
        x=min_route_df["latitude"], y=min_route_df["longitude"],
        mode="lines+markers", name=route,
        # line=dict(color=route_clr, dash="solid"),
        line=dict(color=f"rgb({route_clr[0]},{route_clr[1]},{route_clr[2]})",dash="solid"),
        # marker=dict(color=route_clr, size=10)
        marker=dict(color=f"rgb({route_clr[0]},{route_clr[1]},{route_clr[2]})", size=1)
    ))
    glb_final_fig.add_trace(go.Scatter(
        x=max_route_df["latitude"], y=max_route_df["longitude"],
        mode="lines+markers", name=route,
        line=dict(color=f"rgb({route_clr[0]},{route_clr[1]},{route_clr[2]})",dash="solid"),
        marker=dict(color=f"rgb({route_clr[0]},{route_clr[1]},{route_clr[2]})", size=1)
    ))
depot_clr = 'blue'
glb_first_fig.add_trace(go.Scatter(
    x=df_depot["latitude"], y=df_depot["longitude"],
    marker=dict(color=depot_clr, size=10)
))
glb_final_fig.add_trace(go.Scatter(
    x=df_depot["latitude"], y=df_depot["longitude"],
    marker=dict(color=depot_clr, size=10)
))

c4, c5 = st.columns([1,1])
with c4:
    st.plotly_chart(glb_first_fig, use_container_width=True)
    # st.metric("Rows - min", len(df_min_lat_lon))
    # st.metric("Rows - max", len(df_max_lat_lon))
with c5:
    st.plotly_chart(glb_final_fig, use_container_width=True)











# detail of first and last iteration of one specific route on one specific date
# #############################################################################
# depot
depot_options = sorted(df_route["depot"].dropna().unique())
depots = st.selectbox(label = "Depots", options = depot_options, index = 0, key="dtl_depot")

# route
df_r = df_route[df_route["depot"] == depots] if depots else df_route.iloc[0:0] # empty if none

route_options = sorted(df_r["route"].dropna().unique())
routes = st.selectbox(label = "Routes", options = route_options, index = 0, key="dtl_route")

# date
df_d = df_r[df_r["route"] == routes] if routes else df_route.iloc[0:0]

date_options = sorted(df_d["date"].dropna().unique())
dates = st.selectbox(label = "Date", options = date_options, index = 0, key="dtl_date")

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


c1, c2, c3 = st.columns([1,1,1])
with c1:
    st.plotly_chart(fig1, use_container_width=True)
    # st.metric("Rows - min", len(df_min_lat_lon))
    # st.metric("Rows - max", len(df_max_lat_lon))
with c2:
    st.plotly_chart(fig2, use_container_width=True)
with c3:
    st.plotly_chart(fig3, use_container_width=True)


