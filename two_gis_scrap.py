from aiohttp import ClientSession
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import lxml
import os
import re
import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from seleniumwire import webdriver
import time


headers = {
       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebt/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36' 
    }
URL_PART_1 = 'https://api.reviews.2gis.com/2.0/branches/'
URL_PART_2 = '/reviews?fields=meta.providers%2Cmeta.branch_rating%2Cmeta.branch_reviews_count%2Cmeta.total_count%2Creviews.hiding_reason%2Creviews.is_verified&is_advertiser=false&key=37c04fe6-a560-4549-b459-02309cf643ad&limit=50&locale=ru_RU&offset_date='
URL_PART_3 = 'T12%3A27%3A50.824879%2B07%3A00&rated=true&sort_by=date_edited'
TOWN_PAIRS = {'town' : 'link'}


def get_grefs(city_pairs: dict) -> None:
    """
    Base data scraping, get companys URLS and save them to file with path 2gis\\row_hrefs\\
    """

    login = ''
    password = ''
    proxy_options = {
        'proxy': {
            'https': f'http://{login}:{password}@'
        },
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        "prefs": {"profile.default_content_setting_values.cookies": 2}
    }
    
    cities = [city for city in city_pairs.keys()]
    driver = webdriver.Chrome(executable_path='chromedriver_win32\\chromedriver.exe', seleniumwire_options=proxy_options)
    driver.maximize_window()

    for city in cities:
        hrefs = []
        try:
            page_number = 1
            driver.get(city_pairs[city])
            while True:
                try:  
                    page_number += 1
                    element = driver.find_element(by='class name', value='_1x4k6z7')
                    ActionChains(driver).move_to_element(element).perform()
                    time.sleep(3)
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    for each in soup.find_all('div', class_='_1hf7139'):
                        url = each.find('div', class_='_1h3cgic').find('a').get('href')
                        hrefs.append(url)
                    # Ищем номер страницы, если он будет отсутствовать, тогда записываем полученные данные по городу в файл
                    page = driver.find_element(by='xpath', value = f"//span[text()='{page_number}']")
                    page.click()
                    time.sleep(2)

                except NoSuchElementException:
                    with open(f'2gis\\row_hrefs\\{city}.txt', 'w', encoding='utf8') as file:
                        for href in hrefs:
                            file.write(href+'\n')
                    break
        except Exception as _ex:
            print(_ex)


def prepare_hrefs(city_dict):
    '''
    Create full url links of each company
    '''

    cities = [city for city in city_dict.keys()]
    for city in cities:
        with open(f'2gis\\row_hrefs\\{city}.txt', encoding='utf8') as file:
            with open(f'2gis\\hrefs\\{city}.txt', 'w', encoding='utf8') as result:
                result_url = ['https://2gis.ru'+ url.strip().split('?')[0] for url in file.readlines()]
                # print(result_url)
                for url in result_url:
                    result.write(url+'\n')
        print(f'Ссылки по городу {city} были обработаны.')


async def gather_data(file_path):
    """
    Create massiv of tasks to get base data about company
    """
    tasks = []
    for file in os.listdir(file_path):
        city = file.split('.')[0]
        print(city)
        with open(os.path.join(file_path, file), encoding='utf8') as f:
            urls = [url.strip() for url in f.readlines()]
            # print(urls)
            for pos, url in enumerate(urls):
                # print(url)
                task = asyncio.create_task(get_base_data(url, city, pos, len(urls)))
                tasks.append(task)
        # print(f'Обработано {counter+1}/{TOTAL_FILES} файл(а/ов)')
        await asyncio.sleep(30)
    asyncio.gather(*tasks)


async def get_base_data(url, city, pos, lenght):
    """
    Function parse data from each url and take base info like company_id, company_name, phone, url, social_media
    """
    headers = {
       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebt/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36' 
    }
    # proxy = {'http':'103.95.40.211:3128'}
    async with ClientSession() as session:
        try:
            response = await session.get(url=url, headers=headers)
            soup = BeautifulSoup(await response.text(), 'lxml')
        except Exception as _ex:
            print(_ex)
        try:
            company_id = url.split('firm/')[1]
        except:
            company_id = url.split('geo/')[1]
        try:
            company_name = soup.find('span', class_='_oqoid').text
        except:
            company_name = 'Неизвестно'
        try:
            phone = soup.find('div', class_ = '_b0ke8').find('a', class_='_2lcm958').get('href')
        except AttributeError:
            phone = 'Неизвестно'
        try:
            url = soup.find_all('a', {'target': '_blank', 'class':'_1rehek'})[1]
            if '.ru' or '.com' not in url:
                url = 'Неизветно'
        except AttributeError:
            url = 'Неизвестно'
        try:
            social_media = '\n'.join([url.get('href') for url in soup.find_all('a', class_='_1rehek')[:4]])
        except AttributeError:
            social_media = 'Неизвестно'
        short_data.append([city, company_name, company_id, phone, url, social_media])
        print(f'Обработано: {pos}/{lenght}')


def format_hrefs(file_path):
    '''
    Делаем URLSы для публичной апишки, через которую будут запросы
    '''
    
    for file in os.listdir(file_path):
        urls = []
        with open(os.path.join(file_path, file), encoding='utf8') as f:
            # Забираем id компании            
            for url in f.readlines():
                try:
                    urls.append(url.strip().split('firm/')[1])
                except IndexError:
                    continue               
        
        with open(f'2gis\\review_hrefs\\{file}', 'w', encoding='utf8') as f_result:
            for url in urls:
                # link = URL_PART_1 + url + URL_PART_2 + datetime.today().strftime('%Y-%m-%d') + URL_PART_3 + '\n'     
                f_result.write(url+"\n")

        print(f'Ссылки по городу {file[:-4]} были подготовлены')


def company_total_data():
    """
    Concat dataframes to single frame
    """
    df = pd.DataFrame()
    for file in os.listdir(f'2gis/company_info'):
        try:
            new = pd.read_csv(f'2gis/company_info/{file}')
        except:
            continue
        new['City'] = file.split('.')[0]
        # print(new)
        df = pd.concat([df, new])
    
    df = df.loc[:, ['City', 'text', 'rating', 'date_created', 'user', 'object', 'official_answer']]
    df = df.reset_index(drop=True)
    df['date_created'] = df['date_created'].str[:10]
    df['Comment author'] = df['user'].apply(lambda x: re.findall("'name': '(.+?)', 'p", x))
    df['Company_id'] = df['object'].apply(lambda x: re.findall("'id': '(.+?)', 'typ", x)[0])
    df = df.drop(columns=['user', 'object', 'official_answer'])
    df2 = pd.read_csv('2gis/ALL_DATA/company_base_info_2gis.csv')
    df2 = df2.loc[:, ['Company', 'Company_id']]
    df['Company_id'] = df['Company_id'].astype('int64')
    df2['Company_id'] = df2['Company_id'].astype('int64')
    df = df.merge(df2, how='left', on='Company_id')
    df = df.loc[:, ['City', 'Company', 'Company_id', 'text', 'date_created', 'rating', 'Comment author']]
    df.drop_duplicates(subset=['text', 'date_created'], inplace=True)

    return df


def total_data_requests():
    """
    Send requests to get needed data and save it to csv
    """

    for city_file in os.listdir('2gis/review_hrefs'):
        city = city_file.split('.')[0]
        df = pd.DataFrame()
        with open(os.path.join('2gis/review_hrefs', city_file)) as file:
            urls_id = [url.strip() for url in file.readlines()]
        with requests.Session() as session:
    #         ПО одному городу
            for url_id in urls_id:
                date = str(datetime.now().date() + timedelta(days=1))
                offset = ''
                while True:
                    url = URL_PART_1 + url_id + URL_PART_2 + date + URL_PART_3
                    # print(url)
                    response = session.get(url=url, headers=headers)
                    js = response.json()['reviews']
                    
                    try:
                        date = js[-1]['date_created'][:10]
                        offset_now = js[0]['id']
                        if offset_now == offset:
                            break
                        # offset: last data in review
                        offset = offset_now
                    except IndexError:
                        break
                    new = pd.DataFrame().from_dict(js)
                    df = pd.concat([df,new])
                    if len(js) == 1:
                        break
            df.to_csv(f'2gis\\company_info\\{city}.csv', index=False)
            


def main():
    """
    The main goal of this scraper get reviews, reviews date, author of review
    Right order to achive a result. Run functions is following order: get_grefs -> prepare_hrefs -> gather_data -> total_data_requests ->
    company_total_data
    """
    global short_data
    short_data = []

    get_grefs(TOWN_PAIRS)
    prepare_hrefs(TOWN_PAIRS)
    asyncio.run(gather_data('2gis\\hrefs\\'))
    pd.DataFrame(short_data, columns=['City', 'Company', 'Company_id', 'Phone', 'URL', 'Social new']).to_csv('2gis\\ALL_DATA\\company_base_info_2gis.csv', index=False)
    format_hrefs('2gis\\hrefs\\')
    total_data_requests()
    company_total_data()
    print('Обработка отзывов была полностью завершена.')

if __name__ == '__main__':
    main()