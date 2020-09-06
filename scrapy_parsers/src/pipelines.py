# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


# пайп для сохранения собранных данных в БД Монго
class ScrapyPipeline:
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017')
        self.db = client['scrapy']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]  # Даем имя коллекции монго такое же, как у item
        collection.insert(item)
        return item


# пайп для скачивания изображений, должен запускаться до пайпа сохранения AvitoscrpPipeline
# для этого поменять приоритет в settings на меньший
class ScrapyImagePipeline(ImagesPipeline):
    # pip install Pillow  # поставить для работы с изображениями (скачивание, обрезка, миниатюры)
    def get_media_requests(self, item, info):
        for url in item.get('images', []):
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    # Метод для обработки скаченных изображений. Перезаписываем информацию в item об изображениий,
    # которые удалось скачать
    def item_completed(self, results, item, info):
        if item.get('images'):
            item['images'] = [itm[1] for itm in results if itm[0]]
        return item