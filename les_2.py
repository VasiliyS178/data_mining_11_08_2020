"""
Источник https://geekbrains.ru/posts/
Необходимо обойти все записи в блоге и извлечь из них информацию следующих полей:
url страницы материала
Заголовок материала
Первое изображение материала
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
Пример словаря:
{
    "url": "str",
    "title": "str",
    "image": "str",
    "writer_name": "str",
    "writer_url": "str",
    "pub_date": datetime object,
}
Полученые материалы сохранить в MongoDB.
Предусмотреть метод извлечения данных из БД за период передаваемый в качестве параметров
"""
from typing import Dict
import re
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime as dt


class GBBlogParse:
    domain = 'https://geekbrains.ru'
    start_url = 'https://geekbrains.ru/posts'

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['parse_gb_blog']
        self.collection = self.db['posts']
        self.visited_urls = set()
        self.post_links = set()
        self.posts_data = []
        self.current_url = ''

    def parse_rows(self, url=start_url):
        while url:
            if url in self.visited_urls:
                break
            response = requests.get(url)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soap)
            self.search_post_links(soap)

    def get_next_page(self, soap: BeautifulSoup) -> str:
        ul = soap.find('ul', attrs={'class': 'gb__pagination'})
        a = ul.find('a', text=re.compile('›'))
        return f'{self.domain}{a.get("href")}' if a and a.get("href)") else None

    def search_post_links(self, soap: BeautifulSoup) -> Dict[str, str]:
        wrapper = soap.find('div', attrs={'class': 'post-items-wrapper'})
        posts = wrapper.find_all('div', attrs={'class': 'post-item'})
        links = {f'{self.domain}{itm.find("a").get("href")}' for itm in posts}
        self.post_links.update(links)
        return links

    # Получение страницы материала с блога
    def post_page_parse(self):
        for url in self.post_links:
            if url in self.visited_urls:
                continue
            response = requests.get(url)
            self.visited_urls.add(url)
            self.current_url = url
            soap = BeautifulSoup(response.text, 'lxml')
            # if len(self.posts_data) > 5:
            #     break
            self.posts_data.append(self.get_post_data(soap))

    # Извелечение данных страницы материала
    def get_post_data(self, soap: BeautifulSoup) -> Dict[str, str]:
        result = {}
        result['url'] = self.current_url
        result['title'] = soap.find('h1', attrs={'class': 'blogpost-title'}).text
        content = soap.find('div', attrs={'class': 'blogpost-content', 'itemprop': 'articleBody'})
        img = content.find('img')
        result['image'] = img.get('src') if img else None
        result['post_date'] = dt.datetime.fromisoformat(soap.find('time', attrs={'itemprop': 'datePublished'}).
                                                     get('datetime'))
        writer_info = soap.find('div', attrs={'class': 'row m-t'})
        result['writer_name'] = writer_info.find('div', attrs={'itemprop': 'author'}).text
        result['writer_url'] = f"{self.domain}{writer_info.find('a').get('href')}"
        return result

    def save_to_mongo(self):
        self.collection.insert_many(self.posts_data)

    # Метод для выборки статей за период
    def get_posts_from_mongo_by_dates(self, start_date: str, end_date: str):
        self.collection.find({
            'post_date': {
            '$gte': dt.datetime.fromisoformat(start_date),
            '$lte': dt.datetime.fromisoformat(end_date)
            }
        })


if __name__ == '__main__':
    parser = GBBlogParse()
    parser.parse_rows()
    parser.post_page_parse()
    parser.save_to_mongo()

    # Выборка всех данных из коллекции
    # print(list(parser.collection.find({}).sort([('title', -1)])))

    # Выборка документов из коллекции, у которых в поле title содержатся указанные строки
    # print(list(parser.collection.find({'title': {'Sin': ['Как работать из дома', 'Построение небольшого']}})))
