"""spicy.menu"""
from importlib import import_module
from setuptools import setup, find_packages


version = import_module('src').__version__
LONG_DESCRIPTION = """
spicy.menu package
"""


def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open('README.rst').read()
    except IOError:
        return LONG_DESCRIPTION


setup(
    name='spicy.menu',
    version='1.0',
    author='Stanislav Shtin',
    author_email='antisvin@gmail.com',
    description='Spicy menu',
    license='BSD',
    keywords='django, cms',
    url='',

    packages=find_packages('src'),
    package_dir={
        '': 'src',
    },

    include_package_data=True,
    zip_safe=False,
    long_description=long_description(),
    namespace_packages=['spicy',],

    install_requires=[
        'django-autocomplete-light==2.0.0a15'
    ],
    dependency_links=[
    ],
    classifiers=[
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'License :: Proprietary',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
)
