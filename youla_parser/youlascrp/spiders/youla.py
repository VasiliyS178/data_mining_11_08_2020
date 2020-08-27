import scrapy
from youla_parser.youlascrp.items import YoulascrpItem
from scrapy.loader import ItemLoader

class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/sankt-peterburg/cars/used/bmw/']
    ads_links = []

    __xpath_query = {
        'models_links': '//div[@class="Search_brandModelLinks__1sjuY"]//a[@data-target="model"]/@href',

        'data-target-id': '//article[@data-target="serp-snippet"]/@data-target-id',
        
        'pagination': '//div[contains(@class, "Paginator_block__2XAPy")]//div[@class="Paginator_total__oFW1n"]/text()',

        'ads': '//div[@class="SerpSnippet_titleWrapper__38bZM"]//a[@data-target="serp-snippet-title"]/@href',

        'title': '//h1[@class="title-info-title"]/span[@itemprop="name"]/text()',

        'images': '//div[contains(@class, "gallery-imgs-container")]'
                  '/div[contains(@class, "gallery-img-wrapper")]'
                  '/div[contains(@class, "gallery-img-frame")]/@data-url',

        'prices': '//div[contains(@class, "price-value-prices-wrapper")]'
                  '/ul[contains(@class, "price-value-prices-list")]'
                  '/li[contains(@class, "price-value-prices-list-item_size-normal")]',

        'address': '//div[@itemprop="address"]/span/text()',

        'params': '//div[@class="item-params"]/ul[@class="item-params-list"]/li[@class="item-params-list-item"]'

    }

    def parse(self, response, start=True):
        if start:
            print(1)
            # Получаем число страниц из пагинации
            # pages_count = int(response.xpath(self.__xpath_query['pagination']).extract()[1])
            # Обходим все ссылки на страницы с объявлениями
            # for num in range(2, pages_count):
            #     yield response.follow(
            #         f'/sankt-peterburg/cars/used/bmw/?bodyTypes%5B0%5D=13&page={num}#serp',
            #         callback=self.parse,
            #         cb_kwargs={'start': False}
            #     )
            for link in response.xpath(self.__xpath_query['models_links']):
                yield response.follow(
                    link,
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        # ads_links = response.xpath(self.__xpath_query['models_links'])

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )


    def ads_parse(self, response):
        # self.ads_links.append(response.url)

        item_loader = ItemLoader(YoulascrpItem(), response)
        # for k, v in self.__xpath_query.items():
        #     if k in ('pagination', 'ads'):
        #         continue
        #     item_loader.add_xpath(k, v)
        item_loader.add_value('url', response.url)
        #
        yield item_loader.load_item()
