from ..normalizer import Normalizer
from pathlib import Path
from pandas import DataFrame
import pandas as pd

class IlahuiNormalizer(Normalizer):
    def read(self, pathdir:Path) -> list[DataFrame]:
        if pathdir.is_file():
            df = pd.read_excel(pathdir)
            return [df]
        df_list = []
        for path in pathdir.iterdir():
            df =  pd.read_csv(path, sep=',', encoding='latin1')
            df_list.append(df)
        return df_list
    
    def normalize_sells(self, df:DataFrame, date) -> DataFrame:
        target_columns = [
           # "proveedor",
           # "f_ultima_entrada",
            "f_ultima_venta",
            # "rango_ant",
            "ubicacion",
            # "marca",
            "colección",
            "cod_interno",
            # "barcode",
            "sku",
            "descripción",
            "unidades_vendidas",
            "venta_bruta",
            # "stock",
            # " stock_valorizado "
        ]
        df = df[target_columns]
        df = df[df["unidades_vendidas"] != 0]
        df["f_ultima_venta"] = pd.to_datetime(df["f_ultima_venta"]).dt.normalize()
        nuevas_columnas = ['fecha', 'nombre local','marca', 'cod proveedor', 'sku', 'descripcion', 'venta unidades', 'timbrado']
        renombre = {clave: valor for clave, valor in zip(target_columns, nuevas_columnas)}
        df.rename(columns=renombre, inplace=True)
        df = df.sort_values(by="fecha", ascending=True)
        df = df[
            ['fecha', 'sku', 'marca', 'descripcion', 'cod proveedor', 'nombre local', 'venta unidades', 'timbrado']
        ]
        return df

    def normalize_stock(self, df:DataFrame, date) -> DataFrame:
        return df
    
    def read_stock(self, pathfile:Path) -> DataFrame:
        print(f"Leyendo archivo {pathfile}")
        df =  pd.read_csv(pathfile, sep=',', encoding='latin1')
        return df

    def __str__(self):
        return "ILAHUI"