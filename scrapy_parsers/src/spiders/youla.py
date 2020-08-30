import scrapy
from scrapy_parsers.src.items import YoulaItem
from scrapy.loader import ItemLoader
from ..loaders import YoulaLoader


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/sankt-peterburg/cars/used/audi/']

    __xpath_query = {
        'pagination': '//div[contains(@class, "Paginator_block__2XAPy")]//div[@class="Paginator_total__oFW1n"]/text()',

        'ads': '//div[@class="SerpSnippet_titleWrapper__38bZM"]//a[@data-target="serp-snippet-title"]/@href',

        'author_url': '/html/body/script[contains(text(), "window.transitState = decodeURIComponent")]/text()',

        # 'author_url': '//div[@class="app_gridAsideChildren__wB756")]/div',

        'title': '//div[@class="AdvertCard_advertTitle__1S1Ak"]/text()',

        'images': '//div[contains(@class, "AdvertCard_pageContent")]'
                  '//div[contains(@class, "PhotoGallery_photoWrapper")]//picture/source/@srcset',

        'params': '//div[@class="AdvertCard_specs__2FEHc"]/div',

        'descriptions': '//div[@class="AdvertCard_descriptionInner__KnuRi"]/text()',

        'price': '//div[@class="AdvertCard_priceBlock__1hOQW"]/div[@data-target="advert-price"]/text()'
    }

    def parse(self, response, start=True):
        if start:
            pages_count = int(response.xpath(self.__xpath_query['pagination']).extract()[1])
            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'{self.start_urls[0]}?page={num}#serp',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )

    def ads_parse(self, response):
        loader = YoulaLoader(response=response)
        # for k, v in self.__xpath_query.items():
        #     if k in ('pagination', 'ads'):
        #         continue
        #     loader.add_xpath(k, v)
        loader.add_value('url', response.url)
        loader.add_xpath('author_url', self.__xpath_query['author_url'])
        loader.add_xpath('title', self.__xpath_query['title'])
        loader.add_xpath('images', self.__xpath_query['images'])
        loader.add_xpath('params', self.__xpath_query['params'])
        loader.add_xpath('descriptions', self.__xpath_query['descriptions'])
        loader.add_xpath('price', self.__xpath_query['price'])
        yield loader.load_item()
