from PIL import Image
import requests
from io import BytesIO
from StringIO import StringIO
import requests
from lxml import html
from bs4 import BeautifulSoup
import json

# https://github.com/ysavary/WindMobile2-Server/blob/master/providers/slf.py

sion = {"pixels": [453, 716], "ch": [2592609.3, 1118406.2]}
aarau = {"pixels": [660, 209], "ch": [2645879.6, 1249326.0]}


def get_coefs(p_1, p_2, ch_1, ch_2):
    a = (p_2 - p_1) / (ch_2 - ch_1)
    b = p_1 - ch_1 * a
    return a, b


class SLF:
    def __init__(self):
        pass

        self.xcoefs = get_coefs(p_1=sion["pixels"][0], p_2=aarau["pixels"][0], ch_1=sion["ch"][0], ch_2=aarau["ch"][0])
        self.ycoefs = get_coefs(p_1=sion["pixels"][1], p_2=aarau["pixels"][1], ch_1=sion["ch"][1], ch_2=aarau["ch"][1])

        self.url_map = r"https://www.slf.ch/fragment/img/gk/gk_symbol_2.png"

        r = requests.get(r"https://www.slf.ch/fr/bulletin-davalanches-et-situation-nivologique.html")
        soup = BeautifulSoup(r.content, "html.parser")
        self.soup = soup
        self.imgs_district = {}
        self.forecasts = {}
        self.fetch()
        self.date = self.get_date()

    def get_date(self):
        return  self.soup.find_all(attrs={"class": "date-aktuell"})[0].text.replace("\n", "").replace("\t", "")

    def fetch(self):
        self.fetch_districts()
        self.fetch_forecasts()

    def get_measurements(self):
        url = "https://odb.slf.ch/odb/api/v1/spatial"

    def get_bulletin_images(self):
        url = "https://www.slf.ch/avalanche/bulletin/de/gk1_8943003_a_0.png"

    def get_places_png(self):
        url = r"https://www.slf.ch/fragment/img/gk/gk_symbol_2.png"

    def get_pixels(self, x, y):
        p_x = x * self.xcoefs[0] + self.xcoefs[1]
        p_y = y * self.ycoefs[0] + self.ycoefs[1]
        return (p_x, p_y)

    def fetch_forecasts(self):
        for a in self.soup.find_all(class_="forecast-dialog"):
            district = a.attrs["data-dstid"]
            danger = None
            content = None
            for b in a.find_all(class_="dangerlevel"):
                danger = b.text
            for b in a.find_all(class_="content"):
                content = b.text
            self.forecasts[district] = {"dangerlevel": danger, "content": content}

    def fetch_districts(self):
        self.imgs_district = {}
        for a in self.soup.find_all(attrs={"class": "gk-map"}):
            for district in json.loads(a.attrs["data-districts"])["dstids"]:

                img = self.get_district_img(district)
                self.imgs_district[district] = img

    def get_district_img_url(self, id):
        for a in self.soup.find_all(attrs={"data-id": id}):
            _url = a.find_all(attrs={"class": "gk-l-z2"})[0].attrs["src"]
        return u"https://www.slf.ch/" + _url

    def get_district_img(self, id):
        url = self.get_district_img_url(id)
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img

    def get_danger_by_coord(self, x, y):
        try:
            ps = self.get_pixels(x, y)

            for key in self.imgs_district.keys():
                if self.imgs_district[key].getpixel(ps) > 0:
                    return self.forecasts[key]
        except:
            pass
