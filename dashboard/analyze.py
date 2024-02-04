import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px


def show_analyze(engine):
    st.sidebar.write("\n" * 2000)

    if st.sidebar.button('Rafraîchir les données'):
        st.experimental_rerun()

    def load_data(query):
        return pd.read_sql_query(query, engine)

    query = "SELECT * FROM orders"
    data = load_data(query)

    query = "SELECT * FROM orders_details"
    data_details = load_data(query)

    # Fonction pour tracer les statistiques des commandes par statut
    def plot_order_status(data):
        status_counts = data['status'].value_counts()
        st.bar_chart(status_counts)

    def plot_order_status_purcent(data):
        # Compter le nombre de commandes avec différents statuts
        confirmed_count = len(data[data['status'] == 'Delivery Confirmed'])
        refused_count = len(data[data['status'].isin(['Delivery Refused'])])
        quote_refused_count = len(data[data['status'].isin(['Quote Refused'])])

        # Créer un graphique en camembert avec Plotly
        labels = ['Confirmed Orders', 'Refused Orders', 'Quote Refused']
        sizes = [confirmed_count, refused_count, quote_refused_count]

        fig = px.pie(names=labels, values=sizes, color_discrete_sequence=px.colors.sequential.RdBu)

        fig.update_traces(textinfo='percent+label', pull=[0.1, 0, 0])  # Léger décalage pour les commandes confirmées

        # Afficher le graphique dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

    # Fonction pour afficher les délais de la commande
    def plot_quote_confirmation_time(data):
        data['quoteConfirmation_at'] = pd.to_datetime(data['quoteConfirmation_at'], errors='coerce')
        data['updated_at'] = pd.to_datetime(data['updated_at'], errors='coerce')

        endOrder = data[data['orderEnd'] == 1]
        endOrder['processing_time'] = (endOrder['updated_at'] - endOrder['quoteConfirmation_at']).dt.total_seconds()
        avg_time = endOrder['processing_time'].mean().round(3)
        avg_time_str = f"{avg_time}s"
        st.metric(label="Temps moyen de la commande (en secondes)", value=avg_time_str)

    st.header('Nombre de commandes ouvertes et fermées')
    open_count = len(data[data['orderEnd'] == 0])
    closed_count = len(data[data['orderEnd'] == 1])
    st.write(f"Nombre de commandes ouvertes : {open_count}")
    st.write(f"Nombre de commandes fermées : {closed_count}")

    with st.expander('Voir sous forme de graphique'):
        # Créer un graphique à barres avec Plotly Express
        fig = px.bar(x=['Open Orders', 'Closed Orders'], y=[open_count, closed_count],
                     labels={'x': 'Statut de la commande', 'y': 'Nombre de commandes'},
                     title='Nombre de commandes ouvertes et fermées')

        # Améliorer le layout
        fig.update_layout(xaxis_title="Statut de la commande",
                          yaxis_title="Nombre de commandes",
                          showlegend=False)

        # Afficher le graphique dans Streamlit
        st.plotly_chart(fig, use_container_width=True)


    st.header('Statut des Commandes')
    col1, col2 = st.columns(2, gap="large")
    with col1:
        plot_order_status(data)
    with col2:
        plot_order_status_purcent(data)

    st.header('Temps moyen du traitement de la commande')
    plot_quote_confirmation_time(data)

    def time_difference(data1, data2, label, flag):
        dif = {}
        data1 = pd.to_datetime(data1, errors='coerce')
        data2 = pd.to_datetime(data2, errors='coerce')
        dif['dif_time'] = (data2 - data1).dt.total_seconds()
        avg_time = dif['dif_time'].mean().round(3)
        avg_time_str = f"{avg_time}s"
        if flag:
            st.metric(label=label, value=avg_time_str)
        return avg_time

    with st.expander("Voir les détails"):
        label = 'Temps moyen entre la récéption et le traitement de la commande'
        time_difference(data['created_at'], data['infoChecked_at'], label, True)

        label = 'Temps moyen entre le traitement et la génération du devis'
        time_difference(data['infoChecked_at'], data['quoteCreated_at'], label, True)

        label = 'Temps moyen entre la génération du devis et sa vérification par le service'
        time_difference(data['quoteCreated_at'], data['quoteCheck_at'], label, True)

        label = 'Temps moyen entre la verfication du devis et sa confirmation par le client'
        time_difference(data['quoteCheck_at'], data['quoteConfirmation_at'], label, True)

        label = 'Temps moyen entre la confirmation du devis et la livraison'
        time_difference(data['quoteConfirmation_at'], data['deliverySend_at'], label, True)

        label = 'Temps moyen entre la livraison et la confirmation de la livraison'
        time_difference(data['deliverySend_at'], data['deliveryConfirmed_at'], label, True)

    with st.expander('Voir sous forme de graphiques'):
        times_data = []

        # Définition des étapes
        etapes = [
            ('Réception et traitement', 'created_at', 'infoChecked_at'),
            ('Traitement et génération du devis', 'infoChecked_at', 'quoteCreated_at'),
            ('Génération du devis et vérification', 'quoteCreated_at', 'quoteCheck_at'),
            ('Vérification du devis et confirmation', 'quoteCheck_at', 'quoteConfirmation_at'),
            ('Confirmation du devis et livraison', 'quoteConfirmation_at', 'deliverySend_at'),
            ('Livraison et confirmation de livraison', 'deliverySend_at', 'deliveryConfirmed_at'),
        ]

        # Calculer les temps moyens pour chaque étape
        for label, start, end in etapes:
            avg_time = time_difference(data[start], data[end], label, False)
            times_data.append([label, avg_time])

        # Créer un DataFrame avec les résultats
        df_times = pd.DataFrame(times_data, columns=['Étape', 'Temps moyen (heures)'])

        # Créer un graphique à barres avec Plotly Express
        fig = px.bar(df_times, y='Étape', x='Temps moyen (heures)', orientation='h', color='Étape',
                     labels={'Temps moyen (heures)': 'Temps moyen (heures)', 'Étape': 'Étape'},
                     title='Temps moyen entre différentes étapes du processus de commande')

        # Rendre le graphique plus lisible, surtout pour les petites barres
        fig.update_layout(xaxis_title="Temps moyen (heures)",
                          yaxis_title="",
                          bargap=0.2,  # Ajuster l'espacement entre les barres
                          )

        # Ajouter des annotations de texte sur chaque barre pour afficher la valeur
        fig.update_traces(texttemplate='%{x:.3f}', textposition='outside')

        # Utiliser st.plotly_chart pour afficher le graphique dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

    st.header('Prix moyen des commandes')
    avg_price = data_details['prix_TTC'].mean().round(3)
    avg_price_str = f"{avg_price}€"
    st.metric(label="Prix moyen des commandes (en euros)", value=avg_price_str)

    def avg_price(data, label):
        avg_price = data.mean().round(3)
        avg_price_str = f"{avg_price}€"
        st.metric(label=label, value=avg_price_str)

    with st.expander('Voir les détails'):
        avg_price(data_details['TVA'], 'TVA moyenne')
        avg_price(data_details['main_d_oeuvre'], 'Prix main d\'oeuvre moyenne')
        avg_price(data_details['prix'], 'Prix de base moyen')
        avg_price(data_details['prix_HT'], 'Prix Hors Taxes moyen')

    with st.expander('Voir sous forme de graphiques'):
        # Calculer les moyennes pour les colonnes spécifiées et les stocker dans un nouveau DataFrame
        avg_prices = pd.DataFrame({
            'Catégorie': ['Prix main d\'œuvre', 'Prix de base', 'Prix HT', 'Prix TTC'],
            'Moyenne (€)': [
                data_details['main_d_oeuvre'].mean().round(3),
                data_details['prix'].mean().round(3),
                data_details['prix_HT'].mean().round(3),
                data_details['prix_TTC'].mean().round(3)
            ]
        })

        # Créer un graphique à barres interactif avec Plotly Express
        fig = px.bar(avg_prices, x='Catégorie', y='Moyenne (€)',
                     title='Prix moyen des commandes par catégorie',
                     labels={'Moyenne (€)': 'Moyenne en euros'},
                     color='Catégorie',
                     )

        # Améliorer le layout
        fig.update_layout(xaxis_title='Catégorie',
                          yaxis_title='Moyenne en euros',
                          showlegend=False)

        # Afficher le graphique dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

    st.header('Durée estimée moyenne des travaux')
    avg_time = data_details['estimation_duree'].mean().round(3)
    avg_time_str = f"{avg_time} semaines"
    st.metric(label="Durée estimée moyenne des travaux", value=avg_time_str)

    with st.expander('Voir sous forme de graphique'):

        # Création d'un boxplot pour visualiser la distribution des semaines estimées
        fig = px.box(data_details, y='estimation_duree',
                     title='Distribution du Nombre de Semaines Estimées',
                     labels={'semaines_estimees': 'Nombre de Semaines Estimées'},
                     color_discrete_sequence=['indianred'])  # Personnaliser la couleur

        # Afficher le graphique dans Streamlit
        st.plotly_chart(fig, use_container_width=True)
