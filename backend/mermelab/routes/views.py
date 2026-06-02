from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
@views_bp.route('/index')
def index():
    return render_template('index.html')

@views_bp.route('/recetas')
def recetas():
    return render_template('recetas.html')

@views_bp.route('/produccion')
def produccion():
    return render_template('produccion.html')

@views_bp.route('/resultado')
def resultado():
    return render_template('resultado.html')

@views_bp.route('/inventario')
def inventario():
    return render_template('inventario.html')

@views_bp.route('/residuos')
def residuos():
    return render_template('residuos.html')

@views_bp.route('/ventas')
def ventas():
    return render_template('ventas.html')