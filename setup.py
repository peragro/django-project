try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Django app for project management',
    'author': 'sueastside',
    'url': 'https://github.com/sueastside/django-project',
    'download_url': 'https://github.com/sueastside/django-project',
    'author_email': 'No, thanks',
    'version': '0.1',
    'test_suite': 'tests.suite',
    'install_requires': ['django==1.6.7', 'djangorestframework==2.3.14', 'django-autoslug==1.7.2', 'django-reversion==1.8.1', 'south==1.0', 'pytz==2014.4', 'django-notifications-hq==0.8.0', 'django-follow==0.6.1', 'django-filter==0.7', 'drf-extensions==0.2.5', 'django-cors-headers==0.12', 'django-smart-selects==1.0.9'],
    'test_requires': [],
    'packages': ['django_project'],
    'scripts': [],
    'name': 'django-project',
}

setup(**config)

