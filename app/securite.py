import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

TOKEN_ADMIN = os.environ["API_TOKEN_ADMIN"]
TOKEN_LECTEUR = os.environ["API_TOKEN_READER"]
porteur = HTTPBearer(auto_error=False)
def exiger_token(
    identifiants: HTTPAuthorizationCredentials | None = Depends(porteur)
):
    if identifiants is None:
        raise HTTPException(
            status_code=401,
            detail="Authentification requise"
        )

    if identifiants.credentials == TOKEN_ADMIN:
        return "admin"

    if identifiants.credentials == TOKEN_LECTEUR:
        return "lecteur"
    
    raise HTTPException(
        status_code=401,
        detail="Token invalide"
    )
def exiger_admin(role: str = Depends(exiger_token)):
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Accès interdit"
        )
    return role