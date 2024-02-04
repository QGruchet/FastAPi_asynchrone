import streamlit as st
import sqlalchemy
import pandas as pd
import matplotlib.pyplot as plt


def show_orders(engine):
    def load_data(query):

        return pd.read_sql_query(query, engine)

    st.sidebar.write("\n" * 2000)

    if st.sidebar.button('Rafraîchir les données'):
        st.experimental_rerun()

    query = "SELECT * FROM orders"
    data = load_data(query)
    st.write(data)



