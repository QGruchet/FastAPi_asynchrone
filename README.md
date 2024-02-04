# TP FastApi Asynchrone

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![RabbitMQ](https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white) 
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
-------
## Objectif 📖

Intégration de sources de données textuelles

Dans ce TP, nous allons développer un système de traitement de commandes asynchrone en
utilisant FastAPI. Le système se compose de deux composants principaux : un processus
client pour passer des commandes et un processus fournisseur pour gérer les demandes de
commande, générer des devis et confirmer les commandes.
Les tâches à réaliser sont donc :

1. Implémenter des points d'accès asynchrones pour passer des commandes, vérifier des
commandes, générer des devis et confirmer des réalisations.
2. Utiliser des tâches en arrière-plan et une logique asynchrone pour gérer la
communication asynchrone entre les processus client et fournisseur.
3. Implémenter des tâches d'intervention humaine pour vérifier des commandes,
confirmer des devis et confirmer des réalisations.
4. Gérer l'état et la session des instances de processus et stocker les données de processus
dans une base de données.
5. Créer des tableaux de bord avancés pour surveiller les états des processus et analyser
l'exécution des processus.

-------

## Installation ⚙
Pour installer les librairies nécessaires au projet, lancer la commande:
```shell
pip install -r requirements.txt
```

-------

## Pré-requis 📂
Assurez-vous d'avoir lancé le serveur rabbit-mq sur votre machine. Pour cela, vous pouvez utiliser docker:
```shell
docker run -d --hostname my-rabbit --name some-rabbit -p 8080:15672 -p 5672:5672 rabbitmq:3-management
```
ou en CLI:  
```shell
systemctl start rabbitmq-server (linux)
rabbitmqctl start_app (windows)
```

-------

## Utilisation 🚀
Plusieurs étapes sont nécessaires pour lancer le projet :
1. Démarrer le serveur rabbit-mq


2. Démarrer le serveur client FastAPI  
Pour lancer le serveur client FastAPI, lancer la commande:
```shell
uvicorn main:app_client --reload
```
3. Lancer le serveur fournisseur FastAPI  
Pour lancer le serveur fournisseur FastAPI, lancer la commande:
```shell
uvicorn main:app_supplier --reload
```
4. Entrer les détails de la commande  
Les détails de la commande devront être renseignés dans un fichier `.json` à la racine du projet.


5. Rendez-vous sur le lien suivant en remplacant `{name_json_file}` par le nom du fichier `.json` contenant les détails de la commande
```shell
http://localhost:8002/envoye_commande/{name_json_file}
```

6. Vous pourrez simuler le client et fournisseur via les terminales FastAPI.

## Visualisation 📊

Pour visualiser les données depuis la racine du projet, vous pouvez lancer l'interface réalisée avec Streamlit via les commandes suivantes:
```shell
cd dashboard
streamlit run home.py
```

Puis vous rendre sur le lien suivant:
```shell
http://localhost:8501/
```
-------

## Contributeurs 👥

**Quentin Gruchet** _alias_ [QGruchet](https://github.com/QGruchet)  

**Nicolas Ferrara** _alias_ [nlsferrara](https://github.com/nlsferrara)

