from . import db #importando o objeto instaciado no init
from flask_login import UserMixin # Modelo do flask que ajuda no login de usuários. 
from sqlalchemy.sql import func
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
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary)
    name = db.Column(db.String(100))
    price = db.Column(db.Float(15))
    text = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


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
