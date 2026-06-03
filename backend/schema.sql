-- Esquema de la Base de Datos SQLite

CREATE TABLE Receta (
    id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    cantidad_frascos INTEGER NOT NULL,
    tamano_frasco_gramos INTEGER NOT NULL,
    factor_merma_esperado DECIMAL(5,2) DEFAULT 0.0, -- Ejemplo: 0.20 para 20% de evaporación
    tiempo_preparacion_min INTEGER NOT NULL,
    brix_min DECIMAL(5,2),
    brix_max DECIMAL(5,2),
    temperatura_min DECIMAL(5,2),
    temperatura_max DECIMAL(5,2)
);

CREATE TABLE Ingrediente (
    id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    unidad_medida_base TEXT NOT NULL DEFAULT 'g', -- Estandarizado a gramos
    stock_disponible DECIMAL(10,2) DEFAULT 0,
    stock_minimo DECIMAL(10,2) DEFAULT 0 -- Punto de reorden
);

CREATE TABLE Ingrediente_Receta (
    id_receta INTEGER NOT NULL,
    id_ingrediente INTEGER NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    unidad_medida TEXT NOT NULL,
    PRIMARY KEY (id_receta, id_ingrediente),
    FOREIGN KEY (id_receta) REFERENCES Receta(id_receta) ON DELETE CASCADE,
    FOREIGN KEY (id_ingrediente) REFERENCES Ingrediente(id_ingrediente) ON DELETE CASCADE
);

CREATE TABLE Mermelada (
    id_mermelada INTEGER PRIMARY KEY AUTOINCREMENT,
    sabor TEXT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock_frascos INTEGER DEFAULT 0,
    id_receta INTEGER NOT NULL,
    FOREIGN KEY (id_receta) REFERENCES Receta(id_receta) ON DELETE CASCADE
);

CREATE TABLE Ventas (
    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL DEFAULT (date('now')),
    total DECIMAL(10,2) NOT NULL,
    id_cliente INTEGER NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE CASCADE
);

CREATE TABLE Venta_Mermelada (
    id_venta INTEGER NOT NULL,
    id_mermelada INTEGER NOT NULL,
    cantidad_frascos INTEGER NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_venta, id_mermelada),
    FOREIGN KEY (id_venta) REFERENCES Ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_mermelada) REFERENCES Mermelada(id_mermelada) ON DELETE CASCADE
);

CREATE TABLE Produccion (
    id_produccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_receta INTEGER NOT NULL,
    cantidad_frascos INTEGER NOT NULL,
    fecha_produccion DATETIME DEFAULT CURRENT_TIMESTAMP,
    codigo_lote_alfa TEXT UNIQUE, -- Formato MER-YYYYMMDD-ID
    estado TEXT DEFAULT 'pendiente',
    brix_real_medido DECIMAL(5,2),
    temp_max_alcanzada DECIMAL(5,2),
    FOREIGN KEY (id_receta) REFERENCES Receta(id_receta) ON DELETE CASCADE
);
