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
    'install_requires': ['django== 1.6.7', 'djangorestframework', 'django-autoslug', 'django-reversion', 'south', 'pytz', 'django-notifications-hq', 'django-follow', 'django-filter', 'drf-extensions', 'django-cors-headers', 'django-smart-selects'],
    'test_requires': [],
    'packages': ['django_project'],
    'scripts': [],
    'name': 'django-project',
}

setup(**config)

