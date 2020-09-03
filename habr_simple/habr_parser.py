"""
Источник habr.com/ru
Задача обойти ленту статей (лучшее за сутки), извлечь данные:
заголовок
url статьи
имя автора
ссылка на автора
список тегов (имя тега и url)
список хабов (имя и url)
спроектировать sql базу данных таким образом что-бы данные о тегах хабах и авторах были атомарны,
и не дублировались в БД
"""

import random
import requests
from bs4 import BeautifulSoup
from time import sleep
from habr_simple.habr_db import HabroDB
from habr_simple.habr_models import Writer, Tag, Post, Hab


class HabrParser:
    domain = 'https://habr.com'
    start_url = 'https://habr.com/ru/top/'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.86 YaBrowser/20.8.0.894 Yowser/2.5 Safari/537.36"
    }

    def __init__(self, db):
        self.db = db
        self.visited_urls = set()
        self.post_links = set()

    def parse_rows(self, url=start_url):
        while url:
            sleep(random.randint(1, 3))
            if url in self.visited_urls:
                break
            response = requests.get(url)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soap)
            self.search_post_links(soap)

    def get_next_page(self, soap: BeautifulSoup) -> str:
        a = soap.find('a', attrs={'id': 'next_page'})
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def search_post_links(self, soap: BeautifulSoup):
        posts_list = soap.find('div', attrs={'class': 'posts_list'})
        posts_a = posts_list.find_all('a', attrs={'class': 'post__title_link'})
        links = {f'{itm.get("href")}' for itm in posts_a}
        self.post_links.update(links)
        return links

    def parse(self):
        for url in self.post_links:
            sleep(random.randint(1, 3))
            if url in self.visited_urls:
                continue
            response = requests.get(url)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')
            # Для тестирования берем только 3 статьи. Отключить для полного сбора данных!
            if len(self.visited_urls) > 4:
                break
            self.get_post_data(soap, url)

    def get_post_data(self, soap: BeautifulSoup, url: str):
        result = {'url': url,
                  'title': soap.find('span', attrs={'class': 'post__title-text'}).text,
                  'writer': self.get_writer(soap),
                  'tags': self.get_tags(soap),
                  'habs': self.get_habs(soap)
                  }
        self.db.add_post(Post(**result))

    def get_writer(self, soap: BeautifulSoup):
        author_block = soap.find('div', attrs={'class': 'author-panel__user-info'})
        user_info = author_block.find('div', attrs={'class': 'user-info'})
        writer = {
            'name': user_info.get('data-user-login'),
            'url': user_info.find('a').get('href'),
            'username': user_info.get('data-user-login')
        }
        result = Writer(**writer)
        return result

    def get_tags(self, soap: BeautifulSoup):
        tag_list = soap.find('dl', attrs={'class': 'post__tags'}).\
            find('ul', attrs={'class': 'js-post-tags'}).\
            find_all('a', attrs={'class': 'post__tag'})
        return [Tag(name=itm.text, url=itm.get('href')) for itm in tag_list]

    def get_habs(self, soap: BeautifulSoup):
        hab_list = soap.find('ul', attrs={'class': 'js-post-hubs'}).\
            find_all('a', attrs={'class': 'post__tag'})
        hab_obj_list = [Hab(name=itm.text, url=itm.get('href')) for itm in hab_list]
        return hab_obj_list


if __name__ == '__main__':
    db = HabroDB('sqlite:///habro_blog.db')
    parser = HabrParser(db)
    parser.parse_rows()
    parser.parse()
