import streamlit as st
from snwoflake.snowpark.session import Session

ss = st.session_state
session = ""
if not ss:
  ss.pressed_first_button = False

#with st.container():
#  if 
