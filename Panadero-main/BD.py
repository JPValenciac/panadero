import sqlite3
import os


def inicializar_bd():
    """Crea la base de datos y las tablas si no existen."""
    # Ruta del archivo de base de datos SQLite
    ruta_bd = "panadero.db"

    # Conexión a la base de datos (se crea si no existe)
    conexion = sqlite3.connect(ruta_bd)
    cursor = conexion.cursor()

    # Crear tabla 'corte' si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corte (
            fecha TEXT PRIMARY KEY,
            datos TEXT NOT NULL
        )
    """)

    # Crear tabla 'inventario' si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            PrecioP REAL NOT NULL,
            PrecioV REAL NOT NULL
        )
    """)

    conexion.commit()
    cursor.close()
    conexion.close()


def conectar_bd():
    """Establece la conexión con la base de datos SQLite."""
    return sqlite3.connect("panadero.db")


# Ejecutar la inicialización de la base de datos antes de conectarse
inicializar_bd()
