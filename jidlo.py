#!/usr/bin/python

from datetime import datetime, timedelta
from lxml import etree
import locale
import re
from urllib.request import urlopen, build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar

from gi.repository import Gtk, WebKit
from jinja2 import Template

ICONS_DIR = '/usr/share/pixmaps/pidgin/emotes/default/'

locale.setlocale(locale.LC_ALL, 'cs_CZ')

##############################################################################
# FETCHING:

cj = CookieJar()
opener = build_opener(HTTPCookieProcessor(cj))

def fetch_tree(url):
    response = opener.open(url)
    data = response.readall().decode('utf8').replace('\r\n', '')
    return etree.fromstring(data, parser=etree.HTMLParser())

def kaskada_price(price):
    m = re.match(r'.* (?P<wo>\d+ Kč).* (?P<w>\d+ Kč)', price)
    if not m:
        return price
    return '%s / %s' % (m.group('wo'), m.group('w'))

def meals_dict(meals):
    return list(map(lambda m: {'name': m}, list(meals)))

def merge_meals_prices(meals, prices):
    return list(map(lambda m: {'name': m[0], 'price': m[1]},
                    zip(meals, prices)))

def kaskada(branch_tag, branch_name):
    opener.open('http://www.kaskadarestaurant.cz/%s' % branch_tag)
    tree = fetch_tree('http://www.kaskadarestaurant.cz/denni_nabidky')
    menus = tree.xpath('//div[@class="menuDen"]/following-sibling::table')
    meals = []
    for menu in menus:
        soups = set(menu.xpath(
            './/td[text() = "Polévka"]/following-sibling::td/text()'))
        mains = menu.xpath(
            './/td[text() = "Hlavní chod"]/following-sibling::td/b/text()')
        prices = map(kaskada_price,
                     menu.xpath('.//td[@class="cena"]/b/text()')[:-1:2])
        desserts = set(menu.xpath('''
            .//td[text() = "Dezert" or text() = "Kompot"]
                /following-sibling::td/text()
            '''))
        meals += [meals_dict(soups) + merge_meals_prices(mains, prices) +
                  meals_dict(desserts)]
    return {
        'name': branch_name,
        'meals': meals,
        }

def kaskadaF():
    return kaskada('Ostrava', 'Kaskáda – Futurum')

def kaskadaNK():
    return kaskada('Ostrava_Nova_Karolina', 'Kaskáda – Nová Karolina')

def jetset():
    tree = fetch_tree('http://www.jetsetostrava.cz/tydenni-nabidka')
    menus = tree.xpath('//div[@class="day"]')
    meals = []
    for menu in menus:
        soup = menu.xpath('p[1]/text()')
        mains = menu.xpath('p[position()>1]/text()')
        prices = menu.xpath('p[position()>1]/strong/text()')
        meals += [meals_dict(soup) + merge_meals_prices(mains, prices)]
    return {
        'name': 'Jet Set',
        'meals': meals,
        }

def tryFetchAll():
    data = []
    for fetcher in [jetset, kaskadaNK, kaskadaF]:
        try:
            data += [fetcher()]
        except:
            pass
    return data


##############################################################################
# GUI:

HTML_TEMPLATE = """
{% for rest in restaurants %}
    <h3>{{ rest.name }}</h3>
    <table style="width: 100%">
    {% for meal in rest.meals[day] %}
        <tr>
            <td>{{ meal.name }}
            <td style="text-align: right; white-space: nowrap;">{{ meal.price }}
    {% endfor %}
    </table>
{% endfor %}
"""

class Tray:
    def __init__(self):
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_tooltip_text('Jídlo')
        self.statusicon.set_from_file('%s/pizza.png' % ICONS_DIR)
        self.statusicon.connect('popup-menu', self.menu)
        self.statusicon.connect('activate', self.details)

        self.menu = Gtk.Menu()

        fetchItem = Gtk.MenuItem()
        self.menu.append(fetchItem)
        fetchItem.set_label('Fetch')
        fetchItem.connect('activate', self.fetch)

        quitItem = Gtk.MenuItem()
        self.menu.append(quitItem)
        quitItem.set_label('Quit')
        quitItem.connect('activate', Gtk.main_quit)

        self.fetch()

    def menu(self, icon, button, time):
        self.menu.show_all()
        self.menu.popup(None, None, None, None, button, time)

    def fetch(self, widget=None):
        self.restaurants = tryFetchAll()

    def details(self, widget=None):
        dialog = Gtk.Dialog('Menu', None, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_size_request(1000, 650)

        scroll = Gtk.ScrolledWindow()
        dialog.vbox.pack_start(scroll, True, True, 0)

        view = WebKit.WebView()
        scroll.add(view)

        t = Template(HTML_TEMPLATE)
        html = t.render(restaurants=self.restaurants, day=3)  # example
        view.load_html_string(html, '')

        dialog.show_all()
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    Tray()
    Gtk.main()
