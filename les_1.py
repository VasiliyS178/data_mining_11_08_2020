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
import json
import requests
import time


class Parser5ka:
    _domain = 'https://5ka.ru'
    _api_path = '/api/v2/special_offers/'
    _api_cat_path = '/api/v2/categories/'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 YaBrowser/20.7.3.100 Yowser/2.5 Safari/537.36",
    }

    def __init__(self):
        self.products = []

    def download(self):
        data_for_save = {}
        params = {}
        categories_dict = {}
        url_cat = self._domain + self._api_cat_path

        categories = requests.get(url_cat, headers=self.headers, params=params).json()

        for itm in categories:
            categories_dict[itm['parent_group_code']] = itm['parent_group_name']
        print(categories_dict)

        for k, v in categories_dict.items():
            params['records_per_page'] = 20
            params['categories'] = int(k)
            print(params)
            url = self._domain + self._api_path
            while url:
                response = requests.get(url, headers=self.headers, params=params)
                data = response.json()
                params = {}
                url = data['next']
                self.products.extend(data['results'])
                time.sleep(0.1)

            data_for_save['name'] = v
            data_for_save['code'] = k
            data_for_save['products'] = self.products

            print(data_for_save)

            with open(f'{v}.json', 'w', encoding='utf-8') as f:
                json.dump(data_for_save, f)

            self.products.clear()
            data_for_save.clear()


if __name__ == '__main__':
    parser = Parser5ka()
    parser.download()
