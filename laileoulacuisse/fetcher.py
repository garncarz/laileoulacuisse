from abc import ABCMeta, abstractmethod
from urllib.request import build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar
from lxml import etree
import imp
import inspect
import os
from pluginbase import PluginBase

class Fetcher(metaclass=ABCMeta):
    def __init__(self):
        self.cj = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cj))

    @property
    def id(self):
        return self.__class__.__name__

    @abstractmethod
    def fetch(self):
        pass

    def urlopen(self, url):
        return self.opener.open(url)

    def urlopen_tree(self, url):
        response = self.urlopen(url)
        data = response.readall().decode('utf8').replace('\r\n', '')
        return etree.fromstring(data, parser=etree.HTMLParser())

    def not_upper(self, str):
        return str.capitalize() if str.isupper() else str

    def dict_meals(self, meals):
        return [{'name': self.not_upper(m)} for m in meals]

    def dict_meals_prices(self, meals, prices):
        prices = list(prices)
        return [{'name': self.not_upper(m), 'price': prices[i]}
                        if i < len(prices)
                        else {'name': self.not_upper(m)}
                    for i, m in enumerate(meals)]


abs_path = lambda path: os.path.join(os.path.dirname(
    os.path.realpath(__file__)), path)
plugin_base = PluginBase(package='fetchers')
plugin_source = plugin_base.make_plugin_source(
    searchpath=[abs_path('fetchers')])

def reload_fetchers():
    global fetchers
    fetchers = []
    for plugin_name in plugin_source.list_plugins():
        plugin = plugin_source.load_plugin(plugin_name)
        imp.reload(plugin)
        fetchers += map(lambda f: f[1](),
                        inspect.getmembers(
                            plugin,
                            lambda m: inspect.isclass(m) and
                                      issubclass(m, Fetcher) and
                                      not inspect.isabstract(m)))

def try_fetch_all(config):
    data, errors = [], []
    for fetcher in filter(lambda f: config.is_enabled(f), fetchers):
        try:
            data += [{'name': fetcher.name, 'meals': fetcher.fetch()}]
        except Exception as e:
            errors += [{'name': fetcher.name, 'error': e}]
    return (data, errors)
