import streamlit as st
import orders
import details_orders
import analyze
import sqlalchemy

# Connexion à la base de données SQLite
engine = sqlalchemy.create_engine('sqlite:///./../test.db')


# Fonction pour la page d'accueil
def page_home():
    st.title("Page d'Accueil")
    st.write("Bienvenue sur la page d'accueil !")


# Fonction pour la page de commandes
def page_orders():
    st.title("Page de Commandes")
    st.write("Ici, vous pouvez gérer les commandes.")
    orders.show_orders(engine)


# Fonction pour la page de détails des commandes
def page_order_details():
    st.title("Détails des Commandes")
    st.write("Cette page affiche les détails des commandes.")
    details_orders.show_details_orders(engine)


# Fonction pour la page d'analyse
def page_analyze():
    st.title("Analyse des Commandes")
    st.write("Cette page affiche l'analyse des commandes.")
    analyze.show_analyze(engine)


# Barre latérale pour la navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Choisir une page :", ("Accueil", "Commandes", "Détails des Commandes", "Analyse"))

# Gestion de la navigation
if choice == "Accueil":
    page_home()
elif choice == "Commandes":
    page_orders()
elif choice == "Détails des Commandes":
    page_order_details()
elif choice == "Analyse":
    page_analyze()
