from ..normalizer import Normalizer
import pandas as pd
from pathlib import Path
from pandas import DataFrame

class TottusNormalizer(Normalizer):
    def read(self, pathdir:Path) -> list[DataFrame]:
        if pathdir.is_file():
            df = pd.read_csv(pathdir, sep=',', encoding='latin1')
            return [df]
        df_list = []
        for path in pathdir.iterdir():
            df =  pd.read_csv(path, sep=',', encoding='latin1')
            df['fecha'] = str(path).split('\\')[-1].split('.')[0]
            df_list.append(df)
        return df_list
    
    # def read_stock(self, pathfile:Path) -> DataFrame:
    #     print(f"Leyendo archivo {pathfile}")
    #     df =  pd.read_csv(pathfile, sep=',', encoding='latin1')
    #     df['fecha'] = str(pathfile).split('\\')[-1].split('.')[0]
    #     return df

    def read_stock(self, pathfile:Path) -> DataFrame:
        print(f"Leyendo archivo {pathfile}")
        df =  pd.read_csv(pathfile, sep=',', encoding='latin1')
        return df

    def normalize_sells(self, df:DataFrame, date) -> DataFrame:

        column_sets = [
            ["Historic Sales Tot Pe Fecha Date", "Historic Sales Tot Pe Cod Ean", "Historic Sales Tot Pe Cod SKU", 
            "Historic Sales Tot Pe Desc SKU", "Historic Sales Tot Pe Cod Marca", "Historic Sales Tot Pe Cod Localfisico", 
            "Historic Sales Tot Pe Desc Localfisico", "Historic Sales Tot Pe Qty", 
            "Historic Sales Tot Pe Venta Bruta", "Historic Sales Tot Pe Venta Neta"],

            ["Fecha Date", "Cod Ean", "Cod SKU", "Desc SKU", "Cod Marca", 
            "Cod Localfisico", "Desc Localfisico", "Venta en Unidades", 
            "Venta Bruta", "Venta Neta"]
        ]

        target_columns = evaluate_columns(df, column_sets)

        df = df[target_columns]
        nuevas_columnas = ['date', 'upc','sku', 'descripcion_producto', 'marca', 'cod_local', 'local', 'venta_unidades', "venta_publico", "timbrado"]
        renombre = {clave: valor for clave, valor in zip(target_columns, nuevas_columnas)}
        df.rename(columns=renombre, inplace=True)
        cols = ["venta_publico", "timbrado"]
        df[cols] = df[cols].replace(',', '.', regex=True).astype(float) # Esta línea tenemos que corregirla pero ya!

        df['date'] = pd.to_datetime(df['date'])
        df = df[df["venta_unidades"] != 0]
        df = df.sort_values(by="date", ascending=True)
        return df
    
    def normalize_stock(self, df:DataFrame, date) -> DataFrame:
        df['fecha'] = date

        column_sets = [
            ["fecha",
            "Vw Ventas E Inventario Tot Pe Cod SKU",
            "Vw Ventas E Inventario Tot Pe Cod Localfisico",
            "Vw Ventas E Inventario Tot Pe Stock Cont Qty",
            "Vw Ventas E Inventario Tot Pe In Transit",
            "Vw Ventas E Inventario Tot Pe Stock Cont Cost Amt"],
        
            ["fecha",
            "Sku",
            "Nro Local",
            "Inventario Disponible Unidades",
            "En trÃ¡nsito",
            "Costo Inventario Disponible"]        
        ]

        target_columns = evaluate_columns(df, column_sets)

        df = df[target_columns]
        nuevas_columnas = ["fecha","sku", "cod_local", "stock_locales", "stock_transito", "stock_costo"]
        renombre = {clave: valor for clave, valor in zip(target_columns, nuevas_columnas)}
        df.rename(columns=renombre, inplace=True)

        df["stock_locales"] = df["stock_locales"].apply(lambda x: x if x > 0 else 0)
        df["stock_transito"] = df["stock_transito"].apply(lambda x: x if x > 0 else 0)
        df["stock_costo"] = df["stock_costo"].replace(r'\$', '', regex=True).astype(float)
        df["stock_costo"] = df["stock_costo"].apply(lambda x: x if x > 0 else 0)

        df["stock_total"] = df["stock_locales"] + df["stock_transito"]
        df = df[df["stock_total"] != 0]
        df.reset_index(drop=True, inplace=True)
        df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
        return df
    
    def __str__(self):
        return 'TOTTUS'

def evaluate_columns(df:DataFrame, column_sets:list[list]) -> list[str]:
    target_columns = None

    for cols in column_sets:
        if set(cols).issubset(df.columns):
            target_columns = cols
            break

    if target_columns is None:
        missing_info = [
            [col for col in cols if col not in df.columns]
            for cols in column_sets
        ]
        raise ValueError(
            f"El DataFrame no coincide con ningún formato esperado. "
            f"Columnas faltantes por formato: {missing_info}"
        )
    
    return target_columns