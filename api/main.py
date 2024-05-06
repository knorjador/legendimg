
import os
import pandas as pd
import joblib

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from livereload import Server

from pydantic import BaseModel, Field
from joselib import jwt
from passlib.context import CryptContext

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, Dict, Any
from dotenv import load_dotenv

from annotate import annotate 

load_dotenv()


""" 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    > SETUP APP && MAIN VARIABLES
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
""" 

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


""" 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    > FAKE DB 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
""" 

hashed_password = pwd_context.hash("ok")

print(hashed_password)

allowed = [
    { "name": "alex", "password": hashed_password },
    { "name": "alexis", "password": hashed_password },
    { "name": "philippe", "password": hashed_password },
    { "name": "raph", "password": hashed_password }
]


""" 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    > DEFINE SCHEMAS 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
""" 

class Dev(BaseModel):
    name: str = Field(default=None)
    password: str = Field(default=None)


class Annotate(BaseModel):
    title: str = Field(default=None)


""" 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    > HOME && AUTH  
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
""" 

@app.get("/")
def dev(request: Request):
    context = { "request": request, "message": "Dev Zone" }
    return templates.TemplateResponse("index.html", context)


@app.post("/auth")
async def login(dev: Dev, request: Request):
    data = await request.json()
    print(data)
    if "name" not in data or "password" not in data:
        return { "success" : False, "message": "Nom ou mot de passe incorrect" }
    dev = authenticate_dev(data["name"], data["password"])
    if not dev:
        return { "success" : False, "message": "Nom ou mot de passe incorrect" }

    access_token = create_access_token(dev)

    return { "success" : True, "access_token": access_token }


""" 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    > PROTECTED
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
""" 

async def get_current_dev(access_token):
    if not access_token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    dev = get_dev_from_db(access_token)
    if dev is None:
        raise HTTPException(status_code=401, detail="Non authentifié")

    return dev


@app.get("/protected/{access_token}")
async def protected(request: Request, access_token: str, dev: dict = Depends(get_current_dev)):
    print(dev)
    context = { "request": request, "dev": dev['name'] }
    return templates.TemplateResponse("protected.html", context)


@app.post("/annotate")
async def annotate_protected(request: Request):
    data = await request.json()
    print(data)
    if 'access_token' not in data or data['access_token'] is None:
        return { "fail": "Token expiré" }
    dev = get_dev_from_db(data['access_token'])
    if dev is None:
        return { "fail": "not_allowed" }
    model = data["model"]
    process = data["process"]
    hyparams = data["hyparams"]
    if model in MODELS and process in PROCESSES:
        return train(model, process, hyparams)
    else: 
        return { "fail": True, "message": "Fail in annotate" }


""" 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    > PREDICT FROM APPLICATION WEB localhost:5000
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
""" 

@app.options("/predict", include_in_schema=False)
def options_predict():
    return JSONResponse({ "message": "Options request allowed" }, status_code=200)


@app.post("/predict")
def predict(data: Annotate):
    print(data)
    # todo
    return JSONResponse({ "prediction": "WIP" }, status_code=200)
 

""" 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    > FUNCTIONS 
    ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
""" 

def authenticate_dev(name: str, password: str):
    dev = next((d for d in allowed if d["name"] == name), None)
    if not dev:
        return None
    if not pwd_context.verify(password, dev["password"]):
        return None

    return dev


def create_access_token(dev: dict):
    payload = {
        "sub": dev["name"],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return access_token


def get_dev_from_db(access_token: str):
    for dev in allowed:
        if access_token_decode(access_token).get("sub") == dev["name"]:
            return dev
    return None


def access_token_decode(access_token: str):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Jeton d'accès expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Jeton d'accès invalide")


