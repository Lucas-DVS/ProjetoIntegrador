from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, validators, FloatField

class addProducts(Form): #formulario para adicionar produtos
    
    name = StringField('Nome', [validators.DataRequired()])
    price = FloatField('Preço', [validators.DataRequired()])
    discount = IntegerField('Desconto', default=0)
    stock = IntegerField('Estoque', [validators.DataRequired()])
    description = TextAreaField('Descrição', [validators.DataRequired()])

    image = FileField('Imagem', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'])])