import os
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from google.oauth2.service_account import Credentials

# ===================== CONFIGURACIÓN DESDE GITHUB SECRETS =====================
URL = "https://www.bcv.org.ve"

def obtener_tasas_bcv():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")          # Headless moderno (funciona en GitHub)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options, use_subprocess=True)
    
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "strong")))

        # Tasas
        euro = driver.find_element(By.XPATH, "//*[contains(text(),'EUR')]/following::strong[1]").text.strip()
        dolar = driver.find_element(By.XPATH, "//*[contains(text(),'USD')]/following::strong[1]").text.strip()

        # Fecha limpia
        fecha_element = driver.find_element(By.XPATH, "//*[contains(text(),'Fecha Valor:')]")
        fecha_completa = fecha_element.text.strip()
        fecha = fecha_completa.split("Fecha Valor:")[-1].strip()  # Solo "Lunes, 30 Marzo 2026"

        print(f"✅ Datos obtenidos → {fecha} | Euro: {euro} | Dólar: {dolar}")
        return fecha, euro, dolar

    except Exception as e:
        print(f"❌ Error: {e}")
        driver.save_screenshot("error.png")
        raise
    finally:
        driver.quit()

def actualizar_google_sheets(fecha, euro, dolar):
    creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(os.environ["SHEET_ID"])
    ws = sh.worksheet(os.environ["WORKSHEET_NAME"])

    # Actualiza exactamente las 3 celdas que tú definas
    ws.update(os.environ["DATE_CELL"], fecha)
    ws.update(os.environ["EURO_CELL"], euro)
    ws.update(os.environ["DOLAR_CELL"], dolar)

    print(f"📊 Google Sheets actualizado correctamente")

if __name__ == "__main__":
    fecha, euro, dolar = obtener_tasas_bcv()
    actualizar_google_sheets(fecha, euro, dolar)
