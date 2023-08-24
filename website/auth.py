from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__) #Aqui ficarão as blueprints que irão renderizar os templates. 

@auth.route('/login', methods=['GET', 'POST']) 
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return"<p>logout</p>"

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

        if len(firstName) < 2:
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
            flash('Account created!', category='sucess')

    return render_template("sign_up.html")


