import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
from config import DATA_DIR, BUCKET_JSON, DATA_SOURCES, SELENIUM_CONFIG

# remove old data
folderpath = DATA_DIR

if os.path.exists(folderpath):
    for file in os.listdir(folderpath):
        filepath = os.path.join(folderpath, file)
        if os.path.isfile(filepath):
            os.remove(filepath)

# crawl new data
chrome_options = Options()
if SELENIUM_CONFIG["headless"]:
    chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

dataurl = DATA_SOURCES["tainan_data_url"]
titlelist = DATA_SOURCES["data_titles"]

driver.get(dataurl)

for t in titlelist:
    for i in range(SELENIUM_CONFIG["max_retries"]):
        try:
            title = WebDriverWait(driver, SELENIUM_CONFIG["wait_timeout"]).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'[title="{t}"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", title)
            time.sleep(SELENIUM_CONFIG["scroll_delay"])
            title.click()
            break
        except:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(SELENIUM_CONFIG["scroll_delay"])


    jsonbtn = WebDriverWait(driver, SELENIUM_CONFIG["wait_timeout"]).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "JSON"))
                )
    jsonbtn.click()

    driver.switch_to.window(driver.window_handles[-1])
    jsonurl= driver.current_url
    response = requests.get(jsonurl)

    with open(str(BUCKET_JSON), 'w', encoding='utf-8') as f:
        f.write(response.text)

driver.quit()

print('Data Updated')