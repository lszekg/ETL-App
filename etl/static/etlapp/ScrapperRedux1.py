import time
import requests
from bs4 import BeautifulSoup as Bs
from selenium import webdriver
import re

from django.db import models
from .models import Products

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
        string = "<<\n"
        for attr, value in self.__dict__.items():
            string += (attr + " : " + value + "\n")
        string += ">>"
        return string

def get_tire_widths():
    url = "https://www.oponeo.pl/wybierz-opony/"
    r = requests.get(url)
    s = Bs(r.content, "html.parser")
    widths = list(
        map(lambda x: x.get("value"), (s.find("select", {"name": "_ctTS_ddlDimWidth"}).find_all("option"))))
    widths.pop(0)
    return widths

def extract_data(link, data_list):
    raw_html = requests.get("https://www.oponeo.pl" + link).content
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
    link_width = re.sub("\.", "-", width)
    driver = webdriver.Chrome('/home/sqrtek/Pobrane/chromedriver')
    main_address = "https://www.oponeo.pl/wybierz-opony/"
    driver.get(main_address)
    json = {"productKindId": 2, "vehicleKind": 1, "tireWidth": width, "producersIDs": None, "seasonID": 0,
            "isTireOnOponeoWarehouse": False}
    address = "https://www.oponeo.pl/WS/ShopService.svc/GetTireRatios"
    ratios = requests.post(address, json=json).json()["d"]
    address = "https://www.oponeo.pl/WS/ShopService.svc/GetTireDiameters"
    for ratio in ratios:
        link_ratio = re.sub("\.", "-", ratio)
        json["tireRatio"] = ratio
        diameters = requests.post(address, json=json).json()["d"]
        for diameter in diameters:
            link_diameter = re.sub("\.", "-", diameter)
            sub_address = main_address + "r=1/" + link_width
            if ratio == "-" or ratio == "0":
                sub_address += "-r" + link_diameter + "/"
            else:
                sub_address += "-" + link_ratio + "-r" + link_diameter + "/"
            if width == "37" and ratio == "12.50" and diameter == "16":
                sub_address = main_address  + "r=1/37-12-50-16"
            driver.get(sub_address)
            answer = requests.get(sub_address).content
            while True:
                soup = Bs(answer, "html.parser")
                products = soup.find_all("div", {"class": "product container"})
                links = list(map(lambda x: x.find("a").get("href"), products))
                [extract_data(link, data_list) for link in links]
                if soup.find("a", {"id": "_ctPgrp_pgtnni"}) is not None:
                    driver.get(sub_address)
                    driver.execute_script("javascript:__doPostBack('_ctPgrp_pgtnni','')")
                    answer = driver.page_source
                else:
                    driver.execute_script("javascript:__doPostBack('_ctPgrp_pgtffi','')")
                    break
    driver.close()
    return time.time() - t

def transform(data_list):
    t = time.time()
    data = list()
    for product in data_list:
        for i in product.keys():
            product[i] = re.sub('<.*>| {2,}|szczegóły|[^ ,./=\-\w]', "", product[i], re.M)
    for i in range(len(data_list)-1):
        for j in range(len(data_list)-1):
            if data_list[i] == data_list[j] and i != j:
                data.append(j)
    map(lambda x: data_list.pop(x), data)
    return [list(map(lambda x: Tire(x), data_list)), time.time() - t]


def load(data):
    for obj in data[0]:
        p = Products(ProductID=obj.ID, Manufacturer=obj.manufacturer, Name=obj.name, Price=obj.price, Car_type=obj.car_type, season=obj.season, approval=obj.approval, speed_index=obj.speed_index, weight_index=obj.weight_index, sound_index=obj.sound_index, production_year=obj.production_year, guaranty=obj.guaranty, other_info=obj.other_info)
        p.save()

tire_widths = get_tire_widths()
tires = list()
# Here query user for a desired width. Widths are contained within tire_widths list. They are in string format.
width = tire_widths[16]
print(width)
# Extract takes empty list to put records in, and width that is to be searched for. Returns time it took to complete the
# query. The list itself, as a mutable object is filled with records, without the need for explicitly returning it.
extract_time = extract(tires, width)
print("Extract ended. Parsed " + str(len(tires)) + " records, took " + str(int(extract_time/60)) + "min " + str(int(extract_time%60)) + "sec.")
# Transform again takes the list, this time filled with records, and transforms it into two-element list. Zeroth element
# contains the list of objects to be used in the load function, and the first element contains time the function took to
# complete.
data = transform(tires)
print("Transform ended. Prepared " + str(len(data[0])) + " objects, took " + str(int(data[1]/60)) + "min " + str(int(data[1]%60)) + "sec.")
#print(*data[0]['manufacturer'], sep="\n")
load(data)
print("Loading data to DjangoDB ended.")
# You can try fiddling with it, but what is important:
# 1. Implement load() function, and etl() function combining three earlier functions into one.
# 2. Implement query for the user input regarding the desired tire width.
# 3. Implement function for browsing database, as well as function allowing to download whole or
#    elements of the database to users hard-drive in csv format.
# 4. Connect the frontend to the backend.
