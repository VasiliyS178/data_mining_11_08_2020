import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# before start download webdriver from web-site selenium for your browser
executable_path = r"C:\Users\vsamarin\YandexDisk\projects\parser_skillbox\chromedriver.exe"
browser = webdriver.Chrome(executable_path)  # Открываем браузер
browser.get("https://www.ozon.ru/category/odeyala-15081/")  # Открываем Озон в браузере

FILTER_OZON = '//*[@id="layoutPage"]/div[1]/div[3]/div[2]/div[1]/aside/div[13]/div[2]/div/span[1]/label'
filter = browser.find_element(by=By.XPATH, value=FILTER_OZON)
filter.click()

time.sleep(3)

### Найдем все Цены
# we can copy xpath of element from browser RBM - copy xpath
XPATH_PRICE = '//*[@id="layoutPage"]/div[1]/div[3]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]/div[1]/div[1]/span[1]'
elements = browser.find_elements(by=By.XPATH, value=XPATH_PRICE)
className = elements[0].get_attribute("class")
prices = browser.find_elements(by=By.CSS_SELECTOR, value=f"span[class='{className}']")

print(len(prices))
for element in prices:
    parent1 = element.find_element(by=By.XPATH, value="..")
    parent2 = parent1.find_element(by=By.XPATH, value="..")
    try:
        print(element.text)
        print(parent2.find_element(by=By.TAG_NAME, value="a").text)
    except:
        print("ERROR")

time.sleep(60)
browser.close()
