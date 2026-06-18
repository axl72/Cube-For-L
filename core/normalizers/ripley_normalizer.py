from ..normalizer import Normalizer
import pandas as pd
from pathlib import Path
from pandas import DataFrame


class RipleyNormalizer(Normalizer):
    def read(self, pathdir:Path):
        if pathdir.is_file():
            df = pd.read_excel(pathdir, header=None)
            return [df]
        df_list = [pd.read_excel(path, header=None) for path in pathdir.iterdir() if str(path.absolute()).endswith('.xlsx')]
        return df_list

    def normalize_sells(self, df:DataFrame, date):
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
        temp["sku"] = pd.to_numeric(temp["sku"], errors='coerce')
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
        temp = temp[temp["stock_unidades"] != 0]
        temp["sku"] = pd.to_numeric(temp["sku"], errors='coerce')

        return temp[nuevas_columnas]