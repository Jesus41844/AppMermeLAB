from __future__ import annotations

import math
from marshmallow import Schema, fields, validates, ValidationError, validate, pre_load


class CalculoRequestSchema(Schema):
    receta = fields.Str(required=True, validate=validate.Length(min=1))
    frascos_deseados = fields.Int(required=True, strict=False)

    @validates("frascos_deseados")
    def validate_frascos(self, value: int, **kwargs) -> None:
        if value <= 0:
            raise ValidationError("La cantidad de frascos debe ser mayor a cero.")


class IngredienteRequestSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1))
    stock = fields.Float(required=True, validate=validate.Range(min=0))
    unidad = fields.Str(required=True, validate=validate.Length(min=1))
    stock_minimo = fields.Float(allow_none=True, validate=validate.Range(min=0))

    @pre_load
    def ensure_stock_is_numeric(self, data, **kwargs):
        if "stock" in data and isinstance(data["stock"], str):
            raise ValidationError({
                "stock": ["El stock debe ser un número y no una cadena de texto."]
            })
        return data

    @validates("stock")
    def validate_stock_value(self, value: float, **kwargs) -> None:
        if isinstance(value, float) and math.isnan(value):
            raise ValidationError("El stock no puede ser NaN.")


class ConfirmacionProduccionSchema(Schema):
    id_produccion = fields.Int(required=True, strict=False, validate=validate.Range(min=1))
    brix_real = fields.Float(allow_none=True, validate=validate.Range(min=0))
    temp_real = fields.Float(allow_none=True, validate=validate.Range(min=0))

    @pre_load
    def ensure_numeric_fields(self, data, **kwargs):
        if "id_produccion" in data and isinstance(data["id_produccion"], str):
            raw_id = data["id_produccion"].strip()
            if raw_id == "":
                raise ValidationError({
                    "id_produccion": ["id_produccion es requerido."]
                })
            try:
                data["id_produccion"] = int(raw_id)
            except ValueError:
                raise ValidationError({
                    "id_produccion": ["id_produccion debe ser un número entero."]
                })

        if "brix_real" in data and isinstance(data["brix_real"], str):
            raw_brix = data["brix_real"].strip()
            if raw_brix == "":
                data["brix_real"] = None
            else:
                try:
                    data["brix_real"] = float(raw_brix)
                except ValueError:
                    raise ValidationError({
                        "brix_real": ["brix_real debe ser un número válido."]
                    })

        if "temp_real" in data and isinstance(data["temp_real"], str):
            raw_temp = data["temp_real"].strip()
            if raw_temp == "":
                data["temp_real"] = None
            else:
                try:
                    data["temp_real"] = float(raw_temp)
                except ValueError:
                    raise ValidationError({
                        "temp_real": ["temp_real debe ser un número válido."]
                    })
        return data

    @validates("brix_real")
    def validate_brix_real(self, value: float, **kwargs) -> None:
        if value is not None and math.isnan(value):
            raise ValidationError("brix_real no puede ser NaN.")

    @validates("temp_real")
    def validate_temp_real(self, value: float, **kwargs) -> None:
        if value is not None and math.isnan(value):
            raise ValidationError("temp_real no puede ser NaN.")
