import os
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# URL del excel
TARGET_URL = (
    "https://docs.google.com/spreadsheets/u/1/d/e/"
    "2PACX-1vRvkrtU59YqKYq1zoCIC7x0sItEeq6lUkhmWJpe5BJUg7CRusC2O5WobgBeUS3wT5vWNldJrFkAdy5M"
    "/pubhtml?urp=gmail_link"
)

# Rutas de almacenamiento de datos
DATA_DIR = BASE_DIR / "data"
CURRENT_EXCEL_PATH = DATA_DIR / "current.xlsx"
PREVIOUS_EXCEL_PATH = DATA_DIR / "previous.xlsx"
AUDIT_LOG_PATH = DATA_DIR / "audit_log.csv"
STATE_FILE_PATH = BASE_DIR / "state.json"

# Crear directorio de datos si no existe
DATA_DIR.mkdir(parents=True, exist_ok=True)