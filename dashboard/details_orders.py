import streamlit as st
import sqlalchemy
import pandas as pd


def show_details_orders(engine):

    def load_data(query):
        return pd.read_sql_query(query, engine)

    def add_euros(val):
        return f'{val}€'

    def add_purcent(val):
        return f'{val}%'

    def add_week(val):
        return f'{val} semaines'

    st.sidebar.write("\n" * 2000)

    if st.sidebar.button('Rafraîchir les données'):
        st.experimental_rerun()

    query = "SELECT * FROM orders_details"
    data = load_data(query)
    data['serveur_id'] = data['serveur_id'].astype('str')
    data['commande_id'] = data['commande_id'].astype('str')
    data['estimation_duree'] = data['estimation_duree'].apply(add_week)
    data['prix'] = data['prix'].apply(add_euros)
    data['main_d_oeuvre'] = data['main_d_oeuvre'].apply(add_euros)
    data['prix_HT'] = data['prix_HT'].apply(add_euros)
    data['prix_TTC'] = data['prix_TTC'].apply(add_euros)
    data['TVA'] = data['TVA'].apply(add_purcent)
    st.write(data)

