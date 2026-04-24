import wx
import wx.adv  # Para el DatePicker
from pathlib import Path
import datetime
from datetime import date

class MainWindow(wx.Frame):
    def __init__(self):
        # Inicializa el Frame (Ventana)
        super().__init__(parent=None, title="Cube for L", size=(350, 520))
        
        # Panel principal (necesario para el color de fondo y tabulación correcta)
        self.panel = wx.Panel(self)
        
        # Variables de estado (Equivalentes a BooleanVar y StringVar)
        self.is_directory_val = False
        self.input_path_val = ""
        self.output_path_val = ""
        self.normalizers = {} 

        # --- CREACIÓN DE WIDGETS ---
        
        # 1. Selector de Fecha (Equivalente a tkcalendar)
        self.lbl_fecha = wx.StaticText(self.panel, label="Fecha seleccionada:")
        self.cal = wx.adv.DatePickerCtrl(self.panel, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        # Configurar fecha inicial (Ayer)
        ayer = date.today() - datetime.timedelta(days=1)
        dt_ayer = wx.DateTime(ayer.day, ayer.month - 1, ayer.year)
        self.cal.SetValue(dt_ayer)

        # 2. Input Section
        self.lbl_archivo = wx.StaticText(self.panel, label="Seleccione un archivo/directorio:")
        self.input_selector = wx.TextCtrl(self.panel)
        self.button_input = wx.Button(self.panel, label="...", size=(30, -1))
        
        self.check_button = wx.CheckBox(self.panel, label="Es un directorio")

        # 3. Output Section
        self.lbl_output = wx.StaticText(self.panel, label="Seleccione carpeta de salida:")
        self.input_selector_2 = wx.TextCtrl(self.panel)
        self.button_input_2 = wx.Button(self.panel, label="...", size=(30, -1))

        # 4. Clientes (Combobox)
        self.lbl_cliente = wx.StaticText(self.panel, label="Cliente seleccionado:")
        self.comboBox_clients = wx.ComboBox(self.panel, style=wx.CB_READONLY)

        # 5. Botones de Acción
        self.button_generate_sells = wx.Button(self.panel, label="GENERAR VENTAS")
        self.button_generate_inventory = wx.Button(self.panel, label="GENERAR STOCK")

        # --- DISEÑO (LAYOUT) CON SIZERS ---
        # El Sizer organiza los elementos verticalmente
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Helper para añadir con margen
        def add_widget(widget, proportion=0, flag=wx.EXPAND | wx.ALL, border=10):
            main_sizer.Add(widget, proportion, flag, border)

        # Layout del Input (Hozizontal)
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_sizer.Add(self.input_selector, 1, wx.EXPAND)
        input_sizer.Add(self.button_input, 0, wx.LEFT, 5)

        # Layout del Output (Horizontal)
        output_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_sizer.Add(self.input_selector_2, 1, wx.EXPAND)
        output_sizer.Add(self.button_input_2, 0, wx.LEFT, 5)

        # Agregar todo al Sizer Principal
        add_widget(self.lbl_archivo, border=5)
        add_widget(input_sizer, border=10)
        add_widget(self.check_button, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)
        
        add_widget(self.lbl_output, border=5)
        add_widget(output_sizer, border=10)
        
        add_widget(self.lbl_cliente, border=5)
        add_widget(self.comboBox_clients)
        
        add_widget(self.lbl_fecha, border=5)
        add_widget(self.cal)
        
        add_widget(self.button_generate_sells, border=10)
        add_widget(self.button_generate_inventory, border=10)

        self.panel.SetSizer(main_sizer)

        # --- BINDING DE EVENTOS ---
        self.button_input.Bind(wx.EVT_BUTTON, self.on_select_input)
        self.button_input_2.Bind(wx.EVT_BUTTON, self.on_select_output)
        self.cal.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_change)
        
        # Centrar ventana
        self.Centre()

    # --- MÉTODOS DE LA VISTA ---

    def set_input_selector_2(self, text):
        self.input_selector_2.SetValue(text)

    def get_normalizer_seleccionado(self):
        nombre = self.comboBox_clients.GetValue()
        return self.normalizers.get(nombre)

    def get_date(self):
        # Retorna fecha en formato dd/mm/yyyy
        date_wx = self.cal.GetValue()
        return f"{date_wx.GetDay():02d}/{date_wx.GetMonth()+1:02d}/{date_wx.GetYear()}"

    def on_select_input(self, event):
        if self.check_button.GetValue():
            dlg = wx.DirDialog(self, "Seleccione carpeta")
        else:
            dlg = wx.FileDialog(self, "Seleccione archivo", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.input_selector.SetValue(path)
        dlg.Destroy()

    def on_select_output(self, event):
        dlg = wx.DirDialog(self, "Seleccione carpeta de salida")
        if dlg.ShowModal() == wx.ID_OK:
            self.input_selector_2.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_date_change(self, event):
        print("Fecha seleccionada: ", self.get_date())

    def set_combobox_values(self, normalizers_dict: dict):
        self.normalizers = normalizers_dict
        nombres = list(normalizers_dict.keys())
        self.comboBox_clients.SetItems(nombres)
        if nombres:
            self.comboBox_clients.SetSelection(0)

    def set_on_generate_sells(self, callback):
        self.button_generate_sells.Bind(wx.EVT_BUTTON, callback)

    def set_on_generate_inventory(self, callback):
        self.button_generate_inventory.Bind(wx.EVT_BUTTON, callback)

    def show_success(self, filename):
        msg = f"Archivo {filename} creado con éxito ¿Abrir?"
        dlg = wx.MessageDialog(self, msg, "Terminado", wx.YES_NO | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        return result

if __name__ == "__main__":
    app = wx.App()
    window = MainWindow()
    window.Show()
    app.MainLoop()