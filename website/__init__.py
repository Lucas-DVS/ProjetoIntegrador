from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

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

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' #Para onde o flask irá direcionar o usuário se o mesmo não estiver logado e ocorrer uma requisão para logar.
    login_manager.init_app(app) # Informando o loginManager o aplicativo que iremos utilizar

    @login_manager.user_loader #função que diz ao Flask qual usuário estamos procurando e referenciar o mesmo pelo ID. 
    def load_user(id):
        return User.query.get(int(id)) #Função que irá procurar por uma primarykey e checar se é igual a informação que passamos. 

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

