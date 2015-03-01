from fetcher import urlopen_tree, dict_meals, dict_meals_prices

def fetch():
    tree = urlopen_tree('http://www.jetsetostrava.cz/tydenni-nabidka')
    menus = tree.xpath('//div[@class="day"]')
    meals = []
    for menu in menus:
        soup = menu.xpath('p[1]/text()')
        mains = menu.xpath('p[position()>1]/text()')
        prices = menu.xpath('p[position()>1]/strong/text()')
        meals += [dict_meals(soup) + dict_meals_prices(mains, prices)]
    return {'name': 'Jet Set', 'meals': meals}
