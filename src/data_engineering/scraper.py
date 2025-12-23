# File: src/data_engineering/scraper.py
import requests
from bs4 import BeautifulSoup
import os

class AngkotScraper:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_html(self):
        print(f"Connecting to {self.url}...")
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            print(f"Connection Successful! Status Code: {response.status_code}")
            return response.text
        except Exception as e:
            print(f"Failed to fetch Data: {e}")
            return None

    def extract_relevant_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # DEBUG 1: Cek Judul Halaman (Apakah kita diblokir?)
        page_title = soup.title.string if soup.title else "No Title"
        print(f"Page title obtained: '{page_title}'")
        
        # DEBUG 2: Coba cari konten tanpa filter kelas yang ketat
        content_area = soup.find('div', class_='entry-content') or soup.find('article') or soup.find('body')
        
        if not content_area:
            print("Failed to find main content area (div/article/body).")
            return []

        print(f"Content area found: <{content_area.name}>")

        cleaned_lines = []
        tags_to_search = ['p', 'li', 'td', 'div'] 
        
        found_count = 0
        for tag in content_area.find_all(tags_to_search):
            text = tag.get_text().strip()
           
            if len(text) > 10: 
                # Cek apakah ini terlihat seperti rute (ada panah atau kata Terminal/Jalan)
                if "→" in text or "Terminal" in text or "Jalan" in text or "Angkot" in text:
                    cleaned_lines.append(text)
                    found_count += 1

        print(f"Found {found_count} lines of relevant text.")
        return list(set(cleaned_lines)) # Hapus duplikat

    def save_raw(self, lines, filename="data/01_raw/raw_routes.txt"):
        if not lines:
            print("WARNING: No data is saved because the result is empty.")
            return

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Success! Data saved to {filename} ({len(lines)} lines)")

if __name__ == "__main__":
    url = "https://catperku.com/rute-angkot-bandung/"
    scraper = AngkotScraper(url)
    html = scraper.fetch_html()
    if html:
        lines = scraper.extract_relevant_text(html)
        scraper.save_raw(lines)
