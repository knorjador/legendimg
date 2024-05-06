
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    APP_NAME = "LegendImg"
    APP_SPEECH = "Annoter facilement vos images"
    SECRET_KEY = "you_will_never_guess_even_with_brute_force"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")