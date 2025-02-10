import re
import requests
from bs4 import BeautifulSoup
import time
import random

def get_google_results(query, num_pages=3):
    """
    Scrape les résultats Google pour une requête donnée.
    
    :param query: La requête de recherche (ex: "vetement")
    :param num_pages: Le nombre de pages de résultats à récupérer
    :return: Une liste d'URLs trouvées
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    all_urls = set()

    for page in range(num_pages):
        url = f"https://www.google.com/search?q={query}&start={page * 2}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Erreur lors de la récupération de la page {page + 1}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            print(href)
            match = re.search(r'/url\?q=(https?://[^\s&]+)', href)
            if match:
                real_url = match.group(1)
                if 'fr' in real_url:
                    all_urls.add(real_url)
        time.sleep(random.uniform(1, 3))

    print(all_urls)
    return list(all_urls)
