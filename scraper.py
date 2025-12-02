import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# URL to scrape (you can change this to any news site that allows scraping)
URL = "https://news.ycombinator.com/"

# 1. Send HTTP request to the website
response = requests.get(URL)

# Check if request was successful
if response.status_code != 200:
    print("Failed to retrieve the page. Status code:", response.status_code)
    exit()

# 2. Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# 3. Find the data you want to scrape
# For this site, each headline is inside <a class="storylink"> or <span class="titleline"><a> in newer layouts
headlines_data = []

for index, item in enumerate(soup.select(".titleline a"), start=1):
    title = item.get_text(strip=True)
    link = item.get("href")

    headlines_data.append({
        "S.No": index,
        "Title": title,
        "Link": link
    })

# 4. Define CSV file name
file_name = f"news_headlines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# 5. Write data into a CSV file
with open(file_name, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["S.No", "Title", "Link"])
    writer.writeheader()
    writer.writerows(headlines_data)

print(f"Scraping complete! {len(headlines_data)} headlines saved to {file_name}")
