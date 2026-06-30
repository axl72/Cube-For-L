from ..normalizer import Normalizer
import pandas as pd
from pathlib import Path
from pandas import DataFrame

from zipfile import ZipFile
from io import BytesIO

class OechsleNormalizer(Normalizer):
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
        df = df[df['VTA_PERIODO_UNID'] != 0]
        df = df.sort_values(by="FECHA", ascending=True)
        return df

    def __str__(self):
        return 'OECHSLE'
    
    def normalize_stock(self, df:DataFrame, date):
        df["fecha"] = date
        df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
        target_columns = ["fecha", "COD_OECHSLE", "COD_PRODUCTO_PROVEEDOR", "DESCRIPCION_PRODUCTO", "MARCA",
                          "ESTADO_PRODUCTO", 
                          "COD_LOCAL", "DESCRIPCION_LOCAL", "STOCK(U)", "TRANSITO(U)", "STOCKNODISP.(U)", "ASIGNADO(U)"]
        df = df[target_columns]
        df = df[~df["DESCRIPCION_PRODUCTO"].str.contains(r"\b(REBATE|REB)\b", case=False, na=False)]
        df = df[~df["DESCRIPCION_PRODUCTO"].str.contains(r"\b(OLYMPUS)\b", case=False, na=False)]
        nuevas_columnas = ["fecha", "sku", "cod_intek", "descripcion", "marca", "estado","cod_local", "descripcion_local", "stock", "transito", "stock_no_disponible", "asignado"]
        renombre = {clave:valor for clave, valor in zip(target_columns, nuevas_columnas)}
        df.rename(columns=renombre, inplace=True)
        df["cod_local"] = df["cod_local"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True) # Aplica la función espacios a la columna cod_local
        df["stock"] = df["stock"].apply(lambda x: x if x > 0 else 0) 
        df["transito"] = df["transito"].apply(lambda x: x if x > 0 else 0)
        df["stock_no_disponible"] = df["stock_no_disponible"].apply(lambda x: x if x > 0 else 0)
        df["asignado"] = df["asignado"].apply(lambda x: x if x > 0 else 0)
        df["fecha"] = pd.to_datetime(df["fecha"], format="%Y%m%d")
        df["stock_total"] = df["stock"] + df["transito"] + df["stock_no_disponible"] + df["asignado"]
        df = df[df["stock_total"] > 0]
        return df

    def read_stock(self, pathfile:Path) -> DataFrame:
        with ZipFile(pathfile, 'r') as zip_file:
            nombre_archivo = zip_file.namelist()[0]
            contenido_csv = BytesIO(zip_file.read(nombre_archivo))
            df = pd.read_csv(contenido_csv, sep=',', encoding='latin1')
            return df