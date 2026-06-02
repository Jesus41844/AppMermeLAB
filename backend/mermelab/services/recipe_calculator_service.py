from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Tuple

from sqlalchemy import func

from ..extensions import db
from ..models import IngredienteReceta, Produccion, Receta, Venta, VentaMermelada, Mermelada, Cliente


@dataclass
class CalculatedIngredient:
    nombre: str
    cantidad: Decimal
    unidad: str
    stock_disponible: Decimal | None


@dataclass
class CalculationResult:
    receta: Receta
    frascos_deseados: int
    factor: Decimal
    fruta_total_lb: Decimal | None
    ingredientes: List[CalculatedIngredient]
    stock_suficiente: bool
    faltantes: List[CalculatedIngredient]
    produccion: Produccion


class RecipeCalculatorService:

    @staticmethod
    def _resolver_receta(identificador: str | int) -> Receta | None:
        if identificador is None:
            return None

        try:
            id_int = int(str(identificador).strip())
            receta = Receta.query.get(id_int)
            if receta:
                return receta
        except (ValueError, TypeError):
            pass

        slug_norm = str(identificador).strip().lower()
        receta = Receta.query.filter(func.lower(Receta.nombre) == slug_norm).first()
        return receta

    @staticmethod
    def _calcular_factor_total(receta: Receta, frascos_deseados: int) -> Decimal:
        factor_escala = Decimal(frascos_deseados) / Decimal(receta.cantidad_frascos)
        merma = Decimal(getattr(receta, 'factor_merma_esperado', 0) or 0)
        if merma >= 1:
            raise ValueError("El factor de merma esperado no puede ser igual o mayor al 100% (1.0).")
        ajuste_merma = Decimal("1") / (Decimal("1") - merma)
        return (factor_escala * ajuste_merma).quantize(Decimal("0.0001"))

    @staticmethod
    def _convertir_a_libras(cantidad: Decimal, unidad: str) -> Decimal | None:
        unidad_norm = str(unidad or "").strip().lower()
        if not unidad_norm:
            return None

        unidad_norm = unidad_norm.replace(" ", "")

        if "kg" in unidad_norm or "kilogram" in unidad_norm:
            return cantidad * Decimal("2.20462262185")
        if "lb" in unidad_norm or "libra" in unidad_norm:
            return cantidad
        if "g" in unidad_norm or "gram" in unidad_norm:
            return cantidad / Decimal("453.59237")

        return None

    @staticmethod
    def calcular(slug_receta: str, frascos_deseados: int, persistir: bool = False) -> CalculationResult:
        receta = RecipeCalculatorService._resolver_receta(slug_receta)
        if not receta:
            raise ValueError(f"La receta '{slug_receta}' no existe en la base de datos.")

        if frascos_deseados <= 0:
            raise ValueError("La cantidad de frascos deseados debe ser mayor que cero.")

        if receta.cantidad_frascos <= 0:
            raise ValueError(f"La receta '{receta.nombre}' tiene una cantidad de frascos base inválida (0).")

        factor_total = RecipeCalculatorService._calcular_factor_total(receta, frascos_deseados)

        ingredientes_calc: List[CalculatedIngredient] = []
        faltantes: List[CalculatedIngredient] = []
        fruta_total_lb: Decimal | None = None

        for rel in receta.ingredientes:
            base = Decimal(rel.cantidad)
            total = (base * factor_total).quantize(Decimal("0.01"))
            stock = (
                Decimal(rel.ingrediente.stock_disponible)
                if rel.ingrediente.stock_disponible is not None
                else None
            )

            calc = CalculatedIngredient(
                nombre=rel.ingrediente.nombre,
                cantidad=total,
                unidad=rel.unidad_medida,
                stock_disponible=stock,
            )
            ingredientes_calc.append(calc)

            keywords_fruta = [
                "mora", "fresa", "fruta", "manzana", "piña", "pina", "pera", 
                "durazno", "mango", "guayaba", "arandano", "frambuesa", 
                "kiwi", "higo", "maracuya", "melocoton"
            ]
            nombre_ing = rel.ingrediente.nombre.lower()
            nombre_norm = nombre_ing.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
            
            if any(k in nombre_norm for k in keywords_fruta):
                peso_lb = RecipeCalculatorService._convertir_a_libras(total, rel.unidad_medida)
                if peso_lb is not None:
                    fruta_total_lb = (fruta_total_lb or Decimal("0")) + peso_lb

            if stock is not None and total > stock:
                faltantes.append(calc)

        stock_suficiente = len(faltantes) == 0
        
        if fruta_total_lb is not None:
            fruta_total_lb = fruta_total_lb.quantize(Decimal("0.01"))

        fecha_str = datetime.now().strftime("%Y%m%d")
        
        produccion = Produccion(
            receta=receta,
            cantidad_frascos=frascos_deseados,
            fecha_produccion=datetime.now(timezone.utc),
            estado='pendiente'
        )
        if persistir:
            try:
                db.session.add(produccion)
                db.session.flush()
                produccion.codigo_lote_alfa = f"MER-{fecha_str}-{produccion.id_produccion}"
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return CalculationResult(
            receta=receta,
            frascos_deseados=frascos_deseados,
            factor=factor_total,
            fruta_total_lb=fruta_total_lb,
            ingredientes=ingredientes_calc,
            stock_suficiente=stock_suficiente,
            faltantes=faltantes,
            produccion=produccion,
        )

    @staticmethod
    def confirmar_produccion(
        id_produccion: int, brix_real: float | None = None, temp_real: float | None = None
    ) -> Tuple[bool, str]:
        produccion = Produccion.query.get(id_produccion)
        if not produccion:
            return False, "Producción no encontrada"
            
        if getattr(produccion, 'estado', None) == 'completado':
            return False, "Esta producción ya fue confirmada anteriormente"
        
        receta = produccion.receta
        if receta.cantidad_frascos <= 0:
            return False, f"La receta '{receta.nombre}' tiene una cantidad de frascos base inválida (0)."

        try:
            factor_total = RecipeCalculatorService._calcular_factor_total(receta, produccion.cantidad_frascos)
            
            for rel in receta.ingredientes:
                cantidad_necesaria = (Decimal(rel.cantidad) * factor_total).quantize(Decimal("0.01"))
                ingrediente = rel.ingrediente
                
                stock_actual = Decimal(ingrediente.stock_disponible or 0)
                
                if stock_actual < cantidad_necesaria:
                    db.session.rollback()
                    return False, f"Stock insuficiente para {ingrediente.nombre}"
                
                ingrediente.stock_disponible = stock_actual - cantidad_necesaria

            if hasattr(produccion, 'estado'):
                produccion.estado = 'completado'
                
            if brix_real is not None:
                produccion.brix_real_medido = brix_real
            if temp_real is not None:
                produccion.temp_max_alcanzada = temp_real
                
            db.session.commit()
            return True, "Producción confirmada con éxito"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def registrar_venta(id_produccion: int, cantidad: int, precio_total: float) -> Tuple[bool, any]:
        try:
            id_produccion = int(id_produccion)
            cantidad = int(cantidad)
            precio_total = float(precio_total)

            produccion = Produccion.query.get(id_produccion)
            if not produccion or produccion.estado != 'completado':
                return False, "Producción no encontrada o no completada."

            # Buscar producto asociado (mermelada)
            mermelada = Mermelada.query.filter_by(id_receta=produccion.id_receta).first()
            if not mermelada or mermelada.stock_frascos < cantidad:
                return False, "Stock insuficiente de producto terminado."

            # Asegurar existencia de cliente genérico
            cliente = Cliente.query.filter_by(nombre="Cliente General").first()
            if not cliente:
                cliente = Cliente(nombre="Cliente General")
                db.session.add(cliente)
                db.session.flush()

            # Registrar Venta
            nueva_venta = Venta(total=precio_total, id_cliente=cliente.id_cliente)
            db.session.add(nueva_venta)
            db.session.flush()

            item_venta = VentaMermelada(
                id_venta=nueva_venta.id_venta,
                id_mermelada=mermelada.id_mermelada,
                cantidad_frascos=cantidad,
                subtotal=precio_total
            )
            db.session.add(item_venta)

            # Actualizar Stock
            mermelada.stock_frascos -= cantidad
            
            db.session.commit()
            return True, nueva_venta
        except Exception as e:
            db.session.rollback()
            return False, str(e)
