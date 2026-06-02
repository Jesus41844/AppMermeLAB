from __future__ import annotations

from typing import List

from ..extensions import db


class Receta(db.Model):
    __tablename__ = "receta"
    __allow_unmapped__ = True

    id_receta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.String(255), nullable=True)
    cantidad_frascos = db.Column(db.Integer, nullable=False)
    tamano_frasco_gramos = db.Column(db.Integer, nullable=False)
    tiempo_preparacion_min = db.Column(db.Integer, nullable=False)
    brix_min = db.Column(db.Numeric(5, 2), nullable=True)
    brix_max = db.Column(db.Numeric(5, 2), nullable=True)
    temperatura_min = db.Column(db.Numeric(5, 2), nullable=True)
    temperatura_max = db.Column(db.Numeric(5, 2), nullable=True)

    ingredientes: List["IngredienteReceta"] = db.relationship(
        "IngredienteReceta",
        back_populates="receta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    mermeladas = db.relationship(
        "Mermelada",
        back_populates="receta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    producciones = db.relationship(
        "Produccion",
        back_populates="receta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

