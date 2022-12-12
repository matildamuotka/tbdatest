from datetime import datetime,date,time,timezone,timedelta
import streamlit as st
import pandas as pd
import numpy as np
import ploty.graph_objects as go
from matplotlib import pyplot as plt
from sqlalchemy import create_engine #to access a sql database

engine = create_engine('postgresql://lectura:ncorrea#2022@138.100.82.178:5432/2207')

# Recuperation of all operating modes
OPmodes = pd.read_sql_query("select id_var, value from variable_log_float where id_var=622 limit 1000", con=engine)
list1=OPmodes["value"]
x= np.array(list1)
op_modes = np.unique(x).astype(str)[:-1]
def query(x):
    return pd.read_sql_query("".join(["select id_var, date, to_timestamp(@date/1000) as dateH, value from variable_log_float where id_var=622 and value=",x]),con=engine)
modes = [query(x) for x in op_modes]

st.title("Operating periods")

# Chose time window

start_date = st.date_input("Start date",date(2020,12,28),date(2020,12,28),date(2022,2,23))
start_time = st.time_input("Start time",time(6,00,00))
end_date = st.date_input("End date",date(2020,12,28),date(2020,12,28),date(2022,2,23))
end_time = st.time_input("End time",time(22,00,00))

start_datetime = datetime.combine(start_date,start_time,tzinfo=timezone(timedelta(seconds=3600)))
end_datetime = datetime.combine(end_date,end_time,tzinfo=timezone(timedelta(seconds=3600)))

#Number of minutes in the interval
time_interval = end_datetime - start_datetime
time_interval_min = time_interval.seconds/60


# operations collected and operations per minute
counters_collected = []
counters_per_min = []


for mode in modes:
    op_collected = mode[mode['dateh'] > start_datetime][mode['dateh'] < end_datetime]['dateh'].size
    counters_collected.append(op_collected)
    counters_per_min.append(op_collected/time_interval_min)

st.text("Operating periods for chosen time window")
#st.bar_chart(counters_collected)

# Create the data for the Gantt chart
tasks = {'Task 1': {'start': '2022-12-12', 'finish': '2022-12-14'},
         'Task 2': {'start': '2022-12-12', 'finish': '2022-12-16'},
         'Task 3': {'start': '2022-12-17', 'finish': '2022-12-19'}}

# Create the Gantt chart
fig = go.Figure(go.Gantt(
    tasks=tasks,
    show_colorbar=True,
    bar_width=0.5,
    showgrid_x=True,
    showgrid_y=True))

# Display the chart
st.plotly_chart(fig)
