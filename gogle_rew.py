from bs4 import BeautifulSoup
import lxml
import pandas as pd
import time
from tqdm import tqdm
from selenium import webdriver as wd
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException, TimeoutException, \
    WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
import pyautogui
import pyperclip
from random import randint
# import sys

import os

cities = {'town': 'link'}

test = {
    'DZA': 'https://www.google.com/maps/search/%D0%B4%D0%B6%D0%B0%D0%BD%D0%BA%D0%BE%D0%B9+%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5+%D0%BF%D1%80%D0%B5%D0%B4%D0%BF%D1%80%D0%B8%D1%8F%D1%82%D0%B8%D1%8F/@45.0212787,32.947435,8.25z/data=!5m1!1e1?hl=ru-RU'
}

DELAY = 10


def get_source_html(city_dict: dict) -> None:
    login = ''
    password = ''
    proxy_options = {
        'proxy': {
            'https': f'http://{login}:{password}@'
        },
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
    }

    driver = webdriver.Chrome(executable_path='chromedriver_win32\\chromedriver.exe',
                              seleniumwire_options=proxy_options)
    driver.maximize_window()
    cit_names = [city for city in city_dict.keys()]

    for number, city in enumerate(cit_names):

        driver.get(city_dict[city])
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'x3AX1-LfntMc-header-title-ij8cu')))
        print(f'[INFO] PROGRESS {number}/{len(cit_names) - 1}. CURRENT CITY: {city}')

        while True:
            for _ in range(8):
                # Роллим вниз, цепляться за элемент мы не можем, так как у гугла другие формы. 
                # pyautogui.moveTo(randint(75, 127), randint(413, 513))
                pyautogui.scroll(-500)
                time.sleep(1)

            element = driver.find_element(by='xpath', value='//*[@id="ppdPk-Ej1Yeb-LgbsSe-tJiF1e"]')
            try:
                element.click()
                # Получение ссылок
                with open(f'google_data\\hrefs\\{city}.txt', 'a', encoding='utf8') as file:
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    for url in soup.find_all('a', class_='a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd'):
                        file.write(url['href'] + '\n')
            except WebDriverException:
                # Проверка, если клавиша следующей страницы не будет доступна
                print('Страницы закончились')
                break

            time.sleep(10)
    print(f'Были обработаны следующие города {", ".join(cit_names)}')


def get_full_review_link(file_path: str):
    login = 'dnxfuf'
    password = '24lhnBJG9a'
    proxy_options = {
        'proxy': {
            'https': f'http://{login}:{password}@193.57.136.78:24531'
        },
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
    }

    # driver = webdriver.Chrome(executable_path='chromedriver_win32\\chromedriver.exe', seleniumwire_options=proxy_options)
    driver = webdriver.Chrome(executable_path='chromedriver_win32\\chromedriver.exe')
    # files = os.listdir(file_path)
    files = ["C:/Users/Аяз/PycharmProjects/RevTaking/path.txt"]
    print(files)
    for file in files:
        print(file)
        short_data = []
        city = file.split('.')[0]
        with open(f'{os.path.join(file_path, file)}', encoding='utf8') as file:
            urls = [url.strip() for url in file.readlines()]

        for url in tqdm(urls):
            try:
                # print(url)
                driver.get(url)
                driver.maximize_window()
                WebDriverWait(driver, 10)
                _ = WebDriverWait(driver, DELAY).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'x3AX1-LfntMc-header-title-ij8cu')))
                soup = BeautifulSoup(driver.page_source, 'lxml')
                time.sleep(3)
                pyautogui.hotkey('ctrl', 'shift', 'j')
                # pyautogui.moveTo(x=1620, y=242)
                # time.sleep(0.2)
                # pyautogui.click()
                # time.sleep(0.7)
                pyautogui.moveTo(x=1280, y=270)
                time.sleep(1)
                pyautogui.click()
                reviews_url_button = driver.find_element(by='xpath',
                                                         value='//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span/span[2]/span[1]/button')
                numb_reviews = int(reviews_url_button.text.split(' ')[0])
                reviews_url_button.click()
                WebDriverWait(driver, 10)
                # Сделать пока не загрузится элемент
                # Двигаться должны по процентам, именить на абс
                clicks = [(1620, 242), (1308, 560), (1548, 529), (1646, 631), (1656, 642)]
                click_types = ['left', 'left', 'left', 'right', 'left']

                for j in range(len(clicks)):
                    pyautogui.moveTo(*clicks[j])
                    pyautogui.click(button=click_types[j])
                    time.sleep(2)

                    if (1620, 242) == clicks[j]:
                        pyautogui.hotkey('ctrl', 'a')
                        time.sleep(1.5)
                        pyautogui.press('backspace')
                        time.sleep(2)
                        pyautogui.press([x for x in 'listen'])
                        time.sleep(2)

                request_from_google = pyperclip.paste()
                print(request_from_google)
                reviews_url = driver.current_url

            except TimeoutException:
                print(f'Loading take to much time. URL: {url} skipped')
            except NoSuchElementException:
                # Клавиши отзывов нет
                print('Отзывов нет')
                numb_reviews = 0
                reviews_url = False
                request_from_google = False
            except Exception as _ex:
                print(_ex)
            finally:
                pyautogui.hotkey('ctrl', 'shift', 'j')
                if soup.find('h1'):
                    company_name = soup.find('h1').find('span').text
                else:
                    company_name = 'Сайт не загрузился'
                print(company_name)
                if soup.find('button', {'data-item-id': "address"}):
                    address = soup.find('button', {'data-item-id': "address"})['aria-label']
                else:
                    address = 'Не указан'

                if soup.find('button', {'data-tooltip': 'Перейти на сайт'}):
                    link = soup.find('button', {'data-tooltip': 'Перейти на сайт'})['aria-label']
                else:
                    link = 'Не указан'

                if soup.find('button', {'data-tooltip': 'Скопировать номер'}):
                    phone = soup.find('button', {'data-tooltip': 'Скопировать номер'})['aria-label']
                else:
                    phone = 'Не указан'
                review_str = []
                print(soup)
                if soup.find('span', {"class": "ODSEW-ShBeI-text"}):
                    reviews = soup('span', {"class": "ODSEW-ShBeI-text"})
                    for review in reviews:
                        review_str.append(review.contents[0])
                    print(review_str)
                else:
                    print("Пусто")
                short_data.append(
                    [city, company_name, address, link, phone, numb_reviews, url, reviews_url, request_from_google])
        # pd.DataFrame(short_data, columns=['City', 'Company', 'Address', 'Site', 'Phone', 'Count of reviews', 'Main URL', 'Reviews url', 'JSON ANS']).to_csv(os.path.join(f'google_data\\company_info\\{city}.csv'), index=False)
        # pd.DataFrame(short_data, columns=['City', 'Company', 'Address', 'Site', 'Phone', 'Count of reviews', 'Main URL',
        #                                   'Reviews url', 'JSON ANS']).to_csv(os.path.join(f'fff7123335.csv'), index=False)

        print('2 минуты отдыхаем')
        # driver.close()
        # driver.quit()
        time.sleep(120)


def main():
    get_full_review_link('google_data\\C:/Users/Аяз/PycharmProjects/RevTaking/path.txt\\')


if __name__ == '__main__':
    main()
