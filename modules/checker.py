import hashlib
import json
from pathlib import Path


def calculate_md5(file_path: Path) -> str:
    """Calcula el hash MD5 del archivo binario local mediante chunks para optimizar memoria."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def is_file_updated(current_file_path: Path, state_file_path: Path) -> bool:
    """Compara el hash del archivo descargado con el último hash registrado en state.json.

    Returns:
        bool: True si el archivo es nuevo o sufrió modificaciones.
    """
    new_hash = calculate_md5(current_file_path)

    if state_file_path.exists():
        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                state = json.load(f)
                if state.get("last_hash") == new_hash:
                    return False
        except (json.JSONDecodeError, KeyError):
            print("[WARN CHECKER] Corrupción en state.json. Se reescribirá el estado.")

    # Actualizar estado con el nuevo hash
    with open(state_file_path, "w", encoding="utf-8") as f:
        json.dump({"last_hash": new_hash}, f, indent=4)

    return True