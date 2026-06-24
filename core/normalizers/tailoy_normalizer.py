from ..normalizer import Normalizer
import pandas as pd
from pathlib import Path
from pandas import DataFrame, Timestamp
from datetime import datetime, timedelta
import pyzipper

class TaiLoyNormalizer(Normalizer):
    def obtenerSemanaComercial(self, fecha_inicio:Timestamp):

        # Definir el rango de fechas
        inicio_rango = fecha_inicio

        # Encontrar el primer lunes del año
        primer_lunes = datetime(inicio_rango.year, 1, 1)
        while primer_lunes.weekday() != 0:  # 0 representa lunes en Python
            primer_lunes += timedelta(days=1)

        # Determinar el número de semanas transcurridas desde el primer lunes del año hasta la fecha de inicio
        numero_semanas = ((inicio_rango - primer_lunes).days // 7) + 1
        return numero_semanas


    def read(self, pathdir:Path):
        with pyzipper.AESZipFile(pathdir, mode='r') as rf:
            
            # Buscar archivos CSV dentro del RAR
            rf.setpassword(b'20600768043')
            archivos_csv = [f for f in rf.namelist() if f.endswith('.csv')]
            
            if not archivos_csv:
                raise ValueError("No se encontró ningún archivo CSV dentro del RAR")
            
            # Tomar el primer CSV encontrado
            nombre_csv = archivos_csv[0]
            
            # Abrir el CSV directamente sin extraerlo al disco
            with rf.open(nombre_csv, pwd=b'20600768043') as archivo:
                df = pd.read_csv(archivo, sep=';', encoding='latin1')
                print(df.head())
                return [df]

    # def normalize_sells(self, df:DataFrame):
        # result = df.iloc[6:]
        # result.columns = result.iloc[0]
        # result.reset_index(drop=True, inplace=True)
        # result = result[1:]
        # columnas_a_eliminar = ['GRUPO', 'CATEGORÍA', 'UNIDAD BASE', 'ESTADO', 'TOTAL VENTAS']
        
        # result = result.drop(columnas_a_eliminar, axis=1)
        # result = pd.melt(result, id_vars=['FECHA INICIAL', 'FECHA FINAL', 'CÓDIGO AS400', 'CÓDIGO SAP', 'DESCRIPCIÓN'], var_name='TIENDA', value_name='UNIDADES', col_level=0)
        # result = result[result['UNIDADES'] != 0]
        # result.reset_index(drop=True, inplace=True)
        # result['FECHA INICIAL'] = result['FECHA INICIAL'].str.strip()
        # result['FECHA FINAL'] = result['FECHA FINAL'].str.strip()
        # result['FECHA INICIAL'] = pd.to_datetime(result['FECHA INICIAL'], format='%Y%m%d')
        # result['FECHA FINAL'] = pd.to_datetime(result['FECHA FINAL'], format='%Y%m%d')  


        # result['CÓDIGO AS400'] = result['CÓDIGO AS400'].apply(lambda x: int(x))
        # result['CÓDIGO SAP'] = result['CÓDIGO SAP'].apply(lambda x: int(x))
        # result['SEMANA'] = self.obtenerSemanaComercial(result['FECHA INICIAL'].iloc[0])
        
        # return result

    def normalize_sells(self, df:DataFrame, date):

        df.rename(columns={'FECHA INICIAL': 'FECHA', 'ALMACEN TIENDA': 'ALM', "CÃDIGO AS400": "AS400", "CÃDIGO SAP": "SAP", "DESCRIPCIÃN": "DESCRIPCION"}, inplace=True)
        df['FECHA'] = pd.to_datetime(df['FECHA'], format='%Y%m%d')
        df = df[["FECHA", "ALM", "AS400", "SAP", "DESCRIPCION", "ESTADO", "VENTA S/", "VENTA UNIDADES"]]
        df["SAP"] = pd.to_numeric(df["SAP"], errors='coerce')
        df = df[df['VENTA UNIDADES'] != 0]
        df = df.sort_values(by="FECHA", ascending=True)
        return df
    
    def __str__(self):
        return "TAI LOY"
    
    def normalize_stock(self, df:DataFrame, date) -> DataFrame:
        df = df.drop(columns=["COMPRADOR", "GRUPO", "CATEGORÃA", "UNIDAD BASE", "ABC", "TRÃNSITO TOTAL", "STOCK FÃSICO TOTAL"])
        df = df.melt(
            id_vars=["CÃDIGO AS400", "CÃDIGO SAP", "DESCRIPCIÃN", "ESTADO"],      # columnas que se mantienen fijas
            var_name="TIENDA",           # nombre de la nueva columna con nombres de tienda
            value_name="UNIDADES"        # nombre de la columna con los valores
    )
        df = df[df["UNIDADES"] > 0]
        df = df.reset_index(drop=True)
        df["FECHA"] = date
        df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d/%m/%Y")

        target_columns = [
            "FECHA",
            "CÃDIGO AS400",
            "CÃDIGO SAP",
            "DESCRIPCIÃN",
            "ESTADO",
            "TIENDA",
                "UNIDADES"
            ]
            
        nuevas_columnas = ["FECHA", "SKU AS400", "SKU SAP", "DESCRIPCION", "ESTADO", "TIENDA", "UNIDADES"]
        renombre = {clave: valor for clave, valor in zip(target_columns, nuevas_columnas)}

        df.rename(columns=renombre, inplace=True)
        df = df[nuevas_columnas]    
        return df

    def read_stock(self, pathfile:Path) -> DataFrame:
        with pyzipper.AESZipFile(pathfile, mode='r') as rf:
                
                # Buscar archivos CSV dentro del RAR
                rf.setpassword(b'20600768043')
                archivos_csv = [f for f in rf.namelist() if f.endswith('.csv')]
                
                if not archivos_csv:
                    raise ValueError("No se encontró ningún archivo CSV dentro del RAR")
                
                # Tomar el primer CSV encontrado
                nombre_csv = archivos_csv[0]
                
                # Abrir el CSV directamente sin extraerlo al disco
                with rf.open(nombre_csv, pwd=b'20600768043') as archivo:
                    df = pd.read_csv(archivo, sep=';', encoding='latin1')
                
                return df