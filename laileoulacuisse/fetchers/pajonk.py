from dateutil.parser import parse as parse_datetime

from laileoulacuisse.fetcher import Fetcher

class Pajonk(Fetcher):
    name = 'Pajonk'
    url = 'http://vinorestaurant.cz/den.php'

    def fetch(self):
        tree = self.urlopen_tree(self.url)
        meals = [[]] * 5

        menu = tree.xpath(
            '//td[@align="left"]//center[.//text() = "Týdenní menu"]')[0]
        day = parse_datetime(
            menu.xpath('.//p[position() = 2]/b/font/text()')[0].split()[1]
        ).weekday()
        day_meals = menu.xpath('.//span/text()')
        meals[day] = list(map(self.dict_meal, day_meals))

        return meals
