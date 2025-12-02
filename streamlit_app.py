import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import google.generativeai as genai

# ---------------------------------------------------------
# Configure Gemini
# ---------------------------------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")


def ask_gemini(prompt):
    """Send a prompt to Gemini and return text response."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"


# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------
st.title("🔍 SQL Query Explorer + 🤖 Gemini AI Assistant")
st.write("Interact with your PostgreSQL database and ask Gemini for help writing queries!")


# ---------------------------------------------------------
# Database Connection
# ---------------------------------------------------------
def get_connection():
    try:
        conn = psycopg2.connect(
            host="dpg-d4ltqca4d50c73e9pu8g-a.oregon-postgres.render.com",
            database="mini_project_2_ga5e",
            user="mini_project_2_ga5e_user",
            password=os.getenv("DB_PASSWORD"),
            sslmode="require",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


# ---------------------------------------------------------
# Predefined Queries (PostgreSQL Compatible)
# ---------------------------------------------------------
predefined_queries = {
    "ex1: List all customers": """
        SELECT * FROM Customer LIMIT 20;
    """,

    "ex2: Customer total sales": """
        SELECT 
            C.FirstName || ' ' || C.LastName AS Name,
            SUM(P.ProductUnitPrice * OD.QuantityOrdered)::numeric(10,2) AS Total
        FROM OrderDetail OD
        JOIN Customer C ON OD.CustomerID = C.CustomerID
        JOIN Product P ON OD.ProductID = P.ProductID
        GROUP BY Name
        ORDER BY Total DESC
        LIMIT 10;
    """,

    "ex3: Top 5 products by sales": """
        SELECT 
            P.ProductName,
            SUM(OD.QuantityOrdered * P.ProductUnitPrice)::numeric(10,2) AS Revenue
        FROM OrderDetail OD
        JOIN Product P ON OD.ProductID = P.ProductID
        GROUP BY P.ProductName
        ORDER BY Revenue DESC
        LIMIT 5;
    """,

    "ex4: Orders with customer names": """
        SELECT 
            O.OrderID,
            C.FirstName || ' ' || C.LastName AS Customer,
            O.OrderDate
        FROM Orders O
        JOIN Customer C ON O.CustomerID = C.CustomerID
        ORDER BY O.OrderDate DESC
        LIMIT 20;
    """,

    "ex5: Average product price": """
        SELECT AVG(ProductUnitPrice)::numeric(10,2) AS AvgPrice FROM Product;
    """,

    "ex6: Total number of orders": """
        SELECT COUNT(*) AS TotalOrders FROM Orders;
    """,

    "ex7: Products in stock": """
        SELECT ProductName, UnitsInStock FROM Product ORDER BY UnitsInStock DESC;
    """,

    "ex8: Customers from each city": """
        SELECT City, COUNT(*) AS Count FROM Customer GROUP BY City ORDER BY Count DESC;
    """,

    "ex9: Most ordered product": """
        SELECT 
            P.ProductName,
            SUM(OD.QuantityOrdered) AS TotalQty
        FROM OrderDetail OD
        JOIN Product P ON OD.ProductID = P.ProductID
        GROUP BY P.ProductName
        ORDER BY TotalQty DESC
        LIMIT 1;
    """,

    "ex10: Monthly sales summary": """
        SELECT 
            DATE_TRUNC('month', O.OrderDate)::date AS Month,
            SUM(OD.QuantityOrdered * P.ProductUnitPrice)::numeric(12,2) AS Revenue
        FROM Orders O
        JOIN OrderDetail OD ON O.OrderID = OD.OrderID
        JOIN Product P ON OD.ProductID = P.ProductID
        GROUP BY Month
        ORDER BY Month;
    """,

    "ex11: Customers who spent over 1000": """
        SELECT 
            C.FirstName || ' ' || C.LastName AS Name,
            SUM(OD.QuantityOrdered * P.ProductUnitPrice)::numeric(12,2) AS Total
        FROM OrderDetail OD
        JOIN Customer C ON OD.CustomerID = C.CustomerID
        JOIN Product P ON OD.ProductID = P.ProductID
        GROUP BY Name
        HAVING SUM(OD.QuantityOrdered * P.ProductUnitPrice) > 1000
        ORDER BY Total DESC;
    """
}


# ---------------------------------------------------------
# SELECT Query Option
# ---------------------------------------------------------
st.subheader("📌 Choose a Predefined Query")
query_choice = st.selectbox("Select a query:", list(predefined_queries.keys()))

selected_query = predefined_queries[query_choice]
st.code(selected_query, language="sql")

if st.button("Run Predefined Query"):
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql(selected_query, conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Query Error: {e}")
        conn.close()


# ---------------------------------------------------------
# Custom Query Option
# ---------------------------------------------------------
st.subheader("📝 Custom SQL Query")
custom_query = st.text_area("Write your own SQL query here:")

if st.button("Run Custom Query"):
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql(custom_query, conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Query Error: {e}")
        conn.close()


# ---------------------------------------------------------
# Gemini Helper
# ---------------------------------------------------------
st.subheader("🤖 Ask Gemini to Generate SQL")

user_prompt = st.text_input("Ask Gemini to create a SQL query for your database:")

if st.button("Ask Gemini"):
    final_prompt = f"""
    You are an SQL expert. The database has tables:
    Customer, Orders, OrderDetail, Product.

    Write a clean, PostgreSQL-compatible SQL query.

    User request:
    {user_prompt}
    """

    gemini_answer = ask_gemini(final_prompt)
    st.markdown("### 📌 Gemini Response")
    st.write(gemini_answer)
