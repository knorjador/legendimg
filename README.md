
Après avoir démarré l'environnement : 

### Installer les dépendances 

```bash

pip install -r requirements.txt

```


### Lancer Flask 

> Dans le dossier web 

```bash

# db 
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# lancer flask
flask run 

```

goto: http://localhost:5000


### Lancer FastApi 

> Dans le dossier api 

Renommer .env.example en .env

```bash

# generate secret key && paste it in .env
openssl rand -hex 32

# lancer fastapi
uvicorn main:app --reload --reload-dir static


```

goto: http://localhost:8000


### Lancer Mlflow 

> Dans le dossier api 

```bash

mlflow ui --port 9000

```

goto: http://localhost:9000


### Figer les dépendances

pip freeze > requirements.txt