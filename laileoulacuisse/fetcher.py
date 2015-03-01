from urllib.request import build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar
from lxml import etree

cj = CookieJar()
opener = build_opener(HTTPCookieProcessor(cj))

def urlopen(url):
    return opener.open(url)

def urlopen_tree(url):
    response = urlopen(url)
    data = response.readall().decode('utf8').replace('\r\n', '')
    return etree.fromstring(data, parser=etree.HTMLParser())

def dict_meals(meals):
    return list(map(lambda m: {'name': m}, list(meals)))

def dict_meals_prices(meals, prices):
    return list(map(lambda m: {'name': m[0], 'price': m[1]},
                    zip(meals, prices)))
