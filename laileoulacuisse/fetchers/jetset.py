from laileoulacuisse.fetcher import Fetcher

class JetSet(Fetcher):
    name = 'Jet Set'

    def fetch(self):
        tree = self.urlopen_tree('http://www.jetsetostrava.cz/tydenni-nabidka')
        menus = tree.xpath('//div[@class="day"]')
        meals = []
        for menu in menus:
            soup = menu.xpath('p[1]/text()')
            mains = menu.xpath('p[position()>1]/text()')
            prices = menu.xpath('p[position()>1]/strong/text()')
            meals += [self.dict_meals(soup) +
                      self.dict_meals_prices(mains, prices)]
        return meals
