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

def tryFetchAll():
    data, errors = [], []
    for fetcher in fetchers:
        try:
            data += [{'name': fetcher.name, 'meals': fetcher.fetch()}]
        except Exception as e:
            errors += [{'name': fetcher.name, 'error': e}]
    return (data, errors)
