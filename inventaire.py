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
    if etat == "running":
        stats_rep = session.get(
            f"{DOCKER}/containers/{c['Id']}/stats?stream=false",
            timeout=5
        )
        stats_rep.raise_for_status()
        stats = stats_rep.json()
        cpu = stats["cpu_stats"]
        avant = stats["precpu_stats"]
        delta_cpu = (
            cpu["cpu_usage"]["total_usage"]
            - avant["cpu_usage"]["total_usage"]
        )
        delta_systeme = (
            cpu["system_cpu_usage"]
            - avant.get("system_cpu_usage", 0)
        )
        if delta_systeme:
            pourcent = (
                delta_cpu / delta_systeme
                * cpu["online_cpus"]
                * 100
            )
        else:
            pourcent = 0.0
        memoire_mo = stats["memory_stats"]["usage"] / 1024 / 1024
        print(f"CPU : {pourcent:.2f}%")
        print(f"RAM : {memoire_mo:.2f} Mo")
    else:
        print("Conteneur arrêté")