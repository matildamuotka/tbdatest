from datetime import datetime,date,time,timezone,timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.express as px
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

df = pd.DataFrame([
    dict(Task="Operating, on/off", Start=start_datetime, Finish=end_datetime),
])

fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task")
fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
st.plotly_chart(fig, use_container_width=True)

MACHINE_IN_OPERATION = pd.read_sql_query("select id_var, date, to_timestamp(@date/1000) as dateH, value from variable_log_float where id_var = 575 limit 200", con=engine)

dates = MACHINE_IN_OPERATION["dateh"]
values = MACHINE_IN_OPERATION["value"]

new_dates = []
new_values = []
running = []

for i in range(len(values)):
    if (values[i] == 255.0): # If the value is 255, we put a 0 a the same time exactly to have a square chart
        new_values.append(0)
        running.append(0)
        new_dates.append(dates[i])
        new_values.append(1)
        running.append(1)
    elif (values[i] == 0.0): # If the value is 0, we put a 1 a the same time exactly to have a square chart
        new_values.append(1)
        running.append(1)
        new_dates.append(dates[i])
        new_values.append(0)
        running.append(0)
    new_dates.append(dates[i])

st.plotly_chart(running, use_container_width=True)
