from datetime import datetime, timezone
from pathlib import Path
import pandas as pd


def compare_excel_versions(old_file_path: Path, new_file_path: Path) -> pd.DataFrame:
    """Compara la versión previa y la nueva de la hoja de cálculo de forma robusta 
    evitando conflictos de índices en Pandas.
    """
    if not old_file_path.exists():
        print("[INFO COMPARATOR] Primera ejecución registrada. No hay versión previa para comparar.")
        return pd.DataFrame()

    try:
        # Cargar los archivos asegurando el motor openpyxl
        df_old = pd.read_excel(old_file_path, engine="openpyxl")
        df_new = pd.read_excel(new_file_path, engine="openpyxl")

        # Limpiar espacios en blanco en los nombres de columnas para evitar falsos positivos
        df_old.columns = df_old.columns.astype(str).str.strip()
        df_new.columns = df_new.columns.astype(str).str.strip()

        # Rellenar valores nulos para estandarizar la comparación
        df_old = df_old.fillna("")
        df_new = df_new.fillna("")

        # Validar si son exactamente iguales en contenido plano
        if df_old.equals(df_new):
            print("[INFO COMPARATOR] Los DataFrames son 100% idénticos a nivel de celdas.")
            return pd.DataFrame()

        # Si no son iguales, buscamos las diferencias utilizando un enfoque tolerante a cambios de índice
        print("\n--- ¡CAMBIOS DETECTADOS EN EL CONTENIDO! ---")
        
        # Encontrar filas que difieren
        comparison_mask = df_old.ne(df_new)
        diff_indices = comparison_mask.any(axis=1)
        
        diff_report = pd.DataFrame({
            "fila": df_old.index[diff_indices],
            "estado": "Modificado"
        })

        if not diff_report.empty:
            print(f"Se encontraron diferencias en {len(diff_report)} filas.")
            diff_report["detected_at"] = datetime.now(timezone.utc).isoformat()
        
        print("--------------------------------------------\n")
        return diff_report

    except Exception as err:
        print(f"[ERROR COMPARATOR] Ocurrió un error procesando los DataFrames: {err}")
        return pd.DataFrame()