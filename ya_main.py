from bs4 import BeautifulSoup
import lxml
import json
import os
import pandas as pd
import pyautogui
import requests
import psycopg2
# from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import time
# from fake_head import headers
import random
import sys

STATUS = str

city_comp1 = {
    'town': 'link'
}


def get_source_html(town_pairs: dict) -> None:
    """
    Обычное сохранение через driver.page_source почему-то не сохраняет весь исходник, или сохраняет, но без некоторых тегов, используется pyautogui
    """
    with open('proxy\\proxy.txt', encoding='utf8') as file:
        raw_proxy = file.readlines()
    proxies = [prox.strip() for prox in raw_proxy[:-2]]

    cit_names = [name for name in town_pairs.keys()]
    while len(os.listdir('source_html\\')) < len(city_comp1.keys()):

        # http/https/socks4-5
        # prox_type = proxies[i].split()[1].split(',')[0].lower()
        # prox_ip = proxies[i].split()[0]
        chrome_options = webdriver.ChromeOptions()
        login = '1'
        password = '1'
        proxy_options = {
            'proxy': {
                'https': f'1'
            },
            'user-agent': '1'
        }
        # chrome_options.add_argument('--proxy-server={}://{}'.format(prox_type, prox_ip))
        # chrome_options.add_argument(f'user-agent={headers[random.randint(0, len(headers.keys())-1)]}')
        # chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36')
        driver = webdriver.Chrome(executable_path='chromedriver_win32\\chromedriver.exe', seleniumwire_options=proxy_options)
        driver.maximize_window()

        try:  
            for number, city in enumerate(cit_names):
                # print('[INFO] Proxy now:', proxies[i])
                driver.get(town_pairs[city])
                # driver.get(url='https://www.reg.ru/web-tools/myip')
                print('[INFO] URL NOW:', town_pairs[city])
                time.sleep(5)
                while True:
                    # find_board_el = driver.find_element_by_class_name('search-list-meta-view__breadcrumbs') # не сохраняет html после
                    if driver.find_elements(by="class name", value='add-business-view'):
                        element = driver.find_element(by='class name', value='search-list-meta-view')
                        ActionChains(driver).move_to_element(element).perform()
                        time.sleep(2)
                        with open(f'source_html\\{city}.html', 'w', encoding='utf8') as f:
                            f.write(driver.page_source)
                        break
                    else:
                        pyautogui.moveTo(100, 500)
                        pyautogui.scroll(-500)
                        time.sleep(2)
                time.sleep(10)
        except ConnectionRefusedError:
            # Если будет блочить, то на след цикл меняем прокси
            print('[INFO] PROXY WAS BLOCKED. CHANGING ...')
        except Exception as _ex:
            print(_ex)
            with open(f'source_html\\{city}.html', 'w', encoding='utf8') as f:
                f.write(driver.page_source)
        finally:
            if number < len(cit_names)-1:
                cit_names = cit_names[number:]
            else: break
            driver.close()
            driver.quit()


def get_url_hrefs(file_path: str) -> STATUS:
    """
    Создаем линки компаний из исходников, котоыре были получены в функции get_source_html
    """
    
    html_files = os.listdir(file_path)
    # read html
    for html_file in html_files:
        print(html_file)
        with open(os.path.join(file_path,html_file), 'r', encoding="utf8") as file:
            raw = file.read()
        

        # create links
        bs = BeautifulSoup(raw, 'lxml')
        with open(os.path.join('url_links', html_file.split(".")[0]+'.txt'), 'w') as file:  
            for link in bs.find_all('a', {'class':'search-snippet-view__link-overlay'}):
                file.write('https://yandex.ru'+link.get('href')+'reviews'+'\n')

    return '[INFO] Создание и запись ссылок было выполнено'


def get_reviews(file_path: str) -> list:
    """
    Вытягиваем отзывы, имена авторов, дату отзыва, название компании
    """

    with open('proxy\\proxy.txt', encoding='utf8') as file:
        raw_proxy = file.readlines()
    proxies = [prox.strip() for prox in raw_proxy[:-2]]
    # prox_type = proxies_pairs[i].split()[1].split(',')[0].lower()
    # prox_ip = proxies_pairs[i].split()[0]
    href_files = ["C:/Users/Аяз/PycharmProjects/RevTaking/path.txt"]
    # href_files = os.listdir(file_path)
    print(href_files)
    time.sleep(10)
    reviews_info = []
    for href in href_files:

        with open(os.path.join(file_path, href), 'r', encoding='utf8') as file:
            urls = [url.strip() for url in file.readlines()]
        
        
        i=0
        city_name = href.split('.')[0]
        pos = 0
        reviews_info = []
        # Вытягиваем данные из файла отдельного города
        for url in urls:
            # print(url, urls[:1])

            # Подбираем рабочий проксик
            for idx, proxy in enumerate(proxies[pos:]):
                prox_type = proxy.split()[1].split(',')[0].lower()
                prox_ip = proxy.split()[0]
                pair = {prox_type:prox_ip}
                response = requests.get(url=url, proxies=pair)
                if response.status_code == requests.codes['ok']:
                    pos=idx

                    break
                else: print(f'[WARNING] Proxy changed. Now: {pair}')
            # response = requests.get(url=url, headers=headers, prox)
            response.encoding = 'utf8'
            # response.decoding = 'utf8'
            soup = BeautifulSoup(response.text, 'lxml')
            # print(soup)

            i+=1
            # print('[INFO] Прогресс выполнения:', i, f'/ {len(urls)}', url)
            
            try:
                # Нужны названия компаний, отзыв, дата отзыва, человек его оставивший
                # company_name = soup.find('h1', class_='orgpage-header-view__header').text.strip()
                company_name = "ASGK-GROUP"
                reviews_old = soup.find_all('span', class_='business-review-view__body-text')
                ratings = soup.find_all('rating', class_='business-review-view__body-text')
                script = soup.find('script', class_='config-view').text
                script = json.loads(script)
                reviews = script['searchPreloadedResults']['items'][0]['reviewResults']['reviews']
                print(script['counters']['metrika']['maps']['id'])
                # print(script['searchPreloadedResults']['items']['shortTitle'])
                print(script['searchPreloadedResults']['items'][0]['shortTitle'])
                print(script['searchPreloadedResults']['items'][0]['reviewResults']['reviews'][0]['rating'])
                print(ratings)
                reviews_arr = []
                stars_arr = []
                companies_arr = []
                info= []
                for review in reviews:
                    reviews_arr.append(review['text'])
                    stars_arr.append(review['rating'])
                    companies_arr.append(script['searchPreloadedResults']['items'][0]['shortTitle'])

                for review in zip(companies_arr, reviews_arr, stars_arr):
                    info.append([*review])


                # Отзыва нет
                # print(reviews)
                if len(reviews) == 0:
                    # print('[INFO] Прогресс выполнения:', i, f'/{len(urls)}', url, 'Отзывов нет')
                    authors, reviews_dates, reviews = [['Данных нет']] * 3
                    company_name, city = [company_name], [city_name]
                else:
                    # Если отзыв есть
                    authors = soup.find_all('span', {'itemprop':'name'})
                    reviews_dates = soup.find_all('span', class_='business-review-view__date')
                    
                    reviews_old = [review.text.strip() for review in reviews_old]
                    ratings = [rating.text.strip() for rating in ratings]
                    # print("@@@@@@@@@@@@@")
                    # print(reviews)
                    authors = [author.text.strip() for author in authors]
                    reviews_dates = [date.text.strip() for date in reviews_dates]
                    company_name, city = [company_name] * len(reviews), [city_name] * len(reviews)
                
                for review in zip(company_name, city, authors, reviews_dates, reviews_old, ratings):
                    reviews_info.append([*review])
            except ValueError as _ex:
                print(_ex)

            # time.sleep(1)
        pd.DataFrame(reviews_info, columns=['Company', 'City', 'Name', 'Date', 'Review', 'Rating']).to_excel('two.xls', index=False, encoding='utf-8-sig')
        pd.DataFrame(info, columns=['Company','Review', 'Rating']).to_excel('twooo.xls', index=False, encoding='utf-8-sig')
        # print(f'Переходим на следующий регион. Текущий город был {city_name}')
        time.sleep(1)  

    return f'[INFO] Были обработаны следующие файлы: {", ".join(href_files)}!'

def make_full_csv(file_path):
    files = os.listdir(file_path)
    


def main():
    # get_source_html(city_comp2)
    # print(get_url_hrefs('source_html\\'))
    get_reviews('url_links\\')

if __name__ == '__main__':
    main()