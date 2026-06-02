from __future__ import annotations

from ..extensions import db


class VentaMermelada(db.Model):
    __tablename__ = "venta_mermelada"
    __allow_unmapped__ = True

    id_venta = db.Column(db.Integer, db.ForeignKey("ventas.id_venta", ondelete="CASCADE"), primary_key=True)
    id_mermelada = db.Column(db.Integer, db.ForeignKey("mermelada.id_mermelada", ondelete="CASCADE"), primary_key=True)

    cantidad_frascos = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    venta = db.relationship("Venta", back_populates="items", lazy="joined")
    mermelada = db.relationship("Mermelada", back_populates="ventas", lazy="joined")

