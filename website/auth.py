from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from .models import User, Product
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, photos 
from flask_login import login_user, login_required, logout_user, current_user # objetos que contem as funções de validações de login e logout
from .forms import addProducts
import secrets, os

auth = Blueprint('auth', __name__) #Aqui ficarão as blueprints que irão renderizar os templates. 

@auth.route('/')
def home():
    page = request.args.get('page',1, type=int)
    products = Product.query.filter(Product.stock > 0).order_by(
        Product.id.desc()).paginate(page=page, per_page= 2) # Buscar os produtos(Product) que estão na base de dados, ordena por ID e define a quantidade de produtos por pagina
    return render_template('home.html', user=current_user, products = products) # Colocar a relação de produtos(Product) encontrados na variavel products para enviar ao home.html

@auth.route('/single_page/<int:id>')
def single_page(id):
    product = Product.query.get_or_404(id)
    return render_template('single_page.html', user=current_user, product = product)

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
                return redirect(url_for('auth.home'))
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


@auth.route('/addProduct', methods=['GET', 'POST']) # URL adicionar produto
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

@auth.route('/stock', methods=['GET', 'POST']) # URL do estoque
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado.
def stock():
    products = Product.query.all() # Buscando todos os itens da tabela Product nos models e colocando dentro da variavel products
    return render_template("stock.html", user=current_user, products=products) # Passando a variavel Products com todos os itens da tabela para a pagina stock

@auth.route('/updateproduct/<int:id>', methods=['GET', 'POST']) # URL do updateproduct - Função para atualizar os produtos
def updateProduct(id):
    product = Product.query.get_or_404(id) # pegando os dados do produto no database pelo ID 
    form = addProducts(request.form)

    #Alterando o banco de dados com as informações inseridas no formulário
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.description = form.description.data
        if request.files.get('image'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.img))
                product.img = photos.save(request.files.get('image'), name=secrets.token_hex(10) + ".") # Realizar o upload das imagens enviadas na pagina adicionar produtos
            except:
                product.img = photos.save(request.files.get('image'), name=secrets.token_hex(10) + ".") # Realizar o upload das imagens enviadas na pagina adicionar produtos
        db.session.commit()
        flash(f'Seu produto foi atulizado', 'sucess')
        return redirect(url_for('auth.stock')) # Redirecionando usuário para a login page
    
    # Preenchendo os campos com os dados que foram recuparados do banco de dados. 
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.description.data = product.description

    return render_template("updateProduct.html", user=current_user, form=form, product=product)

@auth.route('/deleteProduct/<int:id>', methods=['POST']) # URL do deleteproduct - Função para deletar os produtos
def deleteProduct(id):

    product = Product.query.get_or_404(id) # pegando os dados do produto no database pelo ID
    if request.method == "POST":
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.img))
            except Exception as e:
                print(e)
            db.session.delete(product)
            db.session.commit()
            flash(f'O produto {product.name} foi deletado do seu estoque', 'sucess')
            return redirect(url_for('auth.stock')) # Redirecionando usuário para a login page
    flash(f'Não foi possível deletar o produto', 'danger')
    return redirect(url_for('auth.stock'))


