from controller.view_controller import ViewController
from controller.view_stock_controller import ViewStockController

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


    