import wx
import wx.grid as gridlib
import pandas as pd



class StockPanel(wx.Panel):
    def __init__(self, parent):
        # Inicializa el panel usando la clase base wx.Panel
        super().__init__(parent)


        # Define el color de fondo del panel
        self.SetBackgroundColour("#F0F0F0")

        # =========================
        # CONTROLES SUPERIORES
        # =========================

        # Crea una etiqueta de texto
        etiqueta = wx.StaticText(self, label="Nombre:")

        # Crea un campo de entrada de texto
        self.input_sku = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)

        # =========================
        # FORMULARIO INTERMEDIO
        # =========================

        # Crea un panel contenedor para los campos intermedios
        form_panel = wx.Panel(self)

        # Crea un GridSizer: 2 columnas, filas automáticas, separación de 10 px
        campos_sizer = wx.GridSizer(rows=0, cols=4, vgap=4, hgap=4)

        # Campo 1
        campos_sizer.Add(wx.StaticText(form_panel, label="Descripción Intek"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_descripcion = wx.TextCtrl(form_panel)
        campos_sizer.Add(self.txt_descripcion, 1, wx.EXPAND)

        # Campo 2
        campos_sizer.Add(wx.StaticText(form_panel, label="PVP"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_pvp = wx.TextCtrl(form_panel)
        campos_sizer.Add(self.txt_pvp, 1, wx.EXPAND)

        # Campo 3
        campos_sizer.Add(wx.StaticText(form_panel, label="Nuevo PVP"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_nuevo_pvp = wx.TextCtrl(form_panel)
        campos_sizer.Add(self.txt_nuevo_pvp, 1, wx.EXPAND)

        # Campo 4
        campos_sizer.Add(wx.StaticText(form_panel, label="Nuevo MG%"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_nuevo_mg = wx.TextCtrl(form_panel)
        campos_sizer.Add(self.txt_nuevo_mg, 1, wx.EXPAND)

        # Asigna el layout al panel intermedio
        form_panel.SetSizer(campos_sizer)

        # =========================
        # TABLA
        # =========================

        # Crea la tabla
        self.grid = gridlib.Grid(self)
        self.grid.CreateGrid(5, 3)

        # =========================
        # LAYOUT PRINCIPAL
        # =========================

        # Crea un sizer vertical principal
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Fila superior: etiqueta + input
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Agrega la etiqueta a la fila superior
        top_sizer.Add(etiqueta, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        # Agrega el input y permite que se expanda horizontalmente
        top_sizer.Add(self.input_sku, 1)

        # Inserta la fila superior en el layout principal
        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Inserta el formulario intermedio con margen lateral
        main_sizer.Add(form_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Inserta la tabla y permite que ocupe todo el espacio restante
        main_sizer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Asigna el layout principal al panel
        self.SetSizer(main_sizer)

    def set_txt_descripcion(self, value):
        self.txt_descripcion.SetValue(value)
    
    def set_txt_pvp(self, value):
        self.txt_pvp.SetValue(value)
    
    def set_txt_nuevo_pvp(self, value):
        self.txt_nuevo_pvp.SetValue(value)
    
    def set_txt_nuevo_mg(self, value):
        self.txt_nuevo_mg.SetValue(value)
    
    def get_input_sku(self):
        return self.input_sku.GetValue()
    
    def get_txt_nuevo_pvp(self):
        return self.txt_nuevo_pvp.GetValue()
    
    def set_input_sku(self, value):
        self.input_sku.SetValue(value)

    def set_dataframe(self, df):
        """
        Carga un DataFrame de pandas en el wx.grid.Grid.
        """
        filas, columnas = df.shape

        # Ajustar número de filas
        filas_actuales = self.grid.GetNumberRows()
        if filas_actuales < filas:
            self.grid.AppendRows(filas - filas_actuales)
        elif filas_actuales > filas:
            self.grid.DeleteRows(0, filas_actuales - filas)

        # Ajustar número de columnas
        columnas_actuales = self.grid.GetNumberCols()
        if columnas_actuales < columnas:
            self.grid.AppendCols(columnas - columnas_actuales)
        elif columnas_actuales > columnas:
            self.grid.DeleteCols(0, columnas_actuales - columnas)

        # Establecer encabezados
        for col, nombre in enumerate(df.columns):
            self.grid.SetColLabelValue(col, str(nombre))

        # Cargar datos
        for fila in range(filas):
            for col in range(columnas):
                valor = df.iat[fila, col]
                self.grid.SetCellValue(fila, col, "" if valor is None else str(valor))

        # Ajustar presentación
        # self.ajustar_columnas()
        self.grid.ForceRefresh()
    
    def bind_search_key_down(self, handler):
        self.input_sku.Bind(wx.EVT_KEY_DOWN, handler)

    def bind_search_key_up(self, handler):
        self.input_sku.Bind(wx.EVT_KEY_UP, handler)


    def bind_search_text(self, handler):
        self.input_sku.Bind(wx.EVT_TEXT, handler)

    def bind_search_enter(self, handler):
        self.input_sku.Bind(wx.EVT_TEXT_ENTER, handler)
    
    def bind_type_new_pvp(self, handler):
        self.txt_nuevo_pvp.Bind(wx.EVT_TEXT, handler)