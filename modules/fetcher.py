import os
from pathlib import Path
import requests


def get_export_url(pubhtml_url: str) -> str:
    """Convierte la URL pubhtml de Google Sheets en un endpoint de exportación XLSX directa."""
    if "/pubhtml" in pubhtml_url:
        base_url = pubhtml_url.split("/pubhtml")[0]
        return f"{base_url}/pub?output=xlsx"
    return pubhtml_url


def fetch_remote_excel(target_url: str, destination_path: Path, timeout: int = 30) -> bool:
    """Descarga el contenido binario del documento de Google Sheets a la ruta especificada.

    Args:
        target_url (str): URL pubhtml original.
        destination_path (Path): Ruta donde se escribirá el archivo local.
        timeout (int): Límite de tiempo en segundos para la petición HTTP.

    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario.
    """
    download_url = get_export_url(target_url)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(download_url, headers=headers, timeout=timeout)
        response.raise_for_status()

        with open(destination_path, "wb") as file:
            file.write(response.content)

        return True

    except requests.exceptions.RequestException as err:
        print(f"[ERROR FETCH] Falló la descarga del archivo: {err}")
        return False
    except IOError as err:
        print(f"[ERROR DISK] No se pudo escribir el archivo en {destination_path}: {err}")
        return False