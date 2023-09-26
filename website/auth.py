from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Product
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, photos 
from flask_login import login_user, login_required, logout_user, current_user # objetos que contem as funções de validações de login e logout
from .forms import addProducts
import secrets

auth = Blueprint('auth', __name__) #Aqui ficarão as blueprints que irão renderizar os templates. 

@auth.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() # procurando user na base de dados
        if user: # caso encontre o usuário
            if check_password_hash(user.password, password): # checar se as senhas estão iguais
                flash('Login efetuado com sucesso!', category='success')
                login_user(user, remember=True) # Função que valida se o usuário está logado. 
                return redirect(url_for('views.home'))
            else:
                flash('Senha incorreta, tente novamente', category='error')
        else:
            flash('E-mail não encontrado', category='error') # Caso não encontre o usuário

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado. 
def logout():
    logout_user() # função que irá deslogar o usuário que estiver logado na sessão
    flash('Logout efeutado com sucesso', category='sucess') #Mensagem de sucesso
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST']) # Obtendo dados do formulário. 
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        cpf = request.form.get('cpf')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        SpecialSym =['$', '@', '#', '%'] # Simbolos especiais. 

        user = User.query.filter_by(email=email).first() #validando se o e-mail já existe
        user_CPF = User.query.filter_by(cpf=cpf).first() #validando se o cpf já existe
        if user:
            flash('E-mail já existente.', category='error')
        elif user_CPF:
            flash('CPF já existente', category='error')
        elif len(firstName) < 2:
            flash('O primeiro nome deve conter mais de um caractere', category='error')
        elif len(cpf) < 11:
            flash('CPF invalido', category='error')
        elif password1 != password2:
            flash('Senhas não são iguais', category='error') # Function to validate the password <<
        elif len(password1) < 7:
            flash('Senha deve conter ao menos 7 caracteres', category='error') 
        elif len(password1) > 20:
            flash('Senha não pode ter mais que 20 caracteres', category='error')
        elif not any(char.isdigit() for char in password1):
            flash('Senha deve ter ao menos um numeral', category='error')
        elif not any(char.isupper() for char in password1):
            flash('Senha deve ter ao menos uma letra maiúsculas', category='error')
        elif not any(char.islower() for char in password1):
            flash('Senha deve ter ao menos uma letra minúsculas', category='error')
        elif not any(char in SpecialSym for char in password1):
            flash('Senha deve conter um desses símbolos: $@#', category='error') # Function to validate the password >>
        else:
            new_user = User(firstName=firstName, cpf=cpf, phone=phone, email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user) #Adicionando novo usuário no banco de dados
            db.session.commit() #efetuando commit
            flash('Account created!', category='sucess') #Mensagem de sucesso
            return redirect(url_for('auth.login')) # Redirecionando usuário para a login page

    return render_template("sign_up.html", user=current_user)


@auth.route('/addProduct', methods=['GET', 'POST'])
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado.
def addProduct():
    form = addProducts(request.form)
    if request.method == 'POST':
        name = form.name.data # pegando os dados da variavel form acima
        price = form.price.data # pegando os dados da variavel form acima
        discount = form.discount.data # pegando os dados da variavel form acima
        stock = form.stock.data # pegando os dados da variavel form acima
        description = form.description.data # pegando os dados da variavel form acima
        img = photos.save(request.files.get('image'), name=secrets.token_hex(10) + ".") # Realizar o upload das imagens enviadas na pagina adicionar produtos

        new_product = Product(name=name, price=price, discount=discount, stock=stock, description=description, user_id=current_user.id, img=img)
        db.session.add(new_product)
        flash(f'O produto {name} foi adicionado com sucesso ao sistema', category='sucess')
        db.session.commit()
        
    return render_template("addProduct.html", user=current_user, form = form)


