import os
from pathlib import Path
import nest_asyncio
from playwright.sync_api import sync_playwright

# Aplicar parche para prevenir conflictos con bucles de eventos activos
nest_asyncio.apply()


def get_export_url(target_url: str) -> str:
    """Transforma una URL pubhtml de Google Sheets en un enlace de exportación XLSX directa."""
    if "/pubhtml" in target_url:
        base_url = target_url.split("/pubhtml")[0]
        return f"{base_url}/pub?output=xlsx"
    return target_url


def fetch_remote_excel(target_url: str, destination_path: Path, timeout: int = 300) -> bool:
    """Descarga el documento protegido de Google Sheets utilizando el contexto autenticado 
    de Playwright mediante una petición HTTP interna que respeta las cookies de sesión.
    """
    download_url = get_export_url(target_url)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_destination = str(destination_path.resolve())

    user_data_dir = destination_path.parent.parent / "playwright_profile"

    playwright = None
    browser_context = None

    try:
        print("Iniciando navegador automatizado con perfil persistente...")
        playwright = sync_playwright().start()
        
        browser_context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            accept_downloads=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ],
            ignore_default_args=["--enable-automation"]
        )
        
        page = browser_context.new_page()

        print(f"Obteniendo archivo desde el endpoint seguro: {download_url}")
        
        # Primero abrimos una página base para que el perfil cargue las cookies de sesión
        page.goto("https://docs.google.com", timeout=timeout * 1000, wait_until="domcontentloaded")

        # Usamos el cliente HTTP interno del contexto de Playwright (comparte las cookies de sesión institucionales)
        response = browser_context.request.get(download_url, timeout=timeout * 1000)
        
        if response.status != 200:
            print(f"[ERROR FETCH] El servidor respondió con estado HTTP: {response.status}")
            return False

        # Guardamos el contenido binario directamente en la ruta de destino
        with open(absolute_destination, "wb") as f:
            f.write(response.body())

        print(f"Archivo descargado exitosamente en: {destination_path}")
        return True

    except Exception as err:
        print(f"[ERROR PLAYWRIGHT] Falló la descarga automatizada: {err}")
        return False
    finally:
        if browser_context:
            try:
                browser_context.close()
            except Exception:
                pass
        if playwright:
            try:
                playwright.stop()
            except Exception:
                pass