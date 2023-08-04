import streamlit as st
import pandas as pd
from PIL import Image
import datetime
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

        datawarehouse_option = st.selectbox(
            "Select Virtual warehouse", datawarehouse_list
        )

        set_warehouse = session.sql(
            f"""USE WAREHOUSE {datawarehouse_option} ;"""
        ).collect()

with st.container():
    if session != "":
        st.title("Snowflake Health Check")
        image = Image.open("banner.jpg")
        st.image(
            image, caption = "Community App Build By Data Superhero - Divyansh Saxena"
        )
        st.header(
            "Get better understanding of Snowflake's Resource Optimization and Performance capabilities on :red[Streamlit]"
        )

        date_range = st.date_input("Select the Starting Date for Report Generation")
        currentdate = datetime.datetime.today().strftime("%Y-%m-%d")
        if str(date_range) > currentdate:
            st.error("The date selected is greated than current date!", icon="🚨")

        tab1, tab2, tab3 = st.tabs(
            ["Warehouse Performance", "Users Profile", "Billing Metrics"]
        )

        with tab1:
            sql_warehouse_performances = session.sql(
                """
                SELECT
                    DATE_TRUNC('HOUR', START_TIME) AS QUERY_START_HOUR
                    , WAREHOUSE_NAME
                    , COUNT(*) AS NUM_QUERIES
                FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
                WHERE START_TIME >= '""" + str(date_range) + """' AND WAREHOUSE_NAME IS NOT NULL
                GROUP BY 1, 2
                ORDER BY 1 DESC, 2
                """
            ).to_pandas()
            st.subheader(
                "Average number of queries run on an hourly basis - :red[Understand Query Activity]"
            )
            sql_warehouse_performances_pivot = sql_warehouse_performances.pivot_table(
                values = "NUM_QUERIES", index = "QUERY_START_HOUR", columns = "WAREHOUSE_NAME"
            )
            st.area_chart(data = sql_warehouse_performances_pivot)

            st.subheader(
                "Queries by # of Times Executed and Execution Time - :red[Opportunity to materialize the result set]"
            )
            sq_exec_time_q_count = session.sql(
                """
                SELECT
                    QUERY_TEXT
                    , CCOUNT(*) AS NUMBER_OF_QUERIES
                    , SUM(TOTAL_ELAPSED_TIME)/1000 AS EXECUTION_SECONDS
                FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY Q
                WHERE 1=1
                    AND (QUERY_TEXT NOT LIKE 'SHOW%' AND QUERY_TEXT NOT LIKE 'USE%')
                    AND TO_DATE(Q.START_TIME) > '""" + str(date_range) + """'
                    AND TOTAL_ELAPSED_TIME > 0 -- only get queries that actually used compute
                    GROUP BY 1
                    HAVING COUNT(*) >= 10 -- configurable/minimal threashold
                    ORDER BY 2 DESC
                """
            )
            st.dateframe(sq_exec_time_q_count)

            st.subheader(
                "Longest Running Queries - :red[opportunity to optimize with clustering of upsize the warehouse]"
            )
            # sq_long_running_quries = session.sql().to_pandas()
