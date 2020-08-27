from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from avito_parser.avitoscrp import settings
from avito_parser.avitoscrp.spiders.avito import AvitoSpider

# Модуль для запуска avitoscrp
if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)

    crawl_proc = CrawlerProcess(settings=crawl_settings)

    crawl_proc.crawl(AvitoSpider)

    crawl_proc.start()