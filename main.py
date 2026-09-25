import shutil
from config.settings import (
    TARGET_URL,
    CURRENT_EXCEL_PATH,
    PREVIOUS_EXCEL_PATH,
    AUDIT_LOG_PATH,
    STATE_FILE_PATH,
)
from modules.fetcher import fetch_remote_excel
from modules.checker import is_file_updated
from modules.comparator import compare_excel_versions


def main() -> None:
    """Orquestador principal del sistema de monitoreo y auditoría de Excel."""
    print("=== [ETL] Iniciando ciclo de verificación de la hoja de cálculo ===")

    # Paso 1: Descargar la versión más reciente a un archivo temporal (current.xlsx)
    success = fetch_remote_excel(TARGET_URL, CURRENT_EXCEL_PATH)
    if not success:
        print("[ERROR] El proceso se interrumpió porque falló la descarga web.")
        return

    # Paso 2: Verificar si el archivo realmente cambió mediante Hash MD5 y state.json
    if not is_file_updated(CURRENT_EXCEL_PATH, STATE_FILE_PATH):
        print("[INFO] Sin novedades: El Excel no ha sufrido modificaciones desde la última revisión.")
        return

    print("[AVISO] ¡Se detectaron cambios en el documento de Google Sheets!")

    # Paso 3: Si existe una versión previa, compararla con la actual usando Pandas
    if PREVIOUS_EXCEL_PATH.exists():
        differences = compare_excel_versions(PREVIOUS_EXCEL_PATH, CURRENT_EXCEL_PATH)

        if not differences.empty:
            print(f"\n--- CAMBIOS ENCONTRADOS ({len(differences)} filas afectadas) ---")
            print(differences)

            # Opcional: Guardar el reporte detallado en un archivo CSV de auditoría
            differences.to_csv(AUDIT_LOG_PATH, mode="a", header=not AUDIT_LOG_PATH.exists(), index=True)
            print(f"\n[LOG] Cambios registrados exitosamente en: {AUDIT_LOG_PATH}")
        else:
            print("[INFO] El hash cambió, pero la estructura tabular arrojó un resultado vacío.")
    else:
        print("[INFO] Primera ejecución: Se ha establecido la línea base del archivo (current.xlsx).")

    # Paso 4: Actualizar la versión previa copiando la actual para el próximo ciclo
    shutil.copy(CURRENT_EXCEL_PATH, PREVIOUS_EXCEL_PATH)
    print("=== [ETL] Ciclo finalizado y estado actualizado correctamente ===")


if __name__ == "__main__":
    main()