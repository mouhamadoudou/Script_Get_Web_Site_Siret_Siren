import requests
from bs4 import BeautifulSoup
import re
import json
from requests.exceptions import RequestException, Timeout
import random
from botData import user_agents

sites = [
    "https://www.jules.com",
    "https://www.zalando.fr",
    "https://www.ruedeshommes.com",
    "https://www.celio.com",
    "https://www.galerieslafayette.com",
    "https://www.brentinyparis.com",
    "https://www.devred.com",
    "https://www.kiabi.com",
    "https://www.atlasformen.fr",
    "https://www.zara.com",
    "https://www.bonoboplanet.com",
    "https://www.leslipfrancais.fr",
    "https://www.tranquilleemile.net",
    "https://www.boohooman.com",
    "https://www.jdsports.fr",
    "https://www.lesitedumadeinfrance.fr",
    "https://www.1083.fr",
    "https://www.armandthiery.fr",
    "https://www.cdiscount.com",
    "https://www.hugoboss.com",
    "https://www.lagentlefactory.com",
    "https://www.cocorico.store",
    "https://www.la-garconniere.fr",
    "https://www.montlimart.com",
    "https://www.amazon.fr",
    "https://www.maisonsolfin.fr",
    "https://fr.shein.com",
    "https://www.lemahieu.com",
    "https://www.madefrance.fr",
    "https://www.masculin.com",
    "https://www2.hm.com",
    "https://www.printemps.com",
    "https://bonnegueule.fr",
    "https://www.laredoute.fr",
    "https://www.spartoo.com",
    "https://www.c-and-a.com",
    "https://izac.fr",
    "https://www.placedestendances.com",
    "https://www.homere.shop",
    "https://www.tbs.fr",
    "https://hartford.fr",
    "https://www.suitable.fr",
    "https://www.levi.com",
    "https://www.primark.com",
    "https://www.degriffstock.com",
    "https://www.casual-senas.fr",
    "https://blacks-legend.com",
    "https://www.decathlon.fr",
    "https://www.footlocker.fr",
    "https://www.sarenza.com",
    "https://emp-online.fr",
    "https://lhabitfrancais.com",
    "https://www.farfetch.com",
    "https://www.asos.com",
    "https://www.eden-park.com",
    "https://www.kaporal.com",
    "https://intl.fursac.com",
    "https://www.b-z-b.com",
    "https://www.uniqlo.com",
    "https://www.citadium.com",
    "https://www.gemo.fr",
    "https://www.selected.com",
    "https://garcon-francais.fr",
    "https://www.bershka.com",
    "https://www.ikks.com",
    "https://www.gant.fr",
    "https://www.intersport.fr",
    "https://www.auchan.fr",
    "https://www.etsy.com",
    "https://ilannfive.com",
    "https://www.espace-des-marques.com",
    "https://www.thenines.fr",
    "https://fr.boohoo.com",
    "https://www.aboutyou.fr",
    "https://www.replayjeans.com",
    "https://www.ateliertuffery.com",
    "https://www.monoprix.fr",
    "https://www.mandmdirect.fr",
    "https://www.loom.fr",
    "https://www.gqmagazine.fr",
    "https://www.superdry.fr",
    "https://shop.mango.com",
    "https://www.destock-sport-et-mode.com",
    "https://www.modz.fr",
    "https://thevillageoutlet.com",
    "https://www.lhommemoderne.fr",
    "https://www.shilton.fr",
    "https://www.calvinklein.fr",
    "https://www.ralphlauren.fr",
    "https://www.street-one.fr",
    "https://www.lacoste.com",
    "https://www.philippemodel.com",
    "https://www.bhv.fr"
]

def sendRequest(url, timeout=5):
    headers = random.choice(user_agents)
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        return response
    except Timeout:
        # print(f"Temps de réponse dépassé pour {url}")
        return None
    except RequestException as e:
        print(f"Erreur lors de la requête vers {url}: {e}")
        return None
       

def extract_siret_from_mentions_legales(url):
    headers = random.choice(user_agents)
    print("Site en cours d'analyse : ", url)
 
    # response = requests.get(url, headers=headers)
    response = sendRequest(url)
    print("ok ici")
    if response is None:
        print(f"Erreur de connexion au site : {url}")
        return None
    
    if response.status_code != 200:
        print(f"Erreur lors de la connexion au site {url}. Code de statut: {response.status_code}")
        return None 
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # print("ee == ", soup)
    
    mentions_legales_link = None

    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        strLink = a.get_text().lower() or ''
        if 'mentions' in a['href'].lower() or 'mentionslegales' in a['href'].lower() or 'mentions' in strLink:
            mentions_legales_link = a['href']
            # print("ok")
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
        if mentions_legales_link.startswith('/'):
            mentions_legales_link = mentions_legales_link[1:]
        if mentions_legales_link.startswith('/'):
            mentions_legales_link = mentions_legales_link[1:]
        
        if mentions_legales_link.startswith('http') :
            full_url = mentions_legales_link 
        elif mentions_legales_link.startswith('www'): 
            full_url = "https://" + mentions_legales_link
        else :
            print("la")
            full_url = url + '/' + mentions_legales_link
        print(full_url)
        
        response = requests.get(full_url,  headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        page_text = soup.get_text().replace(' ', '')
        # print(page_text)
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
    

url_site_ecommerce = 'https://www.calvinklein.fr'  
siret = extract_siret_from_mentions_legales(url_site_ecommerce)
if siret:
    print(f"SIRET/SIREN récupéré : {siret}")


# def get_siret_from_sites(sites):
#     result = []
#     for site in sites:
#         siret = extract_siret_from_mentions_legales(site)
#         if siret:
#             # print(site )
#             result.append({"site": site, "SIRET/SIREN": siret})
#         else:
#             # print(site)
#             result.append({"site": site, "SIRET/SIREN": "Non trouvé"})
#     return result

# result = get_siret_from_sites(sites)

# json_data = json.dumps(result, indent=4)

# with open('result.json', 'w') as file:
#     file.write(json_data)