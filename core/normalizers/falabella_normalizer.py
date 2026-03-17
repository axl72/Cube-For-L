from ..normalizer import Normalizer
import pandas as pd
from pathlib import Path
from pandas import DataFrame

class FalabellaNormalizer(Normalizer):
    def read(self, pathdir:Path):
        print(f"Leyendo archivo {pathdir}")
        if pathdir.is_file():
            df = pd.read_csv(pathdir, sep=',', encoding='latin1', decimal=',', thousands='.')
            return [df]

        df_list = []
        for path in pathdir.iterdir():
            df =  pd.read_csv(path, sep=',', encoding='latin1', decimal=',', thousands='.')
            df_list.append(df)
        return df_list
    
    def normalize_sells(self, df:pd.DataFrame, date):
        df = df.drop(df.columns[[1, 2, 3, 4, 9, 12, 13, 14]], axis=1)
        df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y-%m-%d")
        df = df.sort_values("Fecha").reset_index(drop=True)
        df = df[df["Unidades"] != 0]
        
        target_columns = [
           "Fecha",
            "SKU",
            "Producto",
            "Modelo",
            "Marca",
            "ID Local",
            "Local",
            "Venta bruta",
            "Venta neta",
            "Unidades",
            "Costo", 
        ]
        df = df[target_columns]
        nuevas_columnas = ["fecha", "sku", "descripcion_producto", "modelo", "marca", "cod_local", "local", "venta_publico", "timbrado", "unidades", "venta_costo"]
        renombre = {clave: valor for clave, valor in zip(target_columns, nuevas_columnas)}
        df.rename(columns=renombre, inplace=True)
        df = df[~df["descripcion_producto"].str.startswith("DV_", na=False)]
        cols = ["venta_publico", "timbrado", "venta_costo"]
        # df[cols] = df[cols].replace(',', '.', regex=True).astype(float)
        df[cols] = df[cols].astype(float)
        return df

    def __str__(self):
        return "SAGA-FALABELLA"


    
    def read_stock(self, pathfile:Path) -> DataFrame:
        print(f"Leyendo archivo {pathfile}")
        df =  pd.read_csv(pathfile, sep=',', encoding='latin1', header=0, decimal=',', thousands='.')
        return df

    def normalize_stock(self, df:DataFrame, date) -> DataFrame:
        df = df[[
           "ID Producto",
            "Producto",
            "ID Local",
            "Local",
            "Stock Disponible", 
        ]]

        df = df[df["Stock Disponible"] > 0]
        df = df[~df["Producto"].str.startswith("DV_", na=False)]
        df.insert(0, "fecha", date)

        df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
        return df