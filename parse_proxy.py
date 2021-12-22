from bs4 import BeautifulSoup
import requests
import lxml
import json
# from fake_head import headers
import random
import urllib

# headers = {
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
# }

def get_proxy_site_html(url: str) -> str:

    headers = {
       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebt/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36' 
    }
    proxies = {'http':''}   
    r = requests.Session()
    response = r.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.text, 'lxml')

    html_path = "proxy\\proxy_url\\raw_proxy.html"

    with open(html_path, "w", encoding='utf8') as file:
        file.write(response.text)

    return html_path

def get_correct_proxy(html_path:str):
    
    with open(html_path, encoding='utf8') as file:
        data = file.read()
    
    soup = BeautifulSoup(data, 'lxml')
    elements = soup.find_all('tr')
    list_proxys = []
    for external_td in elements:
        internal_elements = external_td.find_all('td')
        proxy = []
        for el in internal_elements:
            try:
                int(internal_elements[3].text[:-3])
                # print(el)
                proxy.append(el.text)
            except ValueError:
                continue
        if len(proxy): 
            # print(proxy)
            # print(':'.join(proxy[:2]) + proxy[4])
            list_proxys.append(':'.join(proxy[:2]) + ' ' + proxy[4])

    # print(list_proxys)
    with open('proxy\\proxy.txt', 'w', encoding='utf8') as file:
        [file.write(prox+'\n',) for prox in list_proxys]
    # print(result)
    
if __name__ == '__main__':
    
    path = get_proxy_site_html(url='https://hidemy.name/ru/proxy-list/#list')
    get_correct_proxy("proxy\\proxy_url\\raw_proxy.html")
    # with open('proxy\\proxy.txt', encoding='utf8') as file:
    #     print(file.readlines())