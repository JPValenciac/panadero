import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
from BD import conectar_bd
from tkcalendar import DateEntry


def ventana_corte(ventana):
    ventana.title("Corte")
    ventana.geometry("1200x600")
    ventana.config(bg="#fff8e1")
    ventana.iconbitmap("one piece.ico")
    ventana.state("zoomed")

    fecha_actual = datetime.now().strftime("%Y/%m/%d")

    # Estilos
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#ffcc80", foreground="#4e342e")
    style.configure("Treeview", font=("Arial", 11), rowheight=25, background="#fffbe6", foreground="#4e342e")

    # Encabezado
    encabezado = tk.Frame(ventana, bg="#ffcc80", height=100)
    encabezado.pack(fill="x")
    titulo = tk.Label(encabezado, text=f"🍞 Panadería Dulce Hogar 🥐 - Corte del {fecha_actual}",
                      font=("Georgia", 20, "bold"), bg="#ffcc80", fg="#4e342e", pady=20)
    titulo.pack()

    # Contenedor principal
    frame_principal = tk.Frame(ventana, bg="#fff8e1", padx=20, pady=20)
    frame_principal.pack(expand=True, fill="both")

    columnas = (
        "Nombre", "Precio Prod.", "Precio Venta", "Cantidad Prod", "Cant. Vendida", "Total Prod.", "Total Vendido", "Ganancias")
    tabla = ttk.Treeview(frame_principal, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col, anchor="center")
        tabla.column(col, anchor="center", width=120)

    tabla.pack(expand=True, fill="both", pady=10)

    total_label = tk.Label(ventana, text="Ganancias Finales: $0.00", font=("Arial", 14, "bold"), bg="#fff8e1",
                           fg="#4e342e")
    total_label.pack(pady=10)

    def guardar_corte():
        total_ganancias = sum(float(tabla.item(item, "values")[7]) for item in tabla.get_children())

        if all(float(tabla.item(item, "values")[7]) == 0 for item in tabla.get_children()):
            messagebox.showwarning("Aviso", "No hay productos con ganancias registradas.", parent=ventana)
            return

        fecha_corte = datetime.now().strftime("%Y-%m-%d")

        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT COUNT(*) FROM corte WHERE fecha = ?", (fecha_corte,))
        existe_corte = cursor.fetchone()[0]

        corte_data = {
            "fecha": fecha_corte,
            "productos": []
        }

        for item in tabla.get_children():
            valores = tabla.item(item, "values")
            producto = {
                "nombre": valores[0],
                "precio_produccion": valores[1],
                "precio_venta": valores[2],
                "cantidad_producida": valores[3],
                "cantidad_vendida": valores[4],
                "total_produccion": valores[5],
                "total_vendido": valores[6],
                "ganancias": valores[7]
            }
            corte_data["productos"].append(producto)

        if existe_corte > 0:
            respuesta = messagebox.askyesno("Corte existente",
                                            f"Ya existe un corte registrado para la fecha {fecha_corte}.\n¿Deseas actualizarlo?",
                                            parent=ventana)
            if not respuesta:
                cursor.close()
                conexion.close()
                return

            cursor.execute("UPDATE corte SET datos = ? WHERE fecha = ?",
                           (json.dumps(corte_data["productos"]), fecha_corte))
            mensaje_exito = "Corte actualizado correctamente en la base de datos."
        else:
            cursor.execute("INSERT INTO corte (fecha, datos) VALUES (?, ?)",
                           (fecha_corte, json.dumps(corte_data["productos"])))
            mensaje_exito = "Corte guardado correctamente en la base de datos."

        conexion.commit()
        cursor.close()
        conexion.close()

        messagebox.showinfo("Éxito", mensaje_exito, parent=ventana)

    def actualizar_total_final():
        total_ganancias = sum(float(tabla.item(item, "values")[7]) for item in tabla.get_children())
        total_label.config(text=f"Ganancias Finales: ${total_ganancias:.2f}")

    def on_double_click(event):
        item = tabla.selection()[0]
        col = tabla.identify_column(event.x)
        col_index = int(col[1:]) - 1

        if col_index not in [3, 4]:
            return

        valores = list(tabla.item(item, "values"))
        entry = tk.Entry(tabla)
        entry.insert(0, valores[col_index])
        entry.select_range(0, tk.END)
        entry.focus()

        def guardar_valor(event=None):
            nuevo_valor = entry.get()
            if nuevo_valor.isdigit():
                nuevo_valor = int(nuevo_valor)
                cantidad_producida = int(valores[3])

                if col_index == 4 and nuevo_valor > cantidad_producida:
                    messagebox.showwarning("Error", "No puedes vender más de lo producido.", parent=ventana)
                else:
                    valores[col_index] = nuevo_valor
                    precio_produccion = float(valores[1])
                    precio_venta = float(valores[2])
                    cantidad_vendida = int(valores[4])

                    valores[5] = cantidad_producida * precio_produccion
                    valores[6] = cantidad_vendida * precio_venta
                    valores[7] = (cantidad_vendida * precio_venta) - (cantidad_producida * precio_produccion)

                    tabla.item(item, values=valores)
                    actualizar_total_final()

            entry.destroy()

        entry.bind("<Return>", guardar_valor)
        entry.bind("<FocusOut>", guardar_valor)

        x, y, width, height = tabla.bbox(item, col_index)
        entry.place(x=x, y=y, width=width, height=height)

    tabla.bind("<Double-1>", on_double_click)

    def cargar_datos_inventario():
        tabla.delete(*tabla.get_children())

        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT nombre, PrecioP, PrecioV FROM inventario")
        productos = cursor.fetchall()

        for producto in productos:
            tabla.insert("", "end", values=(
                producto[0], producto[1], producto[2],
                0, 0, 0, 0, 0
            ))

        cursor.close()
        conexion.close()
        actualizar_total_final()

    cargar_datos_inventario()

    menu_bar = tk.Menu(ventana)
    ventana.config(menu=menu_bar)
    menu_cortes = tk.Menu(menu_bar, tearoff=0)

    def abrir_ventana_cortes():
        ventana_cortes = tk.Toplevel(ventana)
        ventana_cortes.title("Cortes Anteriores")
        ventana_cortes.geometry("1000x600")
        ventana_cortes.config(bg="#fff8e1")
        ventana_cortes.iconbitmap("one piece.ico")

        tk.Label(ventana_cortes, text="Selecciona la fecha del corte:", font=("Arial", 12, "bold"), bg="#fff8e1",
                 fg="#4e342e").pack(pady=10)

        fecha_selector = DateEntry(ventana_cortes, font=("Arial", 12), date_pattern="dd-mm-yyyy")
        fecha_selector.pack(pady=10)

        frame_tabla = tk.Frame(ventana_cortes, bg="#fff8e1", padx=20, pady=20)
        frame_tabla.pack(expand=True, fill="both")

        tabla_cortes = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        for col in columnas:
            tabla_cortes.heading(col, text=col, anchor="center")
            tabla_cortes.column(col, anchor="center", width=120)
        tabla_cortes.pack(expand=True, fill="both", pady=10)

        total_cortes_label = tk.Label(ventana_cortes, text="Ganancias Finales: $0.00", font=("Arial", 14, "bold"),
                                      bg="#fff8e1", fg="#4e342e")
        total_cortes_label.pack(pady=10)

        def actualizar_total_cortes():
            total_ganancias = sum(float(tabla_cortes.item(item, "values")[7]) for item in tabla_cortes.get_children())
            total_cortes_label.config(text=f"Ganancias Finales: ${total_ganancias:.2f}")

        def cargar_corte_fecha():
            fecha_corte = fecha_selector.get_date().strftime("%Y-%m-%d")
            tabla_cortes.delete(*tabla_cortes.get_children())

            conexion = conectar_bd()
            cursor = conexion.cursor()

            cursor.execute("SELECT datos FROM corte WHERE fecha = ?", (fecha_corte,))
            corte = cursor.fetchone()

            if corte:
                productos = json.loads(corte[0])
                for producto in productos:
                    tabla_cortes.insert("", "end", values=tuple(producto.values()))
                actualizar_total_cortes()
            else:
                messagebox.showwarning("Aviso", "No hay corte en esta fecha.", parent=ventana_cortes)

            cursor.close()
            conexion.close()

        tk.Button(ventana_cortes, text="Cargar Corte", command=cargar_corte_fecha, font=("Arial", 12, "bold"),
                  bg="#ffcc80", fg="#4e342e").pack(pady=10)

    menu_cortes.add_command(label="Ver Cortes", command=abrir_ventana_cortes)

    tk.Button(ventana, text="Guardar Corte", command=guardar_corte, font=("Arial", 12, "bold"), bg="#ffcc80",
              fg="#4e342e").pack(pady=10)

    menu_bar.add_cascade(label="Cortes", menu=menu_cortes)
