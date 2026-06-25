from controller.view_controller import ViewController
from controller.view_stock_controller import ViewStockController

class AppController():
    def __init__(self, app=None):
        self.app = app
        self.etl_controller = ViewController(self.app.frame.panels["ETL"])
        self.view_stock_controller = ViewStockController(self.app.frame.panels["STOCK"])
        self.etl_controller.run()
        print("[APP CONTROLLER LOG] ETL Controller Run")
        self.view_stock_controller.run()
        print("[APP CONTROLLER LOG] Stock Controller Run")

    def run(self):
        self.app.MainLoop()


    