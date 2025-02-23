from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

#selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = "https://dataviz.theanalyst.com/nba-stats-hub/"
driver.get(url)

time.sleep(5)

# players stats
players_data = []

#29 pages (number may change)
total_pages = 29

for page in range(total_pages):
    try:
        
        #table fully loaded
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//table[@class='_data-table_8a6e8_1']"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        #find table 
        table = soup.find('table', class_='_data-table_8a6e8_1')

        #table headers
        thead = table.find('thead', class_='_data-table-head_8a6e8_22')

        #2nd <tr> within the thead
        header_row = thead.find_all('tr')[1]  # This will get the second <tr>

        #column titles from <tr>
        column_titles = [header.text.strip() for header in header_row.find_all('th')]

        #player data
        tbody = table.find('tbody')
        initial_data_len = len(players_data)
        for player in tbody.find_all('tr', class_='_data-table-row_8a6e8_26'):
            rows = player.find_all('td')
            player_stats = {}
            for index, row in enumerate(rows):
                player_stats[column_titles[index]] = row.text.strip()
            players_data.append(player_stats)

        #check if new data was added
        if len(players_data) == initial_data_len:
            print(f"No new data found on page {page + 1}, stopping.")
            break

        driver.switch_to.default_content()

        if page < total_pages - 1:
            try:
                #wait for the "Next" button to be clickable and click it using JavaScript
                next_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, '_pagination-container_6v7ta_1')]//button[2]"))
                )
                driver.execute_script("arguments[0].click();", next_button)

                #wait for the next page to load
                time.sleep(20)
            except Exception as e:
                print(f"Could not navigate to the next page: {e}")
                break
    except Exception as e:
        print(f"Error on page {page + 1}: {e}")
        break

df = pd.DataFrame(players_data)

if df.empty:
    print("No data was extracted.")
else:
    print("Data extracted successfully.")

output_file_path = '../data/raw/csv/drip.csv'
df.to_csv(output_file_path, index=False)

driver.quit()

print(f"Scraped data saved to {output_file_path}")
