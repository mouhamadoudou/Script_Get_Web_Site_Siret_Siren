import requests
from bs4 import BeautifulSoup
import re
import json
from requests.exceptions import RequestException, Timeout
import random
from botData import user_agents

sites = [
    "https://www.backmarket.fr",
    "https://www.largo.fr",
    "https://smaaart.fr",
    "https://www.yes-yes.com",
    "https://www.recommerce.com",
    "https://certideal.com",
    "https://www.fnac.com",
    "https://www.quechoisir.org",
    "https://www.backmarket.fr",
    "https://www.cadaoz.com",
    "https://smaaart.fr",
    "https://fr.e-recycle.com",
    "https://www.quelbonplan.fr",
    "https://www.boulanger.com",
    "https://fr.shopping.rakuten.com",
    "https://www.rebuy.fr",
    "https://remakefrance.com",
    "https://www.leparisien.fr",
    "https://www.samsung.com",
    "https://www.bouyguestelecom.fr",
    "https://boutique.orange.fr",
    "https://www.republik-retail.fr",
    "https://www.economie.gouv.fr",
    "https://rmc.bfmtv.com",
    "https://www.republik-retail.fr",
    "https://www.lesnumeriques.com",
    "https://www.businesscoot.com",
    "https://fr.wikipedia.org",
    "https://www.reepeat.fr",
    "https://www.driphone.fr",
    "https://www.refurbed.fr",
    "https://www.apple.com",
    "https://www.ouest-france.fr",
    "https://www.cdiscount.com",
    "https://www.boulanger.com",
    "https://www.tests-et-bons-plans.fr",
    "https://www.ariase.com",
    "https://www.dipli.com",
    "https://www.rueducommerce.fr",
    "https://www.leboncoin.fr",
    "https://fr.renew.auto",
    "https://www.ldlc.com",
    "https://www.kia.com",
    "https://www.bmw.fr",
    "https://www.itjustgood.com",
    "https://www.decathlon.fr",
    "https://www.lesnumeriques.com",
    "https://www.frandroid.com",
    "https://www.tesla.com",
    "https://www.audi.fr",
    "https://www.surplusmotos.com",
    "https://www.europe-camions.com",
    "https://www.wel-com.fr",
    "https://www.reepeat.fr",
    "https://occasion.largus.fr",
    "https://www.commentcamarche.net",
    "https://www.francecasse.fr",
    "https://www.spoticar.fr",
    "https://www.aramisauto.com",
    "https://occasions.hyundai.fr",
    "https://www.francebleu.fr",
    "https://www.ikea.com",
    "https://www.automobile.fr",
    "https://www.happycash.fr",
    "https://www.ford.fr",
    "https://france3-regions.francetvinfo.fr",
    "https://www.decathlon.fr",
    "https://www.electrodepot.fr",
    "https://www.dacia.fr",
    "https://www.lacentrale.fr",
    "https://www.cashconverters.fr",
    "https://www.ouest-france.fr",
    "https://www.opisto.fr",
    "https://www.volkswagen.fr",
    "https://www.gibert.com",
    "https://www.leparisien.fr",
    "https://www.toyota.fr",
    "https://oxylio.com",
    "https://www.stellantisandyou.com",
    "https://www.mpb.com",
    "https://www.refurbished.fr",
    "https://www.certideal.be",
    "https://occasion.largus.fr",
    "https://www.ecofone.fr",
    "https://www.refurb.me",
    "https://fr.renew.auto",
    "https://www.amazon.fr",
    "https://www.wel-com.fr",
    "https://boutique.orange.fr",
    "https://www.cdiscount.com",
    "https://www.monreconditionne.fr",
    "https://www.electrodepot.fr",
    "https://reconditionner.fr",
    "https://www.lesmobiles.com",
    "https://www.red-by-sfr.fr",
    "https://www.easycash.fr",
    "https://www.recyclivre.com"
]

def sendRequest(url, timeout=8):
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
    print("Site en cours d'analyse : ", url, "\n")
 
    # response = requests.get(url, headers=headers)
    response = sendRequest(url)
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
            full_url = url + '/' + mentions_legales_link
        # print(full_url)
        
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
    else:
        print("Lien vers les mentions légales non trouvé.  URL = ", url)
        return None
    

# url_site_ecommerce = 'https://api.societe.com/'  
# siret = extract_siret_from_mentions_legales(url_site_ecommerce)
# if siret:
#     print(f"SIRET/SIREN récupéré : {siret}")

nbSiteFound = 0

def get_siret_from_sites(sites):
    nbSiteFound = 0
    result = []
    for site in sites:
        siret = extract_siret_from_mentions_legales(site)
        if siret:
            # print(site )
            nbSiteFound += 1
            result.append({"site": site, "SIRET/SIREN": siret})
        else:
            # print(site)
            result.append({"site": site, "SIRET/SIREN": "Non trouvé"})
    return result, nbSiteFound

result, nbSiteFound = get_siret_from_sites(sites)

json_data = json.dumps(result, indent=4)

print("Analyse terminé Nombre de SIREN/SIRET trouvé : ", nbSiteFound, " sur ", len(sites))
with open('result.json', 'w') as file:
    file.write(json_data)