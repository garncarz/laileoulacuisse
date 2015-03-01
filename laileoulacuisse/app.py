#!/usr/bin/env python3

import calendar
from datetime import datetime, timedelta
from gi.repository import Gtk, WebKit
import locale
import os
from pluginbase import PluginBase
from jinja2 import Template

ICONS_DIR = '/usr/share/pixmaps/pidgin/emotes/default/'
APP_TITLE = "Křidýlko nebo stehýnko"
APP_ICON = '%s/pizza.png' % ICONS_DIR

locale.setlocale(locale.LC_ALL, 'cs_CZ')

abs_path = lambda path: os.path.join(os.path.dirname(
    os.path.realpath(__file__)), path)
plugin_base = PluginBase(package='laileoulacuisse')
plugin_source = plugin_base.make_plugin_source(
    searchpath=[abs_path('./fetchers')])

fetchers = []
for plugin_name in plugin_source.list_plugins():
    plugin = plugin_source.load_plugin(plugin_name)
    fetchers += list(map(lambda f: getattr(plugin, f),
                         filter(lambda f: f.startswith('fetch'),
                                dir(plugin))))

def tryFetchAll():
    data = []
    for fetcher in fetchers:
        try:
            data += [fetcher()]
        except Exception as e:
            pass
    return data


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

        fetchItem = Gtk.MenuItem('Aktualizovat')
        self.menu.append(fetchItem)
        fetchItem.connect('activate', self.fetch)

        quitItem = Gtk.MenuItem('Ukončit')
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
        self.maximize()
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
