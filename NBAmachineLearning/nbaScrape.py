from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

#selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = "https://www.nba.com/stats/players/traditional?sort=PTS&dir=-1&PlayerExperience=Sophomore&SeasonType=Regular+Season"
driver.get(url)

# Initialize a list to store all players' stats
players_data = []

#3 pages (number may change)
total_pages = 3

for page in range(total_pages):
    #wait for the table body to be fully loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Crom_body__UYOcU"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #table headers
    headers = soup.find('tr', class_='Crom_headers__mzI_m')
    column_titles = [header.text.strip() for header in headers.find_all('th')]

    #player data
    tbody = soup.find('tbody', class_='Crom_body__UYOcU')
    for player in tbody.find_all('tr'):
        rows = player.find_all('td')
        player_stats = {}
        for index, row in enumerate(rows):
            player_stats[column_titles[index]] = row.text.strip()
        players_data.append(player_stats)

    #Only click "Next" if there are more pages to go through
    if page < total_pages - 1:
        try:
            #wait for the "Next Page" button to be clickable
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Next Page Button']"))
            )
            next_button.click()

            # Wait for the next page to load 
            time.sleep(5) 
        except Exception as e:
            print(f"Could not navigate to the next page: {e}")
            break

df = pd.DataFrame(players_data)

output_file_path = '../data/raw/csv/nba_sophs_stats.csv'
df.to_csv(output_file_path, index=False)

driver.quit()

print(f"Scraped data saved to {output_file_path}")
