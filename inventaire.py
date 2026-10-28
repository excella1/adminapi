import os
import sys

import requests

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
JETON = os.environ["NETBOX_TOKEN"]        # pas de valeur par défaut pour un secret #

session = requests.Session()
reponse = session.get(DOCKER + "/containers/json?all=true", timeout=5)
reponse.raise_for_status()
conteneurs = reponse.json()

for c in conteneurs:



    nom = c["Names"][0].lstrip("/")
    image = c["Image"] 
    etat = c["State"]
    print (nom, image, etat)