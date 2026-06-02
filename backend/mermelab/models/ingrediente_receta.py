from __future__ import annotations

from ..extensions import db


class IngredienteReceta(db.Model):
    __tablename__ = "ingrediente_receta"

    id_receta = db.Column(db.Integer, db.ForeignKey("receta.id_receta", ondelete="CASCADE"), primary_key=True)
    id_ingrediente = db.Column(
        db.Integer, db.ForeignKey("ingrediente.id_ingrediente", ondelete="CASCADE"), primary_key=True
    )

    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    unidad_medida = db.Column(db.String(50), nullable=False)

    receta = db.relationship("Receta", back_populates="ingredientes", lazy="joined")
    ingrediente = db.relationship("Ingrediente", back_populates="recetas", lazy="joined")

