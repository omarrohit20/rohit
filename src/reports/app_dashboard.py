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
st.title('chartink-0')

col1, col2 = st.columns(2)
with col1:
    rb.render(st, 'morning-volume-breakout-buy', 'morning-volume-breakout-buy', color='G')
with col2:
    rb.render(st, 'morning-volume-breakout-sell', 'morning-volume-breakout-sell', color='R')







