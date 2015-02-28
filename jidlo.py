#!/usr/bin/python

import calendar
from datetime import datetime, timedelta
from lxml import etree
import locale
import re
from urllib.request import urlopen, build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar

from gi.repository import Gtk, WebKit
from jinja2 import Template

ICONS_DIR = '/usr/share/pixmaps/pidgin/emotes/default/'
APP_TITLE = 'Menu'
APP_ICON = '%s/pizza.png' % ICONS_DIR

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
    menus = tree.xpath('//table[@class="tblDen"]')
    meals = []
    for menu in menus:
        soups = set(menu.xpath(
            './/td[text() = "Polévka"]/following-sibling::td/text()'))
        mains = menu.xpath(
            './/td[text() = "Hlavní chod"]/following-sibling::td/b/text()')
        prices = map(kaskada_price,
                     menu.xpath('.//td[@class="cena"]/b/text()')[:-1:2])
        desserts = set(menu.xpath('''
            .//td[text() = "Dezert" or text() = "Kompot" or text() = "Salát"]
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

class Tray(Gtk.StatusIcon):
    def __init__(self):
        Gtk.StatusIcon.__init__(self)
        self.set_tooltip_text(APP_TITLE)
        self.set_from_file(APP_ICON)
        self.connect('popup-menu', self.menu)
        self.connect('activate', self.details)

        self.menu = Gtk.Menu()

        fetchItem = Gtk.MenuItem('Fetch')
        self.menu.append(fetchItem)
        fetchItem.connect('activate', self.fetch)

        quitItem = Gtk.MenuItem('Quit')
        self.menu.append(quitItem)
        quitItem.connect('activate', Gtk.main_quit)

        self.window = Window()

    def menu(self, icon, button, time):
        self.menu.show_all()
        self.menu.popup(None, None, None, None, button, time)

    def fetch(self, widget=None):
        self.window.push(tryFetchAll())

    def details(self, widget=None):
        if self.window.get_property('visible'):
            self.window.hide()
        else:
            self.window.show_all()

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=APP_TITLE)
        self.set_default_icon_from_file(APP_ICON)
        self.connect('delete-event', lambda w, e: w.hide() or True)

        self.vbox = Gtk.VBox()
        self.add(self.vbox)

        self.buttons = Gtk.HBox()
        self.vbox.pack_start(self.buttons, False, False, 5)
        last_button = None
        for day in range(0, 5):
            button = Gtk.RadioButton(calendar.day_name[day], group=last_button)
            self.buttons.pack_start(button, True, True, 5)
            button.connect('toggled', self.day_chosen, day)
            button.set_mode(False)  # so it looks like a toggle button
            last_button = button

        scroll = Gtk.ScrolledWindow()
        self.vbox.pack_start(scroll, True, True, 0)

        self.view = WebKit.WebView()
        scroll.add(self.view)

    def push(self, restaurants):
        self.restaurants = restaurants
        buttons = self.buttons.get_children()
        try:
            buttons[datetime.today().weekday()].set_active(True)
        except IndexError:
            buttons[-1].set_active(True)

    def render_day(self, day):
        t = Template(HTML_TEMPLATE)
        html = t.render(restaurants=self.restaurants, day=day)
        self.view.load_html_string(html, '')

    def day_chosen(self, button, day):
        self.render_day(day)


if __name__ == "__main__":
    Tray().fetch()
    Gtk.main()
