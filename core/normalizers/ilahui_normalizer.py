from ..normalizer import Normalizer
from pathlib import Path
from pandas import DataFrame
import pandas as pd

class IlahuiNormalizer(Normalizer):
    def read(self, pathdir:Path) -> list[DataFrame]:
        if pathdir.is_file():
            df = pd.read_csv(pathdir, sep=',', encoding='latin1')
            return [df]
        df_list = []
        for path in pathdir.iterdir():
            df =  pd.read_csv(path, sep=',', encoding='latin1')
            df_list.append(df)
        return df_list
    
    def normalize_sells(self, df:DataFrame, date) -> DataFrame:
        return df

    def normalize_stock(self, df:DataFrame, date) -> DataFrame:
        return df

    def __str__(self):
        return "ILAHUI"