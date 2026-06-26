from controller.app_controller import AppController
from core.normalizer_factory import NormalizerFactory
from view.new_wx_view import MainFrame
import wx

class App(wx.App):
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show()
        return True

if __name__ == "__main__":
    factory = NormalizerFactory()
    factory.create_all()
    app = App(False)
    app_controller = AppController(app=app)
    app_controller.run()