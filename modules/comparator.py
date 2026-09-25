from datetime import datetime, timezone
from pathlib import Path
import pandas as pd


def compare_excel_versions(old_file_path: Path, new_file_path: Path) -> pd.DataFrame:
    """Compara la versión previa y la nueva de la hoja de cálculo.

    Returns:
        pd.DataFrame: Reporte con las filas y celdas modificadas.
    """
    if not old_file_path.exists():
        print("[INFO COMPARATOR] Primera ejecución registrada. No hay versión previa para comparar.")
        return pd.DataFrame()

    try:
        df_old = pd.read_excel(old_file_path)
        df_new = pd.read_excel(new_file_path)

        # Utilizar la función nativa compare de Pandas
        diff = df_old.compare(df_new, align_axis=1, keep_shape=False, keep_equal=False)
        
        if not diff.empty:
            diff["detected_at"] = datetime.now(timezone.utc).isoformat()

        return diff

    except Exception as err:
        print(f"[ERROR COMPARATOR] Ocurrió un error procesando los DataFrames: {err}")
        return pd.DataFrame()