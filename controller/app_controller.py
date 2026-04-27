from core.normalizer_factory import NormalizerFactory
from pathlib import Path
from tkinter import messagebox
from config import AppConfig
from controller.view_controller import ViewController
from controller.view_stock_controller import ViewStockController
import traceback
import os
from core.updater import Updater

AppConfig.load()

OUTPUT_PATH = AppConfig.get_output_path()
ICON_PATH = AppConfig.get_icon_path()
STOCK_FILE_PATH = AppConfig.get_stock_file_path()

class AppController():
    def __init__(self, app=None):
        self.app = app
        self.etl_controller = ViewController(self.app.frame.panels["ETL"])
        self.view_stock_controller = ViewStockController(self.app.frame.panels["STOCK"])
        self.etl_controller.run()
        print("etl controller run")
        self.view_stock_controller.run()
        print("stock controller run")
        
    def run(self):
        self.app.MainLoop()


    