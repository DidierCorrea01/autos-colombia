"""Autos Colombia - Iteración 2: ventana principal (tkinter)."""
import tkinter as tk
from tkinter import ttk

import logica

VERDE, ROJO, AZUL = "#2e9e5b", "#d64545", "#1f4e8c"
FONDO = "#f4f6f9"


GRIS = "#8a8f98"


class Aplicacion(tk.Tk):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """Ventana principal: muestra los datos y le pasa las acciones a logica.py."""

    def __init__(self):
        super().__init__()
        # Variables ligadas a los campos de texto
        self.var_placa = tk.StringVar()
        self.var_placa2 = tk.StringVar()
        self.var_documento_veh = tk.StringVar()
        self.var_tipo_veh = tk.StringVar(value="carro")
        self.var_dias = tk.StringVar(value="30")
        # Clientes
        self.var_busqueda = tk.StringVar()
        self.var_documento = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_correo = tk.StringVar()
        # Celdas
        self.var_numero_celda = tk.StringVar()
        self.var_tipo_celda = tk.StringVar(value="carro")
        # Elementos de la ventana que se crean más abajo
        self.lbl_resumen = None
        self.lbl_estado = None
        self.tab_operacion = None
        self.tab_historial = None
        self.tab_clientes = None
        self.tab_celdas = None
        self.entrada_documento = None
        self.tabla_clientes = None
        self.tabla_celdas = None
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
        """Crea las pestañas Operación, Clientes, Celdas e Historial."""
        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True, padx=12, pady=(10, 0))
        self.tab_operacion = ttk.Frame(pestanas)
        self.tab_clientes = ttk.Frame(pestanas)
        self.tab_celdas = ttk.Frame(pestanas)
        self.tab_historial = ttk.Frame(pestanas)
        pestanas.add(self.tab_operacion, text="  Operación  ")
        pestanas.add(self.tab_clientes, text="  Clientes  ")
        pestanas.add(self.tab_celdas, text="  Celdas  ")
        pestanas.add(self.tab_historial, text="  Historial  ")
        self.armar_operacion()
        self.armar_clientes()
        self.armar_celdas()
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
        ttk.Label(caja2, text="Documento del cliente").pack(anchor="w")
        ttk.Entry(caja2, textvariable=self.var_documento_veh).pack(fill="x", pady=(2, 6))
        ttk.Label(caja2, text="Tipo de vehículo").pack(anchor="w")
        ttk.Combobox(caja2, textvariable=self.var_tipo_veh, values=("carro", "moto"),
                     state="readonly").pack(fill="x", pady=(2, 6))
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

    def armar_clientes(self):
        """Arma la pestaña Clientes: formulario a la izquierda y tabla con buscador."""
        izquierda = ttk.Frame(self.tab_clientes)
        izquierda.pack(side="left", fill="y", padx=(10, 6), pady=10)
        derecha = ttk.Frame(self.tab_clientes)
        derecha.pack(side="left", fill="both", expand=True, padx=(6, 10), pady=10)

        caja = ttk.LabelFrame(izquierda, text="Datos del cliente", padding=12)
        caja.pack(fill="x")
        ttk.Label(caja, text="Documento").pack(anchor="w")
        self.entrada_documento = ttk.Entry(caja, textvariable=self.var_documento)
        self.entrada_documento.pack(fill="x", pady=(2, 6))
        for texto, variable in (("Nombre", self.var_nombre), ("Teléfono", self.var_telefono),
                                ("Correo", self.var_correo)):
            ttk.Label(caja, text=texto).pack(anchor="w")
            ttk.Entry(caja, textvariable=variable).pack(fill="x", pady=(2, 6))
        ttk.Button(caja, text="Registrar cliente nuevo",
                   command=self.hacer_cliente_nuevo).pack(fill="x", pady=(6, 4))
        ttk.Button(caja, text="Guardar cambios",
                   command=self.hacer_cliente_editar).pack(fill="x", pady=4)
        ttk.Button(caja, text="Desactivar / activar",
                   command=self.hacer_cliente_estado).pack(fill="x", pady=4)
        ttk.Button(caja, text="Limpiar formulario",
                   command=self.limpiar_cliente).pack(fill="x", pady=4)

        buscador = ttk.Frame(derecha)
        buscador.pack(fill="x")
        ttk.Label(buscador, text="Buscar por documento o nombre").pack(side="left")
        busqueda = ttk.Entry(buscador, textvariable=self.var_busqueda)
        busqueda.pack(side="left", fill="x", expand=True, padx=8)
        busqueda.bind("<KeyRelease>", lambda e: self.refrescar())
        columnas = ("documento", "nombre", "telefono", "correo", "estado")
        self.tabla_clientes = ttk.Treeview(derecha, columns=columnas, show="headings")
        for col, texto, ancho in [("documento", "Documento", 110), ("nombre", "Nombre", 190),
                                  ("telefono", "Teléfono", 110), ("correo", "Correo", 190),
                                  ("estado", "Estado", 80)]:
            self.tabla_clientes.heading(col, text=texto)
            self.tabla_clientes.column(col, width=ancho, anchor="w")
        self.tabla_clientes.pack(fill="both", expand=True, pady=(10, 0))
        self.tabla_clientes.bind("<<TreeviewSelect>>", lambda e: self.cargar_cliente())

    def armar_celdas(self):
        """Arma la pestaña Celdas: crear celdas, cambiar estado y ver la lista."""
        izquierda = ttk.Frame(self.tab_celdas)
        izquierda.pack(side="left", fill="y", padx=(10, 6), pady=10)
        derecha = ttk.Frame(self.tab_celdas)
        derecha.pack(side="left", fill="both", expand=True, padx=(6, 10), pady=10)

        caja = ttk.LabelFrame(izquierda, text="Crear celda", padding=12)
        caja.pack(fill="x")
        ttk.Label(caja, text="Número").pack(anchor="w")
        ttk.Entry(caja, textvariable=self.var_numero_celda).pack(fill="x", pady=(2, 6))
        ttk.Label(caja, text="Tipo").pack(anchor="w")
        ttk.Combobox(caja, textvariable=self.var_tipo_celda, values=("carro", "moto"),
                     state="readonly").pack(fill="x", pady=(2, 8))
        ttk.Button(caja, text="Crear celda", command=self.hacer_celda_nueva).pack(fill="x")

        caja2 = ttk.LabelFrame(izquierda, text="Estado de la celda seleccionada", padding=12)
        caja2.pack(fill="x", pady=(14, 0))
        ttk.Button(caja2, text="Poner en mantenimiento",
                   command=lambda: self.hacer_celda_estado("mantenimiento")).pack(fill="x", pady=4)
        ttk.Button(caja2, text="Reactivar celda",
                   command=lambda: self.hacer_celda_estado("activa")).pack(fill="x", pady=4)

        columnas = ("numero", "tipo", "estado", "ocupacion")
        self.tabla_celdas = ttk.Treeview(derecha, columns=columnas, show="headings")
        for col, texto, ancho in [("numero", "Celda", 80), ("tipo", "Tipo", 100),
                                  ("estado", "Estado", 140), ("ocupacion", "Ocupación", 120)]:
            self.tabla_celdas.heading(col, text=texto)
            self.tabla_celdas.column(col, width=ancho, anchor="w")
        self.tabla_celdas.pack(fill="both", expand=True)

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
            self.var_placa2.get(), self.var_documento_veh.get(),
            self.var_tipo_veh.get(), self.var_dias.get()))
        if ok:
            self.var_placa.set(self.var_placa2.get().strip().upper())
            self.var_placa2.set("")
            self.var_documento_veh.set("")
            self.var_dias.set("30")

    def hacer_cliente_nuevo(self):
        """Registra el cliente escrito en el formulario."""
        if self.mostrar(logica.registrar_cliente(
                self.var_documento.get(), self.var_nombre.get(),
                self.var_telefono.get(), self.var_correo.get())):
            self.limpiar_cliente()

    def hacer_cliente_editar(self):
        """Guarda los cambios del cliente seleccionado (el documento no cambia)."""
        self.mostrar(logica.editar_cliente(
            self.var_documento.get(), self.var_nombre.get(),
            self.var_telefono.get(), self.var_correo.get()))

    def hacer_cliente_estado(self):
        """Desactiva el cliente seleccionado si está activo, o lo activa si no."""
        seleccion = self.tabla_clientes.selection()
        if not seleccion:
            self.mostrar((False, "Selecciona un cliente de la tabla"))
            return
        valores = self.tabla_clientes.item(seleccion[0], "values")
        self.mostrar(logica.cambiar_estado_cliente(str(valores[0]), valores[4] != "Activo"))

    def cargar_cliente(self):
        """Pasa al formulario los datos del cliente seleccionado en la tabla."""
        seleccion = self.tabla_clientes.selection()
        if not seleccion:
            return
        valores = self.tabla_clientes.item(seleccion[0], "values")
        self.var_documento.set(valores[0])
        self.var_nombre.set(valores[1])
        self.var_telefono.set(valores[2])
        self.var_correo.set(valores[3])
        self.entrada_documento.config(state="disabled")

    def limpiar_cliente(self):
        """Vacía el formulario de clientes y vuelve a habilitar el documento."""
        self.entrada_documento.config(state="normal")
        for variable in (self.var_documento, self.var_nombre,
                         self.var_telefono, self.var_correo):
            variable.set("")
        self.tabla_clientes.selection_remove(*self.tabla_clientes.selection())

    def hacer_celda_nueva(self):
        """Crea la celda indicada en el formulario."""
        if self.mostrar(logica.crear_celda(self.var_numero_celda.get(),
                                           self.var_tipo_celda.get())):
            self.var_numero_celda.set("")

    def hacer_celda_estado(self, estado):
        """Cambia el estado de la celda seleccionada en la tabla."""
        seleccion = self.tabla_celdas.selection()
        if not seleccion:
            self.mostrar((False, "Selecciona una celda de la tabla"))
            return
        numero = int(self.tabla_celdas.item(seleccion[0], "values")[0])
        self.mostrar(logica.cambiar_estado_celda(numero, estado))

    def refrescar(self):
        """Vuelve a leer celdas, clientes, vehículos e historial y los dibuja."""
        self.dibujar_celdas()
        self.tabla_adentro.delete(*self.tabla_adentro.get_children())
        for f in logica.vehiculos_adentro():
            self.tabla_adentro.insert("", "end", values=(f["celda"], f["placa"],
                                                         f["propietario"], f["entrada"]))
        self.tabla_historial.delete(*self.tabla_historial.get_children())
        for f in logica.historial():
            self.tabla_historial.insert("", "end", values=(f["placa"], f["celda"],
                                                           f["entrada"], f["salida"] or "-"))
        self.tabla_clientes.delete(*self.tabla_clientes.get_children())
        for f in logica.buscar_clientes(self.var_busqueda.get()):
            self.tabla_clientes.insert("", "end", values=(
                f["documento"], f["nombre"], f["telefono"] or "", f["correo"] or "",
                "Activo" if f["activo"] else "Inactivo"))

    def dibujar_celdas(self):
        """Dibuja el tablero de celdas y la tabla de la pestaña Celdas."""
        for widget in self.marco_celdas.winfo_children():
            widget.destroy()
        self.tabla_celdas.delete(*self.tabla_celdas.get_children())
        celdas = logica.estado_celdas()
        for i, c in enumerate(celdas):
            if c["estado"] == "mantenimiento":
                color = GRIS
            else:
                color = ROJO if c["ocupada"] else VERDE
            tk.Label(self.marco_celdas, text=f"{c['numero']}\n{c['tipo']}", width=6, height=2,
                     bg=color, fg="white",
                     font=("Segoe UI", 10, "bold")).grid(row=i // 5, column=i % 5,
                                                         padx=4, pady=4, sticky="ew")
            ocupacion = "Ocupada" if c["ocupada"] else "Libre"
            self.tabla_celdas.insert("", "end", values=(
                c["numero"], c["tipo"], c["estado"].capitalize(), ocupacion))
        for col in range(5):
            self.marco_celdas.grid_columnconfigure(col, weight=1)
        libres = sum(1 for c in celdas if not c["ocupada"] and c["estado"] == "activa")
        self.lbl_resumen.config(text=f"Celdas libres: {libres} de {len(celdas)}")


if __name__ == "__main__":
    logica.crear_tablas()
    Aplicacion().mainloop()
