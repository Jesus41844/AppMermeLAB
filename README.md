# 🍓 AppMermeLAB - COIL 2026

![Estado](https://img.shields.io/badge/Estado-Finalizado-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-black)
[![tests](https://github.com/Jesus41844/AppMermeLAB/actions/workflows/tests.yml/badge.svg)](https://github.com/Jesus41844/AppMermeLAB/actions/workflows/tests.yml)
[![licencia](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)

AppMermeLAB es un aplicativo web tipo ERP (Enterprise Resource Planning) diseñado para optimizar y digitalizar las operaciones de un laboratorio de producción de mermeladas.

Este proyecto fue desarrollado en el marco del programa **COIL 2026** (Collaborative Online International Learning), uniendo esfuerzos académicos entre la **Universidad Tecnológica de Panamá (UTP)** y la **Universidad del Valle de Guatemala (UVG)**.

## Características Principales

El sistema está compuesto por 4 módulos principales diseñados para el flujo de trabajo industrial:

- **Inventario:** Gestión de materias primas e insumos con control de stock métrico y alertas de puntos de reorden.
- **Módulo de Planta (Producción):** Motor de cálculo paramétrico para recetas. Evalúa dinámicamente la viabilidad de un lote en función del stock actual y los requerimientos de la fórmula (Grados Brix, Temperatura, Frascos).
- **Control de Mermas:** Registro de pérdidas, residuos operativos y mermas esperadas vs. reales durante la cocción.
- **Ventas:** Panel administrativo para el control de despacho de producto terminado y métricas de rendimiento de lotes.

## Stack Tecnológico

El proyecto utiliza una arquitectura de Monolito Modular con separación de responsabilidades entre el backend y las interfaces:

- **Backend:** Python con Flask (Blueprints para modularidad).
- **Base de Datos:** SQLite gestionado a través de SQLAlchemy (ORM).
- **Frontend:** HTML5, JavaScript Vanilla (Fetch API) y estilizado con Tailwind CSS (Dark Mode corporativo).
- **Arquitectura REST:** Endpoints estructurados para la comunicación asíncrona entre cliente y servidor.

## Instalación y Ejecución Local

Si deseas correr este proyecto en tu entorno local, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Jesus41844/AppMermeLAB.git
   cd AppMermeLAB
   ```

2. **Entorno virtual e dependencias:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Configuración:**
   ```bash
   cp .env.example .env             # Windows: copy .env.example .env
   ```
   Cambia `JWT_SECRET_KEY` por un valor propio. `DATABASE_URL` apunta por
   defecto a `backend/mermelab_v2.db`, que está en `.gitignore`.

4. **Correr la aplicación:**
   ```bash
   python backend/app.py
   ```
   Abre <http://localhost:5000>. Al arrancar se crea el esquema y se siembran
   los datos de ejemplo, así que no hace falta ningún paso de migración.

5. **Pruebas:**
   ```bash
   pytest backend/tests -q
   ```

## Estructura

```
backend/
├── app.py                     # Wrapper para Gunicorn y ejecución directa
├── conftest.py                # Hace importable el paquete `mermelab`
├── schema.sql                 # Esquema SQLite de referencia
├── mermelab/
│   ├── __init__.py            # create_app: config, PRAGMA, seed, blueprints
│   ├── config.py              # Configuración por entorno
│   ├── extensions.py          # db, jwt, cors, migrate
│   ├── models/                # Receta, Ingrediente, Produccion, Venta, Mermelada…
│   ├── routes/                # Blueprints: calculations y views
│   ├── services/              # RecipeCalculatorService
│   ├── schemas.py             # Serialización con marshmallow
│   └── seeds.py               # Datos de ejemplo
└── tests/                     # Pruebas del motor de recetas
frontend/                      # HTML, JS vanilla y Tailwind
scripts/backup_restore.py      # Respaldo y restauración de la base
```

## Motor de cálculo de recetas

El módulo de producción es la parte no trivial del sistema. Dada una receta y
el inventario actual, `RecipeCalculatorService` responde si el lote es viable y
cuánto sale:

- **Grados Brix** — compara el mínimo y el máximo de la fórmula contra lo que
  se mide en la cocción, y avisa cuando el resultado real se sale del rango.
- **Frascos** — descuenta el factor de merma esperado para calcular cuántos
  frascos salen por lote.
- **Alertas de reorden** — señala los ingredientes que quedan por debajo del
  punto de pedido.
- **Mermas** — registra lo esperado frente a lo real durante la cocción.

Los cálculos van en `Decimal`, no en `float`: los grados Brix y los
porcentajes de merma no toleran error de punto flotante.

## Pruebas

`backend/tests/test_recipe_calculator.py` cubre el motor de recetas contra
una base SQLite en memoria, sin depender de datos de producción. Corre en CI
en cada push.
