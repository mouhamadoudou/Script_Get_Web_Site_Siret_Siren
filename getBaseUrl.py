import urllib.parse

def extract_base_url(url):
    parsed_url = urllib.parse.urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def extract_base_urls_from_file(file_path):
    base_urls = set()
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  
            if line:  
                base_url = extract_base_url(line)
                base_urls.add(base_url)
    
    return list(base_urls)

def save_base_urls_to_file(base_urls, output_file):
    with open(output_file, 'w') as file:
        for url in base_urls:
            file.write(url + '\n')


file_path = 'urls.txt'  

base_urls = extract_base_urls_from_file(file_path)

save_base_urls_to_file(base_urls, "BaseUrl.txt")

for base_url in base_urls:
    print(base_url)

