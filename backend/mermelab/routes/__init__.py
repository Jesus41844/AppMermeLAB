from flask import Flask

from .calculations import bp as calculations_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(calculations_bp)

