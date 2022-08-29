import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=0")
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-setuid-sandbox')
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--enable-logging')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--log-level=3')

executable_path = r"C:\Users\vsamarin\YandexDisk\projects\parser_skillbox\chromedriver.exe"
service = Service(executable_path=executable_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

products_data = []
TIMEOUT_SEC = 30
TIME_DELAY_SEC = 1


urls = [
    "https://maxipro.ru/product/mir-instrumenta-i-krepezha/botinki-vysokie-etna-m-s1-chernyy-razmer-43/",
    "https://maxipro.ru/product/mir-obshchestroitelnyh-rabot/kley-plitochnyy-bergauf-keramik-pro-usilennyy-c1t-25-kg/",
    "https://maxipro.ru/product/mir-ehlektriki/kabel-silovoy-elprokabel-kgtp-3x1-5-mm/",
    "https://maxipro.ru/product/mir-instrumenta-i-krepezha/kryuk-koltso-stroybat-4kh50-mm-2-sht/",
    "https://maxipro.ru/product/mir-obshchestroitelnyh-rabot/kley-plitochnyy-paladium-palaflekh-102-professionalnyy-s1t-25-kg/",
    "https://maxipro.ru/product/mir-obshchestroitelnyh-rabot/kley-plitochnyy-volma-keramik-t14-s1-seryy-25-kg/",
    "https://maxipro.ru/product/mir-obshchestroitelnyh-rabot/plenka-polietilenovaya-120-mkm-3-m/",
    "https://maxipro.ru/product/mir-obshchestroitelnyh-rabot/trotuarnaya-plitka-kirpichik-200kh100kh60-mm-seraya/"
]


def check_static_unit_tag(soup):
    try:
        _ = soup.find('h2', attrs={'class': '-mb0'}).find('span', attrs={'class': 'js-price'}).text
    except AttributeError:
        return True
    try:
        _ = soup. \
            find("div", attrs={'class': 'col-auto textstatic -mb0 p_product-price-wrapper'}). \
            find('div', attrs={'class': '-mb0 -grey'}).text.strip()
    except AttributeError:
        return False
    return True


def check_dynamic_unit_tag(soup):
    try:
        _ = soup.find('h2', attrs={'class': '-mb0'}).find('span', attrs={'class': 'js-price'}).text
    except AttributeError:
        return False
    try:
        _ = soup. \
            find("div", attrs={'class': 'col-auto textstatic -mb0 p_product-price-wrapper'}). \
            find('div', attrs={'id': 'bxdynamic_measure-item_start'}).text
    except AttributeError:
        return False
    return True


def check_dynamic_product_info(soup):
    try:
        _ = soup.find('h2', attrs={'class': '-mb0'}).find('span', attrs={'class': 'js-price'}).text
    except AttributeError:
        return False
    try:
        _ = soup. \
            find("div", attrs={'class': 'p_product-info'}). \
            find('div', attrs={'id': 'bxdynamic_delivery_ready_start'}).text
    except AttributeError:
        return False
    return True


def get_product_data(soup):
    properties = ['city', 'vendor', 'category', 'product_name', 'article', 'catalog_unit', 'price',
                  'availability', 'discount', 'discounted_price', 'alternative_catalog_unit',
                  'alternative_price', 'manufacturer', 'url', 'datekey']
    product_info = {column_name: None for column_name in properties}
    product_info['product_name'] = soup.find('h1').text.strip()
    product_info['article'] = soup.find('div', attrs={'class': 'textstatic -mb0 d-flex'}).find('span').text.strip()
    # get category from bread-crumbs
    category_div = soup.find('div', attrs={'class': 'container-fluid -mb20 js-product overflow-hidden'})
    category_ul = category_div.find('ul', attrs={'class': 'list-unstyled list-inline bread-crumbs__list -all-'})
    categories = category_ul.text.split("/")
    if len(categories) >= 5:
        product_info['category'] = f"{categories[3].strip()}. {categories[4].strip()}"
    elif len(categories) == 4:
        product_info['category'] = categories[3].strip()
    elif len(categories) == 3:
        product_info['category'] = categories[2].strip()
    try:
        product_info['price'] = float(soup.find('h2', attrs={'class': '-mb0'}).
                                      find('span', attrs={'class': 'js-price'}).get('data-price').strip())
        # if product has price then it is in stocks
        product_info['availability'] = 'В наличии'
    except AttributeError:
        product_info['availability'] = 'Отсутствует'
    try:
        product_info['catalog_unit'] = soup. \
            find("div", attrs={'class': 'col-auto textstatic -mb0 p_product-price-wrapper'}). \
            find('div', attrs={'class': '-mb0 -grey'}).text.strip()
    except AttributeError:
        try:
            product_info['catalog_unit'] = soup. \
                find("div", attrs={'class': 'col-auto textstatic -mb0 p_product-price-wrapper'}). \
                find('span', attrs={'class': 'js-measure-item-name'}).text.strip()
        except AttributeError:
            try:
                raw_catalog_unit = soup. \
                    find("div", attrs={'class': 'p_product-info'}).contents[7]. \
                    find('li', attrs={'class': 'p_product-param-item'}). \
                    find('div', attrs={'class': 'row'}). \
                    find('span', attrs={'class': 'col-4 textstatic text-right -mb0'}).contents[3].text.strip()
                if 'штук' in raw_catalog_unit:
                    product_info['catalog_unit'] = 'штука'
                elif 'метров' in raw_catalog_unit:
                    product_info['catalog_unit'] = 'метр'
                else:
                    product_info['catalog_unit'] = raw_catalog_unit
            except AttributeError:
                product_info['catalog_unit'] = None
    # check if product has alternative catalog unit and amount
    try:
        alternative_catalog_unit_div = soup.find('div', attrs={'class': 'js-measure-alternative-list'}). \
            find('div', attrs={'class': 'p_product-buy -grey -p8 -mb8 js-measure-quantity'}). \
            find('div', attrs={'class': 'row p_product-unit -sm'})
        alternative_catalog_unit = alternative_catalog_unit_div. \
            find('div', attrs={'class': 'col-auto textstatic -mb0'}).text.strip().lower()
        if 'упаковка' in alternative_catalog_unit:
            product_info['alternative_catalog_unit'] = 'упаковка'
        elif alternative_catalog_unit in ['м2', 'квадратн']:
            product_info['alternative_catalog_unit'] = 'м2'
        elif alternative_catalog_unit in ['м3', 'кубическ']:
            product_info['alternative_catalog_unit'] = 'м3'
        elif 'ролик' in alternative_catalog_unit:
            product_info['alternative_catalog_unit'] = 'ролик'
        elif 'штуках' in alternative_catalog_unit:
            product_info['alternative_catalog_unit'] = 'штука'
        else:
            product_info['alternative_catalog_unit'] = alternative_catalog_unit
        amount = float(alternative_catalog_unit_div.
                       find('input', attrs={'class': 'cf_input -greyborder js-basket-measure-quantity'}).
                       get("data-step"))
    except Exception:
        amount = 0.0
    if amount and product_info['price']:
        product_info['alternative_price'] = round(product_info['price'] / amount, 2)
    # get manufacturer from product's specification
    specification_div = soup.find('div', attrs={'class': 'col-md-6 -mb-md-0'})
    specification_keys = [key.text.lower().strip() for key in
                          specification_div.find_all('span', attrs={'class': 'col-6 textstatic -mb0 -grey'})]
    specification_values = specification_div.find_all('span', attrs={'class': 'col-6 textstatic -mb0'})
    for i, key in enumerate(specification_keys):
        if key == 'бренд':
            product_info['manufacturer'] = specification_values[i].text.strip()
            break
    result_to_write = [str(value) for value in product_info.values()]
    return "|".join(result_to_write).replace('\n', '') + '\n'


def parse_url(product_url):
    response = requests.get(product_url, timeout=TIMEOUT_SEC)
    soup_static = BeautifulSoup(response.text, 'html.parser')
    # try to parse product's properties from html
    if check_static_unit_tag(soup=soup_static):
        try:
            products_data.append(get_product_data(soup=soup_static))
        except Exception:
            print("Can't parse product's URL as STATIC: ", product_url)
        time.sleep(TIME_DELAY_SEC)
    elif check_dynamic_unit_tag(soup=soup_static):
        try:
            # reload page as DYNAMIC content and wait for until dynamic span "js-measure-item-name"
            # will be loaded
            driver.get(product_url)
            WebDriverWait(driver, TIMEOUT_SEC). \
                until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[class='js-measure-item-name']")))
            html_dynamic = driver.page_source
            soup_dynamic = BeautifulSoup(html_dynamic, "html.parser")
        except Exception:
            print("Can't reload product's URL with DYNAMIC unit tag: ", product_url)
            soup_dynamic = None
        try:
            products_data.append(get_product_data(soup=soup_dynamic))
        except Exception:
            print("Can't parse product's URL with DYNAMIC unit tag: ", product_url)
    elif check_dynamic_product_info(soup=soup_static):
        try:
            # reload page as DYNAMIC content and wait for until dynamic span "js-measure-item-name"
            # will be loaded
            driver.get(product_url)
            WebDriverWait(driver, TIMEOUT_SEC). \
                until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='textstatic -mb8 -green']")))
            html_dynamic = driver.page_source
            soup_dynamic = BeautifulSoup(html_dynamic, "html.parser")
        except Exception:
            print("Can't reload product's URL with DYNAMIC product info: ", product_url)
            soup_dynamic = None
        try:
            products_data.append(get_product_data(soup=soup_dynamic))
        except Exception:
            print("Can't parse product's URL with DYNAMIC product info: ", product_url)
    else:
        try:
            products_data.append(get_product_data(soup=soup_static))
        except Exception:
            print("Can't parse product's URL as STATIC: ", product_url)
        time.sleep(TIME_DELAY_SEC)


for url in urls:
    print(url)
    parse_url(url)

driver.quit()

for product in products_data:
    print(product)

# unit_span_xpath = '/html/body/main/div[6]/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[3]/span/span'
# filter = browser.find_element(by=By.XPATH, value=unit_span)
# filter.click()
