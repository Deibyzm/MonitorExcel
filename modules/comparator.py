from datetime import datetime, timezone
from pathlib import Path
import pandas as pd


def compare_excel_versions(
    old_file_path: Path, 
    new_file_path: Path, 
    keywords: list[str] = None
) -> pd.DataFrame:
    """Compara la versión previa y la nueva de la hoja de cálculo. 
    Filtra los cambios para mostrar únicamente aquellos que contengan 
    cualquiera de las palabras clave especificadas en la lista.
    
    Args:
        old_file_path (Path): Ruta del archivo Excel anterior (histórico).
        new_file_path (Path): Ruta del archivo Excel recién descargado.
        keywords (list[str], optional): Lista de términos o palabras clave a filtrar.
        
    Returns:
        pd.DataFrame: DataFrame con el detalle estructurado de los cambios encontrados.
    """
    
    # 1. Validación inicial: Si el archivo histórico no existe, es la primera ejecución
    if not old_file_path.exists():
        print("[INFO COMPARATOR] Primera ejecución registrada. No hay versión previa para comparar.")
        return pd.DataFrame()

    try:
        # 2. Carga de datos: Leer ambos archivos Excel usando el motor openpyxl
        df_old = pd.read_excel(old_file_path, engine="openpyxl")
        df_new = pd.read_excel(new_file_path, engine="openpyxl")

        # 3. Normalización: Estandarizar nombres de columnas (convertir a texto y quitar espacios)
        df_old.columns = df_old.columns.astype(str).str.strip()
        df_new.columns = df_new.columns.astype(str).str.strip()
        
        # Rellenar valores nulos (NaN) con cadenas vacías para evitar conflictos lógicos
        df_old = df_old.fillna("")
        df_new = df_new.fillna("")

        # 4. Verificación rápida de igualdad total en los DataFrames
        if df_old.equals(df_new):
            print("[INFO COMPARATOR] Los DataFrames son 100% idénticos a nivel de celdas.")
            return pd.DataFrame()

        print("\n[INFO] Analizando cambios con filtros múltiples...")
        
        # 5. Detección de diferencias: El método .ne() genera una matriz booleana 
        # donde True indica que la celda cambió respecto al otro DataFrame.
        mask = df_old.ne(df_new)
        changes = []

        # Convertir la máscara booleana a coordenadas numéricas (filas y columnas)
        rows, cols = mask.to_numpy().nonzero()
        
        # 6. Iteración sobre las celdas modificadas
        for r, c in zip(rows, cols):
            col_name = df_old.columns[c]
            old_val = df_old.iloc[r, c]
            new_val = df_new.iloc[r, c]
            
            old_str = str(old_val)
            new_str = str(new_val)

            # 7. Aplicación del filtro por palabras clave (si fueron definidas)
            if keywords:
                match_found = False
                # Unir el texto de toda la fila para evaluar si la palabra clave aparece en algún campo relacionado
                row_text = " ".join(df_new.iloc[r].astype(str)).lower()
                
                for kw in keywords:
                    kw_lower = kw.lower()
                    # Comprobar si la palabra está en el valor anterior, nuevo o en la fila completa
                    if kw_lower in old_str.lower() or kw_lower in new_str.lower() or kw_lower in row_text:
                        match_found = True
                        break
                
                # Si ninguna palabra clave coincide con este cambio, se omite (continúa el ciclo)
                if not match_found:
                    continue

            # 8. Almacenamiento del cambio relevante en la lista estructurada
            changes.append({
                "fila_indice": r,
                "columna": col_name,
                "valor_anterior": old_val,
                "valor_nuevo": new_val,
                "detected_at": datetime.now(timezone.utc).isoformat()
            })
            print(f"[ALERTA] Fila {r} | Columna '{col_name}': '{old_val}'  ==>  '{new_val}'")

        if not changes:
            print("[INFO COMPARATOR] Hubo cambios en el Excel, pero ninguno coincidió con las palabras clave.")
        
        print("-" * 50)
        
        # Retornar los cambios empaquetados en un DataFrame limpio
        return pd.DataFrame(changes)

    except Exception as err:
        # Manejo seguro de excepciones ante archivos corruptos o errores de lectura
        print(f"[ERROR COMPARATOR] Ocurrió un error procesando los DataFrames: {err}")
        return pd.DataFrame()