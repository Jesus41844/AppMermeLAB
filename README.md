# 🍓 AppMermeLAB - COIL 2026

![Estado](https://img.shields.io/badge/Estado-Finalizado-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-black)

AppMermeLAB es un aplicativo web tipo ERP (Enterprise Resource Planning) diseñado para optimizar y digitalizar las operaciones de un laboratorio de producción de mermeladas.

Este proyecto fue desarrollado en el marco del programa **COIL 2026** (Collaborative Online International Learning), uniendo esfuerzos académicos entre la **Universidad Tecnológica de Panamá (UTP)** y la **Universidad del Valle de Guatemala (UVG)**.

## 🚀 Características Principales

El sistema está compuesto por 4 módulos principales diseñados para el flujo de trabajo industrial:

- **📦 Inventario:** Gestión de materias primas e insumos con control de stock métrico y alertas de puntos de reorden.
- **⚙️ Módulo de Planta (Producción):** Motor de cálculo paramétrico para recetas. Evalúa dinámicamente la viabilidad de un lote en función del stock actual y los requerimientos de la fórmula (Grados Brix, Temperatura, Frascos).
- **📉 Control de Mermas:** Registro de pérdidas, residuos operativos y mermas esperadas vs. reales durante la cocción.
- **🛒 Ventas:** Panel administrativo para el control de despacho de producto terminado y métricas de rendimiento de lotes.

## 🛠️ Stack Tecnológico

El proyecto utiliza una arquitectura de Monolito Modular con separación de responsabilidades entre el backend y las interfaces:

- **Backend:** Python con Flask (Blueprints para modularidad).
- **Base de Datos:** SQLite gestionado a través de SQLAlchemy (ORM).
- **Frontend:** HTML5, JavaScript Vanilla (Fetch API) y estilizado con Tailwind CSS (Dark Mode corporativo).
- **Arquitectura REST:** Endpoints estructurados para la comunicación asíncrona entre cliente y servidor.

## ⚙️ Instalación y Ejecución Local

Si deseas correr este proyecto en tu entorno local, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/AppMermeLAB.git](https://github.com/TU_USUARIO/AppMermeLAB.git)
   cd AppMermeLAB
   ```
