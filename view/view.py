import tkinter
import traceback
import datetime
from tkinter import Frame, StringVar
from tkinter.ttk import Button, Notebook, Style
from tkinter.ttk import Combobox, Separator
from core.normalizers import TottusNormalizer, TaiLoyNormalizer, RipleyNormalizer, OechsleNormalizer, FalabellaNormalizer, EstilosNormalizer, CencosudNormalizer, IlahuiNormalizer
from util.whateveryouchooser import Chooser
from pathlib import Path
from tkinter import messagebox
import os
from tkcalendar import Calendar, DateEntry
from datetime import date, timedelta
from config import AppConfig
#
AppConfig.load()

# Ahora ya puedes usarla
output_path = AppConfig.get_output_path()
print("Output path:", output_path)



class MainWindow(tkinter.Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
    # Inicializa configuración
 

        self.geometry("300x470")
        self.is_directory = tkinter.BooleanVar(value=False)
        # self.resizable(False, False)


        ayer = date.today() - datetime.timedelta(days=1)
        self.var_fecha = tkinter.StringVar(
            value=ayer.strftime("%d/%m/%Y")
        )
        self.cal = DateEntry(
            self,
            textvariable=self.var_fecha,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',  # formato de fecha
        )
        self.cal.set_date(ayer)
        self.cal.bind("<<DateEntrySelected>>", self.on_date_change)
        self.cal.configure(state="readonly")
        self.archive_selected = tkinter.Label(self, text="Seleccione un archivo")
        self.var_input_archive_selected = tkinter.StringVar(value="")
        self.label_select_output = tkinter.Label(self, text="Seleccione carpeta de salida")

        self.frame_input = Frame(self)
        self.frame_output = Frame(self)
        self.input_selector = tkinter.Entry(self.frame_input, width=40, textvariable=self.var_input_archive_selected)
        self.button_input = Button(self.frame_input, text="...", command=lambda: self.__select__(self.is_directory.get()))
        self.check_button = tkinter.Checkbutton(self, text="Es un directorio", variable=self.is_directory, onvalue=True, offvalue=False)
        self.comboBox_clients = Combobox(self, state='readonly', width=45)
        self.button_generate_sells = Button(self, text="GENERAR VENTAS", width=40, command=lambda: self.create_output_ventas(self.get_normalizer_seleccionado(), Path(self.var_input_archive_selected.get())))
        self.button_generate_inventory = Button(self, text="GENERAR STOCK", width=40, command=lambda: self.create_output_stock(self.get_normalizer_seleccionado(), Path(self.var_input_archive_selected.get())))    
        
        self.input_selector_2 = tkinter.Entry(self.frame_output, width=40)
        self.button_input_2 = Button(self.frame_output, text="...", command=lambda: self.__select_directory__())



        self.input_selector.pack(side="left")

        self.frame_input.pack(pady=2, padx=10, anchor="w")
        self.label_select_output.pack(pady=2, padx=10, anchor="w")  
        self.frame_output.pack(pady=2, padx=10, anchor="w")
        
        self.input_selector.pack(pady=2, padx=2, anchor="w")
        self.button_input.pack(padx=2, pady=2, anchor="w")

        self.input_selector_2.pack(side="left")
        self.button_input_2.pack(padx=2, pady=2, anchor="w")
        
        self.check_button.pack(pady=2, padx=10, anchor="e")
        self.comboBox_clients.pack(pady=2, padx=10, anchor="w")
        self.cal.pack(padx=10, pady=4, fil="x")

        self.label_select_client = tkinter.Label(self, text="Cliente seleccionado")
        self.button_generate_sells.pack(pady=2, padx=10, anchor="w", fill="x")
        self.button_generate_inventory.pack(pady=2, padx=10, anchor="w", fill="x")




        # This line only works in Windows :(
        try:
            self.iconbitmap(ICON_PATH)
        except Exception as e:
            print("No se puedo cargar la imagen")

        # This line only works in Linux
        # try:
        #     self.iconphoto(False, tkinter.PhotoImage(ICON_PATH))
        # except Exception as e:
        #     print("No se puedo cargar la imagen")

        self.title("ORBACLUAP")

    def set_input_selector_2(self, text):
        self.input_selector_2.delete(0, tkinter.END)
        self.input_selector_2.insert(0, text)

    def get_normalizer_seleccionado(self):
        nombre = self.comboBox_clients.get()
        normalizer = self.normalizers[nombre]
        print(f"Normalizar seleccionado {normalizer}")
        return normalizer
    
    def get_date(self):
        return self.var_fecha.get()



    
    def __select__(self, is_directory: bool) -> Path:
        
        if is_directory:
            path = self.__select_directory__()
        else:
            path =self.__select_file__()
        self.var_input_archive_selected.set(str(path))
        return path

    
    def __select_directory__(self) -> Path:
        selected_directory = Chooser().select_directory()
        if selected_directory == "":
            print("Ningun directorio seleccionado")
            return
        directory = Path(selected_directory)
        return directory
    
    def __select_file__(self) -> Path:
        selected_file = Chooser().select_file()
        if selected_file == "":
            print("Ningun archivo seleccionado")
            return
        file = Path(selected_file)
        return file
    
    def on_date_change(self, event):
        self.var_fecha.set(self.cal.get())
        print("Fecha seleccionada: ", self.var_fecha.get())

    def set_combobox_values(self, normalizers:dict):
        self.comboBox_clients["values"] = list(normalizers.keys())
    
        if normalizers:
            self.comboBox_clients.current(0)

    def set_on_generate_sells(self, callback):
        self.button_generate_sells.config(command=callback)

    def set_on_generate_inventory(self, callback):
        self.button_generate_inventory.config(command=callback)
    
    def get_normalizer(self):
        return self.comboBox_clients.get()
    
    def show_success(self, filename):
        return messagebox.askyesno("Terminado", f"Archivo {filename} creado con éxito ¿Abrir?")

if __name__ == "__main__":
    root = MainWindow()
    root.mainloop() # app