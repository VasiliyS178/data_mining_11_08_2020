import scrapy
from scrapy_parsers.src.items import AvitoItem
from scrapy.loader import ItemLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['http://www.avito.ru/novorossiysk/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="index-content-2lnSO"]//'
                      'div[contains(@data-marker, "pagination-button")]/'
                      'span[@class="pagination-item-1WyVp"]/@data-marker',

        'ads': '//h3[@class="snippet-title"]/a[@class="snippet-link"][@itemprop="url"]/@href',

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
            # Получаем число страниц из пагинации. Для тестирования отключено! Раскоментировать для сбора всех данных
            # pages_count = int(
            #     response.xpath(self.__xpath_query['pagination']).extract()[-1].split('(')[-1].replace(')', ''))

            pages_count = 2  # Для тестирования соберем данные на 1 и 2 страницах с объявлениями

            # Обходим все ссылки на страницы с объявлениями
            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'?p={num}',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )
        # На каждой станице с объявлениями получаем все ссылки на объявления и парсим объявления с помощью метода
        # ads_parse
        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )

    # Поиск тэгов с помощью css-селектора
    # response.css('h1.title-info-title span.title-info-title-text::text').extract()
    # получение значения атрибута через attr + extract()/extract_first()
    # response.css('div.seller-info-value div.seller-info-name a::attr("href")').extract_first()

    # Метод для парсинаг данных из объявления путем загрузки данных в объект класса AvitoItem
    # Предварительно необходимо описать все поля класса AvitoItem в модуле items.py
    # Важно не забыть добавить в ItemLoader поле _id, которое создается в момент записи данных в Монго
    def ads_parse(self, response):
        item_loader = ItemLoader(AvitoItem(), response)
        for k, v in self.__xpath_query.items():
            if k in ('pagination', 'ads'):
                continue
            item_loader.add_xpath(k, v)
        item_loader.add_value('url', response.url)

        yield item_loader.load_item()






