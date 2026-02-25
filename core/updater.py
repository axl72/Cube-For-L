from core.normalizer import Normalizer
from core.reader import Reader
from pathlib import Path
import pandas as pd
import os
from util.xlsx_functions import get_available_path
from tkinter import messagebox
import traceback
from pathlib import Path

class Updater():
    def __init__(self, output_path: Path):
        self.output_path = output_path

    def consolidate_sells(self, path: Path, normalizer:Normalizer, name = f"OUTPUT.xlsx") -> None:
        try:
            df_list = normalizer.read(path)
            df_list = [normalizer.normalize_sells(df) for df in df_list]
            result_df = pd.concat(df_list)
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
            path = path.joinpath(self.output_path, name)
            path = get_available_path(path)
            print(f"Valor del path: {path}")
            result_df.to_excel(path, index=False)
            print("Excel generado")
            print("Valor del path despues de guardar: ", path)
            return path
        except Exception as e:
            raise Exception(f"Algo fue mal {e}")

    def create_stock(self, path: Path, normalizer:Normalizer, name = f"STOCK-OUTPUT.xlsx", date= None) -> None:
        try:
            df = normalizer.read_stock(path)
            df_result = normalizer.normalize_stock(df, date)
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
            path = path.joinpath(self.output_path, name)
            path = get_available_path(path)
            df_result.to_excel(path, index=False)
            return path
        except Exception as e:
            raise Exception(f"Algo fue mal {e}")
        

