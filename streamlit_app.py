import streamlit as st
import pandas as pd
from snowflake.snowpark.session import Session

st.set_page_config(
    page_title="Snowflake Health Check App",
    page_icon="❄️",
    # layout = 'wide',
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": "https://developers.snowflake.com",
        "About": "The Application is built by Snowflake Data Superhero - [Divyansh Saxena](https://www.linkedin.com/in/divyanshsaxena/) . The source code for this application can be accessed on [GitHub](https://github.com/divyanshsaxena11/sfguide-snowpark-streamlit-snowflake-healthcheck) ",
    },
)

ss = st.session_state
session = ""
if not ss:
    ss.pressed_first_button = False

with st.sidebar:
    SF_ACCOUNT = st.text_input(
        "Enter Your Snowflake Account [<account_details>.snowflakecomputing.com] :"
    )
    SF_USR = st.text_input("Snowflake USER ( s2oy2on ):")
    SF_PWD = st.text_input("Snowflake password:", type="password")
    conn = {"ACCOUNT": SF_ACCOUNT, "USER": SF_USR, "PASSWORD": SF_PWD}

    if st.button("Connect") or ss.pressed_first_button:
        session = Session.builder.configs(conn).create()
        ss.pressed_first_button = True
        st.success("Success!", icon="✅")

    if session != "":
        datawarehouse_list = session.sql("show warehouses;").collect()
        datawarehouse_list = pd.DataFrame(datawarehouse_list)
        datawarehouse_list = datawarehouse_list["name"]

        datawarehouse_option = st_selectbox(
            "Select Virtual warehouse", datawarehouse_list
        )

        set_warehouse = session.sql(
            f"""USE WAREHOUSE {datawarehouse_option} ;"""
        ).collect()
