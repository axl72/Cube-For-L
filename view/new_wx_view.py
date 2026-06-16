import wx
import wx.adv
from datetime import date
import datetime
import wx.grid as gridlib
from pathlib import Path
from view.wx_panels.stock_panel import StockPanel


class viewETL(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Variables de estado (Equivalentes a BooleanVar y StringVar)
        self.is_directory_val = False
        self.input_path_val = ""
        self.output_path_val = ""
        self.normalizers = {} 

        # --- CREACIÓN DE WIDGETS ---
        
        # 1. Selector de Fecha (Equivalente a tkcalendar)
        self.lbl_fecha = wx.StaticText(self, label="Fecha seleccionada:")
        self.cal = wx.adv.DatePickerCtrl(self, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        # Configurar fecha inicial (Ayer)
        ayer = date.today() - datetime.timedelta(days=1)
        dt_ayer = wx.DateTime(ayer.day, ayer.month - 1, ayer.year)
        self.cal.SetValue(dt_ayer)

        # 2. Input Section
        self.lbl_archivo = wx.StaticText(self, label="Seleccione un archivo/directorio:")
        self.input_selector = wx.TextCtrl(self)
        self.button_input = wx.Button(self, label="...", size=(30, -1))
        
        self.check_button = wx.CheckBox(self, label="Es un directorio")

        # 3. Output Section
        self.lbl_output = wx.StaticText(self, label="Seleccione carpeta de salida:")
        self.input_selector_2 = wx.TextCtrl(self)
        self.button_input_2 = wx.Button(self, label="...", size=(30, -1))

        # 4. Clientes (Combobox)
        self.lbl_cliente = wx.StaticText(self, label="Cliente seleccionado:")
        self.comboBox_clients = wx.ComboBox(self, style=wx.CB_READONLY)

        # 5. Botones de Acción
        self.button_generate_sells = wx.Button(self, label="GENERAR VENTAS")
        self.button_generate_inventory = wx.Button(self, label="GENERAR STOCK")

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

        self.SetSizer(main_sizer)

        # --- BINDING DE EVENTOS ---
        self.button_input.Bind(wx.EVT_BUTTON, self.on_select_input)
        self.button_input_2.Bind(wx.EVT_BUTTON, self.on_select_output)
        self.cal.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_change)
        
        # Centrar ventana
        self.Centre()

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
            dlg = wx.FileDialog(self, "Seleccione archivo", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
            print("Seleccionar archivo")
        
        if dlg.ShowModal() == wx.ID_OK:
            print("Seleccionado: ", dlg.GetPaths())
            paths = dlg.GetPaths()

            self.input_selector.SetValue(str(paths[0]))
            self.selected_paths = paths

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
        def handler(event):
            callback(
                self.get_normalizer_seleccionado(),
                self.input_selector.GetValue(),
                self.input_selector_2.GetValue(),
                self.get_date()
            )
        self.button_generate_sells.Bind(wx.EVT_BUTTON, handler)

    def set_on_generate_inventory(self, callback):
        def handler(event):
            callback(
                self.get_normalizer_seleccionado(),
                self.input_selector.GetValue(),
                self.input_selector_2.GetValue(),
                self.get_date()
            )  
        self.button_generate_inventory.Bind(wx.EVT_BUTTON, handler)

    def show_success(self, filename):
        msg = f"Archivo {filename} creado con éxito ¿Abrir?"
        dlg = wx.MessageDialog(self, msg, "Terminado", wx.YES_NO | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        return result

class DescargasPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour("#303030")
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Descargador de Videos")
        title.SetForegroundColour(wx.WHITE)
        font = title.GetFont()
        font.PointSize += 8
        font = font.Bold()
        title.SetFont(font)
        sizer.Add(title, 0, wx.ALL, 20)
        self.SetSizer(sizer)






class ConvertidorPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour("#C44A4A")
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Convertidor de Video")
        title.SetForegroundColour(wx.WHITE)
        font = title.GetFont()
        font.PointSize += 8
        font = font.Bold()
        title.SetFont(font)
        sizer.Add(title, 0, wx.ALL, 20)
        self.SetSizer(sizer)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Studio Suite", size=(1400, 800))
        self.SetBackgroundColour("f0f0f0")

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Sidebar
        sidebar = wx.Panel(panel, size=(240, -1))
        sidebar.SetBackgroundColour("#ffffff")
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(sidebar, label="aTube Catcher")
        title.SetForegroundColour(wx.WHITE)
        font = title.GetFont()
        font.PointSize += 5
        font = font.Bold()
        title.SetFont(font)
        sidebar_sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)

        # Área de contenido con cambio de vistas
        self.content_area = wx.Panel(panel)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_area.SetSizer(self.content_sizer)

        self.panels = {
            "ETL": viewETL(self.content_area),
            "STOCK": StockPanel(self.content_area),
            "Convertidor de Video": ConvertidorPanel(self.content_area),
        }

        for view in self.panels.values():
            view.Hide()
            self.content_sizer.Add(view, 1, wx.EXPAND)

        menu_items = list(self.panels.keys())

        for item in menu_items:
            btn = wx.Button(sidebar, label=item)
            btn.SetMinSize((200, 45))
            btn.Bind(wx.EVT_BUTTON, lambda evt, name=item: self.show_panel(name))
            sidebar_sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 8)

        sidebar_sizer.AddStretchSpacer()
        sidebar.SetSizer(sidebar_sizer)

        main_sizer.Add(sidebar, 0, wx.EXPAND)
        main_sizer.Add(self.content_area, 1, wx.EXPAND)

        panel.SetSizer(main_sizer)

        self.show_panel("ETL")
        self.Centre()

    def show_panel(self, panel_name):
        for name, panel in self.panels.items():
            panel.Hide()

        self.panels[panel_name].Show()
        self.content_area.Layout()


class App(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = App(False)
    app.MainLoop()