import json

import os

import requests



from typing import Literal



from fastapi import Depends, FastAPI, HTTPException, Response

from pydantic import BaseModel, Field



from app.securite import exiger_token, exiger_admin



# Il n'existe pas de transaction entre Docker et NetBox.

# Si Docker réussit mais que NetBox échoue, raise_for_status() remonte l'erreur.

# L'incohérence reste visible afin de pouvoir être détectée et corrigée manuellement.

from app.netbox_client import creer_vm, changer_statut, supprimer_vm



app = FastAPI()





class Conteneur(BaseModel):

    id: str

    name: str

    image: str

    state: str





class ConteneurACreer(BaseModel):

    name: str = Field(pattern=r"^[a-z][a-z0-9-]{1,30}$")

    image: Literal[

        "nginx:alpine",

        "redis:alpine",

        "httpd:alpine"

    ]





DOCKER_API_URL = os.environ.get(

    "DOCKER_API_URL",

    "http://127.0.0.1:2375"

)





@app.get("/health", summary="Vérifie que l'API répond")

def sante():

    return {"status": "ok"}





@app.get(

    "/containers",

    summary="Liste les conteneurs gérés",

    response_model=list[Conteneur],

    dependencies=[Depends(exiger_token)]

)

def lister():

    filtre = {"label": ["adminapi.managed=true"]}



    reponse = requests.get(

        DOCKER_API_URL + "/containers/json",

        params={

            "all": "true",

            "filters": json.dumps(filtre)

        },

        timeout=5

    )



    reponse.raise_for_status()



    return [

        {

            "id": c["Id"],

            "name": c["Names"][0].lstrip("/"),

            "image": c["Image"],

            "state": c["State"]

        }

        for c in reponse.json()

    ]





@app.get(

    "/containers/{identifiant}",

    summary="Détail d'un conteneur géré",

    response_model=Conteneur,

    dependencies=[Depends(exiger_token)]

)

def lire(identifiant: str):

    reponse = requests.get(

        f"{DOCKER_API_URL}/containers/{identifiant}/json",

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





@app.post(

    "/containers",

    summary="Crée et démarre un conteneur",

    status_code=201,

    response_model=Conteneur,

    dependencies=[Depends(exiger_admin)]

)

def creer(demande: ConteneurACreer):

    corps = {

        "Image": demande.image,

        "Labels": {

            "adminapi.managed": "true"

        }

    }



    reponse = requests.post(

        f"{DOCKER_API_URL}/containers/create",

        params={"name": demande.name},

        json=corps,

        timeout=10

    )



    if reponse.status_code == 409:

        raise HTTPException(

            status_code=409,

            detail="Nom de conteneur déjà utilisé"

        )



    reponse.raise_for_status()



    identifiant = reponse.json()["Id"]



    reponse = requests.post(

        f"{DOCKER_API_URL}/containers/{identifiant}/start",

        timeout=10

    )



    reponse.raise_for_status()



    creer_vm(demande.name)



    return lire(identifiant)





@app.post(

    "/containers/{identifiant}/stop",

    summary="Arrête un conteneur géré",

    response_model=Conteneur,

    dependencies=[Depends(exiger_admin)]

)

def arreter(identifiant: str):

    actuel = lire(identifiant)



    if actuel["state"] == "exited":

        raise HTTPException(

            status_code=409,

            detail="Conteneur déjà arrêté"

        )



    reponse = requests.post(

        f"{DOCKER_API_URL}/containers/{identifiant}/stop",

        params={"t": 2},

        timeout=30

    )



    if reponse.status_code == 304:

        raise HTTPException(

            status_code=409,

            detail="Conteneur déjà arrêté"

        )



    reponse.raise_for_status()



    changer_statut(actuel["name"], "offline")



    return lire(identifiant)





@app.post(

    "/containers/{identifiant}/start",

    summary="Démarre un conteneur géré",

    response_model=Conteneur,

    dependencies=[Depends(exiger_admin)]

)

def demarrer(identifiant: str):

    actuel = lire(identifiant)



    if actuel["state"] == "running":

        raise HTTPException(

            status_code=409,

            detail="Conteneur déjà démarré"

        )



    reponse = requests.post(

        f"{DOCKER_API_URL}/containers/{identifiant}/start",

        timeout=30

    )



    if reponse.status_code == 304:

        raise HTTPException(

            status_code=409,

            detail="Conteneur déjà démarré"

        )



    reponse.raise_for_status()



    changer_statut(actuel["name"], "active")



    return lire(identifiant)





@app.delete(

    "/containers/{identifiant}",

    summary="Supprime un conteneur",

    status_code=204,

    dependencies=[Depends(exiger_admin)]

)

def supprimer(identifiant: str):

    actuel = lire(identifiant)



    reponse = requests.delete(

        f"{DOCKER_API_URL}/containers/{identifiant}",

        params={"force": "true"},

        timeout=30

    )



    reponse.raise_for_status()



    supprimer_vm(actuel["name"])



    return Response(status_code=204)