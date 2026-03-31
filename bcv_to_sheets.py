import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from google.oauth2.service_account import Credentials

# ===================== CONFIG =====================
URL = "https://www.bcv.org.ve"

# ===================== SCRAPER =====================
def obtener_tasas_bcv():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        # Esperar que cargue algo clave
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "strong")))

        # Obtener EURO
        euro = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'EUR')]/following::strong[1]")
        )).text.strip()

        # Obtener DÓLAR
        dolar = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'USD')]/following::strong[1]")
        )).text.strip()

        # Obtener FECHA
        fecha_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Fecha Valor:')]")
        ))

        fecha = fecha_element.text.split("Fecha Valor:")[-1].strip()

        print(f"✅ Datos obtenidos → {fecha} | EUR: {euro} | USD: {dolar}")

        return fecha, euro, dolar

    except Exception as e:
        print(f"❌ Error en scraping: {e}")
        driver.save_screenshot("error.png")
        raise

    finally:
        driver.quit()


# ===================== GOOGLE SHEETS =====================
def actualizar_google_sheets(fecha, euro, dolar):
    creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])

    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)

    gc = gspread.authorize(creds)

    sh = gc.open_by_key(os.environ["SHEET_ID"])
    ws = sh.worksheet(os.environ["WORKSHEET_NAME"])

    # Actualizar celdas
    ws.update(os.environ["DATE_CELL"], fecha)
    ws.update(os.environ["EURO_CELL"], euro)
    ws.update(os.environ["DOLAR_CELL"], dolar)

    print("📊 Google Sheets actualizado correctamente")


# ===================== MAIN =====================
if __name__ == "__main__":
    print("🚀 Iniciando scraper BCV...")

    fecha, euro, dolar = obtener_tasas_bcv()
    actualizar_google_sheets(fecha, euro, dolar)

    print("✅ Proceso completado con éxito")
