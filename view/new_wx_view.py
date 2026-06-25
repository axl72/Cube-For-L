import wx
import wx.adv
from datetime import date
import datetime
import wx.grid as gridlib
from pathlib import Path
from view.wx_panels.stock_panel import StockPanel

# =====================================================================
# 1. COMPONENTE: VISTA ETL (Extracción, Transformación y Carga)
# =====================================================================
class viewETL(wx.Panel):
    PATH_INDEX = 0

    """
    Representa una vista/pantalla del sistema dedicada al proceso ETL.
    Hereda de wx.Panel, por lo que actúa como un contenedor de widgets 
    que puede ser empotrado en un Frame u otro contenedor.
    """
    def __init__(self, parent):
        # Inicializa el panel base asociándolo a su contenedor padre (parent)
        super().__init__(parent)
        
        # --- VARIABLES DE ESTADO ---
        # Variables de control locales para simular el comportamiento de 
        # StringVar/BooleanVar que se usan habitualmente en Tkinter.
        self.is_directory_val = False
        self.input_path_val = ""
        self.output_path_val = ""
        self.normalizers = {} # Diccionario para mapear nombres de clientes con objetos lógicos

        # --- CREACIÓN DE WIDGETS (CONTROLES) ---
        
        # 1. Selector de Fecha (Date Picker)
        self.lbl_fecha = wx.StaticText(self, label="Fecha seleccionada:") # Etiqueta de texto plano
        # wx.adv.DatePickerCtrl muestra un calendario desplegable nativo del SO
        self.cal = wx.adv.DatePickerCtrl(self, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        
        # Configuración por defecto del calendario: Establecer el día de ayer
        ayer = date.today() - datetime.timedelta(days=1)
        # Convertir la fecha de Python a una fecha compatible con wx (wx.DateTime)
        # Nota: En wx.DateTime, los meses van indexados desde 0 (Enero = 0, Diciembre = 11)
        dt_ayer = wx.DateTime(ayer.day, ayer.month - 1, ayer.year)
        self.cal.SetValue(dt_ayer)

        # 2. Sección de Entrada (Input)
        self.lbl_archivo = wx.StaticText(self, label="Seleccione un archivo/directorio:")
        self.input_selector = wx.TextCtrl(self) # Campo de texto editable (Caja de entrada)
        self.button_input = wx.Button(self, label="...", size=(30, -1)) # Botón de tres puntos. Altura (-1) hereda la de por defecto.

        # 2.1 bottón add path
        # Sizer horizontal para agrupar checkbox y botón juntos
        self.button_generate_sells = wx.Button(self, label="GENERAR VENTAS")
        self.button_generate_inventory = wx.Button(self, label="GENERAR STOCK")
        # ===========================================================================#
        self.box_options = wx.BoxSizer(wx.HORIZONTAL) # Sizer horizontal para agrupar checkbox y botón

        self.comboBox_clients = wx.ComboBox(self, style=wx.CB_READONLY)
        self.check_button = wx.CheckBox(self, label="Es un directorio") # Casilla de verificación
        self.add_path_button = wx.Button(self, label="Agregar ruta", size=(120, -1))
        self.box_options.AddStretchSpacer(1)
        self.box_options.Add(self.comboBox_clients, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5) # Agrega el ComboBox al sizer, alineado verticalmente y con margen derecho
        self.box_options.Add(self.button_generate_sells, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5) # Agrega el botón de generar ventas al mismo sizer, alineado verticalmente y con margen izquierdo
        self.box_options.Add(self.button_generate_inventory, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5) # Agrega el botón de generar stock al mismo sizer, alineado verticalmente y con margen izquierdo
        self.box_options.Add(self.check_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5) # Agrega checkbox al sizer con margen derecho
        self.box_options.Add(self.add_path_button, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        # ===========================================================================#    
        # 3. Sección de Salida (Output)
        self.lbl_output = wx.StaticText(self, label="Seleccione carpeta de salida:")
        self.input_selector_2 = wx.TextCtrl(self)
        self.button_input_2 = wx.Button(self, label="...", size=(30, -1))

        # 3.1 Sección Archivo generado (Output)

        self.lbl_archivo_generado = wx.StaticText(self, label="Archivo generado:")
        self.input_selector_3 = wx.TextCtrl(self)
        self.button_input_3 = wx.Button(self, label="Abrir", size=(60, -1))

        self.box_output_generated = wx.BoxSizer(wx.HORIZONTAL)
        self.box_output_generated.Add(self.lbl_archivo_generado, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.box_output_generated.Add(self.input_selector_3, 1, wx.EXPAND | wx.RIGHT, 5)
        self.box_output_generated.Add(self.button_input_3, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        # 4. Selector de Clientes (Combobox)
        # Lista desplegable estricta de solo lectura (style=wx.CB_READONLY) para evitar que el usuario escriba
        # self.lbl_cliente = wx.StaticText(self, label="Cliente seleccionado:")

        # 5. Botones de Acción final

        self.path_table = gridlib.Grid(self)
        self.path_table.CreateGrid(5, 5) # Crea una tabla de 5 filas y 5 columnas
        self.path_table.HideRowLabels() # Oculta etiquetas de filas para una apariencia más limpia
        self.path_table.SetColLabelValue(0, "Index")
        self.path_table.SetColLabelValue(1, "Input")
        self.path_table.SetColLabelValue(2, "Normalizer")
        self.path_table.SetColLabelValue(3, "Status")
        self.path_table.SetColLabelValue(4, "Execution Path")

        self.path_table.Bind(wx.EVT_SIZE, self.on_grid_resize) # Redimensiona columnas dinámicamente al cambiar el tamaño de la ventana
        # --- DISEÑO MECÁNICO (LAYOUT) CON SIZERS ---
        # Los sizers calculan de forma automática y dinámica el tamaño y la posición de los elementos.
        # main_sizer organiza los sub-bloques o widgets uno debajo del otro (VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Función auxiliar interna para estandarizar el espaciado (padding) de los elementos en el eje principal
        def add_widget(widget, proportion=0, flag=wx.EXPAND | wx.ALL, border=10):
            # proportion=0: No crece verticalmente si la ventana se estira.
            # flag=wx.EXPAND: Se estira a todo lo ancho horizontalmente.
            # flag=wx.ALL: Aplica el margen (border) a los 4 lados.
            main_sizer.Add(widget, proportion, flag, border)

        # Fila horizontal para la caja de texto y botón de Entrada
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_sizer.Add(self.input_selector, 1, wx.EXPAND) # proportion=1 indica que este widget absorbe el espacio sobrante
        input_sizer.Add(self.button_input, 0, wx.LEFT, 5)   # proportion=0 mantiene su tamaño fijo, añade 5px de margen izquierdo

        # Fila horizontal para la caja de texto y botón de Salida
        output_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_sizer.Add(self.input_selector_2, 1, wx.EXPAND)
        output_sizer.Add(self.button_input_2, 0, wx.LEFT, 5)

        add_widget(self.lbl_archivo, border=5)
        add_widget(input_sizer, border=10)

        add_widget(self.box_options, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10) # Agrega el sizer que contiene checkbox y botón juntos
        
        add_widget(self.lbl_output, border=5)
        add_widget(output_sizer, border=10)
        
        add_widget(self.box_output_generated, flag=wx.EXPAND | wx.ALL, border=10) # Agrega el sizer que contiene la sección de archivo generado

        
        add_widget(self.lbl_fecha, border=5)
        add_widget(self.cal)
        
 

        add_widget(self.path_table, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Asigna el sizer al panel y le ordena renderizar la interfaz con estas directrices
        self.SetSizer(main_sizer)

        # --- ENLACE DE EVENTOS (BINDINGS) ---
        # Conecta las interacciones de los controles a sus respectivos métodos manejadores (handlers)
        self.button_input.Bind(wx.EVT_BUTTON, self.on_select_input)
        self.button_input_2.Bind(wx.EVT_BUTTON, self.on_select_output)
        self.button_input_3.Bind(wx.EVT_BUTTON, self.on_add_path)
        self.cal.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_change)
        
        # Intenta centrar el componente (Nota: en sub-paneles esto suele delegarse al layout del Frame superior)
        self.Centre()

    # --- MÉTODOS DE INTERFAZ Y GETTERS/SETTERS ---
    def on_add_path(self, event):
        path = self.input_selector.GetValue().strip()
        normalizer = self.comboBox_clients.GetValue().strip()
        index = self.PATH_INDEX
        self.path_table.SetCellValue(index, 0, str(index + 1)) # Columna de índice
        self.path_table.SetCellValue(index, 1, path)          # Columna de ruta
        self.path_table.SetCellValue(index, 2, normalizer)    # Columna de normalizador
        self.path_table.SetCellValue(index, 3, "Pendiente")   # Columna de estado
        self.path_table.SetCellValue(index, 4, "")            # Columna de ruta de ejecución (vacía por ahora)
        self.input_selector.SetValue("") # Limpia la caja de texto después de agregar a la tabla
        self.PATH_INDEX += 1

    def on_grid_resize(self, event):
        total_width = self.path_table.GetSize().GetWidth()

        prop_col0 = 0.1
        prop_col1 = 0.5
        prop_col2 = 0.1
        prop_col3 = 0.3

        w0 = int(total_width * prop_col0)
        w1 = int(total_width * prop_col1)
        w2 = int(total_width * prop_col2)
        w3 = int(total_width * prop_col3)

        sobrante = total_width - (w0 + w1 + w2 + w3)
        w2 += sobrante

        self.path_table.SetColSize(0, w0)
        self.path_table.SetColSize(1, w1)
        self.path_table.SetColSize(2, w2)
        self.path_table.SetColSize(3, w3)

    def set_input_selector_2(self, text):
        """Asigna texto de forma programática a la segunda caja de texto (output)."""
        self.input_selector_2.SetValue(text)

    def get_normalizer_seleccionado(self):
        """Obtiene el objeto normalizador del cliente seleccionado en el ComboBox."""
        nombre = self.comboBox_clients.GetValue()
        return self.normalizers.get(nombre)

    def get_date(self):
        """
        Recupera el valor del DatePickerCtrl y retorna un string con formato 'dd/mm/yyyy'.
        Suma +1 al mes porque wxPython mapea Enero como 0.
        """
        date_wx = self.cal.GetValue()
        return f"{date_wx.GetDay():02d}/{date_wx.GetMonth()+1:02d}/{date_wx.GetYear()}"

    # --- EVENT HANDLERS (MANEJADORES DE EVENTOS) ---

    def on_select_input(self, event):
        """Lanza un diálogo nativo para elegir directorios o múltiples archivos basado en el checkbox."""
        paths = None
        if self.check_button.GetValue():
            # Abre ventana nativa para seleccionar carpetas
            dlg = wx.DirDialog(self, "Seleccione carpeta", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                paths = [dlg.GetPath()] # Retorna una lista con un único elemento
                self.input_selector.SetValue(paths[0]) # Muestra la ruta seleccionada en la caja de texto
        else:
            # Abre ventana nativa para seleccionar archivos (permite selección múltiple mediante flags)
            dlg = wx.FileDialog(self, "Seleccione archivo", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths() # Retorna una lista de rutas seleccionadas
                if len(paths) == 1:
                    self.input_selector.SetValue(paths[0]) # Muestra la ruta seleccionada en la caja de texto
            print("Seleccionar archivo")
        
        # Muestra el diálogo modal. Si el usuario confirma (Aceptar):
        if paths:
            print("Rutas seleccionadas: ", paths)
            if len(paths) > 1:
                for path in paths:
                    print("Ruta seleccionada: ", path)
                    # añadir a la tabla cada ruta seleccionada con su índice y estado inicial
                    if self.PATH_INDEX == self.path_table.GetNumberRows():
                        self.path_table.AppendRows(1) # Agrega una nueva fila al final de la tabla
                    self.path_table.AppendRows(1) # Agrega una nueva fila al final de la tabla
                    self.path_table.SetCellValue(self.PATH_INDEX, 0, str(self.PATH_INDEX + 1))
                    self.path_table.SetCellValue(self.PATH_INDEX, 1, path)
                    self.path_table.SetCellValue(self.PATH_INDEX, 2, "Pendiente")
                    self.path_table.SetCellValue(self.PATH_INDEX, 3, "")
                    self.PATH_INDEX += 1
            else:
                self.input_selector.SetValue(str(paths[0]))
            # Almacena internamente todas las rutas capturadas por si se necesita procesar selección múltiple
            self.selected_paths = paths

        # Destrucción explícita de la ventana de diálogo para liberar recursos en memoria C++
        dlg.Destroy()

    def on_select_output(self, event):
        """Lanza un diálogo modal nativo enfocado en seleccionar el directorio de destino final."""
        dlg = wx.DirDialog(self, "Seleccione carpeta de salida")
        if dlg.ShowModal() == wx.ID_OK:
            # .GetPath() en plural/singular funciona, en DirDialog .GetPath() retorna un único string
            self.input_selector_2.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_date_change(self, event):
        """Imprime por consola la nueva fecha cada vez que el usuario la cambia en el calendario."""
        print("Fecha seleccionada: ", self.get_date())

    def set_combobox_values(self, normalizers_dict: dict):
        """
        Puebla dinámicamente el Combobox de clientes usando las llaves de un diccionario.
        Selecciona de manera automática el primer cliente de la lista.
        """
        self.normalizers = normalizers_dict
        nombres = list(normalizers_dict.keys())
        self.comboBox_clients.SetItems(nombres) # Llena el Combobox
        if nombres:
            self.comboBox_clients.SetSelection(0) # Posiciona el cursor en el índice 0

    # --- PATRÓN INYECTOR DE CALLBACKS (CONTROLADOR) ---
    # Los siguientes métodos vinculan la lógica de negocio externa (pasada por parámetro) 
    # con los clics de los botones de la interfaz gráfica, abstrayendo la vista del backend.

    # def on_add_path(self, event):
    #     paths = self.paths_selector.GetValue().strip()
    #     if paths:
    #         # Split the paths by newline and add each one
    #         for path in paths.split('\n'):
    #             path = path.strip()
    #             if path:
    #                 # Agrega una nueva fila a la tabla con el índice, ruta y estado inicial
    #                 index = self.path_table.GetNumberRows()
    #                 self.path_table.AppendRows(1)
    #             self.path_table.SetCellValue(index, 0, str(index + 1)) # Columna de índice
    #             self.path_table.SetCellValue(index, 1, path)          # Columna de ruta
    #             self.path_table.SetCellValue(index, 2, "Pendiente")   # Columna de estado
    #             self.path_table.SetCellValue(index, 3, "")            # Columna de ruta de ejecución (vacía por ahora)

        self.add_path_button.Bind(wx.EVT_BUTTON, self.on_add_path)
        self.add_path_button = wx.Button(self, label="Agregar a tabla", size=(120, -1))

    def set_on_generate_sells(self, callback):
        """Inyecta la función encargada de ejecutar el algoritmo de procesamiento de ventas."""
        def handler(event):
            # Ejecuta la función callback externa enviándole los datos actuales de la GUI
            callback(
                self.get_normalizer_seleccionado(),
                self.input_selector.GetValue(),
                self.input_selector_2.GetValue(),
                self.get_date()
            )
        self.button_generate_sells.Bind(wx.EVT_BUTTON, handler)

    def set_on_generate_inventory(self, callback):
        """Inyecta la función encargada de ejecutar el algoritmo de procesamiento de inventario/stock."""
        def handler(event):
            callback(
                self.get_normalizer_seleccionado(),
                self.input_selector.GetValue(),
                self.input_selector_2.GetValue(),
                self.get_date()
            )  
        self.button_generate_inventory.Bind(wx.EVT_BUTTON, handler)

    def show_success(self, filename):
        """
        Muestra una ventana emergente de aviso (Message Dialog) informando que la tarea terminó.
        Tiene botones de "SÍ" y "NO". Retorna True si el usuario cliquea "SÍ".
        """
        msg = f"Archivo {filename} creado con éxito ¿Abrir?"
        # Genera un cuadro de mensaje de información nativo
        dlg = wx.MessageDialog(self, msg, "Terminado", wx.YES_NO | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_YES # Evalúa la respuesta directa
        dlg.Destroy()
        return result


# =====================================================================
# 2. PANEL SECUNDARIO: DESCARGAS (Placeholder)
# =====================================================================
class DescargasPanel(wx.Panel):
    """Vista secundaria para simular una sección de descargas dentro de la suite."""
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour("#303030") # Cambia fondo a gris oscuro
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(self, label="Descargador de Videos")
        title.SetForegroundColour(wx.WHITE) # Texto blanco
        
        # Modificación dinámica de la tipografía base del sistema
        font = title.GetFont()
        font.PointSize += 8 # Aumenta tamaño de la letra
        font = font.Bold()  # Aplica negrita
        title.SetFont(font)
        
        sizer.Add(title, 0, wx.ALL, 20)
        self.SetSizer(sizer)


# =====================================================================
# 3. PANEL SECUNDARIO: CONVERTIDOR (Placeholder)
# =====================================================================
class ConvertidorPanel(wx.Panel):
    """Vista secundaria para simular una sección de conversión de formatos."""
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour("#C44A4A") # Cambia fondo a un tono rojizo
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(self, label="Convertidor de Video")
        title.SetForegroundColour(wx.WHITE)
        
        font = title.GetFont()
        font.PointSize += 8
        font = font.Bold()
        title.SetFont(font)
        
        sizer.Add(title, 0, wx.ALL, 20)
        self.SetSizer(sizer)


# =====================================================================
# 4. CONTENEDOR PRINCIPAL: MAIN FRAME (La Ventana Ejecutable)
# =====================================================================
class MainFrame(wx.Frame):
    """
    Representa la ventana principal de la aplicación en el sistema operativo.
    Orquesta la barra de navegación lateral (Sidebar) y el intercambio dinámico de páneles.
    """
    def __init__(self):
        # Inicializa la ventana sin padre (None), define título y dimensiones (1400x800)
        super().__init__(None, title="Studio Suite", size=(1400, 800))
        self.SetBackgroundColour("f0f0f0")

        # Contenedor raíz para envolver todo el espacio de la ventana
        panel = wx.Panel(self)
        # Sizer horizontal: Divide la pantalla en [ Barra Lateral (Izquierda) | Contenido (Derecha) ]
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # --- CONSTRUCCIÓN DEL SIDEBAR (BARRA LATERAL) ---
        sidebar = wx.Panel(panel, size=(240, -1)) # Ancho fijo de 240px
        sidebar.SetBackgroundColour("#ffffff")
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(sidebar, label="aTube Catcher")
        title.SetForegroundColour(wx.WHITE) # Nota: Al ser fondo blanco, este título podría no leerse bien (cambiar a negro si es necesario)
        font = title.GetFont()
        font.PointSize += 5
        font = font.Bold()
        title.SetFont(font)
        sidebar_sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)

        # --- ÁREA DE CONTENIDO DINÁMICO ---
        self.content_area = wx.Panel(panel)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_area.SetSizer(self.content_sizer)

        # Diccionario que cataloga las instancias de cada panel (vistas de la App)
        # Todas se inicializan teniendo como padre común a 'self.content_area'
        self.panels = {
            "ETL": viewETL(self.content_area),
            "STOCK": StockPanel(self.content_area), # Importado desde otro módulo del proyecto
            "Convertidor de Video": ConvertidorPanel(self.content_area),
        }

        # Oculta todos los paneles inicialmente y los añade al sizer de contenido.
        # Al añadirse con proportion=1 y wx.EXPAND, ocuparán todo el espacio disponible al mostrarse.
        for view in self.panels.values():
            view.Hide()
            self.content_sizer.Add(view, 1, wx.EXPAND)

        # --- GENERACIÓN DE BOTONES DEL MENÚ ---
        menu_items = list(self.panels.keys())

        for item in menu_items:
            btn = wx.Button(sidebar, label=item)
            btn.SetMinSize((200, 45)) # Botones estilizados con un tamaño mínimo estándar
            
            # Conexión del evento clic mediante una función lambda.
            # 'name=item' captura el valor actual del bucle en memoria (Early binding) 
            # para evitar que todos los botones apunten al último elemento.
            btn.Bind(wx.EVT_BUTTON, lambda evt, name=item: self.show_panel(name))
            sidebar_sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 8)

        # Agrega un resorte elástico al final del layout del sidebar. 
        # Empuja todos los botones creados hacia arriba, dejando el espacio sobrante abajo.
        sidebar_sizer.AddStretchSpacer()
        sidebar.SetSizer(sidebar_sizer)

        # --- ENSAMBLAJE FINAL DEL FRAME ---
        # El sidebar mantiene tamaño estático (proportion=0)
        main_sizer.Add(sidebar, 0, wx.EXPAND)
        # El área de contenido es flexible y se expande para rellenar la pantalla (proportion=1)
        main_sizer.Add(self.content_area, 1, wx.EXPAND)

        panel.SetSizer(main_sizer)

        # Lanza por defecto la pantalla "ETL" al iniciar la app
        self.show_panel("ETL")
        # Centra la ventana entera en el monitor del usuario
        self.Centre()

    def show_panel(self, panel_name):
        """
        Manejador encargado del intercambio de pantallas (Routing).
        Oculta todos los páneles registrados y únicamente hace visible el solicitado.
        """
        for name, panel in self.panels.items():
            panel.Hide()

        # Muestra el panel indexado
        self.panels[panel_name].Show()
        # Fuerza una re-evaluación del layout para ajustar dimensiones del nuevo panel visible inmediatamente
        self.content_area.Layout()


# =====================================================================
# 5. INICIALIZADOR: wx.App (El Núcleo del Proceso)
# =====================================================================
class App(wx.App):
    """
    Clase principal de la aplicación exigida por wxPython.
    Maneja el bucle principal de eventos del sistema operativo.
    """
    def OnInit(self):
        """
        Método de inicialización obligatorio (reemplaza al __init__).
        Debe retornar un booleano (True) si la ventana se crea con éxito.
        """
        frame = MainFrame()
        frame.Show() # Muestra físicamente el Frame en la pantalla del usuario
        return True


# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    # Inicializa el motor de la app. False evita que redirija mensajes de error 
    # nativos de C++ a una ventana flotante externa independiente.
    app = App(False)
    # Lanza el ciclo infinito (Event Loop). Captura clics, redimensionamientos y teclas.
    app.MainLoop()