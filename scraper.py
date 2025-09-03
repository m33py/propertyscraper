import csv
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime

## Standard Selenium setup (commented out)
# # Replace the CHROMEDRIVER_PATH with your actual path
# CHROMEDRIVER_PATH = r"C:\Users\tzsia\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# # Set up the service object with the path to chromedriver
# service = Service(CHROMEDRIVER_PATH)

# options = Options()
# # Uncomment the next line if you want the browser to run in headless mode (no UI)
# # options.add_argument('--headless')
# options.add_argument('start-maximized')

# # Set a custom user-agent
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")

# driver = webdriver.Chrome(service=service, options=options)

## Using undetected_chromedriver to bypass Cloudflare
options = uc.ChromeOptions()
options.add_argument('--start-maximized')
# options.add_argument('--headless=new')  # only if you really want headless
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")

driver = uc.Chrome(options=options)
options = uc.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument("--disable-blink-features=AutomationControlled")  # stealth
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")

driver.get('https://www.propertyguru.com.sg/property-for-sale/at-laguna-park-359')

try:
    wait = WebDriverWait(driver, 10)
    
    # Wait until the listings container is present
    listings_container = wait.until(EC.presence_of_element_located((By.ID, 'listings-container')))
    
    # Find all property cards within the container
    property_cards = listings_container.find_elements(By.CLASS_NAME, 'header-wrapper')
    
    # Open a CSV file for writing
    with open('properties.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['PropertyName', 'URL', 'Price', 'Bedrooms', 'Bathrooms', 'FloorArea',
                      'PropertyType', 'Tenure', 'YearBuilt', 'Recency', 'ExtractedDateTime']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Only write the header if the file is new or empty
        if csvfile.tell() == 0:
            writer.writeheader()
        
        for card in property_cards:
            try:
                # Scroll the card into view to handle dynamically loaded content
                driver.execute_script("arguments[0].scrollIntoView();", card)
                
                # Small delay to ensure content is loaded
                time.sleep(1)

                # Find elements relative to the current card context
                url_element = card.find_element(By.CSS_SELECTOR, '.nav-link')
                url = url_element.get_attribute('href')
                name = url_element.text
                
                # Extracting price
                try:
                    price_element = card.find_element(By.XPATH, '../../..//li[@class="list-price pull-left"]/span[@class="price"]')
                    price = price_element.text
                except:
                    price = 'N/A'
                
                # Extracting bedrooms
                try:
                    bedrooms_element = card.find_element(By.XPATH, '../../..//li[@class="listing-rooms pull-left"]/span[@class="bed"]')
                    bedrooms = bedrooms_element.get_attribute('title')
                except:
                    bedrooms = 'N/A'
                
                # Extracting bathrooms
                try:
                    bathrooms_element = card.find_element(By.XPATH, '../../..//li[@class="listing-rooms pull-left"]/span[@class="bath"]')
                    bathrooms = bathrooms_element.get_attribute('title')
                except:
                    bathrooms = 'N/A'
                
                # Extracting floor area
                try:
                    floor_area_element = card.find_element(By.XPATH, '../../..//li[@class="listing-floorarea pull-left"]')
                    floor_area = floor_area_element.text.split(' ')[0]  # Extracting the square footage
                except:
                    floor_area = 'N/A'

                # Extracting property tenure, built and listing posted.
                try:
                    property_type_elements = card.find_elements(By.CSS_SELECTOR, 'ul.listing-property-type li span')
                    property_type_list = [elem.text for elem in property_type_elements]

                    property_type_text = property_type_list[0] if len(property_type_list) > 0 else 'N/A'
                    tenure_text = property_type_list[1] if len(property_type_list) > 1 else 'N/A'
                    year_built_text = property_type_list[2] if len(property_type_list) > 2 else 'N/A'
                except:
                    property_type_text = 'N/A'
                    tenure_text = 'N/A'
                    year_built_text = 'N/A'

                # Recency of listing
                try:              
                    recency_element = card.find_element(By.CSS_SELECTOR, 'div.listing-recency')
                    recency = recency_element.text
                except:
                    recency = 'N/A'
                    
                # Get the current datetime in the specified format
                extracted_datetime = datetime.now().strftime('%d/%b/%y %I:%M%p')

                writer.writerow({
                    'PropertyName': name,
                    'Price': price,
                    'Bedrooms': bedrooms,
                    'Bathrooms': bathrooms,
                    'FloorArea': floor_area,
                    'PropertyType': property_type_text,
                    'Tenure': tenure_text,
                    'YearBuilt': year_built_text,
                    'Recency': recency,
                    'URL': url,
                    'ExtractedDateTime': extracted_datetime
                })
                
            except Exception as e:
                print(f"Error extracting data from property card: {e}")

except TimeoutException:
    print("Loading took too much time or Cloudflare challenge could not be solved automatically.")

finally:
    driver.quit()
