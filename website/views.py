from flask import Blueprint, render_template
from flask_login import login_required, current_user # objetos que contem as funções de validações de login e logout

views = Blueprint('views', __name__) 

# @views.route('/')
# @login_required # função que não permite acesso a homepage sem que o usuário esteja logado. 
# def home():
#    return render_template("home.html", user=current_user)