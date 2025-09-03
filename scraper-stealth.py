import csv
import time
import random
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Set up undetected Chrome with stealth ---
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)

driver = uc.Chrome(options=options)

# Inject stealth: remove webdriver flag
driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """
    },
)

# --- Target URL ---
driver.get(
    "https://www.propertyguru.com.sg/property-for-sale/at-laguna-park-359"
)

try:
    wait = WebDriverWait(driver, 15)
    listings_container = wait.until(
        EC.presence_of_element_located((By.ID, "listings-container"))
    )
    print("✅ Listings container found.")
except TimeoutException:
    print("❌ Loading took too much time or Cloudflare challenge blocked us.")

# --- Scroll page (mimic human) ---
for _ in range(6):  # scroll down multiple times
    driver.execute_script("window.scrollBy(0, 1200);")
    time.sleep(random.uniform(2, 4))  # random wait

# --- Extract property cards ---
property_cards = driver.find_elements(By.CSS_SELECTOR, "div.listing-card-root")

print(f"Found {len(property_cards)} property cards.")

with open("properties.csv", "a", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "URL",
        "Address",
        "Price",
        "Bedrooms",
        "Bathrooms",
        "FloorArea",
        "PricePSF",
        "ExtractedDateTime"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for card in property_cards:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", card)
            time.sleep(1)

            # Listing URL
            url_element = card.find_element(By.CSS_SELECTOR, ".listing-card-link")
            url = url_element.get_attribute("href")

            # Address
            try:
                address_element = card.find_element(By.CSS_SELECTOR, "div.listing-address[da-id='lc-address']")
                address = address_element.text
            except:
                address = "N/A"

            # Price
            try:
                price_element = card.find_element(By.CSS_SELECTOR, "div.listing-price[da-id='lc-price']")
                price = price_element.text
            except:
                price = "N/A"

            # Beds
            try:
                beds_element = card.find_element(By.XPATH, ".//span[@class='info-value' and contains(text(), 'Beds')]")
                beds = beds_element.text
            except:
                beds = "N/A"

            # Baths
            try:
                baths_element = card.find_element(By.XPATH, ".//span[@class='info-value' and contains(text(), 'Baths')]")
                baths = baths_element.text
            except:
                baths = "N/A"

            # Floor Area
            try:
                area_element = card.find_element(By.XPATH, ".//span[@class='info-value' and contains(text(), 'sqft')]")
                area = area_element.text
            except:
                area = "N/A"

            # Price per sqft
            try:
                psf_element = card.find_element(By.XPATH, ".//span[@class='info-value' and contains(text(), 'psf')]")
                psf = psf_element.text
            except:
                psf = "N/A"

            extracted_datetime = datetime.now().strftime("%d/%b/%y %I:%M%p")

            # Log scraped data
            print({
                "URL": url,
                "Address": address,
                "Price": price,
                "Bedrooms": beds,
                "Bathrooms": baths,
                "FloorArea": area,
                "PricePSF": psf,
                "ExtractedDateTime": extracted_datetime,
            })

            writer.writerow(
                {
                    "URL": url,
                    "Address": address,
                    "Price": price,
                    "Bedrooms": beds,
                    "Bathrooms": baths,
                    "FloorArea": area,
                    "PricePSF": psf,
                    "ExtractedDateTime": extracted_datetime,
                }
            )

        except Exception as e:
            print(f"⚠️ Error extracting data from property card: {e}")

driver.quit()
