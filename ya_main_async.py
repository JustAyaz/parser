import asyncio
from aiohttp.client import ClientSession
from bs4 import BeautifulSoup
import lxml
import os
import pandas as pd

reviews_info = []
async def get_page_info(url: str, total_links: int, cur_links_idx: int, name: str) -> None:
    headers = {
       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebt/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36' 
    }
    async with ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        await asyncio.sleep(0.1)
        soup = BeautifulSoup(await response.text(), 'lxml')
        print(soup)
        
        try:
            # Нужны названия компаний, отзыв, дата отзыва, человек его оставивший
            company_name = soup.find('h1', class_='orgpage-header-view__header').text.strip()
            reviews = soup.find_all('span', class_='business-review-view__body-text')
            
            # Если отзывов нет, добавим в файл, что нет данных
            if len(reviews) == 0:
                print('[INFO] Прогресс выполнения:', cur_links_idx, f'/{total_links}', url, 'Отзывов нет')
                authors, reviews_dates, reviews = [['Данных нет']] * 3
                company_name, city = [company_name], [name]
            else:
                authors = soup.find_all('span', {'itemprop':'name'})
                reviews_dates = soup.find_all('span', class_='business-review-view__date')                
                reviews = [review.text.strip() for review in reviews] 
                authors = [author.text.strip() for author in authors]
                reviews_dates = [date.text.strip() for date in reviews_dates]
                company_name, city = [company_name] * len(reviews), [name] * len(reviews)
                
            
            for review in zip(company_name, city, authors, reviews_dates, reviews):
                reviews_info.append([*review])
        except Exception as _ex:
            print(_ex)
        
        print(f'Страница {cur_links_idx}/{total_links}')


async def gather_data(url_path: str):
    files = ["C:/Users/Аяз/PycharmProjects/RevTaking/path.txt"]
    tasks = []
    for file in files:
        name = file.split('.')[0]

        with open(os.path.join(url_path, file), 'r', encoding='utf8') as file:
            urls = [url.strip() for url in file.readlines()]
            length = len(urls)

            for numb, url in enumerate(urls):
                task = asyncio.create_task(get_page_info(url, length, numb, name))
                await asyncio.sleep(0)
                tasks.append(task)

    await asyncio.gather(*tasks)
    print('Обработка завершена')

def main():
    # win politics
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data('url_links\\'))
    pd.DataFrame(reviews_info, columns=['Company', 'City', 'Name', 'Date', 'Review']).to_csv(os.path.join('ALL.csv'), index=False)
    

if __name__ == '__main__':
    main()