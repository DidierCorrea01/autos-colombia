"""Autos Colombia - Iteración 1: ventana principal (tkinter)."""
import tkinter as tk
from tkinter import ttk

import logica

VERDE, ROJO, AZUL = "#2e9e5b", "#d64545", "#1f4e8c"
FONDO = "#f4f6f9"


class Aplicacion(tk.Tk):  # pylint: disable=too-many-instance-attributes
    """Ventana principal: muestra los datos y le pasa las acciones a logica.py."""

    def __init__(self):
        super().__init__()
        # Variables ligadas a los campos de texto
        self.var_placa = tk.StringVar()
        self.var_placa2 = tk.StringVar()
        self.var_propietario = tk.StringVar()
        self.var_dias = tk.StringVar(value="30")
        # Elementos de la ventana que se crean más abajo
        self.lbl_resumen = None
        self.lbl_estado = None
        self.tab_operacion = None
        self.tab_historial = None
        self.marco_celdas = None
        self.tabla_adentro = None
        self.tabla_historial = None
        self.title("Autos Colombia - Control de acceso")
        self.geometry("980x640")
        self.minsize(900, 600)
        self.configure(bg=FONDO)
        self.estilos()
        self.crear_encabezado()
        self.crear_pestanas()
        self.crear_barra_estado()
        self.refrescar()

    def estilos(self):
        """Define colores y tipografías de los componentes."""
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=FONDO)
        estilo.configure("TLabel", background=FONDO, font=("Segoe UI", 10))
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        estilo.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("TLabelframe", background=FONDO)
        estilo.configure("TLabelframe.Label", background=FONDO,
                         font=("Segoe UI", 10, "bold"), foreground=AZUL)

    def crear_encabezado(self):
        """Crea la franja azul superior con el nombre y el contador de celdas."""
        barra = tk.Frame(self, bg=AZUL, height=60)
        barra.pack(fill="x")
        tk.Label(barra, text="Autos Colombia", bg=AZUL, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20, pady=12)
        self.lbl_resumen = tk.Label(barra, text="", bg=AZUL, fg="white",
                                    font=("Segoe UI", 11))
        self.lbl_resumen.pack(side="right", padx=20)

    def crear_pestanas(self):
        """Crea las pestañas Operación e Historial."""
        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True, padx=12, pady=(10, 0))
        self.tab_operacion = ttk.Frame(pestanas)
        self.tab_historial = ttk.Frame(pestanas)
        pestanas.add(self.tab_operacion, text="  Operación  ")
        pestanas.add(self.tab_historial, text="  Historial  ")
        self.armar_operacion()
        self.armar_historial()

    def armar_operacion(self):
        """Arma la pantalla de Operación: formularios, celdas y tabla de vehículos."""
        izquierda = ttk.Frame(self.tab_operacion)
        izquierda.pack(side="left", fill="y", padx=(10, 6), pady=10)
        derecha = ttk.Frame(self.tab_operacion)
        derecha.pack(side="left", fill="both", expand=True, padx=(6, 10), pady=10)

        # --- Acceso rápido: entrada y salida ---
        caja = ttk.LabelFrame(izquierda, text="Entrada / salida", padding=12)
        caja.pack(fill="x")
        ttk.Label(caja, text="Placa").pack(anchor="w")
        entrada = ttk.Entry(caja, textvariable=self.var_placa, width=24,
                            font=("Segoe UI", 14))
        entrada.pack(fill="x", pady=(2, 10))
        entrada.bind("<Return>", lambda e: self.hacer_entrada())
        fila = ttk.Frame(caja)
        fila.pack(fill="x")
        ttk.Button(fila, text="Registrar entrada",
                   command=self.hacer_entrada).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(fila, text="Registrar salida",
                   command=self.hacer_salida).pack(side="left", expand=True, fill="x", padx=(4, 0))

        # --- Registro de vehículo / mensualidad ---
        caja2 = ttk.LabelFrame(
            izquierda, text="Registrar vehículo / renovar mensualidad", padding=12)
        caja2.pack(fill="x", pady=(14, 0))
        ttk.Label(caja2, text="Placa").pack(anchor="w")
        ttk.Entry(caja2, textvariable=self.var_placa2).pack(fill="x", pady=(2, 6))
        ttk.Label(caja2, text="Propietario").pack(anchor="w")
        ttk.Entry(caja2, textvariable=self.var_propietario).pack(fill="x", pady=(2, 6))
        ttk.Label(caja2, text="Días de mensualidad desde hoy").pack(anchor="w")
        ttk.Entry(caja2, textvariable=self.var_dias).pack(fill="x", pady=(2, 4))
        ttk.Label(caja2, text="(un número negativo la deja vencida, sirve para probar)",
                  foreground="#666666", font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 8))
        ttk.Button(caja2, text="Guardar vehículo",
                   command=self.hacer_registro).pack(fill="x")

        # --- Celdas ---
        caja3 = ttk.LabelFrame(derecha, text="Celdas", padding=10)
        caja3.pack(fill="x")
        self.marco_celdas = tk.Frame(caja3, bg=FONDO)
        self.marco_celdas.pack(fill="x")

        # --- Vehículos adentro ---
        caja4 = ttk.LabelFrame(derecha, text="Vehículos adentro", padding=10)
        caja4.pack(fill="both", expand=True, pady=(12, 0))
        columnas = ("celda", "placa", "propietario", "entrada")
        self.tabla_adentro = ttk.Treeview(caja4, columns=columnas, show="headings", height=8)
        for col, texto, ancho in [("celda", "Celda", 60), ("placa", "Placa", 110),
                                  ("propietario", "Propietario", 200), ("entrada", "Entró", 170)]:
            self.tabla_adentro.heading(col, text=texto)
            self.tabla_adentro.column(col, width=ancho, anchor="w")
        self.tabla_adentro.pack(fill="both", expand=True)

    def armar_historial(self):
        """Arma la tabla de la pestaña Historial."""
        columnas = ("placa", "celda", "entrada", "salida")
        self.tabla_historial = ttk.Treeview(self.tab_historial, columns=columnas,
                                            show="headings")
        for col, texto, ancho in [("placa", "Placa", 140), ("celda", "Celda", 80),
                                  ("entrada", "Entrada", 220), ("salida", "Salida", 220)]:
            self.tabla_historial.heading(col, text=texto)
            self.tabla_historial.column(col, width=ancho, anchor="w")
        self.tabla_historial.pack(fill="both", expand=True, padx=10, pady=10)

    def crear_barra_estado(self):
        """Crea la barra inferior donde se muestra el resultado de cada acción."""
        self.lbl_estado = tk.Label(self, text="Listo", anchor="w", bg="#e3e8ef",
                                   fg="#333333", font=("Segoe UI", 10), padx=14, pady=8)
        self.lbl_estado.pack(fill="x", side="bottom")

    # ---------- acciones ----------
    def mostrar(self, resultado):
        """Muestra el mensaje en verde (ok) o rojo (error) y refresca la pantalla."""
        ok, mensaje = resultado
        self.lbl_estado.config(text=("✔ " if ok else "✖ ") + mensaje,
                               bg="#d9f2e3" if ok else "#fbe0e0",
                               fg="#17653a" if ok else "#9c2323")
        self.refrescar()
        return ok

    def hacer_entrada(self):
        """Registra la entrada de la placa escrita arriba."""
        if self.mostrar(logica.registrar_entrada(self.var_placa.get())):
            self.var_placa.set("")

    def hacer_salida(self):
        """Registra la salida de la placa escrita arriba."""
        if self.mostrar(logica.registrar_salida(self.var_placa.get())):
            self.var_placa.set("")

    def hacer_registro(self):
        """Guarda el vehículo del formulario (alta o renovación de mensualidad)."""
        ok = self.mostrar(logica.registrar_vehiculo(
            self.var_placa2.get(), self.var_propietario.get(), self.var_dias.get()))
        if ok:
            self.var_placa.set(self.var_placa2.get().strip().upper())
            self.var_placa2.set("")
            self.var_propietario.set("")
            self.var_dias.set("30")

    def refrescar(self):
        """Vuelve a leer celdas, vehículos adentro e historial y los dibuja."""
        for widget in self.marco_celdas.winfo_children():
            widget.destroy()
        celdas = logica.estado_celdas()
        for i, c in enumerate(celdas):
            libre = not c["ocupada"]
            tk.Label(self.marco_celdas, text=str(c["numero"]), width=6, height=2,
                     bg=VERDE if libre else ROJO, fg="white",
                     font=("Segoe UI", 11, "bold")).grid(row=i // 5, column=i % 5,
                                                         padx=4, pady=4, sticky="ew")
        for col in range(5):
            self.marco_celdas.grid_columnconfigure(col, weight=1)
        libres = sum(1 for c in celdas if not c["ocupada"])
        self.lbl_resumen.config(text=f"Celdas libres: {libres} de {len(celdas)}")

        self.tabla_adentro.delete(*self.tabla_adentro.get_children())
        for f in logica.vehiculos_adentro():
            self.tabla_adentro.insert("", "end", values=(f["celda"], f["placa"],
                                                         f["propietario"], f["entrada"]))
        self.tabla_historial.delete(*self.tabla_historial.get_children())
        for f in logica.historial():
            self.tabla_historial.insert("", "end", values=(f["placa"], f["celda"],
                                                           f["entrada"], f["salida"] or "-"))


if __name__ == "__main__":
    logica.crear_tablas()
    Aplicacion().mainloop()
