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
    __query_hash = '845e0309ad78bd16fc862c04ff9d8939'  # заменить на свой из запроса в браузере!


    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        super().__init__(*args, **kwargs)
        self.posts_list = []

    def parse(self, response: Response, **kwargs):
        try:
            js_data = self.get_js_shared_data(response)

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
                yield response.follow(self.__tag_url, callback=self.tag_page_parse)

    # Получение ссылок на посты со старницы тэга
    def tag_page_parse(self, response: Response):
        js_data = self.get_js_shared_data(response)
        hashtag: dict = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']

        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {"tag_name": hashtag['name'],
                         "first": 50,
                         "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

            url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables, ensure_ascii=False)}'

            yield response.follow(url, callback=self.get_api_hastag_posts)

        hashtag['posts_count'] = hashtag['edge_hashtag_to_media']['count']
        posts = hashtag.pop('edge_hashtag_to_media')['edges']  # через pop удаляем данные о постах перед сохранением в айтем тэга

        yield InstaHashTagItem(data=hashtag)  # сохранение айтема хэштэга в базу

        for post in posts:
            yield InstaPostItem(data=post['node'])
            if post['node']['edge_media_to_comment']['count'] > 30 or post['node']['edge_liked_by']['count'] > 100:
                yield response.follow(f'/p/{post["node"]["shortcode"]}/', callback=self.post_page_parse)

    # Получение данных из постов по указанному тэгу из полученной ранее структуры данных
    def get_api_hastag_posts(self, response: Response):
        hashtag = response.json()['data']['hashtag']

        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:  # тут возникает ошибка KeyError: 'edge_hashtag_to_media'
            variables = {"tag_name": hashtag['name'],
                         "first": 50,
                         "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}
            url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables, ensure_ascii=False)}'
            yield response.follow(url, callback=self.get_api_hastag_posts)

        posts: list = hashtag['edge_hashtag_to_media']['edges']

        for post in posts:
            yield InstaPostItem(data=post['node'])
            if post['node']['edge_media_to_comment']['count'] > 30 or post['node']['edge_liked_by']['count'] > 100:
                yield response.follow(f'/p/{post["node"]["shortcode"]}/', callback=self.post_page_parse)

    # Сохранение данных об авторах постов, у которых больше 30 комментариев или более 100 лайков
    def post_page_parse(self, response):
        # data = self.get_js_shared_data(response)
        # yield InstaUserItem(data=data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner'])
        data = self.get_js_owner_data(response)
        yield InstaUserItem(data=data['graphql']['shortcode_media']['owner'])

    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(f'/html/body/script[@type="text/javascript" and contains(text(), "{marker}")]/text()'
                              ).extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data)

    @staticmethod
    def get_js_owner_data(response):
        data = response.xpath('/html/body/script[@type="text/javascript" and contains(text(), "window.__additionalDataLoaded")]/text()'
                              ).extract_first()
        data = data[data.find('{'):-1][:-1]
        return json.loads(data)