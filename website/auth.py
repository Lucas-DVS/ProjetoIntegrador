from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user # objetos que contem as funções de validações de login e logout

auth = Blueprint('auth', __name__) #Aqui ficarão as blueprints que irão renderizar os templates. 

@auth.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() # procurando user na base de dados
        if user: # caso encontre o usuário
            if check_password_hash(user.password, password): # checar se as senhas estão iguais
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) # Função que valida se o usuário está logado. 
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('E-mail does not exist.', category='error') # Caso não encontre o usuário

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado. 
def logout():
    logout_user() # função que irá deslogar o usuário que estiver logado na sessão
    return redirect(url_for('auth.logout'))

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
            flash('E-mail already exist.', category='error')
        elif user_CPF:
            flash('CPF already exist', category='error')
        elif len(firstName) < 2:
            flash('First name must be more than one caracters', category='error')
        elif len(cpf) < 11:
            flash('CPF invalid', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error') # Function to validate the password <<
        elif len(password1) < 7:
            flash('Password should be at least 7 characters', category='error') 
        elif len(password1) > 20:
            flash('Password should be not be greater than 20', category='error')
        elif not any(char.isdigit() for char in password1):
            flash('Password should have at least one numeral', category='error')
        elif not any(char.isupper() for char in password1):
            flash('Password should have at least one uppercase letter', category='error')
        elif not any(char.islower() for char in password1):
            flash('Password should have at least one lowercase letter', category='error')
        elif not any(char in SpecialSym for char in password1):
            flash('Password should have at least one of the symbols $@#', category='error') # Function to validate the password >>
        else:
            new_user = User(firstName=firstName, cpf=cpf, phone=phone, email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user) #Adicionando novo usuário no banco de dados
            db.session.commit() #efetuando commit
            login_user(user, remember=True)
            flash('Account created!', category='sucess') #Mensagem de sucesso
            return redirect(url_for('views.home')) # Redirecionando usuário para a homepage


    return render_template("sign_up.html", user=current_user)


