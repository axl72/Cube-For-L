from ..normalizer import Normalizer
from pathlib import Path
import pandas as pd

class EstilosNormalizer(Normalizer):
    def read(self, pathdir:Path):
        if pathdir.is_file():
            df = pd.read_excel(pathdir)
            df = df.iloc[:-1].copy()
            return [df]

    
    def normalize_sells(self, df:pd.DataFrame, date):

        date = pd.to_datetime(date, format="%d/%m/%Y")
        print("El datetime es: ", date)
        df["Venta UN AAc"] = pd.to_numeric(df["Venta UN AAc"], errors="coerce").fillna(0)
        df["DiaMes"] = pd.to_numeric(df["DiaMes"], errors="coerce").fillna(0).astype(int)
        df["Fecha"] = pd.to_datetime(date.strftime("%Y-%m-") + df["DiaMes"].astype(str), format="%Y-%m-%d")
        df = df[["Fecha", "Sku", "Descripcion", "Tienda", "Venta UN AAc", "Venta Neta AAc"]]
        df = df[df["Venta UN AAc"] > 0]
        df = df.sort_values(by="Fecha", ascending=True)
        df = df.reset_index(drop=True)

        return df
    
    def normalize_stock(self, df:pd.DataFrame, date):
        df = df.copy()
        date = pd.to_datetime(date)
        df["DiaMes"] = pd.to_numeric(df["DiaMes"], errors="coerce").fillna(0).astype(int)
        df["Fecha"] = pd.to_datetime(date.strftime("%Y-%m-") + df["DiaMes"].astype(str), format="%Y-%m-%d")
        max_dia = pd.to_numeric(df["DiaMes"], errors="coerce").max()
        # Convertir stock a numérico
        df["Stk UN Empresa"] = pd.to_numeric(df["Stk UN Empresa"], errors="coerce").fillna(0)
        
        df = df[df["DiaMes"] == max_dia].copy()
        
        
        # Seleccionar solo las columnas que interesan
        df = df[["Fecha", "Sku", "Descripcion", "Tienda", "Stk UN Empresa"]]
        df = df.reset_index(drop=True)
        return df 
    
    def __str__(self):
        return "ESTILOS"

    def read_stock(self, pathfile:Path) -> pd.DataFrame:
        df = pd.read_excel(pathfile)
        df = df.iloc[:-1].copy()
        return df