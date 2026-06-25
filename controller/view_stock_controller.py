from pathlib import Path
import pandas as pd
from view.wx_panels.stock_panel import StockPanel
import wx
import config


class ViewStockController():
    def __init__(self, view=StockPanel):
        self.view = view
        self.df = None
        self.costo_unitario = 0
    
    def set_stock_data(self, data:pd.DataFrame):
        self.view.set_dataframe(data)
    
    def read_data_stock(self) -> pd.DataFrame:
        df = pd.read_excel(config.STOCK_FILE_PATH, sheet_name="ABRIL2026", header=2)
        df = df[["SKU", "DESCRIPCION", "STOCK  LOS OLIVOS21.04.26\n", "Costo Unit Reg. \nSistema", "PVP", "VALORIZADO \nCOD SIST 101",
                 "UNIDAD MÍNIMA DESPACHO", "MASTER\nPACK", "MARCA"
                 ]]
        self.df = df
        return df

    def run(self):
        if Path(config.STOCK_FILE_PATH).exists() == False:
            wx.MessageBox("No se ha configurado la ruta del archivo de stock. Por favor, configurela en AppConfig.", "Error", wx.OK | wx.ICON_ERROR)
            return
        df = self.read_data_stock()
        self.set_stock_data(df)
        print(f"[STOCK CONTROLLER LOG] Stock loaded: {config.STOCK_FILE_PATH}")
        self.set_on_search()
        self.set_on_type_new_pvp()

    def set_on_search(self):
        # self.view.bind_search_key_down(self._search_stock)
        # self.view.bind_search_key_up(self._search_stock)
        self.view.bind_search_text(self._search_stock)
        self.view.bind_search_enter(self._search_stock_key_down)
    
    def set_on_type_new_pvp(self):
        self.view.bind_type_new_pvp(self._type_new_pvp)
    
    def _search_stock_key_down(self, event):
        sku_buscado = self.view.get_input_sku().strip()
        print("Enter key pressed: ", sku_buscado)
        
        if self.df is not None:
            # 1. Intentar búsqueda exacta primero
            exact_match = self.df[self.df["SKU"].astype(str) == sku_buscado]
            
            if not exact_match.empty:
                # Si hay coincidencia exacta (ej. 1416228), mostramos solo esa
                self.set_stock_data(exact_match)
                print(f"Coincidencia exacta encontrada: {sku_buscado}")
                
                # Opcional: Rellenar los campos intermedios con la data de esta fila
                print((exact_match.iloc[0]))

                self.view.set_txt_descripcion(str(exact_match.iloc[0]["DESCRIPCION"]))
                self.view.set_txt_pvp(str(exact_match.iloc[0]["PVP"]))
                self.costo_unitario = exact_match.iloc[0]["Costo Unit Reg. \nSistema"]


            # else:
            #     # 2. Si no hay exacta, buscar por coincidencia parcial y tomar la primera
            #     partial_match = self.df[self.df["SKU"].astype(str).str.contains(sku_buscado, case=False, na=False)]
                
            #     if not partial_match.empty:
            #         # Tomamos solo la primera fila de los resultados parciales
            #         primera_fila = partial_match.iloc[[0]] 
            #         self.set_stock_data(primera_fila)
            #         print(f"No hay exacta. Mostrando primer resultado parcial para: {sku_buscado}")
                    
            #         print((primera_fila.iloc[0]))
        
        event.Skip()

    def _search_stock(self, event):
        texto = self.view.get_input_sku().strip()

        if self.df is None:
            return

        # Buscar en SKU
        filtered_df = self.df[
            self.df["SKU"].astype(str).str.contains(texto, case=False, na=False)
        ]

        # Si no encuentra, buscar en descripción
        if filtered_df.empty:
            filtered_df = self.df[
                self.df["DESCRIPCION"].astype(str).str.contains(texto, case=False, na=False)
            ]

        # Si tampoco encuentra, buscar en marca
        if filtered_df.empty:
            filtered_df = self.df[
                self.df["MARCA"].astype(str).str.contains(texto, case=False, na=False)
            ]

        if filtered_df.empty:
            filtered_df = self.df[self.df["PVP"] == float(texto)]

        self.set_stock_data(filtered_df) 

        
    def _type_new_pvp(self, event):
        nuevo_pvp = float(self.view.get_txt_nuevo_pvp().strip())
        print("Nuevo PVP ingresado: ", nuevo_pvp)
        nuevo_mg = round((1 - self.costo_unitario/(nuevo_pvp*0.65/1.18))*100, 2)
        print("Nuevo MG% calculado: ", nuevo_mg)
        self.view.set_txt_nuevo_mg(str(nuevo_mg) + "%")
        # Aquí podrías agregar lógica para validar el nuevo PVP o actualizar la tabla según corresponda
        
