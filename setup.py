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
    'install_requires': [],
    'test_requires': [],
    'packages': ['django_project', 'follow'],
    'scripts': [],
    'name': 'django-project',
}

setup(**config)
