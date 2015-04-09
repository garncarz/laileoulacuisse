import re

from laileoulacuisse.fetcher import Fetcher

class Kaskada(Fetcher):
    def fetch(self):
        def price(price):
            m = re.match(r'.*?(?P<wo>\d+ Kč).*?(?P<w>\d+ Kč)', price)
            return price if not m \
              else '%s / %s' % (m.group('wo'), m.group('w'))

        self.urlopen(self.url)
        tree = self.urlopen_tree(
                    'http://www.kaskadarestaurant.cz/denni_nabidky')
        menus = tree.xpath('//table[@class="tblDen"]')
        meals = []
        for menu in menus:
            soups = set(menu.xpath(
                './/td[text() = "Polévka"]/following-sibling::td/text()'))
            mains = menu.xpath(
                './/td[text() = "Hlavní chod"]/following-sibling::td/b/text()')
            prices = map(price, menu.xpath('.//td[@class="cena"]/b/text()') \
                                    [:-1:2])
            desserts = set(menu.xpath('''
                .//td[text() = "Dezert" or text() = "Kompot" or
                        text() = "Salát"]
                    /following-sibling::td/text()
                '''))
            meals += [self.dict_meals(soups) +
                      self.dict_meals_prices(mains, prices) +
                      self.dict_meals(desserts)]
        return meals

class Futurum(Kaskada):
    name = 'Kaskáda – Futurum'
    url = 'http://www.kaskadarestaurant.cz/Ostrava'

class NK(Kaskada):
    name = 'Kaskáda – Nová Karolina'
    url = 'http://www.kaskadarestaurant.cz/Ostrava_Nova_Karolina'
