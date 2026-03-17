from ..normalizer import Normalizer
import pandas as pd
from pathlib import Path
from pandas import DataFrame
from zipfile import ZipFile
from io import BytesIO

class CencosudNormalizer(Normalizer):
    def read(self, pathdir:Path):

        with ZipFile(pathdir) as rf:
            
            # Buscar archivos CSV dentro del RAR
            archivos_csv = [f for f in rf.namelist() if f.endswith('.csv')]
            
            if not archivos_csv:
                raise ValueError("No se encontró ningún archivo CSV dentro del RAR")
            
            # Tomar el primer CSV encontrado
            nombre_csv = archivos_csv[0]
            
            # Abrir el CSV directamente sin extraerlo al disco
            with rf.open(nombre_csv) as archivo:
                df = pd.read_csv(archivo, sep=',', encoding='latin1')
            
            return [df]

    def normalize_sells(self, df:DataFrame, date):
        df = df.rename(columns={'PERIODO': 'FECHA'})
        df['FECHA'] = pd.to_datetime(df['FECHA'])
        df = df[df['VTA_PERIODO(u)'] != 0]
        columnas = [
            "FECHA",
            "COD_CENCOSUD",
            "COD_PRODUCTO_PROVEEDOR",
            "DESCRIPCION",
            "MARCA",
            "COD_LOCAL",
            "DESCRIPCION_LOCAL",
            "VTA_PERIODO(u)",
            "VTA_PUBLICO($)",
            "VTA_COSTO($)",
            "CANAL_VTA"
        ]

        df = df[columnas]
        df = df.sort_values(by="FECHA", ascending=True)
        return df

    def __str__(self):
        return 'CENCOSUD'
    
    def normalize_stock(self, df:DataFrame, date):
        df["FECHA"] = date
        df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d/%m/%Y")
        target_columns = [
            "FECHA",
            "COD_CENCOSUD",
            "COD_PRODUCTO_PROVEEDOR",
            "DESCRIPCION",
            "MARCA",
            "COD_LOCAL",
            "DESCRIPCION_LOCAL",
            "INVENTARIO(u)",
            "TRANSITO(u)",
            "PRECIO_COSTO"
        ]
        df = df[target_columns].copy()
        nuevas_columnas = ["fecha", "sku", "cod_intek", "descripcion", 
                           "marca", "cod_local", "descripcion_local", 
                           "stock", "transito", "costo unitario"]
        renombre = {clave:valor for clave, valor in zip(target_columns, nuevas_columnas)}
        df.rename(columns=renombre, inplace=True)

        # Convertir columnas a numéricas antes de operar
        df["stock"] = pd.to_numeric(df["stock"], errors="coerce").clip(lower=0)
        df["transito"] = pd.to_numeric(df["transito"], errors="coerce").clip(lower=0)
        df["costo unitario"] = pd.to_numeric(df["costo unitario"], errors="coerce")

        df["stock"] = df["stock"].apply(lambda x: x if x > 0 else 0) 
        df["transito"] = df["transito"].apply(lambda x: x if x > 0 else 0)
        df["stock total"] = df["stock"] + df["transito"]
        df["costo tot stock"] = df["costo unitario"]*df["stock total"]
        df = df[["fecha", "sku", "cod_intek", "descripcion", 
                           "marca", "cod_local", "descripcion_local", 
                           "stock total", "stock", "transito", "costo unitario", "costo tot stock"]]
        df = df[df["stock total"] > 0]
        return df

    def read_stock(self, pathfile:Path) -> DataFrame:
        with ZipFile(pathfile, 'r') as zip_file:
            nombre_archivo = zip_file.namelist()[0]
            contenido_csv = BytesIO(zip_file.read(nombre_archivo))
            df = pd.read_csv(contenido_csv, sep=',', encoding='latin1')
            return df