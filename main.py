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
      "https://www.maxi-pieces-50.fr/",
      "https://www.ase-energy.com/",
      "https://www.cuisinieresgrandelargeur.com/",
      "https://www.ludifolie.com/",
      "https://www.equipementech.com/",
      "https://www.donuts-racing.com/",
      "https://myperfumeshome.com/",
      "https://www.ohmykitchen.com/",
      "https://www.veloactif.com/",
      "https://www.cernunos.fr/",
      "https://www.boutikazik.com/fr",
      "https://www.gt-outillage.com/",
      "https://amijardin.fr/",
      "https://www.kokmaison.com/",
      "https://www.pro-mob.fr/",
      "https://www.sofamed.com/",
      "https://www.tinkco.com/",
      "https://www.mariannemelodie.fr/",
      "https://www.bricoflor.fr/",
      "https://www.7days.fr/",
      "https://www.calicosy.com/fr",
      "https://objet-expression.com/",
      "https://www.direct-mat.com/",
      "https://www.fusil-calais.com/fr",
      "https://www.croquegel.com/",
      "https://www.drawer.fr/",
      "https://happy-garden.fr/"
]

def extract_siret_from_mentions_legales(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Erreur de connexion au site. URL = ", url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    mentions_legales_link = None

    for a in soup.find_all('a', href=True):
        if 'mentions' in a['href'].lower():
            # print(a)
            mentions_legales_link = a['href']
            break
    # print(soup.find_all('a', href=True))
    
    if mentions_legales_link is None:
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            print(href, '\n')
            if ('confidentialites' in href or 'conditions' in href) and ('politique' in href or 'generales' in href):
                mentions_legales_link = a['href']
                break
    
    if mentions_legales_link:
        full_url = mentions_legales_link if mentions_legales_link.startswith('http') else url + mentions_legales_link
        response = requests.get(full_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        page_text = soup.get_text().replace(' ', '')
        
        siret_siren_list = re.findall(r'(?<!\d)\d{9}(?!\d)|(?<!\d)\d{14}(?!\d)', page_text)

        # print(siret_siren_list)
        if siret_siren_list:

            return siret_siren_list[0]  
        else:
            print("SIRET/SIREN non trouvé. URL = ", url)
            return None
    else:
        print("Lien vers les mentions légales non trouvé.  URL = ", url)
        return None

url_site_ecommerce = 'https://www.maxi-pieces-50.fr/'  
siret = extract_siret_from_mentions_legales(url_site_ecommerce)
if siret:
    print(f"SIRET/SIREN récupéré : {siret}")


# def get_siret_from_sites(sites):
#     result = []
#     for site in sites:
#         siret = extract_siret_from_mentions_legales(site)
#         if siret:
#             result.append({"site": site, "SIRET/SIREN": siret})
#         else:
#             result.append({"site": site, "SIRET/SIREN": "Non trouvé"})
#     return result

# result = get_siret_from_sites(sites)

# print(result)