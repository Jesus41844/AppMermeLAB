import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path)

def _get_sqlite_uri():
    """Genera una ruta absoluta para la base de datos SQLite."""
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "mermelab_v2.db"
    return f"sqlite:///{db_path.as_posix()}"


class Config:
    """Configuración base para Flask."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _get_sqlite_uri())


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "https://tudominio.com")
    SESSION_COOKIE_SECURE = True

    @classmethod
    def validate(cls):
        if os.environ.get("FLASK_ENV") == "production" and cls.DEBUG:
            raise ValueError(
                "DEBUG debe estar desactivado en el entorno de producción."
            )


def get_config():
    """Retorna la clase de configuración según el ambiente."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "production":
        ProductionConfig.validate()
        return ProductionConfig
    return DevelopmentConfig