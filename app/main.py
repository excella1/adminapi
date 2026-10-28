import json
import os
import requests
from fastapi import FastAPI
from fastapi import HTTPException

app = FastAPI()

DOCKER_API_URL = os.environ.get(
    "DOCKER_API_URL",
    "http://127.0.0.1:2375"
)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/containers")
def containers():
    filtre = {"label": ["adminapi.managed=true"]}
    reponse = requests.get(
        DOCKER_API_URL + "/containers/json",
        params={"all": "true", "filters": json.dumps(filtre)},
        timeout=5
    )
    reponse.raise_for_status()
    resultat = []
    for c in reponse.json():
        infos = {
            "id": c["Id"],
            "name": c["Names"][0].lstrip("/"),
            "image": c["Image"],
            "state": c["State"]
        }
    
        resultat.append(infos)
    return resultat

@app.get("/containers/{identifiant}")
def lire(identifiant: str):
    reponse = requests.get(
        DOCKER_API_URL + f"/containers/{identifiant}/json",
        timeout=5
    )
    if reponse.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Conteneur inconnu"
        )
    reponse.raise_for_status()
    detail = reponse.json()
    labels = detail["Config"]["Labels"]
    if labels is None or labels.get("adminapi.managed") != "true":
        raise HTTPException(
            status_code=404,
            detail="Conteneur non géré"
        )
    return {
        "id": detail["Id"],
        "name": detail["Name"].lstrip("/"),
        "image": detail["Config"]["Image"],
        "state": detail["State"]["Status"]
    }