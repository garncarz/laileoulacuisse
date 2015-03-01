import re

from fetcher import urlopen, urlopen_tree, dict_meals, dict_meals_prices

def _fetch(branch_tag, branch_name):
    def price(price):
        m = re.match(r'.*?(?P<wo>\d+ Kč).*?(?P<w>\d+ Kč)', price)
        return price if not m \
          else '%s / %s' % (m.group('wo'), m.group('w'))

    urlopen('http://www.kaskadarestaurant.cz/%s' % branch_tag)
    tree = urlopen_tree('http://www.kaskadarestaurant.cz/denni_nabidky')
    menus = tree.xpath('//table[@class="tblDen"]')
    meals = []
    for menu in menus:
        soups = set(menu.xpath(
            './/td[text() = "Polévka"]/following-sibling::td/text()'))
        mains = menu.xpath(
            './/td[text() = "Hlavní chod"]/following-sibling::td/b/text()')
        prices = map(price, menu.xpath('.//td[@class="cena"]/b/text()')[:-1:2])
        desserts = set(menu.xpath('''
            .//td[text() = "Dezert" or text() = "Kompot" or text() = "Salát"]
                /following-sibling::td/text()
            '''))
        meals += [dict_meals(soups) + dict_meals_prices(mains, prices) +
                  dict_meals(desserts)]
    return {'name': branch_name, 'meals': meals}

def fetch_f():
    return _fetch('Ostrava', 'Kaskáda – Futurum')

def fetch_nk():
    return _fetch('Ostrava_Nova_Karolina', 'Kaskáda – Nová Karolina')
