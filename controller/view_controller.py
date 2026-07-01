from core.normalizer_factory import NormalizerFactory
from pathlib import Path
from tkinter import messagebox
import config
import traceback
import os
from core.updater import Updater
import pandas as pd




class ViewController():
    def __init__(self, view=None):
        self.updater = Updater(output_path=config.OUTPUT_PATH)
        self.view = view
        self.normalizers = NormalizerFactory.create_all()

    def print(self):
        print("ViewController initialized")
    
    
    def create_output_stock(self, normalizer, path:Path, output_path:Path, fecha):
        filename = f"STOCK-OUTPUT-{normalizer}.xlsx"
        output_path = self.updater.create_stock(Path(path), normalizer, filename, self.view.get_date())
        print(f"[ETL CONTROLLER LOG] Output path: {type(config.OUTPUT_PATH)}")
        output_path = Path(config.OUTPUT_PATH) / output_path
        if self.view.show_success(filename):
            self.open_excel(output_path)

    def create_output_ventas(self, normalizer, input_path:Path, output_path:Path, fecha):
        try:

            filename = f"OUTPUT-{self.view.get_normalizer_seleccionado()}.xlsx"
            print(f"[ETL CONTROLLER LOG] Input path: {input_path}, Type: {type(input_path)}")
            output_path = self.updater.consolidate_sells(Path(input_path), normalizer, filename, fecha)
            output_path = Path(config.OUTPUT_PATH) / output_path
            if self.view.show_success(filename):
                self.open_excel(output_path)

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror(message=f"Problema al generar las ventas: {e}")
    
    def create_consolidated_output_ventas(self, paths: tuple[Path, str]):
        print(f"[ETL CONTROLLER LOG] Consolidating sells for paths:")
        df_list = {}

        paths = [(path, normalizer) for path, normalizer in paths if path != "" and normalizer != ""]

        # For normalizador
        for path, normalizer in paths:
            normalizer = self.normalizers.get(normalizer)
            df = normalizer.read(Path(path))[0]
            normalized_df = normalizer.normalize_sells(df, self.view.get_date())
            if normalizer not in df_list:
                df_list[normalizer] = [normalized_df]
            else:
                df_list[normalizer].append(normalized_df)
        
        # For concatenador
        for normalizer, dfs in df_list.items():
            concatenated_df = pd.concat(dfs)
            filename = f"OUTPUT-{normalizer}.xlsx"
            output_path = Path(config.OUTPUT_PATH) / filename
            concatenated_df.to_excel(output_path, index=False)
            if self.view.show_success(filename):
                self.open_excel(output_path)
                
    

    def run(self):
        self.view.set_combobox_values(self.normalizers)
        self.view.set_input_selector_2(str(config.OUTPUT_PATH))
        self.view.set_on_generate_inventory(lambda n, i, o, f: self.create_output_stock(n, i, o, f))
        self.view.set_on_generate_sells(lambda n, i, o, f: self.create_output_ventas(n, i, o, f))
        self.view.set_on_consolidate_paths(lambda paths: self.create_consolidated_output_ventas(paths))

    def open_excel(self, path):
        print("Abriendo archivo: ", path)
        os.startfile(path)
    
