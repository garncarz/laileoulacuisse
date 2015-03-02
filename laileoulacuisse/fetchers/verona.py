from datetime import datetime, timedelta
from lxml import etree
import os
import re
import subprocess
import tempfile

from laileoulacuisse.fetcher import Fetcher

class Verona(Fetcher):
    name = 'Verona'

    def fetch(self):
        def day_meals(meal):
            return [{'name': meal, 'price': price},
                    {'name': whole_week_meal, 'price': price}]

        response = self.urlopen(
                    self.urlopen_tree('http://verona.pribor.cz') \
                        .xpath('//a[contains(., "Denní menu")]/@href')[0]
                    )
        tmpfile = tempfile.NamedTemporaryFile()
        tmpfile.write(response.readall())

        env = dict(os.environ)
        env['LANG'] = 'cs_CZ.UTF-8'
        p = subprocess.Popen(['antiword', '-x', 'db', tmpfile.name],
                             stdout=subprocess.PIPE,
                             env=env)
        out, _ = p.communicate()
        tmpfile.close()

        first_day = datetime.now() - timedelta(days=datetime.today().weekday())
        week = [first_day + timedelta(days=days) for days in range(5)]

        tree = etree.fromstring(out)
        price = re.search(
            r'.*?(?P<price>\d+ Kč).*',
            tree.xpath('//para/emphasis[contains(., "Kč")]/text()')[0]) \
            .group('price')
        menu = tree.xpath('//sect1[./para[contains(., "%s")]]'
                            % first_day.strftime('%-d.%-m.'))[0]
        whole_week_meal = ''.join(
            menu.xpath(
                './para[position() > 5]/descendant-or-self::*/text()'
            )).strip()
        meals = []
        for day in week:
            meal = re.split('–|-', ''.join(
                menu.xpath(
                    './para[contains(., "%s")]/descendant-or-self::*/text()'
                        % day.strftime('%-d.%-m.')
                )), 1)[-1].strip()
            meals += [day_meals(meal)]

        return meals
