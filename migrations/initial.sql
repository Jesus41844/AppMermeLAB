-- Initial migration (derived from backend/schema.sql)

CREATE TABLE IF NOT EXISTS receta (
    id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    cantidad_frascos INTEGER NOT NULL,
    tamano_frasco_gramos INTEGER NOT NULL,
    tiempo_preparacion_min INTEGER NOT NULL,
    brix_min DECIMAL(5,2),
    brix_max DECIMAL(5,2),
    temperatura_min DECIMAL(5,2),
    temperatura_max DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS ingrediente (
    id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    unidad_medida_base TEXT NOT NULL,
    stock_disponible DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ingrediente_receta (
    id_receta INTEGER NOT NULL,
    id_ingrediente INTEGER NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    unidad_medida TEXT NOT NULL,
    PRIMARY KEY (id_receta, id_ingrediente),
    FOREIGN KEY (id_receta) REFERENCES receta(id_receta) ON DELETE CASCADE,
    FOREIGN KEY (id_ingrediente) REFERENCES ingrediente(id_ingrediente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mermelada (
    id_mermelada INTEGER PRIMARY KEY AUTOINCREMENT,
    sabor TEXT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock_frascos INTEGER DEFAULT 0,
    id_receta INTEGER NOT NULL,
    FOREIGN KEY (id_receta) REFERENCES receta(id_receta) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    correo TEXT,
    direccion TEXT
);

CREATE TABLE IF NOT EXISTS ventas (
    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL DEFAULT (date('now')),
    total DECIMAL(10,2) NOT NULL,
    id_cliente INTEGER NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS venta_mermelada (
    id_venta INTEGER NOT NULL,
    id_mermelada INTEGER NOT NULL,
    cantidad_frascos INTEGER NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_venta, id_mermelada),
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_mermelada) REFERENCES mermelada(id_mermelada) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS produccion (
    id_produccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_receta INTEGER NOT NULL,
    cantidad_frascos INTEGER NOT NULL,
    fecha_produccion DATE DEFAULT (date('now')),
    FOREIGN KEY (id_receta) REFERENCES receta(id_receta) ON DELETE CASCADE
);
