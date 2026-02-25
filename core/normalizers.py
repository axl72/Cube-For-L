import pandas as pd
import datetime
from core.normalizer import Normalizer
from pathlib import Path
from pandas import DataFrame
from datetime import datetime, timedelta
from pandas._libs.tslibs.timestamps import Timestamp
from zipfile import ZipFile
from io import BytesIO
import numpy as np
import rarfile
import zipfile
import pyzipper

class EstilosNormalizer(Normalizer):
    def read(self, pathdir:Path):
        if pathdir.is_file():
            df = pd.read_excel(pathdir)
            df = df.iloc[:-1].copy()
            return [df]

    
    def normalize_sells(self, df:DataFrame):
        df["Venta UN AAc"] = pd.to_numeric(df["Venta UN AAc"], errors="coerce").fillna(0)
        df["DiaMes"] = pd.to_numeric(df["DiaMes"], errors="coerce").fillna(0).astype(int)
        df["Fecha"] = pd.to_datetime("2026-01-" + df["DiaMes"].astype(str), format="%Y-%m-%d")
        df = df[["Fecha", "Sku", "Descripcion", "Tienda", "Venta UN AAc", "Venta Neta AAc"]]
        df = df[df["Venta UN AAc"] > 0]
        df = df.reset_index(drop=True)
        return df
    
    def normalize_stock(self, df:DataFrame, date):
        df = df.copy()
        df["DiaMes"] = pd.to_numeric(df["DiaMes"], errors="coerce").fillna(0).astype(int)
        df["Fecha"] = pd.to_datetime("2026-01-" + df["DiaMes"].astype(str), format="%Y-%m-%d")
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

    def read_stock(self, pathfile:Path) -> DataFrame:
        df = pd.read_excel(pathfile)
        df = df.iloc[:-1].copy()
        return df
class OechsleNormalizer(Normalizer):
    def read(self, pathdir:Path):

        with zipfile.ZipFile(pathdir) as rf:
            
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

    def normalize_sells(self, df:DataFrame):
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
        nuevas_columnas = ["fecha", "sku", "cod_intek", "descripcion", "marca", "estado","cod_local", "descripcion_local", "stock", "transito", "stock_no_disponible", "asignado"]
        renombre = {clave:valor for clave, valor in zip(target_columns, nuevas_columnas)}
        df.rename(columns=renombre, inplace=True)

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
class RipleyNormalizer(Normalizer):
    def read(self, pathdir:Path):
        if pathdir.is_file():
            df = pd.read_excel(pathdir, header=None)
            return [df]
        df_list = [pd.read_excel(path, header=None) for path in pathdir.iterdir() if str(path.absolute()).endswith('.xlsx')]
        return df_list

    def normalize_sells(self, df:DataFrame):
        """Funcion que sirve para normalizar un dataframe de Ripley. Normalizar implica que el archivo descargado del B2B de ripley quede en forma normal para el análisis."""
        target_columns = ["Fecha","Codigo Sucursal", "Codigo Modelo", "Venta S/.", "Venta Unid.", "Costo Venta Actual"]
        extrae = lambda x, y: df.iloc[x, y]
        lista_campos = {extrae(i,0) if i == 0 else extrae(i, 0):extrae(i, 1) for i in range(5)}
        temp = df.drop(index=range(8))
        # Establecer la primera fila como columnas
        temp.columns = temp.iloc[0]
        temp = temp[1:]

        temp.reset_index(drop=True, inplace=True)

        for campo, valor in lista_campos.items():
            temp[campo] = valor    

        temp["Fecha"] = pd.to_datetime(temp["Fecha"], format="%d-%m-%Y")
        temp = temp[temp['Venta Unid.'] != 0]

        nuevas_columnas = ["fecha", "codigo_sucursal", "sku", "venta_soles", "venta_unidades", "costo_venta"]
        renombre = {clave: valor for clave, valor in zip(target_columns, nuevas_columnas)}
        temp.rename(columns=renombre, inplace=True)
        # Corregir esto, puede ser algo como return temp[nuevas_columas] if complete else temp
        return temp[nuevas_columnas]
    
    def __str__(self):
        return "RIPLEY"
    
    def read_stock(self, pathfile:Path) -> DataFrame:
        if str(pathfile.absolute()).endswith('.xlsx'):
            df = pd.read_excel(pathfile, header=None)
            print("Archivo Ripley leido con exito")
            return df

    
    def normalize_stock(self, df:DataFrame, date):
        """Funcion que sirve para normalizar un dataframe de Ripley. Normalizar implica que el archivo descargado del B2B de ripley quede en forma normal para el análisis."""

        target_columns = ["Fecha","Codigo Sucursal", "Codigo Modelo", "Stock S/.", "Stock Und."]
        extrae = lambda x, y: df.iloc[x, y]
        lista_campos = {extrae(i,0) if i == 0 else extrae(i, 0):extrae(i, 1) for i in range(5)}
        temp = df.drop(index=range(8))
        # Establecer la primera fila como columnas
        temp.columns = temp.iloc[0]
        temp = temp[1:]

        temp.reset_index(drop=True, inplace=True)

        for campo, valor in lista_campos.items():
            temp[campo] = valor    

        temp["Fecha"] = pd.to_datetime(temp["Fecha"], format="%d-%m-%Y")

        nuevas_columnas = ["fecha", "codigo_sucursal", "sku", "stock_soles", "stock_unidades"]
        renombre = {clave: valor for clave, valor in zip(target_columns, nuevas_columnas)}
        temp.rename(columns=renombre, inplace=True)
        print("Se filtraran la unidades")
        temp = temp[temp["stock_unidades"] != 0]

        return temp[nuevas_columnas]

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

    def normalize_sells(self, df:DataFrame):

        df.rename(columns={'FECHA INICIAL': 'FECHA', 'ALMACEN TIENDA': 'ALM', "CÃDIGO AS400": "AS400", "CÃDIGO SAP": "SAP", "DESCRIPCIÃN": "DESCRIPCION"}, inplace=True)
        df['FECHA'] = pd.to_datetime(df['FECHA'], format='%Y%m%d')
        df = df[["FECHA", "ALM", "NOMBRE TIENDA", "AS400", "SAP", "DESCRIPCION", "ESTADO", "VENTA S/", "VENTA UNIDADES"]]
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

    def normalize_sells(self, df:DataFrame) -> DataFrame:
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

class SagaNormalizer(Normalizer):
    def read(self, pathdir:Path):
        print(f"Leyendo archivo {pathdir}")
        if pathdir.is_file():
            df = pd.read_csv(pathdir, sep=',', encoding='latin1')
            return [df]

        df_list = []
        for path in pathdir.iterdir():
            df =  pd.read_csv(path, sep=',', encoding='latin1')
            df_list.append(df)
        return df_list
    
    def normalize_sells(self, df:pd.DataFrame):
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
        df[cols] = df[cols].replace(',', '.', regex=True).astype(float)
        return df

    def __str__(self):
        return "SAGA-FALABELLA"


    
    def read_stock(self, pathfile:Path) -> DataFrame:
        print(f"Leyendo archivo {pathfile}")
        df =  pd.read_csv(pathfile, sep=',', encoding='latin1', header=0)
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

class CencosudNormalizer(Normalizer):
    def read(self, pathdir:Path):

        with zipfile.ZipFile(pathdir) as rf:
            
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

    def normalize_sells(self, df:DataFrame):
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