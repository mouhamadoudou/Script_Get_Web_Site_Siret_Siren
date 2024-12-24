import requests
from bs4 import BeautifulSoup
import re

sites = [
      "https://www.outilsdespros.fr",
      "https://www.bionoble.co",
      "https://www.cuisissimo.com",
      "https://www.allpneus.com",
      "https://www.cimaises-et-plus.com",
      "https://www.azialo.com",
      "https://www.officeeasy.fr",
      "https://www.maxi-pieces-50.fr",
      "https://www.ase-energy.com",
      "https://www.cuisinieresgrandelargeur.com",
      "https://www.ludifolie.com",
      "https://www.equipementech.com",
      "https://www.donuts-racing.com",
      "https://myperfumeshome.com",
      "https://www.ohmykitchen.com",
      "https://www.veloactif.com",
      "https://www.cernunos.fr",
      "https://www.boutikazik.com/fr",
      "https://www.gt-outillage.com",
      "https://amijardin.fr",
      "https://www.kokmaison.com",
      "https://www.pro-mob.fr",
      "https://www.sofamed.com",
      "https://www.tinkco.com",
      "https://www.mariannemelodie.fr",
      "https://www.bricoflor.fr",
      "https://www.7days.fr",
      "https://www.calicosy.com/fr",
      "https://objet-expression.com",
      "https://www.direct-mat.com",
      "https://www.fusil-calais.com/fr",
      "https://www.croquegel.com",
      "https://www.drawer.fr",
      "https://happy-garden.fr"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_siret_from_mentions_legales(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Erreur de connexion au site. res = ", response)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # print("ee == ", soup)
    
    mentions_legales_link = None

    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        strLink = a.get_text().lower() or ''
        if 'mentions' in a['href'].lower() or 'mentionslegales' in a['href'].lower() or 'mentions' in strLink:
            mentions_legales_link = a['href']
            break
    # print(soup.find_all('a', href=True))
    
    if mentions_legales_link is None:
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            # print('mentions' in strLink)
            if ('confidentialites' in href or 'conditions' in href) and ('politique' in href or 'generales' in href):
                mentions_legales_link = a['href']
                break
    
    if mentions_legales_link:
        if mentions_legales_link.startswith('http') :
            full_url = mentions_legales_link 
        else : 
            if mentions_legales_link.startswith('/'):
                mentions_legales_link = mentions_legales_link[1:]
            full_url = url + '/' + mentions_legales_link
        
        response = requests.get(full_url,  headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        page_text = soup.get_text().replace(' ', '')
        
        siret_siren_list = re.findall(r'(?<!\d)\d{9}(?!\d)|(?<!\d)\d{14}(?!\d)', page_text)

        # print(page_text)
        if siret_siren_list:
            return siret_siren_list[0]  
        else:
            print("SIRET/SIREN non trouvé. URL = ", url)
            return None
        return None
    else:
        print("Lien vers les mentions légales non trouvé.  URL = ", url)
        return None
    

url_site_ecommerce = 'https://www.croquegel.com'  
siret = extract_siret_from_mentions_legales(url_site_ecommerce)
if siret:
    print(f"SIRET/SIREN récupéré : {siret}")


# def get_siret_from_sites(sites):
#     result = []
#     for site in sites:
#         siret = extract_siret_from_mentions_legales(site)
#         if siret:
#             print(site)
#             result.append({"site": site, "SIRET/SIREN": siret})
#         else:
#             print(site)
#             result.append({"site": site, "SIRET/SIREN": "Non trouvé"})
#     return result

# result = get_siret_from_sites(sites)

# print(result)