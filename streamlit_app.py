import streamlit as st

conn = st.experimental_connection("snowpark")
df = conn.query("select * from pet_owners")
st.dataframe(df)
