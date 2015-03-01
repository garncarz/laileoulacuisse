import calendar
import re

from fetcher import urlopen_tree

def fetch():
    def dict_meal(meal):
        m = re.match(r'(?P<name>.*) (?P<price>\d+),-', meal)
        return {'name': meal} if not m \
          else {'name': m.group('name'),
                'price': '%s Kč' % m.group('price')}

    tree = urlopen_tree('http://vinorestaurant.cz/den.php')
    meals = [[]] * 5

    menu = tree.xpath(
        '//td[@align="left"]//center[.//text() = "Týdenní menu"]')[0]
    day_name = menu.xpath('.//p[position() = 2]/b/font/text()')[0].split(' ')[0]
    day = next(i for i, v in enumerate(calendar.day_name) if v == day_name)
    day_meals = menu.xpath('.//span/text()')
    meals[day] = list(map(dict_meal, day_meals))

    return {'name': 'Pajonk', 'meals': meals}
