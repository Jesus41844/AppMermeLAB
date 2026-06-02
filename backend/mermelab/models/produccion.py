from __future__ import annotations

from datetime import datetime

from ..extensions import db


class Produccion(db.Model):
    __tablename__ = "produccion"
    __allow_unmapped__ = True

    id_produccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey("receta.id_receta", ondelete="CASCADE"), nullable=False, index=True)
    cantidad_frascos = db.Column(db.Integer, nullable=False)
    fecha_produccion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    codigo_lote_alfa = db.Column(db.String(50), unique=True, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')
    brix_real_medido = db.Column(db.Numeric(5, 2), nullable=True)
    temp_max_alcanzada = db.Column(db.Numeric(5, 2), nullable=True)

    receta = db.relationship("Receta", back_populates="producciones", lazy="joined")

