from laileoulacuisse.fetcher import Fetcher

class JetSet(Fetcher):
    name = 'Jet Set'
    url = 'http://www.jetsetostrava.cz/denni-menu/'

    def fetch(self):
        tree = self.urlopen_tree(self.url)
        # TODO missing days
        menus = tree.xpath('//div[@class="container"]'
                           '//div[@class="page-outer"]'
                           '/h2/following-sibling::p[1]')
        meals = []
        for menu in menus:
            lines = menu.xpath('string(.)').split('\n')
            soup = [lines[0]]
            mains = [self.dict_meal(meal) for meal in lines[1:]]
            meals += [self.dict_meals(soup) + mains]
        return meals
