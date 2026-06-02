from ..normalizer import Normalizer
from pathlib import Path
from pandas import DataFrame
import pandas as pd


class VegaNormalizer(Normalizer):

    def normalize_sells(self, df: DataFrame, date) -> DataFrame:
        target_columns = [
            "FECHA",
            "DESC_MARCA",
            "CodProducto",
            "PRODUCTO",
            "Sucursal",
            "Formato",
            "ValorVenta",
            "Cantidad",
            "COD_SUCURSAL",
        ]

        df = df[target_columns]
        nuevas_columnas = [
            "fecha",
            "marca",
            "sku",
            "descripcion_producto",
            "local",
            "formato",
            "venta_publico",
            "venta_unidades",
            "cod_sucursal",
        ]
        renombre = {
            clave: valor for clave, valor in zip(target_columns, nuevas_columnas)
        }
        df.rename(columns=renombre, inplace=True)
        df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")
        df = df[df["venta_unidades"] != 0]
        df["sku"] = pd.to_numeric(df["sku"], errors="coerce")

        return df

    def normalize_stock(self, df: DataFrame, date) -> DataFrame:
        target_columns = [
            "FECHA",
            "Producto",
            "Sucursal",
            "CodProducto",
            "StockFisico",
            "TCP",
            "CUC",
            "COD_SUCURSAL",
        ]
        df = df[target_columns]
        nuevas_columnas = [
            "fecha",
            "linea",
            "local",
            "sku",
            "stock_fisico",
            "tcp",
            "cuc",
            "cod_sucursal",
        ]
        renombre = {
            clave: valor for clave, valor in zip(target_columns, nuevas_columnas)
        }
        df.rename(columns=renombre, inplace=True)
        df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")
        df["sku"] = pd.to_numeric(df["sku"], errors="coerce")
        df = df[df["stock_fisico"] != 0]

        return df

    def read(self, pathdir: Path) -> list[DataFrame]:
        if pathdir.is_file():
            df = pd.read_csv(pathdir, sep=",", encoding="latin1", decimal=".")
            return [df]
        df_list = []
        for path in pathdir.iterdir():
            df = pd.read_csv(path, sep=",", encoding="latin1", decimal=".")
            df["fecha"] = str(path).split("\\")[-1].split(".")[0]
            df_list.append(df)
        return df_list

    def read_stock(self, pathdir: Path) -> DataFrame:
        if pathdir.is_file():
            df = pd.read_csv(pathdir, sep=",", encoding="latin1", decimal=".")
            return df
        df_list = []
        for path in pathdir.iterdir():
            df = pd.read_csv(path, sep=",", encoding="latin1", decimal=".")
            df["fecha"] = str(path).split("\\")[-1].split(".")[0]
            df_list.append(df)
        return df_list

    def __str__(self):
        return "GRUPO VEGA"
