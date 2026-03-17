from ..normalizer import Normalizer
import pandas as pd

class EstilosNormalizer(Normalizer):
    def read(self, pathdir:Path):
        if pathdir.is_file():
            df = pd.read_excel(pathdir)
            df = df.iloc[:-1].copy()
            return [df]

    
    def normalize_sells(self, df:DataFrame, date):

        date = pd.to_datetime(date, format="%d/%m/%Y")
        print("El datetime es: ", date)
        df["Venta UN AAc"] = pd.to_numeric(df["Venta UN AAc"], errors="coerce").fillna(0)
        df["DiaMes"] = pd.to_numeric(df["DiaMes"], errors="coerce").fillna(0).astype(int)
        df["Fecha"] = pd.to_datetime(date.strftime("%Y-%m-") + df["DiaMes"].astype(str), format="%Y-%m-%d")
        df = df[["Fecha", "Sku", "Descripcion", "Tienda", "Venta UN AAc", "Venta Neta AAc"]]
        df = df[df["Venta UN AAc"] > 0]
        df = df.sort_values(by="Fecha", ascending=True)
        df = df.reset_index(drop=True)

