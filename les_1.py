"""
Источник данных: https://5ka.ru/special_offers/
Задача организовать сбор данных, необходимо иметь метод сохранения данных в .json файлы
Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json файлы,
для каждой категории товаров должен быть создан отдельный файл и содержать товары
исключительно соответсвующие данной категории.
Пример структуры данных для файла:
{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT},  {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""
from typing import List, Dict
import datetime as dt
import os
from pathlib import Path
import json
import requests
from time import sleep


class Parser5ka:
    __urls = {
        'categories': 'https://5ka.ru/api/v2/categories/',
        'products': 'https://5ka.ru/api/v2/special_offers/'
    }

    __params = {
        'records_per_page': 50,
        'categories': '',
    }

    __headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
    }

    __replaces = (',', '-', '/', '\\', '.', '"', "'", '*', '#',)

    def __init__(self, folder_name='data'):
        self.category = self.__get_categories()
        # self.folder_data = Path(os.path.dirname(__file__)).join(folder_name)

    def __get_categories(self) -> List[Dict[str, str]]:
        response = requests.get(self.__urls['categories'])
        return response.json()

    def parse(self):
        for category in self.category:
            self.get_products(category)

    def get_products(self, category=None):
        url = self.__urls['products']
        params = self.__params
        params['categories'] = int(category['parent_group_code'])

        while url:
            sleep(0.2)
            response = requests.get(url, params=params, headers=self.__headers)
            data = response.json()
            url = data['next']
            params = {}

            if category.get('products'):
                category['products'].extend(data['results'])
            else:
                category['products'] = data['results']
            category['parse_date'] = dt.datetime.now().timestamp()
            self.save_to_file(category)
            print(1)

    def save_to_file(self, category):
        name = category['parent_group_name']
        for itm in self.__replaces:
            name = name.replace(itm, '')
        name = '_'.join(name.split()).lower()

        # file_path = os.path.join(self.folder_data, f'{name}.json')
        file_path = os.path.join(f'{name}.json')

        with open(file_path, 'w', encoding='UTF-8') as file:
            json.dump(category, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parser5ka()
    parser.parse()

