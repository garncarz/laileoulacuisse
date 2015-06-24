from datetime import datetime
from jinja2 import Environment

from laileoulacuisse.app import config
from laileoulacuisse import fetcher

TEMPLATE = """
{% for rest in restaurants %}
{{ rest.name }}
===============
{% for meal in rest.meals[day] %}
{% if meal.price %}{{ meal.price }} {% endif %}{{ meal.name }}
{% endfor %}

{% endfor %}
"""

def run():
    fetcher.reload_fetchers()
    data, errors = fetcher.try_fetch_all(config)
    jinja = Environment(trim_blocks=True)
    t = jinja.from_string(TEMPLATE)
    text = t.render(restaurants=data, day=datetime.today().weekday())
    print(text)
