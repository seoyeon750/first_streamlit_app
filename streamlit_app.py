import streamlit as st
from snwoflake.snowpark.session import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import *

ss = st.session_state
session = ""
if not ss:
  ss.pressed_first_button = False

#with st.container():
#  if 
