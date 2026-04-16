import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import date, timedelta
from tkcalendar import DateEntry

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración de Ventana
        self.title("ORBACLUAP")
        self.geometry("350x500")
        
        # Variables de control
        self.is_directory = tk.BooleanVar(value=False)
        self.var_input_path = tk.StringVar(value="")
        self.var_output_path = tk.StringVar(value="")
        self.normalizers = {}

        # Variable de Fecha (Ayer por defecto)
        ayer = date.today() - timedelta(days=1)
        self.var_fecha = tk.StringVar(value=ayer.strftime("%d/%m/%Y"))

        self._crear_widgets()
        self._layout()

    def _crear_widgets(self):
        """Inicializa todos los componentes de la interfaz"""
        
        # Sección Origen
        self.lbl_origen = tk.Label(self, text="Seleccione origen de datos:")
        self.frame_input = tk.Frame(self)
        self.entry_input = tk.Entry(self.frame_input, textvariable=self.var_input_path, width=40)
        self.btn_input = ttk.Button(self.frame_input, text="...", width=3, command=self._seleccionar_origen)
        self.chk_dir = tk.Checkbutton(self, text="Es un directorio", variable=self.is_directory)

        # Sección Salida
        self.lbl_destino = tk.Label(self, text="Carpeta de salida:")
        self.frame_output = tk.Frame(self)
        self.entry_output = tk.Entry(self.frame_output, textvariable=self.var_output_path, width=40)
        self.btn_output = ttk.Button(self.frame_output, text="...", width=3, command=self._seleccionar_destino)

        # Cliente y Fecha
        self.lbl_cliente = tk.Label(self, text="Cliente seleccionado:")
        self.combo_clients = ttk.Combobox(self, state='readonly')
        
        self.lbl_fecha_txt = tk.Label(self, text="Fecha de proceso:")
        self.cal = DateEntry(
            self, textvariable=self.var_fecha, date_pattern='dd/mm/yyyy',
            background='darkblue', foreground='white', borderwidth=2
        )

        # Botones de Acción
        self.btn_ventas = ttk.Button(self, text="GENERAR VENTAS")
        self.btn_stock = ttk.Button(self, text="GENERAR STOCK")

    def _layout(self):
        """Organiza los widgets en la ventana"""
        padding = {'padx': 15, 'pady': 5}
        
        # Origen
        self.lbl_origen.pack(anchor="w", **padding)
        self.frame_input.pack(fill="x", **padding)
        self.entry_input.pack(side="left", expand=True, fill="x")
        self.btn_input.pack(side="right", padx=(5, 0))
        self.chk_dir.pack(anchor="e", padx=15)

        # Destino
        self.lbl_destino.pack(anchor="w", **padding)
        self.frame_output.pack(fill="x", **padding)
        self.entry_output.pack(side="left", expand=True, fill="x")
        self.btn_output.pack(side="right", padx=(5, 0))

        # Configuración
        self.lbl_cliente.pack(anchor="w", **padding)
        self.combo_clients.pack(fill="x", **padding)
        
        self.lbl_fecha_txt.pack(anchor="w", **padding)
        self.cal.pack(fill="x", **padding)

        # Botones finales
        self.btn_ventas.pack(fill="x", padx=15, pady=(20, 5))
        self.btn_stock.pack(fill="x", padx=15, pady=5)

    # --- Lógica de Archivos (Reemplaza a Chooser) ---

    def _seleccionar_origen(self):
        if self.is_directory.get():
            path = filedialog.askdirectory(title="Seleccionar Carpeta")
        else:
            path = filedialog.askopenfilename(title="Seleccionar Archivo")
        
        if path:
            self.var_input_path.set(path)

    def _seleccionar_destino(self):
        path = filedialog.askdirectory(title="Seleccionar Carpeta de Salida")
        if path:
            self.var_output_path.set(path)

    # --- Métodos de Interfaz (API para el Controlador) ---

    def set_combobox_values(self, normalizers: dict):
        self.normalizers = normalizers
        self.combo_clients["values"] = list(normalizers.keys())
        if normalizers:
            self.combo_clients.current(0)

    def get_normalizer_seleccionado(self):
        nombre = self.combo_clients.get()
        return self.normalizers.get(nombre)

    def get_date(self):
        return self.var_fecha.get()

    def set_on_generate_sells(self, callback):
        # El callback ahora recibirá los parámetros necesarios directamente
        self.btn_ventas.config(command=lambda: callback(
            self.get_normalizer_seleccionado(), 
            Path(self.var_input_path.get())
        ))

    def set_on_generate_inventory(self, callback):
        self.btn_stock.config(command=lambda: callback(
            self.get_normalizer_seleccionado(), 
            Path(self.var_input_path.get())
        ))

    def show_success(self, filename):
        return messagebox.askyesno("Terminado", f"Archivo {filename} creado con éxito. ¿Desea abrirlo?")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()