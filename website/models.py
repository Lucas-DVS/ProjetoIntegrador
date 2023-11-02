from . import db #importando o objeto instaciado no init
from flask_login import UserMixin # Modelo do flask que ajuda no login de usuários. 
from sqlalchemy.sql import func
from datetime import date, time, datetime, timedelta
import json

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    cpf = db.Column(db.Integer, unique=True)
    phone = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(20))
    notes = db.relationship('Order')

class Product(db.Model):
    __seachbale__ = ['name', 'description'] # Itens que poderão ser pesquisados pelo flask_msearch
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    img = db.Column(db.String(150), nullable=False, default='image.jpg')


class JsonEcodeDict(db.TypeDecorator): # Classe para pegar uma lista com os pedidos. 
    impl = db.Text

    def set_Value(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)
        
    def get_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    userId = db.Column(db.Integer, unique=False, nullable=False)
    date = db.Column(db.DateTime(timezone = True), default=func.now())
    orders = db.Column(JsonEcodeDict)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return'<Order %r>' % self.invoice
