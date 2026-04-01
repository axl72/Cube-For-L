from core.normalizer_factory import NormalizerFactory
from pathlib import Path
from tkinter import messagebox
from config import AppConfig
import traceback
import os
from core.updater import Updater

AppConfig.load()

OUTPUT_PATH = AppConfig.get_output_path()
ICON_PATH = AppConfig.get_icon_path()

class ViewController():
    def __init__(self, view=None):
        self.updater = Updater(output_path=OUTPUT_PATH)
        self.view = view
        self.normalizers = NormalizerFactory.create_all()

    def print(self):
        print("ViewController initialized")
    
    
    def create_output_stock(self, path:Path):
        name_normalizer = self.view.get_normalizer()
        normalizer = self.normalizers[name_normalizer]
        filename = f"STOCK-OUTPUT-{name_normalizer}.xlsx"
        output_path = self.updater.create_stock(path, normalizer, filename, self.view.get_date())
        output_path = Path(OUTPUT_PATH) / output_path
        if self.view.show_success(filename):
            self.open_excel(output_path)

    def create_output_ventas(self, path:Path):
        try:

            name_normalizer = self.view.get_normalizer()
            normalizer = self.normalizers[name_normalizer]
            filename = f"OUTPUT-{name_normalizer}.xlsx"
            output_path = self.updater.consolidate_sells(path, normalizer, filename, self.view.get_date())
            output_path = Path(OUTPUT_PATH) / output_path
            if self.view.show_success(filename):
                self.open_excel(output_path)

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror(message=f"Problema al generar las ventas: {e}")
    
    

    def run(self):
        self.view.set_combobox_values(self.normalizers)
        self.view.set_input_selector_2(OUTPUT_PATH)
        self.view.set_on_generate_inventory(lambda: self.create_output_stock(Path(self.view.var_input_archive_selected.get())))
        self.view.set_on_generate_sells(lambda: self.create_output_ventas(Path(self.view.var_input_archive_selected.get())))
        self.view.mainloop()

    def open_excel(self, path):
        print("Abriendo archivo: ", path)
        os.startfile(path)
    
