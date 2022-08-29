import time
import requests
from bs4 import BeautifulSoup
import datetime as dt
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from airflow.models import Variable


class ShopkeramplitkaParser:
    START_URL = 'https://shopkeramplitka.ru/catalog'
    DOMAIN = 'https://shopkeramplitka.ru'
    VENDOR = 'ИП Салюкова Г.Ш.'
    CITY = 'Москва'
    IS_IN_STOCK = 'В наличии'
    DISCOUNT = 0.0
    PARSER_PAUSE = 0.2
    TIMEOUT = 10

    def __init__(self):
        self.visited_urls = set()
        self.data_columns = ['city', 'vendor', 'category', 'name', 'article', 'catalog_unit', 'price',
                             'is_in_stock', 'discount', 'discounted_price', 'alternative_catalog_unit',
                             'alternative_price', 'manufacturer', 'datekey']
        self.products_data = []
        self.current_url = None
        self.datekey = int(dt.datetime.now().strftime('%Y%m%d'))
        self.products_count = 0

    def parse_sections(self, start_url):
        """
        Parse site by sections of the Catalog
        :param start_url: start URL
        :return: None
        """
        response = requests.get(start_url, timeout=self.TIMEOUT)
        soap = BeautifulSoup(response.text, 'html.parser')
        category_urls = self.search_category_links(soap=soap)
        for category_url in category_urls:
            # print(f'category_url: {category_url}')
            response = requests.get(category_url, timeout=self.TIMEOUT)
            soap = BeautifulSoup(response.text, 'html.parser')
            product_urls = self.search_product_links(soap)
            self.products_count += len(product_urls)
            for product_url in product_urls:
                self.current_url = product_url
                if self.current_url not in self.visited_urls:
                    response = requests.get(product_url, timeout=self.TIMEOUT)
                    soap = BeautifulSoup(response.text, 'html.parser')
                    self.products_data.append(self.get_product_data(soap))
                    self.visited_urls.add(product_url)
                    time.sleep(self.PARSER_PAUSE)

    def search_category_links(self, soap):
        """
        Search all links of the product's Categories
        :param soap: BeautifulSoup
        :return: List of URLs
        """
        try:
            catalog_navigation = soap.find('nav', attrs={'class': 'catalog-nav-collections list-group'})
            link_tags = catalog_navigation.find_all('div', attrs={'class': 'position-relative d-flex '
                                                                           'align-items-center bg-light border-t'
                                                                           'op rounded-0 px-3 py-2'})
            links = [f'{self.DOMAIN}{link_tag.find("a").get("href")}' for link_tag in link_tags]
        except AttributeError:
            print('There are no Categories')
            links = []
        return links

    def search_product_links(self, soap):
        """
        Search all links of Products in the Category
        :param soap: BeautifulSoup
        :return: List of URLs
        """
        try:
            wrapper = soap.find('div', attrs={'class': 'row usage-list'})
            products = wrapper.find_all('a', attrs={'class': 'm-0 h4 stretched-link text-dark text-decoration-none'})
            links = [f'{self.DOMAIN}{product.get("href")}' for product in products]
        except AttributeError:
            print('There are no Products in this Category')
            links = []
        return links

    def get_product_data(self, soap):
        """
        Get data about Product
        :param soap: BeautifulSoup
        :return: Dict
        """
        result = {column_name: None for column_name in self.data_columns}
        result['datekey'] = self.datekey
        result['city'] = self.CITY
        result['vendor'] = self.VENDOR
        name = soap.find('h1')
        result['name'] = name.text if name else None
        article = soap.find('div', attrs={'class': 'mr-6'}).find('b')
        result['article'] = article.text if article else None
        price_tag = soap.find('div', attrs={'class': 'h3 font-weight-bold text-primary'})
        price = price_tag.text[:-5].replace(' ', '') if price_tag else 0.0
        amount_tag = soap.find('input', attrs={'name': 'mtr'})
        try:
            result['price'] = float(price)
            amount = float(amount_tag.get('value')) if amount_tag else 0.0
        except ValueError:
            print("Price or Amount was not converted to float. Check the parser's config")
            result['price'] = 0.0
            amount = 0.0
        alternative_catalog_unit_tag = soap.find('div', attrs={'class': 'col-xx-3 col-xl-4 col-md-6 d-md-block '
                                                                        'd-sm-flex d-block align-items-start mt-1 '
                                                                        'mt-md-0'})
        if alternative_catalog_unit_tag and result['price']:
            result['alternative_catalog_unit'] = alternative_catalog_unit_tag.find('label').text
            result['alternative_price'] = round(amount * result['price'], 2)
        else:
            result['alternative_catalog_unit'] = None
            result['alternative_price'] = 0.0

        specification_data = {}
        specification_table = soap.find('table').find('tbody')
        specification_rows = specification_table.find_all('tr')
        if specification_rows:
            for row in specification_rows:
                specification_data[row.find('th').text.lower().strip()] = row.find('td').text.strip()
            result['category'] = specification_data.get('тип')
            result['manufacturer'] = specification_data.get('производитель')
            result['catalog_unit'] = specification_data.get('единица измерения')
        else:
            result['category'] = None
            result['manufacturer'] = None
            result['catalog_unit'] = None

        result['discount'] = self.DISCOUNT
        result['is_in_stock'] = self.IS_IN_STOCK
        result['discounted_price'] = result['price'] * (1 - result['discount'])
        return tuple(result.values())


def write_data_to_hdfs(spark_session, data, path, schema):
    """
    Prepare and write Spark DataFrame to HDFS
    :param schema: DataFrame Schema
    :param spark_session: Spark session
    :param data: Dict
    :param path: path to write data in HDFS
    :return: None
    """
    result_df = spark_session.createDataFrame(data=data, schema=schema)
    result_df.show(5, False)
    result_df.printSchema()
    result_df.coalesce(1).write.format("parquet").mode("overwrite").partitionBy("datekey").save(path)


if __name__ == '__main__':
    LOAD_SOURCE_PATH = Variable.get('load_source_path') + '/shopkeramplitka'
    conf = SparkConf().setAppName("get_shopkeramplitka_data")
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")
    spark = SparkSession(sc)
    parser = ShopkeramplitkaParser()
    parser.parse_sections(parser.START_URL)
    write_data_to_hdfs(spark_session=spark,
                       data=parser.products_data,
                       path=LOAD_SOURCE_PATH,
                       schema=parser.data_columns)
    print('Site shopkeramplitka.ru was parsed successfully')
    print(f'Total number of products in the catalog: {parser.products_count}')
    spark.stop()
