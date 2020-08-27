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
class YoulascrpPipeline:
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017')
        self.db = client['youla_parse']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        collection.insert(item)
        print(1)
        return item
