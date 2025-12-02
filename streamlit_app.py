import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from google import genai

# ==========================
# GEMINI CLIENT SETUP
# ==========================
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(prompt: str) -> str:
    try:
        resp = gemini_client.models.generate_content(
            model="gemini-2.5-flash",  # choose a supported Gemini model
            contents=prompt
        )
        return resp.text
    except Exception as e:
        return f"Gemini Error: {e}"

# ==========================
# STREAMLIT PAGE SETUP
# ==========================
st.set_page_config(page_title="Mini Project 2", layout="wide")

# ==========================
# LOGIN PAGE
# ==========================
st.title("🔐 Mini Project 2 — Secure Dashboard")
password = st.text_input("Enter password:", type="password")

if password != "abc123":  # Change to your desired password
    st.stop()

st.success("Logged in successfully!")

# ==========================
# DATABASE CONNECTION
# ==========================
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="dpg-d4ltqca4d50c73e9pu8g-a.oregon-postgres.render.com",
        database="mini_project_2_ga5e",
        user="mini_project_2_ga5e_user",
        password="n1JnTZoEbDnU982DU5aVpWwQl2EJXlF4",
        port=5432,
        sslmode="require",
        cursor_factory=RealDictCursor
    )

conn = get_connection()
cursor = conn.cursor()

# ==========================
# PREDEFINED SQL QUERIES (PostgreSQL compatible)
# ==========================
PREDEFINED = {
    "ex1: All Regions":
        "SELECT * FROM Region LIMIT 20;",

    "ex2: Customer Total Sales":
        """
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

    "ex3: Top 10 Products by Sales":
        """
        SELECT 
            P.ProductName,
            SUM(OD.QuantityOrdered) AS TotalUnits
        FROM OrderDetail OD
        JOIN Product P ON OD.ProductID = P.ProductID
        GROUP BY P.ProductName
        ORDER BY TotalUnits DESC
        LIMIT 10;
        """,

    "ex4: Customers per Country":
        """
        SELECT 
            Ctry.Country,
            COUNT(*) AS NumCustomers
        FROM Customer Cust
        JOIN Country Ctry ON Cust.CountryID = Ctry.CountryID
        GROUP BY Ctry.Country
        ORDER BY NumCustomers DESC;
        """,

    "ex5: Orders per Day":
        """
        SELECT 
            OrderDate,
            COUNT(*) AS NumOrders
        FROM OrderDetail
        GROUP BY OrderDate
        ORDER BY OrderDate;
        """,

    "ex6: Total Revenue":
        """
        SELECT 
            SUM(P.ProductUnitPrice * OD.QuantityOrdered)::numeric(12,2) AS Revenue
        FROM OrderDetail OD
        JOIN Product P ON OD.ProductID = P.ProductID;
        """,

    "ex7: Product Categories Total Units":
        """
        SELECT 
            PC.ProductCategory,
            SUM(OD.QuantityOrdered) AS UnitsSold
        FROM OrderDetail OD
        JOIN Product P ON OD.ProductID = P.ProductID
        JOIN ProductCategory PC ON P.ProductCategoryID = PC.ProductCategoryID
        GROUP BY PC.ProductCategory
        ORDER BY UnitsSold DESC;
        """,

    "ex8: Last 20 Orders":
        "SELECT * FROM OrderDetail ORDER BY OrderID DESC LIMIT 20;",

    "ex9: Customers with > 20 Orders":
        """
        SELECT 
            C.FirstName || ' ' || C.LastName AS Name,
            COUNT(*) AS NumOrders
        FROM OrderDetail OD
        JOIN Customer C ON OD.CustomerID = C.CustomerID
        GROUP BY Name
        HAVING COUNT(*) > 20
        ORDER BY NumOrders DESC;
        """,

    "ex10: Average Product Price per Category":
        """
        SELECT 
            PC.ProductCategory,
            AVG(P.ProductUnitPrice)::numeric(10,2) AS AvgPrice
        FROM Product P
        JOIN ProductCategory PC ON P.ProductCategoryID = PC.ProductCategoryID
        GROUP BY PC.ProductCategory;
        """,

    "ex11: Top Customers by Revenue":
        """
        SELECT
            C.FirstName || ' ' || C.LastName AS Name,
            SUM(P.ProductUnitPrice * OD.QuantityOrdered)::numeric(12,2) AS Revenue
        FROM OrderDetail OD
        JOIN Customer C ON OD.CustomerID = C.CustomerID
        JOIN Product P ON OD.ProductID = P.ProductID
        GROUP BY Name
        ORDER BY Revenue DESC
        LIMIT 10;
        """
}

# ==========================
# TWO COLUMN LAYOUT
# ==========================
left, right = st.columns(2)

# ===================================
# LEFT COLUMN → SQL QUERY EXECUTION
# ===================================
with left:
    st.header("📊 SQL Query Runner")

    query_type = st.selectbox("Choose a type:", ["Predefined Query", "Custom Query"])

    if query_type == "Predefined Query":
        selected = st.selectbox("Choose query:", list(PREDEFINED.keys()))
        sql = PREDEFINED[selected]
        st.code(sql, language="sql")
    else:
        sql = st.text_area("Write your SQL query here:")

    if st.button("Run Query"):
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows)
            st.dataframe(df)
        except Exception as e:
            st.error(f"SQL Error: {e}")

# ===================================
# RIGHT COLUMN → GEMINI SQL HELPER
# ===================================
with right:
    st.header("🤖 Gemini SQL Helper")

    user_prompt = st.text_area("Ask Gemini anything about SQL:")

    if st.button("Ask Gemini"):
        answer = ask_gemini(user_prompt)
        st.write(answer)
