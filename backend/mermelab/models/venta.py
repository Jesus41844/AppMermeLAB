from __future__ import annotations

from datetime import datetime

from ..extensions import db


class Venta(db.Model):
    __tablename__ = "ventas"
    __allow_unmapped__ = True

    id_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente", ondelete="CASCADE"), nullable=False, index=True)
    cliente = db.relationship("Cliente", back_populates="ventas", lazy="joined")

    items = db.relationship(
        "VentaMermelada",
        back_populates="venta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

