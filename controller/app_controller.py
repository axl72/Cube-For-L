from core.normalizer_factory import NormalizerFactory
from pathlib import Path
from tkinter import messagebox
from config import AppConfig
from controller.view_controller import ViewController
import traceback
import os
from core.updater import Updater

AppConfig.load()

OUTPUT_PATH = AppConfig.get_output_path()
ICON_PATH = AppConfig.get_icon_path()

class AppController():
    def __init__(self, app=None):
        self.app = app
        self.etl_controller = ViewController(self.app.frame.panels["ETL"])
        self.etl_controller.run()
        
    def run(self):
        self.app.MainLoop()


    