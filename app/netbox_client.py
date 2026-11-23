import os
import requests
NETBOX_URL = os.environ.get(
    "NETBOX_URL",
    "http://127.0.0.1:8080"
)
NETBOX_TOKEN = os.environ["NETBOX_TOKEN"]
session = requests.Session()
session.headers["Authorization"] = f"Bearer {NETBOX_TOKEN}"
session.headers["Accept"] = "application/json"
N = f"{NETBOX_URL}/api/virtualization"
def id_cluster():
    reponse = session.get(
        f"{N}/clusters/",
        params={"name": "docker-local"},
        timeout=10
    )
    reponse.raise_for_status()
    return reponse.json()["results"][0]["id"]
def creer_vm(nom):
    reponse = session.post(
        f"{N}/virtual-machines/",
        json={
            "name": nom,
            "cluster": id_cluster(),
            "status": "active"
        },
        timeout=10
    )
    reponse.raise_for_status()
def trouver_vm(nom):
    reponse = session.get(
        f"{N}/virtual-machines/",
        params={
            "name": nom,
            "cluster_id": id_cluster()
        },
        timeout=10
    )
    reponse.raise_for_status()
    resultats = reponse.json()["results"]
    if not resultats:
        return None
    return resultats[0]["id"]
def changer_statut(nom, statut):
    id_vm = trouver_vm(nom)
    if id_vm is None:
        return
    reponse = session.patch(
        f"{N}/virtual-machines/{id_vm}/",
        json={"status": statut},
        timeout=10
    )
    reponse.raise_for_status()
def supprimer_vm(nom):
    id_vm = trouver_vm(nom)
    if id_vm is None:
        return
    reponse = session.delete(
        f"{N}/virtual-machines/{id_vm}/",
        timeout=10
    )
    reponse.raise_for_status()