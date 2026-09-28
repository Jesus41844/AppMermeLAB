"""Hace que `mermelab` sea importable al correr pytest desde la raíz.

El paquete vive en `backend/`, así que sin esto `pytest backend/tests`
falla con ModuleNotFoundError. Se resuelve en el conftest de `backend/`
porque pytest solo añade al path el directorio de las pruebas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
