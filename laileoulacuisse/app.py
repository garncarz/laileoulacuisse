#!/usr/bin/env python3

import calendar
from datetime import datetime, timedelta
from gi.repository import Gtk, WebKit
import locale
import os
from jinja2 import Template

import fetcher

ICONS_DIR = '/usr/share/pixmaps/pidgin/emotes/default/'
APP_TITLE = "Křidýlko nebo stehýnko"
APP_ICON = os.path.join(ICONS_DIR, 'pizza.png')

locale.setlocale(locale.LC_ALL, 'cs_CZ')

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
    options_dialog = None

    def __init__(self):
        Gtk.StatusIcon.__init__(self)
        self.set_tooltip_text(APP_TITLE)
        self.set_from_file(APP_ICON)
        self.connect('popup-menu', self.menu)
        self.connect('activate', self.details)

        self.menu = Gtk.Menu()

        updateItem = Gtk.MenuItem('Aktualizovat')
        self.menu.append(updateItem)
        updateItem.connect('activate', self.update)

        optionsItem = Gtk.MenuItem('Možnosti')
        self.menu.append(optionsItem)
        optionsItem.connect('activate', self.edit_options)

        quitItem = Gtk.MenuItem('Ukončit')
        self.menu.append(quitItem)
        quitItem.connect('activate', Gtk.main_quit)

        self.window = Window()

    def menu(self, icon, button, time):
        self.menu.show_all()
        self.menu.popup(None, None, None, None, button, time)

    def update(self, widget=None, reload_fetchers=True):
        if reload_fetchers:
            fetcher.reload_fetchers()
            self.options_dialog = None
        data, errors = fetcher.try_fetch_all()
        if errors:
            print(errors)
        self.window.push(data)

    def edit_options(self, widget=None):
        if not self.options_dialog:
            self.options_dialog = OptionsDialog()
        response = self.options_dialog.run()
        self.options_dialog.hide()
        if response == Gtk.ResponseType.OK:
            self.options_dialog.apply_states()
            self.update(reload_fetchers=False)

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
            if datetime.today().weekday() == 0:
                buttons[0].toggled()  # unfortunately needs to be done
        except IndexError:
            buttons[-1].set_active(True)

    def render_day(self, day):
        t = Template(HTML_TEMPLATE)
        html = t.render(restaurants=self.restaurants, day=day)
        self.view.load_html_string(html, '')

    def day_chosen(self, button, day):
        self.render_day(day)

class OptionsDialog(Gtk.Dialog):
    def __init__(self):
        Gtk.Dialog.__init__(self, 'Možnosti', None, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = self.get_content_area()

        self.checks = {}
        for f in fetcher.fetchers:
            check = self.checks[f] = Gtk.CheckButton(f.name)
            check.set_active(f.enabled)
            box.add(check)

        self.show_all()

    def apply_states(self):
        for f in fetcher.fetchers:
            f.enabled = self.checks[f].get_active()


if __name__ == "__main__":
    Tray().update()
    Gtk.main()
