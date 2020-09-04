import json
import scrapy
from scrapy.http.response import Response
from scrapy_parsers.src.items import InstaPostItem
from scrapy_parsers.src.items import InstaUserItem
from scrapy_parsers.src.items import InstaHashTagItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __tag_url = '/explore/tags/рождественно/'
    __api_tag_url = '/graphql/query/'
    # заменить query_hash на свой из запроса в браузере, может измениться, что приведет к тому, что в API-запросе будет
    # только название тэга вместо данных. Есть разные queryhash, нужен именно для запроса!!!
    __query_hash = '9b498c08113f1e09617a1703c22b2f32'

    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        super().__init__(*args, **kwargs)
        self.posts_list = []

    def parse(self, response: Response, **kwargs):
        try:
            js_data = self.get_js_shared_data(response)
            # для авторизации используем FormRequest, а не follow
            yield scrapy.FormRequest(self.__login_url,
                                     method='POST',
                                     callback=self.parse,
                                     formdata={
                                         'username': self.__login,
                                         'enc_password': self.__password
                                     },
                                     headers={'X-CSRFToken': js_data['config']['csrf_token']}
                                     )
        except AttributeError as e:
            if response.json().get('authenticated'):
                yield response.follow(self.__tag_url, callback=self.first_tag_page_parse)

    # Метод парсинга постов с ПЕРВОЙ старницы тэга
    def first_tag_page_parse(self, response: Response):
        js_data = self.get_js_shared_data(response)
        hashtag: dict = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        # Формируем url для создания запроса на следующую порцию постов через запрос по API
        url = self.get_url_to_query_next_posts_for_api(hashtag)
        if url:
            yield response.follow(url, callback=self.get_api_hastag_posts)  # делаем запрос к API
        hashtag['posts_count'] = hashtag['edge_hashtag_to_media']['count']
        # с помощью pop удаляем данные о постах, что их не дублировать перед сохранением в айтем самого тэга
        posts = hashtag.pop('edge_hashtag_to_media')['edges']
        yield InstaHashTagItem(data=hashtag)  # сохранение айтема хэштэга в базу
        for post in posts:
            yield InstaPostItem(data=post['node'])
            if post['node']['edge_media_to_comment']['count'] > 30 or post['node']['edge_liked_by']['count'] > 100:
                yield response.follow(f'/p/{post["node"]["shortcode"]}/', callback=self.post_page_parse)

    # Метод обхода пагинации через запрос по API и обработки получаемых постов запросу (обход погинации)
    def get_api_hastag_posts(self, response: Response):
        hashtag = response.json()['data']['hashtag']
        url = self.get_url_to_query_next_posts_for_api(hashtag)
        if url:
            yield response.follow(url, callback=self.get_api_hastag_posts)  # обходим пагинацию
            posts: list = hashtag['edge_hashtag_to_media']['edges']
            for post in posts:
                yield InstaPostItem(data=post['node'])
                if post['node']['edge_media_to_comment']['count'] > 30 or post['node']['edge_liked_by']['count'] > 100:
                    yield response.follow(f'/p/{post["node"]["shortcode"]}/', callback=self.post_page_parse)

    # Метод формирования url для запроса по API для получения следующей порции постов в ленте постов по тэгу
    def get_url_to_query_next_posts_for_api(self, hashtag: dict):
        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {"tag_name": hashtag['name'],
                         "first": 50,
                         "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}
            return f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables=' \
                  f'{json.dumps(variables, ensure_ascii=False)}'
        return None

    # Метод сохранения данных об авторах постов, у которых больше 30 комментариев или более 100 лайков
    def post_page_parse(self, response):
        data = response.xpath(
            '/html/body/script[@type="text/javascript" and contains(text(), "window.__additionalDataLoaded")]/text()'
                                  ).extract_first()
        data = json.loads(data[data.find('{'):-1][:-1])
        yield InstaUserItem(data=data['graphql']['shortcode_media']['owner'])

    # Метод извлечения структуры данных из скрипта, формуирующего ПЕРВУЮ старницу с постами по выбранному тэгу
    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(f'/html/body/script[@type="text/javascript" and contains(text(), "{marker}")]/text()'
                              ).extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data)
