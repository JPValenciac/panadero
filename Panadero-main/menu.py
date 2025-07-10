import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from Inventario import ventana_inventario
from corte import ventana_corte

# Variable global para las ventanas secundarias y la imagen de fondo
ventana_abierta = None
imagen_fondo_tk = None  # Para evitar que la imagen sea eliminada por el recolector de basura


def quitar_fondo_blanco(imagen_path, nuevo_ancho, nuevo_alto):
    """Elimina el fondo blanco de una imagen y devuelve un objeto PhotoImage con fondo transparente y redimensionado."""
    img = Image.open(imagen_path).convert("RGBA")
    datos = img.getdata()
    nueva_img = []

    for item in datos:
        # Si el color es blanco (o casi blanco), hacerlo transparente
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            nueva_img.append((255, 255, 255, 0))  # Transparente
        else:
            nueva_img.append(item)

    img.putdata(nueva_img)
    img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def ventana_menu():
    global ventana_abierta, imagen_fondo_tk
    root = tk.Tk()
    root.title("Panadería Dulce Hogar")
    root.state("zoomed")  # Abre la ventana en modo maximizado
    root.iconbitmap("one piece.ico")  # Icono personalizado

    # Canvas para la imagen de fondo
    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Cargar y ajustar la imagen de fondo
    def actualizar_fondo(event=None):
        global imagen_fondo_tk
        ancho, alto = root.winfo_width(), root.winfo_height()
        imagen_fondo = Image.open("one piece2.jpg").resize((ancho, alto), Image.Resampling.LANCZOS)
        imagen_fondo_tk = ImageTk.PhotoImage(imagen_fondo)
        canvas.delete("fondo")  # Eliminar fondo anterior antes de actualizar
        canvas.create_image(0, 0, image=imagen_fondo_tk, anchor="nw", tags="fondo")

        # Reubicar elementos
        canvas.coords(texto_bienvenida_id, ancho // 2, alto // 4)
        canvas.coords(btn_inventario_id, ancho // 2 - 150, alto // 2)
        canvas.coords(btn_corte_id, ancho // 2 + 150, alto // 2)

    # Vincular evento de cambio de tamaño para actualizar la imagen
    root.bind("<Configure>", actualizar_fondo)

    # Estilos de los botones con bordes redondeados y colores personalizados
    style = ttk.Style()
    style.configure("TButton",
                    font=("Verdana", 14),
                    padding=10,
                    relief="flat",
                    background="#ffcc80",
                    foreground="#4e342e",
                    borderwidth=5)

    # Efectos de hover para los botones
    def on_enter(e):
        e.widget.configure(style="Hover.TButton")

    def on_leave(e):
        e.widget.configure(style="TButton")

    style.configure("Hover.TButton",
                    font=("Verdana", 14),
                    padding=10,
                    relief="flat",
                    background="#d4a373",
                    foreground="white",
                    borderwidth=5)

    def abrir_ventana(funcion_ventana):
        global ventana_abierta
        if ventana_abierta and ventana_abierta.winfo_exists():
            ventana_abierta.destroy()

        ventana_abierta = tk.Toplevel()  # No le pasamos root
        ventana_abierta.geometry("600x400")
        ventana_abierta.title("Gestión de Panadería")

        # Asegurar que solo se cierre la ventana secundaria
        ventana_abierta.protocol("WM_DELETE_WINDOW", lambda: ventana_abierta.destroy())

        funcion_ventana(ventana_abierta)

    # Definir el tamaño de los botones
    boton_ancho = 120
    boton_alto = 120

    # Texto de bienvenida
    texto_bienvenida = tk.Label(root, text="🍞 Bienvenido a la Panadería Dulce Hogar 🥐",
                                font=("Georgia", 24, "bold"), fg="white", bg="black", padx=20, pady=10)

    # Cargar imágenes sin fondo y ajustarlas al tamaño del botón
    icono_inv = quitar_fondo_blanco("inventario.png", boton_ancho, boton_alto)
    icono_corte = quitar_fondo_blanco("corte.png", boton_ancho, boton_alto)

    # Crear botones con iconos grandes y cuadrados
    btn_inventario = ttk.Button(root, text="  Inventario  ", command=lambda: abrir_ventana(ventana_inventario))
    btn_inventario.config(compound="top", image=icono_inv, padding=40, width=12)

    btn_corte = ttk.Button(root, text="  Corte  ", command=lambda: abrir_ventana(ventana_corte))
    btn_corte.config(compound="top", image=icono_corte, padding=40, width=12)

    # Posicionar elementos en el canvas con separación entre los botones
    texto_bienvenida_id = canvas.create_window(0, 0, window=texto_bienvenida, anchor="center")
    btn_inventario_id = canvas.create_window(0, 0, window=btn_inventario, anchor="center")
    btn_corte_id = canvas.create_window(0, 0, window=btn_corte, anchor="center")

    # Reubicar los botones con separación mayor
    canvas.coords(btn_inventario_id, root.winfo_width() // 2 - 150, root.winfo_height() // 2)
    canvas.coords(btn_corte_id, root.winfo_width() // 2 + 150, root.winfo_height() // 2)

    # Iniciar la aplicación
    root.mainloop()
