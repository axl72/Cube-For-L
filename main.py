from controller.view_controller import ViewController
from core.normalizer_factory import NormalizerFactory
from view.view import MainWindow

if __name__ == "__main__":
    ViewController().print()
    factory = NormalizerFactory()
    factory.create_all()
    view = MainWindow()
    controller = ViewController(view=view)
    controller.run()