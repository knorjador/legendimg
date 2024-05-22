
import os
import flask
import requests
import time
import sklearn
import pickle
import pandas as pd
import numpy as np

from flask import render_template, flash, redirect, url_for, request, Response, jsonify
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from datetime import datetime, timezone
from urllib.parse import urlsplit

from app import app, Config, db
from app.models import Member, History


@app.before_request
def before_request():
    db.session.query(History).delete()
    db.session.commit()
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
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
            return redirect(url_for('upload'))
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
            return redirect(url_for('upload'))
    return flask.render_template('register.html', app_name=Config.APP_NAME)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/upload', methods=['OPTIONS', 'GET', 'POST'])
def upload():
    if request.method == 'OPTIONS':
        return jsonify({ 'message': 'Options request allowed' })
    if request.method == 'POST':
        data = request.json
        # print(data) 
        response = requests.post('http://localhost:8000/annotate', json=data)
        if response.status_code == 200:
            result = response.json()
            caption = result['caption'] 
            trad = result['trad']
            sentiment = result['sentiment']
            history = History(
                caption=caption,
                trad=trad,
                sentiment=sentiment['trad'],
                img=data['url'], 
                member_id=current_user.id
            )
            db.session.add(history)
            db.session.commit()
            return jsonify({ 'caption': caption, 'trad': trad, 'sentiment': sentiment })
        else:
            print('nope')
    if current_user.is_authenticated:
        return render_template('upload.html', app_name=Config.APP_NAME, name=current_user.name)
    return redirect(url_for('index'))


@app.route('/history')
def history():
    if current_user.is_authenticated:
        query = (
            db.session.query(History)
            .filter_by(member_id=current_user.id)
        )
        images = query.all()
        images.reverse()
        print()
        print()
        # print(' > IMAGES')
        # print(images)
        print()
        print()
        return render_template('history.html', app_name=Config.APP_NAME, name=current_user.name, images=images)
    return redirect(url_for('index'))


