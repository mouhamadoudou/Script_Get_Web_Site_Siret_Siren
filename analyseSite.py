import requests
from bs4 import BeautifulSoup
import re
import json
from requests.exceptions import RequestException, Timeout
import random
import string
from env.botData import user_agents
from extractBaseUrls import extractBaseUrls
from flask_socketio import SocketIO
import http.client
import json
from urllib.parse import urlparse

def sendRequest(url, timeout=8):
    headers = random.choice(user_agents)
    
    if ".gouv" in url:
        return None
    
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
    # print(mentions_legales_link)
    
    if mentions_legales_link is None:
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            # print('mentions' in strLink)
            if ('confidentialites' in href or 'conditions' in href) and ('politique' in href or 'generales' in href):
                mentions_legales_link = a['href']
                break
    # print(mentions_legales_link)
    
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
        page_text = page_text.replace(')', '')
        page_text = page_text.replace('(', '')  
        page_text = page_text.replace('.', '')
        page_text = page_text.replace(' ', '')  
        page_text = page_text.replace('\t', '')  
        page_text = page_text.replace('\n', '')  
        page_text = page_text.replace('\r', '')

        # printable_chars = string.printable  
        # page_text = ''.join(char for char in page_text if char in printable_chars)

        siret_siren_list = re.findall(r'(?<!\d)\d{9}(?!\d|€)', page_text)
        if siret_siren_list:
            # print("rees = ", siret_siren_list)
            return siret_siren_list[0]
        else:
            print("SIRET/SIREN non trouvé. URL = ", url)
            return None
    else:
        print("Lien vers les mentions légales non trouvé.  URL = ", url)
        return None
    

def get_base_urls_from_file(file_path = "BaseUrl.txt"):
    base_urls = set()
    # print(file_path)d)\d{9}(?!\d)|(?<!\d)\d{14}(?!\d)
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip() 
            if line:  
                base_urls.add(line)

    return list(base_urls)

def get_siret_from_sites(sites, request_id, socketio):
    # print("sittttttes == ", sites)
    nbSiteFound = 0
    result = []
    count = 0
    sitesLen = len(sites)
    for site in sites:
        count += 1
        parsed_url = urlparse(site['link'])
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        siret = extract_siret_from_mentions_legales(base_url)
        print("bassee === ", base_url)
        if siret:
            # print("laaa")
            nbSiteFound += 1
            # result.append({"id": count, "url": site, "status": "getIt", "checked": False, "identifier": {"type": "siren", "value": siret}})
            socketio.emit('analyse_done', {'message': f"{count} Sites traité sur {sitesLen}", 'data': [{"id": count, "url": base_url, "status": "getIt", "checked": False, "identifier": {"type": "siren", "value": siret}}], 'nb_site_found': nbSiteFound, 'request_id': request_id})
        else:
            socketio.emit('analyse_done', {'message': f"Site {count} traité", 'data': [{"id": count, "url": base_url, "status": "didntGetIt", "checked": False, "identifier": {"type": "siren", "value": "Non trouvé"}}], 'nb_site_found': nbSiteFound, 'request_id': request_id})
            # result.append()
        
        # Emitting the result after processing each site

    return result, nbSiteFound


def analyseSite(request_id, socketio, searchKey : None) :
    
    if (searchKey != None) :
        webList = getWeblist(searchKey)
        result, nbSiteFound = get_siret_from_sites(webList, request_id, socketio)
        return result, nbSiteFound
        
    # extractBaseUrls()
    # sites = get_base_urls_from_file()
    
    # if (webList == None) :
    #     return None
    # print(webList)
    # result, nbSiteFound = get_siret_from_sites(webList, request_id, socketio)


    # json_data = json.dumps(result, indent=4)
    print("Analyse terminé Nombre de SIREN/SIRET trouvé : ", nbSiteFound, " sur ", len(sites))

    # return result, nbSiteFound
    # with open('result.json', 'w') as file:
        # file.write(json_data)
    
    
# url_site_ecommerce = 'https://www.ldlc.com'  
# siret = extract_siret_from_mentions_legales(url_site_ecommerce)
# if siret:
#     print(f"SIRET/SIREN récupéré : {siret}")


def getWeblist(query) :
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": query,
        "location": "France",
        "gl": "fr",
        "hl": "fr",
        "num": 10
    })
    headers = {
        'X-API-KEY': 'c7c659885cae9960e43d8b16382919fcd40716a9',
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()

    result = json.loads(data.decode("utf-8"))

    if 'organic' in result:
        return result['organic']
    else:
        return None

