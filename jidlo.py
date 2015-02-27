#!/usr/bin/python

from datetime import datetime
from lxml import etree
import locale
import re
from urllib.request import urlopen, build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar

from gi.repository import Gtk, WebKit
from django.template import Context, Template
import django.conf

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

def merge_meals_prices(meals, prices):
    return map(lambda m: {'name': m[0], 'price': m[1]},
               zip(meals, prices))

def kaskada(branch_tag, branch_name):
    opener.open('http://www.kaskadarestaurant.cz/%s' % branch_tag)
    tree = fetch_tree('http://www.kaskadarestaurant.cz/denni_nabidky')
    menu = tree.xpath(
        '//div[@class="menuDen" and text()="%s"]/following-sibling::table'
            % datetime.now().strftime('%A').upper()
        )[0]
    soup = menu.xpath(
        './/td[text() = "Polévka"]/following-sibling::td/text()')[0]
    meals = menu.xpath(
        './/td[text() = "Hlavní chod"]/following-sibling::td/b/text()')
    prices = map(kaskada_price,
               menu.xpath('.//td[@class="cena"]/b/text()')[:-1:2])
    desserts = set(menu.xpath(
        './/td[text() = "Dezert"]/following-sibling::td/text()'))
    return {
        'name': branch_name,
        'soup': soup,
        'meals': merge_meals_prices(meals, prices),
        'desserts': desserts,
        }

def kaskadaF():
    return kaskada('Ostrava', 'Kaskáda – Futurum')

def kaskadaNK():
    return kaskada('Ostrava_Nova_Karolina', 'Kaskáda – Nová Karolina')

def jetset():
    tree = fetch_tree('http://www.jetsetostrava.cz/#poledni-nabidka')
    menu = tree.xpath('//div[@id="poledni-nabidka"]')[0]
    soup = menu.xpath('p[1]/text()')[0]
    meals = menu.xpath('p[position()>1]/text()')
    prices = menu.xpath('p[position()>1]/span[@class="cena"]/text()')

    return {
        'name': 'Jet Set',
        'soup': soup,
        'meals': merge_meals_prices(meals, prices),
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

django.conf.settings.configure()

HTML_TEMPLATE = """
{% for rest in restaurants %}
    <h3>{{ rest.name }}</h3>
    <table style="width: 100%">
        <tr>
            <td>{{ rest.soup }}
    {% for meal in rest.meals %}
        <tr>
            <td>{{ meal.name }}
            <td style="text-align: right">{{ meal.price }}
    {% endfor %}
    {% for des in rest.desserts %}
        <tr>
            <td>{{ des }}
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
        dialog = Gtk.Dialog("Menu", None, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_size_request(1000, 500)

        scroll = Gtk.ScrolledWindow()
        dialog.vbox.pack_start(scroll, True, True, 0)

        view = WebKit.WebView()
        scroll.add(view)

        t = Template(HTML_TEMPLATE)
        c = Context({"restaurants": self.restaurants})
        view.load_html_string(t.render(c), '')

        dialog.show_all()
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    Tray()
    Gtk.main()
