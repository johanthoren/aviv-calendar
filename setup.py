from codecs import open
from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_D = f.read()

setup(
    name='aviv',
    version='0.1.3',
    description='Biblical calendar tool',
    long_description=LONG_D,
    author='Johan Thorén',
    author_email='johan@avivcalendar.com',
    license='GPLv2',
    url='https://www.avivcalendar.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['astral'],
    python_requires='>=3.5',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Religion',
        'Topic :: Religion',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
