from setuptools import setup, find_packages
from codecs import open
from os import path

setup(
    name='aviv',
    version='0.1.1',
    description='Biblical calendar tool',
    author='Johan Thorén',
    author_email='johan@avivcalendar.com',
    url='https://www.avivcalendar.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['astral'],
    python_requires='>=3.6',
)
