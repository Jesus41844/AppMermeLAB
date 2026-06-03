import os
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy import event, text

from .config import get_config
from .extensions import cors, db, jwt, migrate
from .routes import register_blueprints
from . import models  # noqa: F401
from .routes.views import views_bp
from .seeds import seed_all


def create_app() -> Flask:
    # Resolución de rutas absolutas multiplataforma para templates y estáticos
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    frontend_dir = os.path.join(root_path, "frontend")

    app = Flask(
        __name__,
        template_folder=frontend_dir,
        static_folder=frontend_dir,
        static_url_path="/static"
    )
    app.config.from_object(get_config())

    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Activar soporte de Claves Foráneas para SQLite
        if "sqlite" in app.config.get("SQLALCHEMY_DATABASE_URI", ""):
            @event.listens_for(db.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        db.create_all()

        # Asegurar columnas nuevas en SQLite cuando la base de datos es antigua.
        if "sqlite" in app.config.get("SQLALCHEMY_DATABASE_URI", ""):
            with db.engine.connect() as conn:
                existing_columns = {
                    row[1]
                    for row in conn.execute(text("PRAGMA table_info(Produccion)"))
                }

                alter_stmts = []
                if "codigo_lote_alfa" not in existing_columns:
                    alter_stmts.append(
                        "ALTER TABLE Produccion ADD COLUMN codigo_lote_alfa TEXT"
                    )
                if "brix_real_medido" not in existing_columns:
                    alter_stmts.append(
                        "ALTER TABLE Produccion ADD COLUMN brix_real_medido NUMERIC(5,2)"
                    )
                if "temp_max_alcanzada" not in existing_columns:
                    alter_stmts.append(
                        "ALTER TABLE Produccion ADD COLUMN temp_max_alcanzada NUMERIC(5,2)"
                    )

                for stmt in alter_stmts:
                    conn.execute(text(stmt))
                if alter_stmts:
                    conn.commit()

        seed_all()

    # Registro centralizado de Blueprints activos
    app.register_blueprint(views_bp)
    register_blueprints(app)

    @app.errorhandler(Exception)
    def handle_exception(err: Exception):
        if isinstance(err, HTTPException):
            return jsonify({"error": err.name, "message": err.description, "status": err.code}), err.code
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal Server Error", "message": "Unexpected error", "status": 500}), 500

    return app
