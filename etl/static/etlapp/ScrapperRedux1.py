import time
import requests
import re
from bs4 import BeautifulSoup as Bs
from etlapp.models import Products
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.options import Options


class Tire:
    def __init__(self, tire_dict):
        self.ID = tire_dict.get("ID", "")
        self.manufacturer = tire_dict.get("Producent:", "")
        self.name = tire_dict.get("Nazwa:", "")
        self.price = tire_dict.get("Cena", "")
        self.car_type = tire_dict.get("Typ:", "")
        self.season = tire_dict.get("Sezon:", "")
        self.size = tire_dict.get("Rozmiar:", "")
        self.approval = tire_dict.get("Homologacja:", "")
        self.speed_index = tire_dict.get("Indeks prędkości:", "")
        self.weight_index = tire_dict.get("Indeks nośności:", "")
        self.sound_index = tire_dict.get("Etykieta UE:", "")
        self.production_year = tire_dict.get("Rok produkcji:", "")
        self.country_of_origin = tire_dict.get("Kraj produkcji:", "")
        self.guaranty = tire_dict.get("Gwarancja:", "")
        self.other_info = tire_dict.get("Inne:", "")

    def __str__(self):
        string = '"'
        string += '","'.join(map(str, self.__dict__.values()))
        string += '"'
        return string

    def __eq__(self, other):
        if isinstance(other, Tire):
            return self.__hash__() == other.__hash__()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.ID)


def get_tire_widths():
    url = "https://www.oponeo.pl/wybierz-opony/"
    r = requests.get(url)
    s = Bs(r.content, "html.parser")
    widths = list(
        map(lambda x: x.get("value"), (s.find("select", {"name": "_ctTS_ddlDimWidth"}).find_all("option"))))
    widths.pop(0)
    return widths

def find_and_get_product_instance(driver):
    element = driver.find_elements_by_id("productName")
    if element:
        return element
    else:
        return False


def extract_data(link, data_list):
    while True:
        try:
            raw_html = requests.get("https://www.oponeo.pl" + link).content
        except requests.exceptions.RequestException:
            time.sleep(5)
            continue
        break
    html = Bs(raw_html, features="html.parser")
    opinion = {}
    opinion.update({"ID" : re.sub("/.*/|#.*$", "", link)})
    for h in html.find_all("h1"):
        for span in h.find_all("span"):
            if span.get("class") == ["model"]:
                opinion.update({"Nazwa:": span.text})
            elif span.get("class") == ["producer"]:
                opinion.update({"Producent:": span.text})
    opinion.update({"Cena" : html.find("meta", {"itemprop" : "price"}).get("content")})
    for parameters in html.find_all("div", {"class": "parameters"}):
        for li in parameters.find_all("div", {"class": "list"}):
            for div in li.find_all("div"):
                if div.get("class") == ["label"]:
                    data = div.find_next_sibling("div", "data")
                    if div.text != "Producent":
                        opinion.update({div.text: data.text})
    data_list.append(opinion)

def extract(data_list, width):
    t = time.time()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    main_address = "https://www.oponeo.pl/wybierz-opony/"
    driver.get(main_address)
    WebDriverWait(driver, 5)
    driver.find_element_by_id("cookiePolicyTooltip").find_element_by_class_name("button").click()
    select = Select(driver.find_element_by_name("_ctTS_ddlDimWidth"))
    select.select_by_visible_text(width)
    WebDriverWait(driver, 5)
    json = {"productKindId": 2, "vehicleKind": 1, "tireWidth": width, "producersIDs": None, "seasonID": 0,
            "isTireOnOponeoWarehouse": False}
    address = "https://www.oponeo.pl/WS/ShopService.svc/GetTireRatios"
    ratios = requests.post(address, json=json).json()["d"]
    for ratio in ratios:
        if re.match("^[0-9]*\.[0-9]$", ratio) is not None:
            continue
        while True:
            try:
                WebDriverWait(driver, 10)
                Select(driver.find_element_by_name("_ctTS_ddlDimRatio")).select_by_value(ratio)
            except exceptions.WebDriverException:
                continue
            break
        address = "https://www.oponeo.pl/WS/ShopService.svc/GetTireDiameters"
        json["tireRatio"] = ratio
        diameters = requests.post(address, json=json).json()["d"]
        for diameter in diameters:
            while True:
                try:
                    WebDriverWait(driver, 10)
                    old_value = driver.find_element_by_class_name('productName').text
                except exceptions.WebDriverException:
                    continue
                break
            try:
                Select(driver.find_element_by_name("_ctTS_ddlDimDiameter")).select_by_value(diameter)
            except exceptions.WebDriverException:
                continue
            for i in range(500):
            # while True:
                try:
                    WebDriverWait(driver, 10)
                    new_value = driver.find_element_by_class_name('productName').text
                    assert new_value != old_value
                except exceptions.WebDriverException:
                    continue
                except AssertionError:
                    continue
                break
            answer = driver.page_source
            while True:
                soup = Bs(answer, "html.parser")
                products = soup.find_all("div", {"class": "product container"})
                links = list(map(lambda x: x.find("a").get("href"), products))
                [extract_data(link, data_list) for link in links]
                while True:
                    try:
                        WebDriverWait(driver, 10)
                        old_value = driver.find_element_by_class_name('productName').text
                    except exceptions.WebDriverException:
                        continue
                    break
                try:
                    driver.find_element_by_id("_ctPgrp_pgtnni").click()
                except exceptions.WebDriverException:
                    break
                while True:
                    try:
                        WebDriverWait(driver, 10)
                        new_value = driver.find_element_by_class_name('productName').text
                        assert new_value != old_value
                    except exceptions.WebDriverException:
                        continue
                    except AssertionError:
                        continue
                    break
                answer = driver.page_source
                continue
    driver.close()
    return time.time() - t

def transform(data_list):
    t = time.time()
    for product in data_list:
        for i in product.keys():
            product[i] = re.sub('<.*>| {2,}|szczegóły|[^ ,./=\-\w]', "", product[i], re.M)
    data = list(map(lambda x: Tire(x), data_list))
    data = list(set(data))
    return [data, time.time() - t]

def load(data, date):
    t = time.time()
    for obj in data:
        p = Products(ProductID=obj.ID,
                     Manufacturer=obj.manufacturer,
                     Name=obj.name,
                     Price=obj.price,
                     Car_type=obj.car_type,
                     season=obj.season,
                     size=obj.size,
                     approval=obj.approval,
                     speed_index=obj.speed_index,
                     weight_index=obj.weight_index,
                     sound_index=obj.sound_index,
                     production_year=obj.production_year,
                     guaranty=obj.guaranty,
                     other_info=obj.other_info,
                     pub_date=date)
        p.save()
    return time.time() - t