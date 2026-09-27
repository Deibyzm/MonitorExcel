from pathlib import Path
from modules.fetcher import fetch_remote_excel
from modules.comparator import compare_excel_versions
# from modules.notifier import send_telegram_alert  # Lo activaremos en un momento

# Configuración de rutas y URL institucional
TARGET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRvkrtU59YqKYq1zoCIC7x0sItEeq6lUkhmWJpe5BJUg7CRusC2O5WobgBeUS3wT5vWNldJrFkAdy5M/pubhtml?urp=gmail_link"
DATA_DIR = Path("data")
CURRENT_FILE = DATA_DIR / "current.xlsx"
OLD_FILE = DATA_DIR / "old.xlsx"


def main():
    print("=== [ETL] Iniciando ciclo de verificación de la hoja de cálculo ===")

    # Paso 1: Descargar la versión más reciente
    success = fetch_remote_excel(TARGET_URL, CURRENT_FILE)
    if not success:
        print("[ERROR] El proceso se interrumpió porque falló la descarga web.")
        return

    # Paso 2: Comparar con la versión anterior
    diff_result = compare_excel_versions(OLD_FILE, CURRENT_FILE)

    # Paso 3: Evaluar si hubo cambios reales
    if not diff_result.empty:
        print("[AVISO] ¡Se detectaron cambios reales en las celdas del Excel!")
        
        # AQUÍ CONECTAREMOS TELEGRAM PRONTO:
        # send_telegram_alert(token="TU_TOKEN", chat_id="TU_CHAT_ID", message="¡Hay cambios en el Excel!")
        
    else:
        print("[INFO] No hay modificaciones en los datos tabulares.")

    # Paso 4: Rotar archivos (actualizar el histórico)
    if CURRENT_FILE.exists():
        # Si ya teníamos un archivo viejo, lo reemplazamos o actualizamos
        import shutil
        shutil.copy(CURRENT_FILE, OLD_FILE)

    print("=== [ETL] Ciclo finalizado y estado actualizado correctamente ===")


if __name__ == "__main__":
    main()