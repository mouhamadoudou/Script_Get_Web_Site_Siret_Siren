import requests
from bs4 import BeautifulSoup
import time

def rechercher_societe(nom_societe):
    base_url = 'https://www.societe.com/cgi-bin/liste?'  # URL de recherche
    params = {'nom': nom_societe}
    
    # Ajout des en-têtes HTTP pour simuler un navigateur
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Pause initiale avant la requête
    time.sleep(2)  # Attendre 2 secondes avant la première requête
    
    # Faire la requête
    response = requests.get(base_url, params=params, headers=headers)
    
    if response.status_code == 429:
        print("Erreur 429 - Trop de requêtes, attente...")
        time.sleep(10)  # Attendre 10 secondes avant de réessayer
        response = requests.get(base_url, params=params, headers=headers)  # Réessayer la requête
    
    if response.status_code != 200:
        print(f"Erreur de requête: {response.status_code}")
        return None
    
    # Analyser le HTML si la requête est réussie
    soup = BeautifulSoup(response.content, 'html.parser')
    print("soup == ", soup)
    resultats = soup.find_all('tr', class_='resultat')
    
    entreprises = []
    for resultat in resultats:
        nom = resultat.find('td', class_='denomination').get_text(strip=True)
        siren = resultat.find('td', class_='siren').get_text(strip=True)
        url_details = resultat.find('a', href=True)['href']
        
        entreprises.append({
            'Nom': nom,
            'SIREN': siren,
            'Détails URL': url_details
        })
    
    return entreprises

# Exemple d'utilisation
nom_societe = '484374830'
entreprises = rechercher_societe(nom_societe)

if entreprises:
    for entreprise in entreprises:
        print(entreprise)
else:
    print("Aucune société trouvée.")
