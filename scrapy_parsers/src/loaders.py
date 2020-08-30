import re
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader
from scrapy import Selector

from .items import YoulaItem


def search_author_id(itm):
    re_str = re.compile(r'youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar')
    result = re.findall(re_str, itm)
    return result


def create_user_url(itm):
    base_url = "https://youla.ru/user/"
    result = base_url + itm
    return result


def clear_photo(itm):
    result = dict(reversed(line.split()) for line in itm.split(','))
    return result.get('2x') or result.get('1x')


# def get_author_url(itm):
#     tag = Selector(text=itm)
#     result = tag.xpath('.//a[@data-target="advert-seller-name"]/@href').extract()
#     return result


def get_youla_params(itm):
    tag = Selector(text=itm)
    labels = tuple(tag.xpath('.//div[@class="AdvertSpecs_label__2JHnS"]/text()').extract())
    values = tuple(tag.xpath('//div[@class="AdvertSpecs_data__xK2Qx"]/text() | '
                             '//div[@class="AdvertSpecs_row__ljPcX"]//a[@class="blackLink"]/text()').extract())
    result = dict(zip(labels, values))
    return result


def get_price(itm):
    reg = re.compile('[^0-9]')
    result = float(reg.sub('', itm))
    return result


class YoulaLoader(ItemLoader):
    default_item_class = YoulaItem
    url_out = TakeFirst()
    author_url_in = MapCompose(search_author_id, create_user_url)
    # author_url_in = MapCompose(get_author_url)
    author_url_out = TakeFirst()
    title_out = TakeFirst()
    images_in = MapCompose(clear_photo)
    params_in = MapCompose(get_youla_params)
    params_out = TakeFirst()
    descriptions_out = TakeFirst()
    price_in = MapCompose(get_price)
    price_out = TakeFirst()


