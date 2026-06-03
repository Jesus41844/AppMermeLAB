import traceback
import sys
import unicodedata
from flask import Blueprint, jsonify, request, current_app
from decimal import Decimal, InvalidOperation
from sqlalchemy import func
from marshmallow import ValidationError

from ..schemas import CalculoRequestSchema, ConfirmacionProduccionSchema, IngredienteRequestSchema
from ..models import (
    Cliente,
    Mermelada,
    Receta,
    Produccion,
    Venta,
    VentaMermelada,
    Ingrediente,
    IngredienteReceta,
)
from ..services.recipe_calculator_service import RecipeCalculatorService
from ..extensions import db

bp = Blueprint("calculations", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    return jsonify({"status": "ok", "message": "MermeLAB API is running"}), 200

@bp.post("/calcular")
def calcular():
    schema = CalculoRequestSchema()
    try:
        payload = schema.load(request.get_json() or {})
    except ValidationError as exc:
        return jsonify({"error": "Error de validación", "details": exc.messages}), 400

    try:
        result = RecipeCalculatorService.calcular(
            slug_receta=payload["receta"],
            frascos_deseados=payload["frascos_deseados"],
            persistir=True
        )
    except ValueError as exc:
        current_app.logger.warning(f"Error de negocio en cálculo: {str(exc)}")
        return jsonify({"error": str(exc)}), 404
    except Exception as e:
        print("---------- ERROR CRÍTICO EN /api/calcular ----------", file=sys.stderr)
        traceback.print_exc()
        print("-----------------------------------------------------", file=sys.stderr)
        return jsonify({
            "error": "Error interno del servidor",
            "message": str(e),
            "type": e.__class__.__name__
        }), 500

    receta = result.receta

    brix = None
    if receta.brix_min is not None and receta.brix_max is not None:
        brix = f"{receta.brix_min}-{receta.brix_max} °Bx"
    temp = None
    if receta.temperatura_min is not None and receta.temperatura_max is not None:
        temp = f"{receta.temperatura_min}-{receta.temperatura_max} °C"

    ingredientes_response = [
        {
            "nombre": ing.nombre,
            "cantidad": float(ing.cantidad),
            "unidad": ing.unidad,
        }
        for ing in result.ingredientes
    ]

    response = {
        "producto": receta.nombre,
        "id_produccion": result.produccion.id_produccion,
        "lote_id": f"PROD-{result.produccion.id_produccion}",
        "fruta_libras_calculada": float(result.fruta_total_lb or 0),
        "ingredientes_adicionales": ingredientes_response,
        "rendimiento_estimado": f"{result.frascos_deseados} frascos de {receta.tamano_frasco_gramos}g",
        "controles_calidad": {
            "brix_requerido": brix or "",
            "temperatura_coccion": temp or "",
        },
        "stock_suficiente": result.stock_suficiente,
    }

    if not result.stock_suficiente:
        response["faltantes"] = [
            {
                "nombre": ing.nombre,
                "cantidad_requerida": float(ing.cantidad),
                "stock_disponible": float(ing.stock_disponible or 0),
                "unidad": ing.unidad,
            }
            for ing in result.faltantes
        ]

    return jsonify(response), 200

@bp.get("/recetas")
@bp.get("/recipes")
def get_recetas():
    recetas = Receta.query.all()
    data = []
    for r in recetas:
        try:
            with db.session.no_autoflush:
                calc = RecipeCalculatorService.calcular(r.nombre, r.cantidad_frascos, persistir=False)
            faltantes = len(calc.faltantes)
            critico = any(i.stock_disponible is not None and i.stock_disponible < 5 for i in calc.ingredientes)
        except Exception:
            faltantes = 0
            critico = False

        data.append({
            "id": r.id_receta,
            "nombre": r.nombre,
            "descripcion": r.descripcion,
            "cantidad_frascos_base": r.cantidad_frascos,
            "tamano_frasco_gramos": r.tamano_frasco_gramos,
            "tiempo_preparacion_min": r.tiempo_preparacion_min,
            "brix_min": float(r.brix_min) if r.brix_min is not None else None,
            "brix_max": float(r.brix_max) if r.brix_max is not None else None,
            "temperatura_min": float(r.temperatura_min) if r.temperatura_min is not None else None,
            "temperatura_max": float(r.temperatura_max) if r.temperatura_max is not None else None,
            "insumos_faltantes": faltantes,
            "stock_critico": critico,
            "ingredientes": [
                {
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad),
                    "unidad": ir.unidad_medida,
                }
                for ir in r.ingredientes
            ],
        })
    return jsonify(data), 200

@bp.get("/recetas/<string:slug>")
def get_receta(slug):
    receta = RecipeCalculatorService._resolver_receta(slug)
    if not receta:
        return jsonify({"error": "Receta no encontrada"}), 404
    return jsonify({
        "id": receta.id_receta,
        "nombre": receta.nombre,
        "descripcion": receta.descripcion
    }), 200

@bp.delete("/recetas/<int:id_receta>")
def eliminar_receta(id_receta):
    receta = Receta.query.get(id_receta)
    if not receta:
        return jsonify({"error": "Receta no encontrada"}), 404

    try:
        db.session.delete(receta)
        db.session.commit()
        return jsonify({"message": "Receta eliminada"}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "No se pudo eliminar la receta", "details": str(exc)}), 500

@bp.get("/lotes")
@bp.get("/produccion")
def get_lotes():
    producciones = Produccion.query.order_by(Produccion.id_produccion.desc()).all()
    return jsonify([{
        "id": p.id_produccion,
        "receta": p.receta.nombre,
        "cantidad_frascos": p.cantidad_frascos,
        "stock_frascos": (p.receta.mermeladas[0].stock_frascos if p.receta.mermeladas else 0),
        "fecha": p.fecha_produccion.isoformat() if p.fecha_produccion else None,
        "estado": p.estado
    } for p in producciones]), 200

@bp.post("/sales")
def crear_venta():
    data = request.get_json() or {}
    id_produccion = data.get("id_produccion")
    cantidad = data.get("cantidad")
    precio_total = data.get("precio_total")

    try:
        success, result = RecipeCalculatorService.registrar_venta(
            id_produccion=id_produccion,
            cantidad=cantidad,
            precio_total=precio_total
        )
        if not success:
            return jsonify({"error": result}), 400
        
        return jsonify({"message": "Venta registrada correctamente."}), 201
    except Exception as exc:
        return jsonify({"error": "No se pudo registrar la venta.", "details": str(exc)}), 500

@bp.post("/produccion/confirmar")
def confirmar_produccion():
    schema = ConfirmacionProduccionSchema()
    try:
        payload = schema.load(request.get_json() or {})
    except ValidationError as exc:
        return jsonify({"error": "Error de validación", "details": exc.messages}), 400

    success, message = RecipeCalculatorService.confirmar_produccion(
        payload["id_produccion"],
        brix_real=payload.get("brix_real"),
        temp_real=payload.get("temp_real")
    )

    if not success:
        return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200

def _normalize_ingredient_name(nombre: str) -> str:
    raw = str(nombre or "").strip().lower()
    normalized = unicodedata.normalize("NFD", raw)
    without_accents = "".join(
        ch for ch in normalized if not unicodedata.combining(ch)
    )
    return " ".join(without_accents.split())


@bp.get("/ingredientes")
@bp.get("/inventario")
def get_ingredientes():
    insumos = Ingrediente.query.order_by(func.lower(Ingrediente.nombre)).all()
    agrupados = {}

    for ing in insumos:
        key = (_normalize_ingredient_name(ing.nombre), str(ing.unidad_medida_base or "").strip().lower())
        stock_actual = float(ing.stock_disponible or 0)
        if key in agrupados:
            existente = agrupados[key]
            existente["stock"] += stock_actual
        else:
            agrupados[key] = {
                "id": ing.id_ingrediente,
                "nombre": ing.nombre.strip(),
                "stock": stock_actual,
                "unidad": ing.unidad_medida_base,
                "stock_minimo": float(getattr(ing, "stock_minimo", 0) or 0),
            }

    return jsonify(list(agrupados.values())), 200


@bp.post("/ingredientes")
def crear_ingrediente():
    schema = IngredienteRequestSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as exc:
        return jsonify({"error": "Datos inválidos", "details": exc.messages}), 400

    nombre_raw = data['nombre'].strip()
    unidad_raw = data['unidad'].strip()
    stock = Decimal(str(data['stock']))

    nombre_normalizado = _normalize_ingredient_name(nombre_raw)
    unidad_normalizada = unidad_raw.lower()

    existentes = []
    for item in Ingrediente.query.all():
        if _normalize_ingredient_name(item.nombre) == nombre_normalizado:
            existentes.append(item)

    if existentes:
        principal = existentes[0]
        if principal.unidad_medida_base.strip().lower() != unidad_normalizada:
            return jsonify({"error": "El ingrediente ya existe con otra unidad de medida."}), 400

        if len(existentes) > 1:
            for duplicate in existentes[1:]:
                principal.stock_disponible = (
                    (principal.stock_disponible or Decimal('0'))
                    + (duplicate.stock_disponible or Decimal('0'))
                )
                db.session.delete(duplicate)

        principal.stock_disponible = (
            (principal.stock_disponible or Decimal('0')) + stock
        )
        if 'stock_minimo' in data and hasattr(principal, 'stock_minimo'):
            principal.stock_minimo = data['stock_minimo']

        db.session.commit()
        return jsonify({"message": "Ingrediente existente actualizado."}), 200

    nuevo = Ingrediente(
        nombre=nombre_raw,
        stock_disponible=stock,
        unidad_medida_base=unidad_raw,
    )
    if 'stock_minimo' in data and hasattr(nuevo, 'stock_minimo'):
        nuevo.stock_minimo = data['stock_minimo']

    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"message": "Ingrediente creado"}), 201


@bp.post("/inventario/residuos")
def registrar_residuo():
    data = request.get_json() or {}
    try:
        id_ingrediente = int(data.get("id_ingrediente"))
        cantidad = Decimal(str(data.get("cantidad")))
    except (TypeError, ValueError, InvalidOperation):
        return jsonify({"error": "id_ingrediente y cantidad deben ser valores numéricos válidos."}), 400

    motivo = str(data.get("motivo", "")).strip()
    if cantidad <= 0:
        return jsonify({"error": "La cantidad debe ser mayor que cero."}), 400

    ingrediente = Ingrediente.query.get(id_ingrediente)
    if not ingrediente:
        return jsonify({"error": "Ingrediente no encontrado."}), 404

    stock_actual = ingrediente.stock_disponible or Decimal("0")
    if cantidad > stock_actual:
        return jsonify({"error": "No hay suficiente stock para descontar esa cantidad."}), 400

    ingrediente.stock_disponible = stock_actual - cantidad
    db.session.commit()

    return jsonify({
        "message": "Residuo registrado y stock actualizado.",
        "id": ingrediente.id_ingrediente,
        "stock": float(ingrediente.stock_disponible),
        "motivo": motivo,
    }), 200

@bp.post("/recetas")
def crear_receta():
    data = request.get_json() or {}
    required_fields = [
        'nombre',
        'ingredientes',
        'cantidad_frascos_base',
        'tamano_frasco',
        'tiempo_preparacion_min'
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Datos de receta incompletos: {', '.join(missing)}"}), 400

    try:
        nueva_receta = Receta(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', '').strip(),
            cantidad_frascos=int(data['cantidad_frascos_base']),
            tamano_frasco_gramos=int(data['tamano_frasco']),
            tiempo_preparacion_min=int(data['tiempo_preparacion_min']),
            brix_min=data.get('brix_min') if data.get('brix_min') is not None else None,
            brix_max=data.get('brix_max') if data.get('brix_max') is not None else None,
            temperatura_min=data.get('temperatura_min', data.get('temp_min')),
            temperatura_max=data.get('temperatura_max', data.get('temp_max'))
        )
        db.session.add(nueva_receta)
        db.session.flush()

        for ing in data['ingredientes']:
            base = Ingrediente.query.filter_by(nombre=ing['nombre']).first()
            if not base:
                base = Ingrediente(
                    nombre=ing['nombre'],
                    unidad_medida_base=ing.get('unidad', 'unidad'),
                    stock_disponible=0
                )
                db.session.add(base)
                db.session.flush()

            relacion = IngredienteReceta(
                id_receta=nueva_receta.id_receta,
                id_ingrediente=base.id_ingrediente,
                cantidad=ing['cantidad'],
                unidad_medida=ing['unidad']
            )
            db.session.add(relacion)

        db.session.commit()
        return jsonify({"message": "Receta creada exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "No se pudo crear la receta", "details": str(e)}), 500
