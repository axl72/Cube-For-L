import sys
import getpass
from pathlib import Path
import json
import os

# sys.path.append('C:\\Users\\USUARIO\\Desktop\\INTEK\\updata_database')

USER = getpass.getuser()
documents_path = Path.home() / "Documents"
CONFIG_PATH = Path(documents_path) / "config.json"
class AppConfig:

    _config_file = Path(CONFIG_PATH)
    _data = {}

    @classmethod
    def load(cls):
        if not cls._config_file.exists():
            print("Config file not found. Creating default config.")
            cls._create_default_config()

        with open(cls._config_file, "r", encoding="utf-8") as f:
            cls._data = json.load(f)
            print(f"Config loaded: {cls._data}")

        # Si OUTPUT_PATH está vacío lo genera automáticamente
        if not cls._data.get("OUTPUT_PATH"):
            user = getpass.getuser()
            default_path = Path(f"C:/Users/{user}/Desktop/REGISTROS INTEK/OUTPUTS")
            cls._data["OUTPUT_PATH"] = str(default_path)
            cls._save()
        
        if "STOCK_FILE_PATH" not in cls._data:
            cls._data["STOCK_FILE_PATH"] = str(Path(f"C:/Users/{USER}/Desktop/INTEK/inventarios/INVENTARIO DISPONIBLE - 21.04.26.xlsx"))
            cls._save()

    @classmethod
    def _create_default_config(cls):
        default_data = {
            "OUTPUT_PATH": f"C:\\Users\\{USER}\\Desktop\\REGISTROS INTEK\\OUTPUTS",
            "ICON_PATH": "assets/perro-tejonero.ico"
        }
        with open(cls._config_file, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)

    @classmethod
    def _save(cls):
        with open(cls._config_file, "w", encoding="utf-8") as f:
            json.dump(cls._data, f, indent=4)

    # --------- GETTERS ---------

    @classmethod
    def get_output_path(cls) -> Path:
        return Path(cls._data["OUTPUT_PATH"])

    @classmethod
    def get_icon_path(cls) -> Path:
        return Path(cls._data["ICON_PATH"])
    
    @classmethod
    def get_stock_file_path(cls) -> Path:
        return Path(cls._data["STOCK_FILE_PATH"])

    # --------- SETTERS ---------

    @classmethod
    def set_output_path(cls, new_path: str):
        cls._data["OUTPUT_PATH"] = new_path
        Path(new_path).mkdir(parents=True, exist_ok=True)
        cls._save()

    @classmethod
    def set_icon_path(cls, new_path: str):
        cls._data["ICON_PATH"] = new_path
        cls._save()