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

st.markdown('''
    This is a GANTT chart informing about periods of *automatic/manual* operations''')
    
    if st.button('Generate Gantt Chart'): 
        fig = px.timeline(
                        df, 
                        x_start="Start", 
                        x_end="End", 
                        y="Mode",
                        color="Mode",
                        hover_name="Mode"
                        )

        fig.update_yaxes(autorange="reversed")          #if not specified as 'reversed', the tasks will be listed from bottom up       
        
        fig.update_layout(
                        title='Project Plan Gantt Chart',
                        hoverlabel_bgcolor='#DAEEED',   #Change the hover tooltip background color to a universal light blue color. If not specified, the background color will vary by team or completion pct, depending on what view the user chooses
                        bargap=0.2,
                        height=600,              
                        xaxis_title="", 
                        yaxis_title="",                   
                        title_x=0.5,                    #Make title centered                     
                        xaxis=dict(
                                tickfont_size=15,
                                tickangle = 270,
                                rangeslider_visible=True,
                                side ="top",            #Place the tick labels on the top of the chart
                                showgrid = True,
                                zeroline = True,
                                showline = True,
                                showticklabels = True,
                                tickformat="%x\n",      #Display the tick labels in certain format. To learn more about different formats, visit: https://github.com/d3/d3-format/blob/main/README.md#locale_format
                                )
                    )
        
        fig.update_xaxes(tickangle=0, tickfont=dict(family='Rockwell', color='blue', size=15))

        st.plotly_chart(fig, use_container_width=True)  #Display the plotly chart in Streamlit
