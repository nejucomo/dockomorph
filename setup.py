#! /usr/bin/env python

from setuptools import setup, find_packages

Package = 'dockomorph'

setup(
    name=Package,
    description='Deploy docker images based on github repositories.',
    url='https://github.com/nejucomo/{}'.format(Package),
    license='GPLv3',
    version='0.2.1',
    author='Nathan Wilcox',
    author_email='nejucomo@gmail.com',
    packages=find_packages(),
    install_requires=[
        'twisted >= 13.1',
        'Mock >= 1.0.1',
        ],
    entry_points={
        'console_scripts': [
            '{0} = {0}.main:main'.format(Package),
            ],
        },
    test_suite='{}.tests'.format(Package),
    package_data={
        Package: ['web/static/*'],
        },
    )
