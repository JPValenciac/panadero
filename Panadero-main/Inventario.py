import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from BD import conectar_bd


def ventana_inventario(ventana):
    """Crea la ventana de inventario"""
    ventana.state("zoomed")
    ventana.title("Inventario - Panadería Dulce Hogar")
    ventana.geometry("900x600")
    ventana.config(bg="#fff8e1")
    ventana.iconbitmap("one piece.ico")
    ventana.attributes('-topmost', False)

    encabezado = tk.Frame(ventana, bg="#ffcc80", height=80)
    encabezado.pack(fill="x")
    titulo = tk.Label(encabezado, text="📦 Inventario de Productos", font=("Georgia", 20, "bold"),
                      bg="#ffcc80", fg="#4e342e", pady=10)
    titulo.pack()

    frame_principal = tk.Frame(ventana, bg="#fff8e1", padx=20, pady=20)
    frame_principal.pack(expand=True, fill="both")

    # Configuración de la tabla
    columnas = ("Nombre", "Precio Producción", "Precio Venta")
    tabla = ttk.Treeview(frame_principal, columns=columnas, show="headings", style="Custom.Treeview")

    # Definir la fuente y tamaño para los encabezados y las celdas
    estilo = ttk.Style()
    estilo.configure("Custom.Treeview.Heading", font=("Arial", 14, "bold"))  # Encabezados más grandes
    estilo.configure("Custom.Treeview", font=("Arial", 12))  # Datos en la tabla

    for col in columnas:
        tabla.heading(col, text=col, anchor="center")
        tabla.column(col, anchor="center", width=180)

    tabla.pack(expand=True, fill="both", pady=10)

    cargar_datos(tabla)

    frame_botones = tk.Frame(ventana, bg="#fff8e1")
    frame_botones.pack(pady=10, fill="x", padx=20)
    frame_botones.grid_columnconfigure((0, 1, 2), weight=1)  # Centrar botones

    # Estilo de los botones
    boton_ancho = 12  # Ajusta el ancho
    boton_alto = 3  # Ajusta la altura

    btn_agregar = tk.Button(frame_botones, text="➕ Agregar", font=("Arial", 14, "bold"), bg="#ffcc80", fg="#4e342e",
                            padx=10, width=boton_ancho, height=boton_alto, relief="raised",
                            command=lambda: agregar_producto(tabla))
    btn_agregar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    btn_editar = tk.Button(frame_botones, text="✏️ Editar", font=("Arial", 14, "bold"), bg="#ffcc80", fg="#4e342e",
                           padx=10, width=boton_ancho, height=boton_alto, relief="raised",
                           command=lambda: editar_producto(tabla, ventana))
    btn_editar.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    btn_eliminar = tk.Button(frame_botones, text="🗑️ Eliminar", font=("Arial", 14, "bold"), bg="#ffcc80", fg="#4e342e",
                             padx=10, width=boton_ancho, height=boton_alto, relief="raised",
                             command=lambda: eliminar_producto(tabla, ventana))
    btn_eliminar.grid(row=0, column=2, padx=10, pady=10, sticky="ew")


def cargar_datos(tabla):
    """Carga los productos desde la base de datos en la tabla"""
    tabla.delete(*tabla.get_children())
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, Nombre, PrecioP, PrecioV FROM inventario")
    for fila in cursor.fetchall():
        id_producto = fila[0]
        datos_visibles = fila[1:]  # Nombre, PrecioP, PrecioV
        tabla.insert("", "end", text=id_producto, values=datos_visibles)  # El ID queda oculto en "text"
    conn.close()



def centrar_ventana(ventana, ancho, alto):
    """Centra una ventana en la pantalla"""
    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() - ancho) // 2
    y = (ventana.winfo_screenheight() - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def agregar_producto(tabla):
    """Permite agregar un nuevo producto"""
    ventana_agregar = tk.Toplevel()
    ventana_agregar.title("➕ Agregar Nuevo Producto")
    ventana_agregar.geometry("500x400")
    ventana_agregar.config(bg="#fff8e1")
    ventana_agregar.iconbitmap("one piece.ico")
    ventana_agregar.attributes('-topmost', False)

    centrar_ventana(ventana_agregar, 500, 400)  # Centra la ventana

    fuente_label = ("Arial", 16, "bold")
    fuente_entry = ("Arial", 14)
    fuente_boton = ("Arial", 16, "bold")

    tk.Label(ventana_agregar, text="📌 Nombre:", bg="#fff8e1", font=fuente_label).pack(pady=8)
    entry_nombre = tk.Entry(ventana_agregar, font=fuente_entry, width=25)
    entry_nombre.pack(pady=5)

    tk.Label(ventana_agregar, text="💰 Precio de Producción:", bg="#fff8e1", font=fuente_label).pack(pady=8)
    entry_precio_produccion = tk.Entry(ventana_agregar, font=fuente_entry, width=25)
    entry_precio_produccion.pack(pady=5)

    tk.Label(ventana_agregar, text="💵 Precio de Venta:", bg="#fff8e1", font=fuente_label).pack(pady=8)
    entry_precio_venta = tk.Entry(ventana_agregar, font=fuente_entry, width=25)
    entry_precio_venta.pack(pady=5)

    def guardar_nuevo_producto():
        """Guarda un nuevo producto en la base de datos"""
        nombre = entry_nombre.get().strip()
        precio_venta = entry_precio_venta.get().strip()
        precio_produccion = entry_precio_produccion.get().strip()

        if not nombre or not precio_venta or not precio_produccion:
            messagebox.showwarning("⚠ Campos Vacíos", "Por favor, complete todos los campos antes de guardar.",
                                   parent=ventana_agregar)
            return

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventario (nombre, PrecioP, PrecioV) VALUES (?, ?, ?)",
                       (nombre, precio_produccion, precio_venta))
        conn.commit()
        conn.close()
        cargar_datos(tabla)
        ventana_agregar.destroy()

    tk.Button(ventana_agregar, text="💾 Guardar", font=fuente_boton, bg="#ff9800", fg="white",
              padx=20, pady=10, relief="raised", command=guardar_nuevo_producto).pack(pady=20)

def eliminar_producto(tabla, ventana):
    """Elimina un producto seleccionado de la tabla y la base de datos"""
    item_seleccionado = tabla.selection()
    if not item_seleccionado:
        messagebox.showwarning("🗑️ Eliminar Producto", "Seleccione un producto para eliminar.", parent=ventana)
        return

    item = item_seleccionado[0]
    id_producto = tabla.item(item, "text")  # El ID oculto
    producto = tabla.item(item, "values")  # Nombre, PrecioP, PrecioV

    respuesta = messagebox.askyesno("🗑️ Confirmar Eliminación",
                                    f"¿Está seguro de que desea eliminar '{producto[0]}'?",
                                    parent=ventana)

    if respuesta:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario WHERE id = ?", (id_producto,))
        conn.commit()
        conn.close()

        tabla.delete(item)  # Elimina visualmente
        messagebox.showinfo("✅ Eliminado", f"'{producto[0]}' ha sido eliminado.", parent=ventana)


def editar_producto(tabla, ventana):
    """Permite editar un producto existente"""
    item_seleccionado = tabla.selection()
    if not item_seleccionado:
        messagebox.showwarning("✏️ Editar Producto", "Seleccione un producto para editar.", parent=ventana)
        return

    item = item_seleccionado[0]
    producto_id = tabla.item(item, "text")  # Aquí obtienes el ID real
    producto = tabla.item(item, "values")  # Aquí obtienes los demás datos visibles

    # Crear la ventana para editar el producto
    ventana_editar = tk.Toplevel()
    ventana_editar.title("✏️ Editar Producto")
    ventana_editar.geometry("500x400")
    ventana_editar.config(bg="#fff8e1")
    ventana_editar.iconbitmap("one piece.ico")
    ventana_editar.attributes('-topmost', False)

    centrar_ventana(ventana_editar, 500, 400)  # Centra la ventana

    fuente_label = ("Arial", 16, "bold")
    fuente_entry = ("Arial", 14)
    fuente_boton = ("Arial", 16, "bold")

    # Campos para editar el producto
    tk.Label(ventana_editar, text="📌 Nombre:", bg="#fff8e1", font=fuente_label).pack(pady=8)
    entry_nombre = tk.Entry(ventana_editar, font=fuente_entry, width=25)
    entry_nombre.insert(0, producto[0])
    entry_nombre.pack(pady=5)

    tk.Label(ventana_editar, text="💰 Precio de Producción:", bg="#fff8e1", font=fuente_label).pack(pady=8)
    entry_precio_produccion = tk.Entry(ventana_editar, font=fuente_entry, width=25)
    entry_precio_produccion.insert(0, producto[1])
    entry_precio_produccion.pack(pady=5)

    tk.Label(ventana_editar, text="💵 Precio de Venta:", bg="#fff8e1", font=fuente_label).pack(pady=8)
    entry_precio_venta = tk.Entry(ventana_editar, font=fuente_entry, width=25)
    entry_precio_venta.insert(0, producto[2])
    entry_precio_venta.pack(pady=5)

    def guardar_edicion_producto():
        """Guarda los cambios realizados en el producto"""
        nombre = entry_nombre.get().strip()
        precio_venta = entry_precio_venta.get().strip()
        precio_produccion = entry_precio_produccion.get().strip()

        if not nombre or not precio_venta or not precio_produccion:
            messagebox.showwarning("⚠ Campos Vacíos", "Por favor, complete todos los campos antes de guardar.",
                                   parent=ventana_editar)
            return

        # Actualizar el producto en la base de datos
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventario SET nombre = ?, PrecioP = ?, PrecioV = ? WHERE id = ?",
                       (nombre, precio_produccion, precio_venta, producto_id))  # Usamos producto_id aquí
        conn.commit()
        conn.close()

        # Actualizar la vista de la tabla
        cargar_datos(tabla)

        # Cerrar la ventana de edición
        ventana_editar.destroy()

    # Botón para guardar los cambios
    tk.Button(ventana_editar, text="💾 Guardar Cambios", font=fuente_boton, bg="#ff9800", fg="white",
              padx=20, pady=10, relief="raised", command=guardar_edicion_producto).pack(pady=20)
