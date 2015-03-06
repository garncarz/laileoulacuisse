import calendar
import configparser
from datetime import datetime, timedelta
import gettext
from gi.repository import Gtk, GLib, WebKit
import os
from jinja2 import Template

from laileoulacuisse import fetcher

APP_NAME = 'laileoulacuisse'
CONFIG_FILE = os.path.expanduser('~/.%s.conf' % APP_NAME)

icon_loader = Gtk.IconTheme.get_default()
icon_loader.append_search_path('data')
try:
    APP_ICON = icon_loader.load_icon(APP_NAME, 24, 0)
except GLib.GError:
    APP_ICON = icon_loader.load_icon('default', 24, 0)

gettext.install(APP_NAME)
for locale_dir in ['../build/mo', '~/.local/share/locale']:
    dir = fetcher.abs_path(os.path.expanduser(locale_dir))
    if os.path.isdir(dir):
        gettext.install(APP_NAME, dir)
        break

APP_TITLE = _('The Wing or the Thigh')

class Config(configparser.ConfigParser):
    def __init__(self):
        configparser.ConfigParser.__init__(self)
        self['restaurants'] = {}

    def load(self):
        self.read(CONFIG_FILE)

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            self.write(f)

    def is_enabled(self, fetcher):
        return True if self['restaurants'].getboolean(fetcher.id) else False

    def set_enabled(self, fetcher, enabled):
        self['restaurants'][fetcher.id] = '%d' % enabled

config = Config()
config.load()


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
        self.set_from_gicon(APP_ICON)
        self.connect('popup-menu', self.menu)
        self.connect('activate', self.details)

        self.menu = Gtk.Menu()

        updateItem = Gtk.MenuItem(_('Update'))
        self.menu.append(updateItem)
        updateItem.connect('activate', self.update)

        optionsItem = Gtk.MenuItem(_('Options'))
        self.menu.append(optionsItem)
        optionsItem.connect('activate', self.edit_options)

        quitItem = Gtk.MenuItem(_('Quit'))
        self.menu.append(quitItem)
        quitItem.connect('activate', Gtk.main_quit)

        self.window = Window()

    def menu(self, icon, button, time):
        self.menu.show_all()
        self.menu.popup(None, None, None, None, button, time)

    def update(self, widget=None, reload_fetchers=True):
        if reload_fetchers:
            fetcher.reload_fetchers()
        data, errors = fetcher.try_fetch_all(config)
        if errors:
            print(errors)
        self.window.push(data)

    def edit_options(self, widget=None):
        dialog = OptionsDialog()
        if dialog.run() == Gtk.ResponseType.OK:
            dialog.save()
            self.update(reload_fetchers=False)
        dialog.destroy()

    def details(self, widget=None):
        if self.window.get_property('visible'):
            self.window.hide()
        else:
            self.window.show_all()

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=APP_TITLE)
        self.set_default_icon(APP_ICON)
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
        today = datetime.today().weekday()
        try:
            button = buttons[today]
        except IndexError:
            button = buttons[-1]
        if button.get_active():
            self.render_day(today)  # manual refresh
        else:
            button.set_active(True)  # automatic refresh

    def render_day(self, day):
        t = Template(HTML_TEMPLATE)
        html = t.render(restaurants=self.restaurants, day=day)
        self.view.load_html_string(html, '')

    def day_chosen(self, button, day):
        self.render_day(day)

class OptionsDialog(Gtk.Dialog):
    def __init__(self):
        Gtk.Dialog.__init__(self, _('Options'), None, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = self.get_content_area()

        self.checks = {}
        for f in fetcher.fetchers:
            check = self.checks[f] = Gtk.CheckButton(f.name)
            check.set_active(config.is_enabled(f))
            box.add(check)

        self.show_all()

    def save(self):
        for f in fetcher.fetchers:
            config.set_enabled(f, self.checks[f].get_active())
        config.save()


def run():
    Tray().update()
    Gtk.main()
