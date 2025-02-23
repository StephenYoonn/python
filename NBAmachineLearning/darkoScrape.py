from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

#selenium webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = "https://apanalytics.shinyapps.io/DARKO/"
driver.get(url)

try:
    tab_element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//li/a[@data-value='Current Player Skill Projections']"))
    )
    tab_element.click()
    print("Switched to the 'Current Player Skill Projections' tab.")
except Exception as e:
    print(f"Could not switch to the desired tab: {e}")
    driver.quit()

try:
    iframe = driver.find_element(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(iframe)
    print("Switched to iframe containing the table.")
except Exception:
    print("No iframe found or needed.")

players_data = []

#54 pages (number may change)
total_pages = 54

for page in range(total_pages):
    try:
        #check table is present and visible
        table_body = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//table[@class='display dataTable no-footer' and @id='DataTables_Table_0']"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        #table headers
        headers = soup.find('tr')
        column_titles = [header.text.strip() for header in headers.find_all('th')]

        #player data
        tbody = soup.find('tbody')
        for player in tbody.find_all('tr'):
            rows = player.find_all('td')
            player_stats = {}
            for index, row in enumerate(rows):
                player_stats[column_titles[index]] = row.text.strip()
            players_data.append(player_stats)

        #Only click "Next" if there are more pages to go through
        if page < total_pages - 1:
            try:
                #Wait for the "Next Page" button to be clickable 
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@id='DataTables_Table_0_next']"))
                )
                next_button.click()

                # Wait for the next page to load
                time.sleep(5)  
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

output_file_path = '../data/raw/csv/darko.csv'
df.to_csv(output_file_path, index=False)

driver.quit()

print(f"Scraped data saved to {output_file_path}")
