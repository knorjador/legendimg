
import os
import flask
import time
import sklearn
import pickle
import pandas as pd
import numpy as np

from flask import render_template, flash, redirect, url_for, request, Response
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from datetime import datetime, timezone
from urllib.parse import urlsplit

from app import app, Config, db
from app.models import Member


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('predict'))
    return flask.render_template('index.html', app_name=Config.APP_NAME, speech=Config.APP_SPEECH)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        member = db.session.scalar(sa.select(Member).where(Member.name == name))
        time.sleep(2)
        if name == "" or member is None or not member.check_password(password):
            return redirect(url_for('login', e='1'))
        else: 
            login_user(member)
            return redirect(url_for('dashboard'))
    return flask.render_template('login.html', app_name=Config.APP_NAME)
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        time.sleep(2)
        if name == "" or password == "":
            return redirect(url_for('register', e='0'))
        member = db.session.scalar(sa.select(Member).where(Member.name == name))
        if member is None:
            member = Member(name=name)
            member.set_password(password)
            db.session.add(member)
            db.session.commit()
            return redirect(url_for('dashboard'))
    return flask.render_template('register.html', app_name=Config.APP_NAME)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        return render_template('dashboard.html', app_name=Config.APP_NAME, name=current_user.name)
    return redirect(url_for('index'))


@app.route('/predict')
def predict():
    if current_user.is_authenticated:
        return render_template('predict.html', app_name=Config.APP_NAME, name=current_user.name)
    return redirect(url_for('index'))



