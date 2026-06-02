from __future__ import annotations

from typing import List

from ..extensions import db


class Ingrediente(db.Model):
    __tablename__ = "ingrediente"
    __allow_unmapped__ = True

    id_ingrediente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False, index=True)
    unidad_medida_base = db.Column(db.String(50), nullable=False)
    stock_disponible = db.Column(db.Numeric(10, 2), nullable=False, server_default="0")

    recetas: List["IngredienteReceta"] = db.relationship(
        "IngredienteReceta",
        back_populates="ingrediente",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

