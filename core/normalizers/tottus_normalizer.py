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
        df = df.drop(df.columns[[1, 2, 3, 4, 11, 12, 13]], axis=1)
        target_columns = ["Historic Sales Tot Pe Fecha Date", "Historic Sales Tot Pe Cod Ean", "Historic Sales Tot Pe Cod SKU", "Historic Sales Tot Pe Desc SKU", "Historic Sales Tot Pe Cod Marca", "Historic Sales Tot Pe Cod Localfisico", "Historic Sales Tot Pe Desc Localfisico", "Historic Sales Tot Pe Qty", "Historic Sales Tot Pe Venta Bruta", "Historic Sales Tot Pe Venta Neta"]
        df = df[target_columns]
        nuevas_columnas = ['date', 'upc','sku', 'descripcion_producto', 'marca', 'cod_local', 'local', 'venta_unidades', "venta_publico", "timbrado"]
        renombre = {clave: valor for clave, valor in zip(target_columns, nuevas_columnas)}
        df.rename(columns=renombre, inplace=True)
        cols = ["venta_publico", "timbrado"]
        df[cols] = df[cols].replace(',', '.', regex=True).astype(float)

        df['date'] = pd.to_datetime(df['date'])
        df = df[df["venta_unidades"] != 0]
        df = df.sort_values(by="date", ascending=True)
        return df
    
    def normalize_stock(self, df:DataFrame, date) -> DataFrame:
        df = df.drop(df.columns[[0, 2, 3, 5, 6, 7, 8, 9, 10, 11, 14, 15]], axis=1)
        df['fecha'] = date

        # target_columns = [
        #     "fecha",
        #     "Vw Ventas E Inventario Tot Pe Cod SKU",
        #     "Vw Ventas E Inventario Tot Pe Cod Localfisico",
        #     "Vw Ventas E Inventario Tot Pe Stock Cont Qty",
        #     "Vw Ventas E Inventario Tot Pe In Transit",
        #     "Vw Ventas E Inventario Tot Pe Stock Cont Cost Amt"
        # ]
        
        target_columns = [
            "fecha",
            "Sku",
            "Nro Local",
            "Inventario Disponible Unidades",
            "En trÃ¡nsito",
            "Costo Inventario Disponible"
        ]        
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