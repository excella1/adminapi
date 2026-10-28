import os
import sys

import json
from datetime import datetime

import requests

DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
JETON = os.environ["NETBOX_TOKEN"]        # pas de valeur par défaut pour un secret #

session = requests.Session()
reponse = session.get(DOCKER + "/containers/json?all=true", timeout=5)
reponse.raise_for_status()
conteneurs = reponse.json()

inventaire = []
for c in conteneurs:



    nom = c["Names"][0].lstrip("/")
    image = c["Image"] 
    etat = c["State"]

    infos = {
        "nom": nom,
        "image": image,
        "etat": etat,
        "cpu": None,
        "memoire_mo": None
    }

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

        infos["cpu"] = pourcent
        infos["memoire_mo"] = memoire_mo
    else:
        print("Conteneur arrêté")
    inventaire.append(infos)
reponse_netbox = session.get(
    NETBOX + "/api/status/",
    headers={"Authorization": "Bearer " + JETON},
    timeout=5
)
reponse_netbox.raise_for_status()
infos_netbox = reponse_netbox.json()
url = NETBOX + "/api/core/object-types/?limit=50"
types_objets = []
while url:
    reponse = session.get(
        url,
        headers={"Authorization": "Bearer " + JETON},
        timeout=5
    )
    reponse.raise_for_status()
    page = reponse.json()
    types_objets.extend(page["results"])
    total_annonce = page["count"]
    url = page["next"]
resultat = {
    "date": datetime.now().isoformat(),
    "netbox_version": infos_netbox["netbox-version"],
    "netbox_types_objets": len(types_objets),
    "conteneurs": inventaire
}
with open("inventaire.json", "w") as f:
    json.dump(resultat, f, indent=2)
nb_running = sum(1 for c in inventaire if c["etat"] == "running")
print(f"Nombre total de conteneurs : {len(inventaire)}")
print(f"version NetBox : {infos_netbox['netbox-version']}")
print(f"Types d'objets annoncés par NetBox : {total_annonce}")
print(f"Types d'objets récupérés : {len(types_objets)}")

print(f"Nombre de conteneurs démarrés : {nb_running}")