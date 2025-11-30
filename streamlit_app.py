import streamlit as st
import psycopg2
import pandas as pd

# --------------------------
# Password protection
# --------------------------
PASSWORD = "project2demo"

st.title("Mini Project 2 Dashboard 🔥")

user_pass = st.text_input("Enter password:", type="password")
if user_pass != PASSWORD:
    st.warning("Incorrect password!")
    st.stop()

# --------------------------
# Connect to Render DB
# --------------------------
conn = psycopg2.connect(
    host="dpg-d4ltqca4d50c73e9pu8g-a.oregon-postgres.render.com",
    database="mini_project_2_ga5e",
    user="mini_project_2_ga5e_user",
    password="n1JnTZoEbDnU982DU5aVpWwQl2EJXlF4",
    port=5432,
    sslmode="require"
)

# --------------------------
# Two-column layout
# --------------------------
col1, col2 = st.columns(2)

with col1:
    st.header("Run SQL Queries")
    query = st.text_area("Enter your SQL query here")
    if st.button("Run Query"):
        try:
            df = pd.read_sql_query(query, conn)
            st.dataframe(df)
        except Exception as e:
            st.error(e)

with col2:
    st.header("Info")
    st.write("Use this panel to explain tables, queries, or instructions to the grader.")
