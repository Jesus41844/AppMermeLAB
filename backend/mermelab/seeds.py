from __future__ import annotations

from decimal import Decimal

from .extensions import db
from .models import Ingrediente, IngredienteReceta, Mermelada, Receta


def seed_all() -> None:
    """Seed inicial basado en el SQL proporcionado.

    Idempotente: si ya hay recetas, no hace nada.
    """
    if Receta.query.first() is not None:
        return

    # =========================
    # Ingredientes
    # =========================
    ingredientes_data = [
        ("Azúcar", "g", 50000),
        ("Agua", "ml", 20000),
        ("Jugo de limón", "g", 10000),
        ("Manzana", "lb", 100),
        ("Fresa", "lb", 100),
        ("Piña", "lb", 100),
        ("Pera", "lb", 100),
        ("Mora", "lb", 100),
        ("Durazno", "lb", 100),
        ("Mango", "lb", 100),
        ("Guayaba", "lb", 100),
        ("Arándanos", "lb", 100),
        ("Frambuesa", "lb", 100),
        ("Kiwi", "lb", 100),
        ("Higo", "lb", 100),
        ("Maracuyá", "lb", 100),
        ("Melocotón", "lb", 100),
        ("Frutos Rojos", "lb", 100),
    ]
    ingredientes_by_name: dict[str, Ingrediente] = {}
    for nombre, unidad, stock in ingredientes_data:
        ingr = Ingrediente(
            nombre=nombre,
            unidad_medida_base=unidad,
            stock_disponible=Decimal(str(stock)),
        )
        db.session.add(ingr)
        ingredientes_by_name[nombre] = ingr

    # =========================
    # Recetas
    # =========================
    recetas_data = [
        "Mermelada de Manzana",
        "Mermelada de Fresa",
        "Mermelada de Piña",
        "Mermelada de Pera",
        "Mermelada de Mora",
        "Mermelada de Durazno",
        "Mermelada de Mango",
        "Mermelada de Guayaba",
        "Mermelada de Arándanos",
        "Mermelada de Frambuesa",
        "Mermelada de Kiwi",
        "Mermelada de Higo",
        "Mermelada de Maracuyá",
        "Mermelada de Melocotón",
        "Mermelada de Mango y Maracuyá",
        "Mermelada de Frutos Rojos",
        "Mermelada de Pera y Manzana",
    ]

    recetas_by_index: dict[int, Receta] = {}
    for idx, nombre in enumerate(recetas_data, start=1):
        receta = Receta(
            nombre=nombre,
            descripcion="Conserva artesanal",
            cantidad_frascos=6 if idx != 1 else 4,
            tamano_frasco_gramos=250,
            tiempo_preparacion_min=60,
            brix_min=Decimal("65.00"),
            brix_max=Decimal("68.00"),
            temperatura_min=Decimal("104.00"),
            temperatura_max=Decimal("106.00"),
        )
        db.session.add(receta)
        recetas_by_index[idx] = receta

    db.session.flush()

    # =========================
    # Ingrediente_Receta
    # =========================

    def add_ing(receta_idx: int, ingr_nombre: str, cantidad: float, unidad: str) -> None:
        receta = recetas_by_index[receta_idx]
        ingrediente = ingredientes_by_name[ingr_nombre]
        db.session.add(
            IngredienteReceta(
                receta=receta,
                ingrediente=ingrediente,
                cantidad=Decimal(str(cantidad)),
                unidad_medida=unidad,
            )
        )

    # MANZANA (1)
    add_ing(1, "Manzana", 3, "lb")
    add_ing(1, "Azúcar", 1369, "g")
    add_ing(1, "Jugo de limón", 2, "cucharadas")
    add_ing(1, "Agua", 0.5, "taza")

    # FRESA (2)
    add_ing(2, "Fresa", 4, "lb")
    add_ing(2, "Azúcar", 1200, "g")
    add_ing(2, "Jugo de limón", 30, "g")
    add_ing(2, "Agua", 60, "ml")

    # PIÑA (3)
    add_ing(3, "Piña", 3.23, "lb")
    add_ing(3, "Azúcar", 1465, "g")
    add_ing(3, "Jugo de limón", 2, "cucharadas")
    add_ing(3, "Agua", 0.5, "taza")

    # PERA (4)
    add_ing(4, "Pera", 1.25, "lb")
    add_ing(4, "Azúcar", 566, "g")
    add_ing(4, "Jugo de limón", 1, "cucharada")
    add_ing(4, "Agua", 0.5, "taza")

    # MORA (5)
    add_ing(5, "Mora", 4, "lb")
    add_ing(5, "Azúcar", 1200, "g")
    add_ing(5, "Jugo de limón", 30, "g")
    add_ing(5, "Agua", 60, "ml")

    # DURAZNO (6)
    add_ing(6, "Durazno", 4, "lb")
    add_ing(6, "Azúcar", 1200, "g")
    add_ing(6, "Jugo de limón", 30, "g")
    add_ing(6, "Agua", 60, "ml")

    # MANGO (7)
    add_ing(7, "Mango", 4, "lb")
    add_ing(7, "Azúcar", 1200, "g")
    add_ing(7, "Jugo de limón", 30, "g")
    add_ing(7, "Agua", 60, "ml")

    # GUAYABA (8)
    add_ing(8, "Guayaba", 4, "lb")
    add_ing(8, "Azúcar", 1200, "g")
    add_ing(8, "Jugo de limón", 30, "g")
    add_ing(8, "Agua", 60, "ml")

    # ARÁNDANOS (9)
    add_ing(9, "Arándanos", 4, "lb")
    add_ing(9, "Azúcar", 1200, "g")
    add_ing(9, "Jugo de limón", 30, "g")
    add_ing(9, "Agua", 60, "ml")

    # FRAMBUESA (10)
    add_ing(10, "Frambuesa", 4, "lb")
    add_ing(10, "Azúcar", 1200, "g")
    add_ing(10, "Jugo de limón", 30, "g")
    add_ing(10, "Agua", 60, "ml")

    # KIWI (11)
    add_ing(11, "Kiwi", 4, "lb")
    add_ing(11, "Azúcar", 1200, "g")
    add_ing(11, "Jugo de limón", 30, "g")
    add_ing(11, "Agua", 60, "ml")

    # HIGO (12)
    add_ing(12, "Higo", 4, "lb")
    add_ing(12, "Azúcar", 1200, "g")
    add_ing(12, "Jugo de limón", 30, "g")
    add_ing(12, "Agua", 60, "ml")

    # MARACUYÁ (13)
    add_ing(13, "Maracuyá", 4, "lb")
    add_ing(13, "Azúcar", 1200, "g")
    add_ing(13, "Jugo de limón", 30, "g")
    add_ing(13, "Agua", 60, "ml")

    # MELOCOTÓN (14)
    add_ing(14, "Melocotón", 4, "lb")
    add_ing(14, "Azúcar", 1200, "g")
    add_ing(14, "Jugo de limón", 30, "g")
    add_ing(14, "Agua", 60, "ml")

    # MANGO Y MARACUYÁ (15)
    add_ing(15, "Mango", 2, "lb")
    add_ing(15, "Maracuyá", 2, "lb")
    add_ing(15, "Azúcar", 1200, "g")
    add_ing(15, "Jugo de limón", 30, "g")
    add_ing(15, "Agua", 60, "ml")

    # FRUTOS ROJOS (16)
    add_ing(16, "Frutos Rojos", 4, "lb")
    add_ing(16, "Azúcar", 1200, "g")
    add_ing(16, "Jugo de limón", 30, "g")
    add_ing(16, "Agua", 60, "ml")

    # PERA Y MANZANA (17)
    add_ing(17, "Pera", 2, "lb")
    add_ing(17, "Manzana", 2, "lb")
    add_ing(17, "Azúcar", 1200, "g")
    add_ing(17, "Jugo de limón", 30, "g")
    add_ing(17, "Agua", 60, "ml")

    # =========================
    # Mermeladas
    # =========================
    mermeladas_data = [
        ("Manzana", 4.50, 50, 1),
        ("Fresa", 5.00, 50, 2),
        ("Piña", 5.00, 50, 3),
        ("Pera", 5.00, 50, 4),
        ("Mora", 5.50, 50, 5),
        ("Durazno", 5.50, 50, 6),
        ("Mango", 5.50, 50, 7),
        ("Guayaba", 5.00, 50, 8),
        ("Arándanos", 6.00, 50, 9),
        ("Frambuesa", 6.00, 50, 10),
        ("Kiwi", 6.00, 50, 11),
        ("Higo", 6.00, 50, 12),
        ("Maracuyá", 5.50, 50, 13),
        ("Melocotón", 5.50, 50, 14),
        ("Mango y Maracuyá", 6.50, 50, 15),
        ("Frutos Rojos", 6.50, 50, 16),
        ("Pera y Manzana", 5.50, 50, 17),
    ]

    for sabor, precio, stock, idx_receta in mermeladas_data:
        receta = recetas_by_index[idx_receta]
        db.session.add(
            Mermelada(
                sabor=sabor,
                precio=Decimal(str(precio)),
                stock_frascos=stock,
                receta=receta,
            )
        )

    db.session.commit()

