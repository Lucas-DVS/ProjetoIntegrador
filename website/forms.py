from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, validators, FloatField, PasswordField, SubmitField

class addProducts(Form): #formulario para adicionar produtos
    
    name = StringField('Nome', [validators.DataRequired()])
    price = FloatField('Preço', [validators.DataRequired()])
    discount = IntegerField('Desconto', default=0)
    stock = IntegerField('Estoque', [validators.DataRequired()])
    description = TextAreaField('Descrição', [validators.DataRequired()])

    image = FileField('Imagem', validators=[FileAllowed(['jpg','png','gif','jpeg'])])

class attUser(Form): #formulario para atualizar usuário
    
    firstName = StringField('Nome', [validators.DataRequired()])
    cpf = FloatField('CPF', [validators.DataRequired()])
    phone = StringField('Telefone', [validators.DataRequired()])
    email = StringField('email', [validators.DataRequired()])
    password = StringField('senha', [validators.DataRequired()])


class attpass(Form): #formulario para atualizar usuário
    
    passcurrent = PasswordField('Senha atual', [validators.DataRequired()])
    password1 = PasswordField('Nova senha', [validators.DataRequired()])
    password2 = PasswordField('Repita a nova senha', [validators.DataRequired()])



