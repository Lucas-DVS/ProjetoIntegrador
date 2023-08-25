from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy() #instanciação do SQLAchemy
DB_NAME = "database.db" #localização do data base

def create_app(): #Fábricas Básicas flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'QWERTY'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # Informando a localização do database
    db.init_app(app) #Iniciando o database

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Order, Product

    with app.app_context(): #https://stackoverflow.com/questions/73968584/flask-sqlalchemy-db-create-all-got-an-unexpected-keyword-argument-app
        db.create_all

    return app

