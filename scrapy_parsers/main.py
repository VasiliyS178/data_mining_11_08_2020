import os
from pathlib import Path
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy_parsers.src import settings
from scrapy_parsers.src.spiders.avito import AvitoSpider
from scrapy_parsers.src.spiders.youla import YoulaSpider
from scrapy_parsers.src.spiders.instagram import InstagramSpider

# Модуль для запуска парсинга с пом пауков. Пауки могут собирать информацию с разных сайтов одновременно
if __name__ == '__main__':
    load_dotenv(dotenv_path=Path('.env').absolute())
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    # crawl_proc.crawl(AvitoSpider)
    # crawl_proc.crawl(YoulaSpider)
    crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('ENC_PASSWORD'))
    crawl_proc.start()