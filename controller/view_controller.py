from core.normalizer_factory import NormalizerFactory
from pathlib import Path
from tkinter import messagebox
from config import AppConfig
import traceback
import os
from core.updater import Updater

AppConfig.load()

OUTPUT_PATH = AppConfig.get_output_path()
print("OUTPUT_PATH: ", OUTPUT_PATH)
ICON_PATH = AppConfig.get_icon_path()
print("ICON_PATH: ", ICON_PATH)

class ViewController():
    def __init__(self, view=None):
        self.updater = Updater(output_path=OUTPUT_PATH)
        self.view = view
        self.normalizers = NormalizerFactory.create_all()

    def print(self):
        print("ViewController initialized")
    
    
    def create_output_stock(self, normalizer, path:Path, output_path:Path, fecha):
        filename = f"STOCK-OUTPUT-{normalizer}.xlsx"
        output_path = self.updater.create_stock(Path(path), normalizer, filename, self.view.get_date())
        print("Output path: ", type(OUTPUT_PATH))
        output_path = Path(OUTPUT_PATH) / output_path
        if self.view.show_success(filename):
            self.open_excel(output_path)

    def create_output_ventas(self, normalizer, input_path:Path, output_path:Path, fecha):
        try:

            filename = f"OUTPUT-{self.view.get_normalizer_seleccionado()}.xlsx"
            print(input_path, type(input_path))
            output_path = self.updater.consolidate_sells(Path(input_path), normalizer, filename, fecha)
            output_path = Path(OUTPUT_PATH) / output_path
            if self.view.show_success(filename):
                self.open_excel(output_path)

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror(message=f"Problema al generar las ventas: {e}")
    
    

    def run(self):
        self.view.set_combobox_values(self.normalizers)
        self.view.set_input_selector_2(str(OUTPUT_PATH))
        self.view.set_on_generate_inventory(lambda n, i, o, f: self.create_output_stock(n, i, o, f))
        self.view.set_on_generate_sells(lambda n, i, o, f: self.create_output_ventas(n, i, o, f))

    def open_excel(self, path):
        print("Abriendo archivo: ", path)
        os.startfile(path)
    
