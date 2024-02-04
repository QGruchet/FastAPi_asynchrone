import streamlit as st
import sqlalchemy
import pandas as pd
import matplotlib.pyplot as plt


def show_orders():

    # Connexion à la base de données SQLite
    engine = sqlalchemy.create_engine('sqlite:///./../test.db')

    def load_data(query):

        return pd.read_sql_query(query, engine)

    st.title('Mon Dashboard')

    if st.button('Rafraîchir les données'):
        st.rerun()

    if st.checkbox('Afficher les détails des commandes'):
        query = "SELECT * FROM orders INNER JOIN orders_details ON orders.order_no = orders_details.commande_id"
        data = load_data(query)
        st.write(data)
    else:
        query = "SELECT * FROM orders"
        data = load_data(query)
        st.write(data)

    if st.button('Exécuter une autre requête SQL'):
        user_query = st.text_input("Entrez votre requête SQL:")
        if user_query:
            user_data = load_data(user_query)
            st.write(user_data)
        else:
            st.warning("Veuillez entrer une requête SQL valide.")

    # Afficher les données
    st.write(data)

    # Compter le nombre de commandes avec le statut "Delivery Confirmed"
    confirmed_orders = data[data['status'] == 'Delivery Confirmed']
    confirmed_count = len(confirmed_orders)

    # Compter le nombre de commandes avec "Quote refused" ou "Delivery Refused
    refused_orders = data[data['status'].isin(['Delivery Refused', 'Quote Refused'])]
    refused_count = len(refused_orders)  # Correction : utiliser len(refused_orders) au lieu de len(confirmed_orders)

    # Compter le nombre de commandes avec d'autres statuts
    other_orders = data[data['status'] != 'Delivery Confirmed']
    other_count = len(other_orders)

    # Créer un graphique en camembert pour le nombre de commandes confirmées par rapport aux autres
    labels = ['Orders success', 'Orders in progress', 'Orders refused']
    sizes = [confirmed_count, other_count, refused_count]  # Correction : ajuster l'ordre des tailles
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Pour que le graphique soit un cercle.

    # Afficher le graphique en camembert dans Streamlit
    st.pyplot(fig)
