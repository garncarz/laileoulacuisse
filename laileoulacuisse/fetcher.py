from abc import ABCMeta, abstractmethod
from urllib.request import build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar
from lxml import etree

class Fetcher(metaclass=ABCMeta):
    def __init__(self):
        self.cj = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cj))

    @abstractmethod
    def fetch(self):
        pass

    def urlopen(self, url):
        return self.opener.open(url)

    def urlopen_tree(self, url):
        response = self.urlopen(url)
        data = response.readall().decode('utf8').replace('\r\n', '')
        return etree.fromstring(data, parser=etree.HTMLParser())

    def dict_meals(self, meals):
        return list(map(lambda m: {'name': m}, list(meals)))

    def dict_meals_prices(self, meals, prices):
        return list(map(lambda m: {'name': m[0], 'price': m[1]},
                        zip(meals, prices)))
