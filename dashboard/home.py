import streamlit as st
import orders


# Fonction pour la page d'accueil
def page_home():
    st.title("Page d'Accueil")
    st.write("Bienvenue sur la page d'accueil !")


# Fonction pour la page de commandes
def page_orders():
    st.title("Page de Commandes")
    st.write("Ici, vous pouvez gérer les commandes.")
    orders.show_orders()


# Fonction pour la page de détails des commandes
def page_order_details():
    st.title("Détails des Commandes")
    st.write("Cette page affiche les détails des commandes.")


# Barre latérale pour la navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Choisir une page :", ("Accueil", "Commandes", "Détails des Commandes"))

# Gestion de la navigation
if choice == "Accueil":
    page_home()
elif choice == "Commandes":
    page_orders()
elif choice == "Détails des Commandes":
    page_order_details()
