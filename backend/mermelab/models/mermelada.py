from __future__ import annotations

from ..extensions import db


class Mermelada(db.Model):
    __tablename__ = "mermelada"
    __allow_unmapped__ = True

    id_mermelada = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sabor = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock_frascos = db.Column(db.Integer, nullable=False, server_default="0")

    id_receta = db.Column(db.Integer, db.ForeignKey("receta.id_receta", ondelete="CASCADE"), nullable=False, index=True)
    receta = db.relationship("Receta", back_populates="mermeladas", lazy="joined")

    ventas = db.relationship(
        "VentaMermelada",
        back_populates="mermelada",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

