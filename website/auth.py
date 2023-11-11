from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from .models import User, Product, Order
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, photos, search
from flask_login import login_user, login_required, logout_user, current_user # objetos que contem as funções de validações de login e logout
from .forms import addProducts, attUser, attpass
import secrets, os
import stripe


auth = Blueprint('auth', __name__) #Aqui ficarão as blueprints que irão renderizar os templates. 

chave_publicavel = 'pk_test_51O9dwrLWAB2Es0IYTsEktdoO1rGSlKbduA073KdZlFpPX1AkTp6Xb8G4n1lS7a0xDya9cj9vuzPgECal80ivrcXB00XuURtg8M'

stripe.api_key = 'sk_test_51O9dwrLWAB2Es0IYvrEMRkV3CX449tbmRpo3E2l4Cz3gkhgoa0TNHbvWMud3KKhppBZgrYRpIwmsoZQN6277OelG00hUywv6Zu'

@auth.route('/payment', methods=['POST'])
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado.  
def payment():

    total = request.form.get('total')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description='Cupcake gourmet',
        amount=amount,
        currency='brl',
    )

    orders = Order.query.filter_by(userId=current_user.id, total = total).order_by(Order.id.desc()).first() # Aqui ele sempre vai pegar o ultimo total"identificação do pedido" CONTINUAR
    orders.status = 'Pago'
    db.session.commit()
    return redirect(url_for('auth.obrigado'))

@auth.route('/obrigado')
def obrigado():
    return render_template("thank.html", user=current_user)


@auth.route('/') #Home
def home():
    page = request.args.get('page',1, type=int)
    products = Product.query.filter(Product.stock > 0).order_by(
        Product.id.desc()).paginate(page=page, per_page= 8) # Buscar os produtos(Product) que estão na base de dados, ordena por ID e define a quantidade de produtos por pagina
    return render_template('home.html', user=current_user, products = products) # Colocar a relação de produtos(Product) encontrados na variavel products para enviar ao home.html


@auth.route('/result') # Pesquisa
def result():
    searchword = request.args.get('q')
    products = Product.query.msearch(searchword, fields=['name', 'description'], limit=15)
    return render_template('result.html', user=current_user, products = products)

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
    clearcart()
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
            flash('Conta Criada!', category='sucess') #Mensagem de sucesso
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

def MargerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict1
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@auth.route('/addcart', methods=['POST']) # adicionando itens no carrinho
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        product = Product.query.filter_by(id=product_id).first()
        
        if product_id and quantity and request.method == "POST":
            DicItems = {product_id:{'name': product.name, 'price':product.price, 'discount': product.discount, 'quantity': quantity, 'image': product.img}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                else:
                    session['Shoppingcart'] = MargerDicts(session['Shoppingcart'], DicItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DicItems
                return redirect(request.referrer)
            
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)
    
@auth.route('/carts') # Acessando o carrinho
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart'])<= 0:
        return redirect(url_for('auth.home'))
    subtotal = 0
    total = 0
    for key, product in session['Shoppingcart'].items(): 
        subtotal += float(product['price']) * int(product['quantity'])
        discount = subtotal * (product['discount']/100)
        subtotal -= discount
        total += float("%.2f" % (subtotal))
        discount = 0
        subtotal = 0

    return render_template('carts.html', user=current_user, total = total)

@auth.route('/updatecart/<int:code>', methods=['POST']) # Editando itens do carrinho
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('auth.home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    flash('O item foi atualizado!')
                    return redirect(url_for('auth.getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('auth.getCart'))
        

@auth.route('/deleteitem/<int:id>') # Excluindo itens do carrinho
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('/'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('auth.getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('auth.getCart'))
    

@auth.route('/clearcart') # limpando carrinho
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('auth.home'))
    except Exception as e:
        print(e)


@auth.route('/updateuserinfo/<int:id>', methods=['GET', 'POST']) # URL do updateproduct - Função para atualizar os usuários CONTINUAR 
def updateuserinfo(id):
    user = User.query.get_or_404(id) # pegando os dados do produto no database pelo ID 
    form = attUser(request.form)

    if request.method == "POST":
        user.firstName = form.firstName.data
        user.phone = form.phone.data
        user.email = form.email.data
        db.session.commit()
        flash(f'Seu perfil foi atulizado', 'sucess')
        return redirect(url_for('auth.home')) 
    
    # Preenchendo os campos com os dados que foram recuparados do banco de dados. 
    form.firstName.data = user.firstName
    form.cpf.data = user.cpf
    form.phone.data = user.phone 
    form.email.data = user.email 
    #form.password.data = user.password 

    return render_template("updateuserinfo.html", user=current_user, form=form, infoUser = user)

@auth.route('/alterpass/<int:id>', methods=['GET', 'POST'])
def alterpass(id):
    user = User.query.get_or_404(id) # pegando os dados do produto no database pelo ID 
    form = attpass(request.form)

    if request.method == 'POST':

        passcurrent = form.passcurrent.data
        password1 = form.password1.data
        password2 = form.password2.data
        SpecialSym =['$', '@', '#', '%'] # Simbolos especiais. 
    
        if check_password_hash(user.password, passcurrent): # checar se as senhas estão iguais
            login_user(user, remember=True) # Função que valida se o usuário está logado. 
            if password1 != password2:
                flash('A nova senha não está igual!', category='error') # Function to validate the password <<
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
                user.password = generate_password_hash(password1, method='sha256')
                db.session.commit()
                flash('Senha alterada com sucesso', category='success')
                return redirect(url_for('auth.updateuserinfo', id=user.id)) 
        else:
            flash('Senha atual incorreta', category='error')

    return render_template("alterpass.html", user=current_user, form=form)

def updateshoppingcart(): #Remover as imagens na hora de salvar o pedido no banco de dados
    for _key, product in session['Shoppingcart'].items():
        session.modified = True
        del product['image']
    return updateshoppingcart

@auth.route('/getorder') # Função que finaliza o pedido
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado.
def get_order():
    if current_user.is_authenticated:
        userId = current_user.id
        total = secrets.token_hex(5)
        updateshoppingcart()
        try:
            order = Order(total=total, userId=userId, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Seu pedido foi enviado', 'sucess')
            return redirect(url_for('auth.orders', total=total))
        except Exception as e:
            print(e)
            flash('Algo deu errado obtendo o pedido', 'danger')
            return redirect(url_for('auth.getCart'))


@auth.route('/orders/<total>') # pagina do pedido
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado.
def orders(total):
    if current_user.is_authenticated:
        totalDoPedido = 0
        subtotal = 0
        customer_id = current_user.id
        customer = User.query.filter_by(id=customer_id).first()
        orders = Order.query.filter_by(userId=customer_id).order_by(Order.id.desc()).first() # Aqui ele sempre vai pegar o ultimo total"identificação do pedido" 
        for _key, product in orders.orders.items():
            subtotal += float(product['price']) * int(product['quantity'])
            discount = subtotal * (product['discount']/100)
            subtotal -= discount
            totalDoPedido += float("%.2f" % (subtotal))
            discount = 0
            subtotal = 0

        somaTotal = ("%.2f" % float((totalDoPedido)))

    else:
        return redirect(url_for('auth.home'))
    return render_template('/order.html', user=current_user, total=total, subtotal=subtotal, somaTotal=somaTotal, customer=customer, orders=orders)


@auth.route('/allorders', methods=['GET', 'POST']) # Histórico de pedidos
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado.
def allorders():

    if current_user.is_authenticated:
        
        customer_id = current_user.id
        orders = Order.query.filter_by(userId=customer_id)

    return render_template('/allorders.html', user=current_user, orders=orders)


@auth.route('/userorders/<total>', methods=['GET', 'POST']) # Detalhe do pedido
@login_required # Decorador que só vai permitir acesso ao logout caso o usuário estiver logado.
def userOrders(total):
    
    if current_user.is_authenticated:
        totalDoPedido = 0
        subtotal = 0
        customer_id = current_user.id
        customer = User.query.filter_by(id=customer_id).first()
        orders = Order.query.filter_by(total=total).order_by(Order.id.desc()).first() # Aqui ele sempre vai pegar o ultimo total"identificação do pedido"
        for _key, product in orders.orders.items():
            subtotal += float(product['price']) * int(product['quantity'])
            discount = subtotal * (product['discount']/100)
            subtotal -= discount
            totalDoPedido += float("%.2f" % (subtotal))
            discount = 0
            subtotal = 0
        
        somaTotal = ("%.2f" % float((totalDoPedido)))

    return render_template('/userOrder.html', user=current_user, subtotal=subtotal, somaTotal=somaTotal, customer=customer, orders=orders, total=total)



