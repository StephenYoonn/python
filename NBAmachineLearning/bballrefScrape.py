import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

#selenium webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


url ='https://www.basketball-reference.com/leagues/NBA_2025_per_game.html'
driver.get(url)

time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')

#table = soup.find('div', {'class':"table_container tabbed current hide_long long_note is_setup", 'id': 'div_advanced'})
table = soup.find('div', {'class':"table_container tabbed current hide_long long_note is_setup", 'id': 'div_per_game_stats'})

# header row in table
header_row = table.find('tr')  # find first <tr> inside  table
#print(header_row)

# column titles
column_titles = [header.text.strip() for header in header_row.find_all('th')]
#print(column_titles)
# player data
players_data = []


tbody = soup.find('tbody')

for player in tbody.find_all('tr'):
    if 'thead' in player.get('class', []):
        continue
    rows = player.find_all('td')
    player_stats = {}
    
    for index, row in enumerate(rows):
        player_stats[column_titles[index]] = row.text.strip()
        #print(row.text.strip())
    
    players_data.append(player_stats)


df = pd.DataFrame(players_data)

output_file_path = '../data/raw/csv/2024allNonAdvanced.csv'

df.to_csv(output_file_path, index=False)

driver.quit()
