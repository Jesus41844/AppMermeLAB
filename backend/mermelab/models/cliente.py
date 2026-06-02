from __future__ import annotations

from ..extensions import db


class Cliente(db.Model):
    __tablename__ = "cliente"
    __allow_unmapped__ = True

    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)

    ventas = db.relationship(
        "Venta",
        back_populates="cliente",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

