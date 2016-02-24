from models import Country, Footballer

commands = [
        {'func': Country.objects.all, 'kwargs': {}},
        {'func': Country.objects.get, 'kwargs': {}},
        {'func': Country.objects.first, 'kwargs': {}},
        {'func': Country.objects.last, 'kwargs': {}},
        {'func': Country.objects.filter, 'kwargs': {}}
            ]