import configparser
import gettext
import os

APP_NAME = 'laileoulacuisse'
CONFIG_FILE = os.path.expanduser('~/.%s.conf' % APP_NAME)

abs_path = lambda path: os.path.join(os.path.dirname(
    os.path.realpath(os.path.expanduser(__file__))), path)

gettext.install(APP_NAME)
for locale_dir in ['../build/mo', '~/.local/share/locale']:
    dir = abs_path(locale_dir)
    if os.path.isdir(dir):
        gettext.install(APP_NAME, dir)
        break

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
        return True if self['restaurants'].getboolean(fetcher.id) \
               else False

    def set_enabled(self, fetcher, enabled):
        self['restaurants'][fetcher.id] = '%d' % enabled

config = Config()
config.load()


def run():
    if 'DISPLAY' in os.environ:
        from laileoulacuisse import gtk
        gtk.run()
    else:
        from laileoulacuisse import console
        console.run()
