from setuptools import setup, find_packages

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
    'packages': find_packages(exclude=['example_project']),
    'scripts': [],
    'name': 'django-project',
}

setup(**config)
