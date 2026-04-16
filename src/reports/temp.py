# Create a streamlit app that shows the mongodb data
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import rbase as rb

# Run the autorefresh approximately every 30000 milliseconds (30 seconds)
st_autorefresh(interval=30000, key="data_refresher")

# setting the screen size
st.set_page_config(layout="wide",
                   page_title="Dashboard",
                   initial_sidebar_state="expanded",)

# main title
st.title('chartink-1')


col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[

            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, '', color='LG')
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[

        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, '', color='LG')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[

            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, '', color='LG')
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[

        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, '', color='LG')











