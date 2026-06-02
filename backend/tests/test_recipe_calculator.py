import pytest
from decimal import Decimal

from flask import Flask

from mermelab.extensions import db
from mermelab.services.recipe_calculator_service import RecipeCalculatorService
from mermelab.models import Receta, Ingrediente, IngredienteReceta


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app


def seed_simple_receta(app):
    receta = Receta(
        nombre="Mermelada de Manzana",
        descripcion="Receta para pruebas",
        cantidad_frascos=10,
        tamano_frasco_gramos=250,
        tiempo_preparacion_min=30,
    )
    db.session.add(receta)
    db.session.flush()

    ingrediente = Ingrediente(nombre="Manzana", unidad_medida_base="lb", stock_disponible=Decimal("100"))
    db.session.add(ingrediente)
    db.session.flush()

    rel = IngredienteReceta(id_receta=receta.id_receta, id_ingrediente=ingrediente.id_ingrediente, cantidad=Decimal("5"), unidad_medida="lb")
    db.session.add(rel)
    db.session.commit()
    return receta


def test_calculator_basic(app):
    with app.app_context():
        receta = seed_simple_receta(app)

        result = RecipeCalculatorService.calcular("Mermelada de Manzana", 20)

        assert result.frascos_deseados == 20
        assert result.factor == Decimal("2")
        assert result.fruta_total_lb == Decimal("10.00")
        assert result.stock_suficiente is True
        assert result.produccion is not None


def test_calculator_con_gramos(app):
    with app.app_context():
        receta = Receta(
            nombre="Mermelada de Fresa",
            descripcion="Prueba con gramos",
            cantidad_frascos=10,
            tamano_frasco_gramos=250,
            tiempo_preparacion_min=30,
        )
        db.session.add(receta)
        db.session.flush()

        ingrediente = Ingrediente(
            nombre="Fresa",
            unidad_medida_base="g",
            stock_disponible=Decimal("1000"),
        )
        db.session.add(ingrediente)
        db.session.flush()

        rel = IngredienteReceta(
            id_receta=receta.id_receta,
            id_ingrediente=ingrediente.id_ingrediente,
            cantidad=Decimal("500"),
            unidad_medida="g",
        )
        db.session.add(rel)
        db.session.commit()

        result = RecipeCalculatorService.calcular("Mermelada de Fresa", 10)

        assert result.frascos_deseados == 10
        assert result.factor == Decimal("1")
        assert result.fruta_total_lb == Decimal("1.10")
        assert result.stock_suficiente is True
        assert result.produccion is not None
