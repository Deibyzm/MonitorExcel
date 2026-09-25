import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def get_export_url(target_url: str) -> str:
    """Transforma una URL pubhtml de Google Sheets en un enlace de exportación XLSX directa."""
    if "/pubhtml" in target_url:
        base_url = target_url.split("/pubhtml")[0]
        return f"{base_url}/pub?output=xlsx"
    return target_url


def fetch_remote_excel(target_url: str, destination_path: Path, timeout: int = 60) -> bool:
    """Descarga el documento de Google Sheets institucional utilizando automatización de navegador con Playwright."""
    download_url = get_export_url(target_url)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_destination = str(destination_path.resolve())

    try:
        print("Iniciando navegador automatizado para descargar el archivo institucional...")
        with sync_playwright() as p:
            # Usamos chromium en modo visible (headless=False) para que puedas iniciar sesión si te lo pide la universidad
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            print(f"Navegando a: {download_url}")
            with page.expect_download() as download_info:
                page.goto(download_url, timeout=timeout * 1000)
            
            download = download_info.value
            download.save_as(absolute_destination)
            browser.close()

        print(f"Archivo descargado exitosamente en: {destination_path}")
        return True

    except Exception as err:
        print(f"[ERROR PLAYWRIGHT] Falló la descarga automatizada: {err}")
        return False