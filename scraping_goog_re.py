import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import lxml

async def gather_data(file_path):
    
    global reviews_list
    reviews_list = []
    tasks = []
    files = os.listdir(file_path)
    for each in files:
        df = pd.read_csv(os.path.join(file_path, each))
        df = df.loc[df['JSON ANS'] != 'False']
        df = df.loc[:, ['City', 'Company', 'Count of reviews', 'JSON ANS']]
        sh = df.shape[0]
        for pos, row in enumerate(df.iterrows()):
            task = asyncio.create_task(parse_rew(row, sh, pos))
            tasks.append(task)
        await asyncio.sleep(35)
    await asyncio.gather(*tasks)
    
    

async def parse_rew(element_pair: set, max_elements:int, current_pos:int):
    '''
    Вытягиваем отзывы
    '''

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}
    async with ClientSession() as session:
        # В зависимости от количества отзывов будет подставляться значение
        for page in range(0, (element_pair[1][2]//9)*10+11, 10):
            url  = element_pair[1][3].replace('1i0', f'1i{page}')
            try:
                response = await session.get(url = url, headers=headers)
                soup = BeautifulSoup(await response.text())
                response = soup.get_text()
                response = response.replace('null', '').replace('\\n', '').replace("Высокое качество", '').replace('Низкое качество', '')\
                    .replace('Качество', '').replace('Хорошее соотношение цены и качества', '')\
                    .replace('Плохое соотношение цены и качества', '').replace('Цена/качество', '')\
                    .replace('Хорошее отношение к клиентам', '').replace('Плохое отношение к клиентам', '')\
                    .replace('Отношение к клиентам', '').replace('Непрофессионализм', '').replace('Профессионализм', '')

                result = re.findall('RU","(.+?)",\d{1},,"', response)
                for rev in range(len(result)):
                    name = re.findall('(.+?)","htt', result[rev])[0]
                    date = re.findall('\d+ \S+ назад', result[rev])
                    if len(date):
                        date = date[0]
                    else: date = 'Неизвестно'
                    review = result[rev].split(',,')[-1]
                    reviews_list.append([element_pair[1][0], element_pair[1][1], name, date, review])
            except Exception as _ex:
                print(_ex)
        print(current_pos, '/', max_elements)

def main():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data('google_data\\company_info\\'))
    pd.DataFrame(reviews_list, columns=['City', 'Company', 'Name', 'Date', 'Review']).to_csv(os.path.join('ALL_goog.csv'), index=False)

if __name__ == '__main__':
    main()