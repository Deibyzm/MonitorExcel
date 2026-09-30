from datetime import datetime, timezone
from pathlib import Path
import pandas as pd


def compare_excel_versions(old_file_path: Path, new_file_path: Path) -> pd.DataFrame:
    """Compara la versión previa y la nueva de la hoja de cálculo detallando 
    las celdas, columnas y valores exactos que sufrieron modificaciones.
    """
    if not old_file_path.exists():
        print("[INFO COMPARATOR] Primera ejecución registrada. No hay versión previa para comparar.")
        return pd.DataFrame()

    try:
        df_old = pd.read_excel(old_file_path, engine="openpyxl")
        df_new = pd.read_excel(new_file_path, engine="openpyxl")

        # Estandarizar nombres de columnas y rellenar nulos
        df_old.columns = df_old.columns.astype(str).str.strip()
        df_new.columns = df_new.columns.astype(str).str.strip()
        df_old = df_old.fillna("")
        df_new = df_new.fillna("")

        if df_old.equals(df_new):
            print("[INFO COMPARATOR] Los DataFrames son 100% idénticos a nivel de celdas.")
            return pd.DataFrame()

        print("\n--- ¡DETALLE EXACTO DE CAMBIOS EN LAS CELDAS! ---")
        
        # Encontrar diferencias celda por celda
        mask = df_old.ne(df_new)
        changes = []

        # Recorrer las coordenadas donde hubo cambios
        rows, cols = mask.to_numpy().nonzero()
        for r, c in zip(rows, cols):
            col_name = df_old.columns[c]
            old_val = df_old.iloc[r, c]
            new_val = df_new.iloc[r, c]
            
            changes.append({
                "fila_indice": r,
                "columna": col_name,
                "valor_anterior": old_val,
                "valor_nuevo": new_val,
                "detected_at": datetime.now(timezone.utc).isoformat()
            })
            print(f"-> Fila {r} | Columna '{col_name}': '{old_val}'  ==>  '{new_val}'")

        print("--------------------------------------------------\n")
        
        return pd.DataFrame(changes)

    except Exception as err:
        print(f"[ERROR COMPARATOR] Ocurrió un error procesando los DataFrames: {err}")
        return pd.DataFrame()