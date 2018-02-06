#!/usr/bin/env python3
"""A simple program to find out the biblical date."""
# -- BEGINNING OF INTRO: -- #

# A SHORT DESCRIPTION:
# Aviv Calendar, a small program to find out what day it is according
# to the Biblical calendar. Also attempts to let you know about
# the Feasts of the Lord as well as the Sabbath.

# CURRENT STATUS:
# Currently, it only decides what day of week, month and year it is according
# to biblical timekeeping. It will also tell you some details about sunset
# and sunrise and wether or not is is a weekly sabbath or a feast day.

# COPYRIGHT:
# Copyright (C) 2017 - 2018 Johan Thorén <johan@thoren.xyz>

# LICENSE:
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# -- END OF INTRO -- #
import argparse
import datetime
import logging
import os
import re
import shelve
import sys
import time
import urllib.request
# Uncomment the following line to use the astral builtin geocoder.
# Se Astral documentation for alternatives.
from astral import Astral
# Using GoogleGeocoder requires you to accept their licenses and terms
# of service.
from astral import GoogleGeocoder
from astral import AstralError
import hist_data

_DEBUG = False


def main():
    """Find out the biblical calendar data for a
    given location.
    """
    parser = argparse.ArgumentParser(
        description='Find out the biblical time for a given location.')
    parser.add_argument(
        '--debug',
        metavar='D',
        type=bool,
        default=False,
        nargs='?',
        help='show debug messages')
    parser.add_argument(
        '--country',
        metavar='C',
        type=str,
        nargs='?',
        help='specify the country where the location is located')
    parser.add_argument(
        '--location',
        metavar='L',
        default='Jerusalem',
        type=str,
        nargs='?',
        help='specify the location where the time will be calculated')
    parser.add_argument(
        '--geocoder',
        metavar='G',
        default='astral',
        type=str,
        nargs='?',
        help='specify the geocoder to use for calculating the location')
    parser.add_argument(
        '--year', metavar='Y', type=int, nargs='?', help='specify the year')
    parser.add_argument(
        '--month', metavar='M', type=int, nargs='?', help='specify the month')
    parser.add_argument(
        '--day',
        metavar='D',
        type=int,
        nargs='?',
        help='specify the day of month')
    parser.add_argument(
        '--hour',
        metavar='H',
        type=int,
        nargs='?',
        help='specify the hour of the day')

    args = parser.parse_args()

    # Check for the --debug flag and set the corresponding debug settings.
    global _DEBUG
    _DEBUG = args.debug
    _debug()

    # Since the --geocoder 'astral' does not work with the --country option,
    # check if --country has been used and ignore it with a message to the user.
    if args.country:
        if args.geocoder == 'astral':
            print(
                'Astral Geocoder does not like to have the country specified.')
            print('Ignoring "--country {}"'.format(args.country))
            print('To use "--country {}", please specify "--geocoder google".'.
                  format(args.country))
        elif args.geocoder == 'google':
            args.location = str(args.location + ', ' + args.country)

    # Put everything together and create the main object that _info will be
    # based on.
    main_city = BibTime(args.location, args.geocoder, args.year, args.month,
                        args.day, args.hour)
    _info(main_city)


def _info(loc):
    """Prints information about the given location and it's calendar data."""

    # To shorten all the references to loc.b_location.location.name, which is so
    # long it tends to mess up rows just a bit too much.
    city_re = re.compile(r'\w+$')
    match_obj = city_re.search(loc.b_location.location.name)
    city_name = match_obj.group()

    def _location_info():
        # Print information about the location.
        print('Location '.ljust(40, '.'))
        print('{:20s}{:>20s}'.format('City:', city_name))
        print('{:20s}{:>20s}'.format('Country:',
                                     loc.b_location.location.region))
        print('')

    def _bib_info():
        # Print information about the biblical calendar data.
        print('Biblical '.ljust(40, '.'))
        # Create a string in the format 'YYYY-MM-DD' using the biblical
        # calendar data.
        bib_date_str = str(loc.b_time.year) + '-' + '{0:02d}'.format(
            loc.b_time.month) + '-' + '{0:02d}'.format(loc.b_time.day)
        print('{:20s}{:>20s}'.format('Short (ISO) Date:', bib_date_str))
        print('')
        print('{:20s}{:>20d}'.format('Year:', loc.b_time.year))
        print('{:20s}{:>20s}'.format('Month:', loc.b_time.month_name))
        print('{:25s}{:>15s}'.format('Month (traditional name):',
                                     loc.b_time.month_trad_name))
        print('{:20s}{:>20s}'.format('Day of month:', loc.b_time.day_name))
        print('')
        print('{:20s}{:>20s}'.format('Weekday:', loc.b_time.weekday))
        print('')

        ws_print = 'Yes' if loc.b_time.sabbath.weekly_sabbath is True else 'No'
        fd_print = 'Yes' if loc.b_time.sabbath.high_feast_day is True else 'No'
        hd_print = 'Yes' if loc.b_time.sabbath.holy_day_of_rest is True else 'No'
        print('{:20s}{:>20s}'.format('Weekly Sabbath:', ws_print))
        print('{:20s}{:>20s}'.format('Feast Day:', fd_print))
        print('{:20s}{:>20s}'.format('Holy Day of rest:', hd_print))
        print('')
        if loc.b_time.sabbath.high_feast_day is True:
            if len(loc.b_time.sabbath.feast_name) >= 28:
                name_re_1 = re.compile(r"^([^/]*)/*")
                name_mo_1 = name_re_1.search(loc.b_time.sabbath.feast_name)
                name_part_1 = name_mo_1.group()
                name_part_2 = loc.b_time.sabbath.feast_name[len(name_part_1):]
                print('{:12s}{:>28s}'.format('Feast name:', name_part_1))
                print('{:>40s}'.format(name_part_2))
                print('')
            else:
                print('{:20s}{:>20s}'.format('Feast name:',
                                             loc.b_time.sabbath.feast_name))
                print('')
            if loc.aviv_barley is None:
                barley_statement = 'Not yet time for the barley'
            elif loc.aviv_barley is True:
                barley_statement = 'The barley IS Aviv'
            else:
                barley_statement = 'The barley is NOT Aviv'
            print('{:12s}{:>28s}'.format('Barley:', barley_statement))
            print('')

    def _greg_info():
        # Print information about the gregorian calendar data.
        print('Gregorian '.ljust(40, '.'))
        print('{:20s}{:>20s}'.format(
            'Short (ISO) Date:',
            loc.b_location.g_time.date().strftime('%Y-%m-%d')))
        print('')
        print('{:20s}{:>20s}'.format('Year:',
                                     loc.b_location.g_time.strftime('%Y')))
        print('{:20s}{:>20s}'.format('Month:',
                                     loc.b_location.g_time.strftime('%B')))
        print('{:20s}{:>20s}'.format('Day of month:',
                                     loc.b_location.g_time.strftime('%d')))
        print('')
        print('{:20s}{:>20s}'.format(
            'Weekday:', GREG_WEEKDAYS[loc.b_location.g_time.weekday()]))
        print('')
        print('{:20s}{:>20s}'.format(
            'Time:', loc.b_location.g_time.strftime('%H:%M:%S')))
        print('')

    def _solar_info():
        # Print information about the sun, such as daylight, sunset and
        # sunrise etc.
        print('Solar info '.ljust(40, '.'))
        if loc.b_location.sun_info['has_set'] is True:
            print('{:20s}{:>20s}'.format('Daylight:', 'No'))
            print('{:20s}{:>20s}'.format('Sun has set:', 'Yes'))
            sunset_time = loc.b_location.sun_info['sunset'].strftime(
                '%H:%M:%S')
            print('{:20s}{:>20s}'.format('Time of sunset:', sunset_time))
        elif loc.b_location.sun_info['has_risen'] is False:
            print('{:20s}{:>20s}'.format('Daylight:', 'No'))
            print('{:20s}{:>20s}'.format('Sun has risen:', 'No'))
            sunrise_time = loc.b_location.sun_info['sunrise'].strftime(
                '%H:%M:%S')
            print('{:20s}{:>20s}'.format('Time of sunrise:', sunrise_time))
        else:
            print('{:20s}{:>20s}'.format('Daylight:', 'Yes'))
            sunrise_time = loc.b_location.sun_info['sunrise'].strftime(
                '%H:%M:%S')
            sunset_time = loc.b_location.sun_info['sunset'].strftime(
                '%H:%M:%S')
            print('{:20s}{:>20s}'.format('Time of sunrise:', sunrise_time))
            print('{:20s}{:>20s}'.format('Time of sunset:', sunset_time))

    _location_info()
    _bib_info()
    _greg_info()
    _solar_info()


def _debug():
    if _DEBUG is True:
        logging.basicConfig(
            level=logging.DEBUG,
            format=' %(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=' %(asctime)s - %(levelname)s - %(message)s')


# Define the traditional names of the biblical months of the year.
# These are not per definition biblical, rather they come from the exile
# in Babylon.
TRAD_MONTH_NAMES = ('Nisan', 'Iyyar', 'Sivan', 'Tammuz', 'Av', 'Elul',
                    'Tishri', 'Marheshvan', 'Kislev', 'Tevet', 'Shvat', 'Adar',
                    'Adar (2)')

# Define the biblical months. 1st month could be named Aviv. Maybe later.
BIB_MONTHS = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th',
              '10th', '11th', '12th', '13th')

# Define the gregorian weekdays. Wrapping for ease of index reference.
GREG_WEEKDAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                 'Saturday', 'Sunday', 'Monday')

# Tuple containing the biblical weekday names. Simply refered to by
# their number.
BIB_WEEKDAYS = ('2nd', '3rd', '4th', '5th', '6th', '7th', '1st', '2nd')

# Define the biblical days of the months.
BIB_DAY_OF_MONTH = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
                    '9th', '10th', '11th', '12th', '13th', '14th', '15th',
                    '16th', '17th', '18th', '19th', '20th', '21st', '22nd',
                    '23rd', '24th', '25th', '26th', '27th', '28th', '29th',
                    '30th')

# List of feast days that are NOT biblically commanded to keep but still
# of interest.
FIXED_FEAST_DAYS = {
    (9, 25): ('1st day of Hanukkah', False),
    (9, 26): ('2nd day of Hanukkah', False),
    (9, 27): ('3rd day of Hanukkah', False),
    (9, 28): ('4th day of Hanukkah', False),
    (9, 29): ('5th day of Hanukkah', False),
    (9, 30): ('6th day of Hanukkah', False),
    (12, 14): ('Purim', False)
}

HANUKKAH_DAYS_REALLY_SHORT_9 = {
    (10, 1): ('5th day of Hanukkah', False),
    (10, 2): ('6th day of Hanukkah', False),
    (10, 3): ('7th day of Hanukkah', False),
    (10, 4): ('8th day of Hanukkah', False)
}

HANUKKAH_DAYS_SHORT_9 = {
    (10, 1): ('6th day of Hanukkah', False),
    (10, 2): ('7th day of Hanukkah', False),
    (10, 3): ('8th day of Hanukkah', False)
}

HANUKKAH_DAYS_LONG_9 = {
    (10, 1): ('7th day of Hanukkah', False),
    (10, 2): ('8th day of Hanukkah', False)
}

# List of high feast days. Boolean True if they are considered
# "High days of convocation" where no work shall be done.
FIXED_HIGH_FEAST_DAYS = {
    (1, 1): ('1st day of the Aviv Year.', False),
    (1, 14): ('Passover', False),
    (1, 15): ('1st day of "Feast of Unleavened Bread"', True),
    (1, 16): ('2nd day of "Feast of Unleavened Bread"', False),
    (1, 17): ('3rd day of "Feast of Unleavened Bread"', False),
    (1, 18): ('4th day of "Feast of Unleavened Bread"', False),
    (1, 19): ('5th day of "Feast of Unleavened Bread"', False),
    (1, 20): ('6th day of "Feast of Unleavened Bread"', False),
    (1, 21): ('Last day of "Feast of Unleavened Bread"', True),
    (7, 1): ('Yom Teruah / "Feast of Trumpets or Feast of Shouting"', True),
    (7, 10): ('Yom Kippur / "Day of Atonement"', True),
    (7, 15): ('1st day of Sukkot / "Feast of Tabernacles"', True),
    (7, 16): ('2nd day of Sukkot / "Feast of Tabernacles"', False),
    (7, 17): ('3rd day of Sukkot / "Feast of Tabernacles"', False),
    (7, 18): ('4th day of Sukkot / "Feast of Tabernacles"', False),
    (7, 19): ('5th day of Sukkot / "Feast of Tabernacles"', False),
    (7, 20): ('6th day of Sukkot / "Feast of Tabernacles"', False),
    (7, 21): ('Last day of Sukkot / "Feast of Tabernacles"', False),
    (7, 22): ('Last Great Day', True)
}


def get_latest_data():
    """Fetches the latest data available from avivcalendar.com."""
    # Download the file from `https://www.avivcalendar.com/latest_data`
    # and save it locally under `latest_data.py`. This is updated as soon
    # as news of the new moon or the Aviv barley breaks.
    url = 'https://www.avivcalendar.com/latest-data'
    latest_file = os.path.join(sys.path[0], 'latest_data.py')
    try:
        with urllib.request.urlopen(url) as response, open(latest_file,
                                                           'wb') as out_file:
            data = response.read()
            out_file.write(data)
            out_file.close()
    except urllib.error.URLError:
        raise Exception(
            'Unable to connect to {}\nPlease check your internet connection.'.
            format(url))


# Working with a DB_FILE since we will be joining dictionaries from both git
# synced sources, as well as the latest_data.py that is retrieved from
# online.
DB_FILE = os.path.join(sys.path[0], 'current_data')
DB_ACTUAL_FILE = os.path.join(sys.path[0], 'current_data.DB')
DB_EXISTS = os.path.exists(DB_ACTUAL_FILE)
if DB_EXISTS:
    DB_MOD_TIME = datetime.datetime.fromtimestamp(
        os.path.getmtime(DB_ACTUAL_FILE))


# Combine the data from hist_data (which is distributed with the source code),
# and data from latest_data, which is synced in get_latest_data above.
def combine_data():
    """Combine data from source code with data fetched online and create DB."""
    get_latest_data()
    # I didn't want this import to be at the top of the file, since the
    # latest_data.py file will not exist on first run.
    # TODO: Is that the correct way to do it?
    import latest_data
    database = shelve.open(DB_FILE)

    # Potentially needed clearing of DB befor each run. Or is that overkill?
    # TODO: Needs testing.
    database.clear()

    def merge_two_dicts(dict_x, dict_y):
        """Merges two dictionaries: historical data and latest data."""
        dict_z = dict_x.copy()  # start with dict_x's keys and values
        dict_z.update(
            dict_y
        )  # modifies dict_z with dict_y's keys and values & returns None
        return dict_z

    # Combine hist_data and latest_data and stash it in the database.
    temp_moons = merge_two_dicts(latest_data.LAST_MOON, hist_data.MOONS)
    moons = merge_two_dicts(temp_moons, latest_data.NEXT_MOON)

    database['MOONS'] = moons
    database['AVIV_BARLEY'] = latest_data.AVIV_BARLEY
    database.close()


# Open the database, if none exists run the function to create one.
if DB_EXISTS is not True:
    logging.debug('DB_FILE does not exist on this system. Creating a new one.')
    combine_data()

# Get the database in order.
DB = shelve.open(DB_FILE)
MOONS = DB['MOONS']
AVIV_BARLEY = DB['AVIV_BARLEY']
DB.close()


def datetime_from_key(k):
    """Creates a datetime object from key (k).

    First tries to find the month in the ´MOONS´.

    Also sets the value of the attribute is_known to reflect wether or not
    it was based on observation (and therefore confirmed) or if it's an
    estimated guess. Note that most historical MOONS before 6001 will always
    be estimated.

    Keys need to be in the form of YYYYMM (example: 600101)."""
    try:
        if MOONS[k]:
            year = MOONS[k][2]
            month = MOONS[k][3]
            day = MOONS[k][4]
            is_known = MOONS[k][5]
            date = datetime.date(year, month, day)
            # Returns as a tuple.
            return (date, is_known)
        is_known = False
        date = None
        return (date, is_known)
    except KeyError:
        is_known = False
        date = None
        # Returns as a tuple.
        return (date, is_known)


def test_year(year):
    """Tests if a year is within the scope of the program. Namely 4001-8001."""
    year = int(year)
    try:
        if year <= 4000:
            print('Error: Year value lower than 4001. Not searchable.')
            raise IndexError
        elif year >= 8001:
            print('Error: Year value higher than 8000. Not searchable.')
            raise IndexError
        return year
    except ValueError:
        raise Exception('Error: Input not a valid value')
    except IndexError:
        raise Exception('Error: Input out of range')


def test_month(month):
    """Tests if a month is within the range of a biblical year: 1-13."""
    month = int(month)
    try:
        if month <= 0:
            print('Error: Month value lower than 1.')
            raise IndexError
        elif month > 13:
            print('Error: Month value higher than 13.')
            raise IndexError
        return month
    except ValueError:
        print('Error: Not an integer.')
    except IndexError:
        print('Error: The specified value is out of the allowed range.')


def test_day(day, length):
    """Tests if a day is within the range of a biblical month: 1-30"""
    day = int(day)
    length = int(length)
    try:
        if day <= 0:
            print('Error: Day value lower than 1.')
            raise IndexError
        elif day > 30:
            print('Error: Day value higher than 30.')
            raise IndexError
        elif day > length:
            print('Error: The month did not contain that many days.')
            raise IndexError
        return day
    except ValueError:
        print('Error: Could not convert the value to an integer.')
    except IndexError:
        print('Error: The value is out of the allowed range.')


# TODO: Work in progress.
def test_is_feast(month, day, p_length):
    """Tests if a day is a High Feast Day.

    Needs 2 integers as arguments: Month, Day.
    Example: 1, 15
    Optional length of previous month as integer.
    Example: 10, 1, 29"""
    pf = (month, day)
    if p_length is not None:
        logging.debug('p_length is %s', p_length)
        if month == 10 and p_length <= 28:
            try:
                if HANUKKAH_DAYS_REALLY_SHORT_9[pf]:
                    is_hfd = True
                    is_hfs = HANUKKAH_DAYS_REALLY_SHORT_9[pf][1]
                    feast_name = HANUKKAH_DAYS_REALLY_SHORT_9[pf][0]
                    return (is_hfd, is_hfs, feast_name)
            except KeyError:
                is_hfd, is_hfs, feast_name = False, False, None
        elif month == 10 and p_length == 29:
            try:
                if HANUKKAH_DAYS_SHORT_9[pf]:
                    is_hfd = True
                    is_hfs = HANUKKAH_DAYS_SHORT_9[pf][1]
                    feast_name = HANUKKAH_DAYS_SHORT_9[pf][0]
                    return (is_hfd, is_hfs, feast_name)
            except KeyError:
                is_hfd, is_hfs, feast_name = False, False, None
        elif month == 10 and p_length >= 30:
            try:
                if HANUKKAH_DAYS_LONG_9[pf]:
                    is_hfd = True
                    is_hfs = HANUKKAH_DAYS_LONG_9[pf][1]
                    feast_name = HANUKKAH_DAYS_LONG_9[pf][0]
                    return (is_hfd, is_hfs, feast_name)
            except KeyError:
                is_hfd, is_hfs, feast_name = False, False, None
    elif p_length is None:
        try:
            if FIXED_HIGH_FEAST_DAYS[pf]:
                is_hfd = True
                is_hfs = FIXED_HIGH_FEAST_DAYS[pf][1]
                feast_name = FIXED_HIGH_FEAST_DAYS[pf][0]
        except KeyError:
            try:
                if FIXED_FEAST_DAYS[pf]:
                    is_hfd = True
                    is_hfs = FIXED_FEAST_DAYS[pf][1]
                    feast_name = FIXED_FEAST_DAYS[pf][0]
            except KeyError:
                is_hfd, is_hfs, feast_name = False, False, None
    return (is_hfd, is_hfs, feast_name)


def last_moon_check():
    """Imports latest data and sets the last_moon variables."""
    import latest_data
    last_moon = latest_data.LAST_MOON
    last_moon_key = list(last_moon.keys())[0]
    return (last_moon, last_moon_key)


class BibLocation:
    """Define a location. Takes city_name as argument.

       Also takes optional time as argument (which will
       usually be passed on from BibTime.)
       Arguments: city_name, geocoder, year, month, day, hour.
       Example:
       s = BibLocation('Stockholm, Sweden', 'google', 2018, 1, 1, 12)"""

    def __init__(self,
                 city_name,
                 geocoder='astral',
                 year=None,
                 month=None,
                 day=None,
                 hour=None):
        try:
            r"""Creates an object using the Astral or Google Geocoder.

            You need to choose whether to use Astral or Google Geocoder.
            To use the GoogleGeocoder you have to agree to GoogleGeocoder
            terms and license found here:
            https://developers.google.com/maps/documentation/geocoding/usage-limits#terms-of-use-restrictions"""

            if geocoder == 'astral':
                self.geo = Astral()
            elif geocoder == 'google':
                self.geo = GoogleGeocoder()
            else:
                raise Exception('Error: Unknown geocoder: {}'.format(geocoder))

            self.geo.solar_depression = 'civil'
            logging.debug('city_name is %s', city_name)
            logging.debug('trying to find the coordinates for %s', city_name)
            try:
                location = self.geo[city_name]
            except AstralError:
                print('Please wait...')
                url = 'https://www.avivcalendar.com/latest-data'
                connection_msg = (
                    'Unable to connect to {}\n'
                    'Please check your internet connection.'.format(url))
                try:
                    if urllib.request.urlopen(url).code != 200:
                        raise Exception(connection_msg)
                except urllib.error.URLError:
                    raise Exception(connection_msg)
                time.sleep(2)
                try:
                    location = self.geo[city_name]
                except AstralError:
                    print('Please wait some more...')
                    time.sleep(2)
                    try:
                        location = self.geo[city_name]
                    except AstralError:
                        raise Exception(
                            'The Geocoder ({}) is having a fit.'
                            # 'GoogleGeocoder is having a fit. '
                            "Or the location really can't be found.".format(
                                self.geo))
        except KeyError:
            raise Exception(
                'Error: That city is not found. Please try another.')
        self.location = location

        # If no date input it given, defaults to the current date and time.
        if year == month == day == hour == None:
            logging.debug('No date input given.')
            self.g_time = self._set_g_time_now()
        else:
            year = 2018 if year is None else year
            month = 1 if month is None else month
            day = 1 if day is None else day
            hour = 12 if hour is None else hour
            self.g_time = self._set_g_time(year, month, day, hour)

        # The following attributes are set by `sun_status` function.
        self.sun_info = {
            'sunrise': None,
            'sunset': None,
            'has_set': None,
            'has_risen': None,
            'daylight': None
        }

        self.sun_status()

    def _get_entry(self):
        return 'The city name is set to {}'.format(self.location)

    def _set_entry(self, city_name):
        try:
            self.geo.solar_depression = 'civil'
            location = self.geo[city_name]
        except KeyError:
            raise Exception(
                'Error: That city is not found. Please try another.')
        self.location = location

    city = property(_get_entry, _set_entry)

    def _set_g_time(self, year, month, day, hour):
        """Sets the object at a point in time to use for calculation of sun."""
        g_time = datetime.datetime(year, month, day, hour, 0, 0,
                                   0).replace(tzinfo=self.location.tzinfo)
        return g_time

    def update_g_time(self):
        """Updates the g_time to reflect current time."""
        self.g_time = self._set_g_time_now()
        self.sun_status()

    def _set_g_time_now(self):
        """Updates the g_datetime to reflect current time."""
        g_time = datetime.datetime.now(
            self.location.tz).replace(tzinfo=self.location.tzinfo)
        return g_time

    def sun_status(self):
        """Updates the sunrise and sunset status based on location and time."""
        g_time = self.g_time
        loc_sun = self.location.sun(date=g_time, local=True)

        has_set = g_time >= loc_sun['sunset']
        has_risen = g_time >= loc_sun['sunrise']

        def check_daylight(has_set, has_risen):
            """Checks if there is still daylight."""
            if has_set is not None:
                daylight = not has_set
            if has_risen is not None:
                daylight = has_risen
            return daylight

        daylight = check_daylight(has_set, has_risen)

        self.sun_info['sunrise'] = loc_sun['sunrise']
        self.sun_info['sunset'] = loc_sun['sunset']
        self.sun_info['has_set'] = has_set
        self.sun_info['has_risen'] = has_risen
        self.sun_info['daylight'] = daylight

    def sun_status_now(self):
        """Updates the g_datetime to reflect current time and then the sun."""
        self._set_g_time_now()
        self.sun_status()


class BibTime:
    """Define biblical time and date.

    Needs a city name as a string.
    Takes optional time as an argument
    as year, month, day.
    Defaults to 2018, 1, 1.
    Example: m = BibTime('Manila')
    Example: s = BibTime('Skepplanda, Sweden', 'google', 2018, 2, 1)
    """

    def __init__(self, city, geocoder='astral', year=1, month=1, day=1,
                 hour=1):
        try:
            b_location = BibLocation(city, geocoder, year, month, day, hour)
        except ValueError:
            raise Exception('Error: Not a valid string.')
        self.b_location = b_location
        self._check_db_status()
        self.aviv_barley = None
        self.b_time = self._set_b_time()

    def update_time(self):
        """Update time to current."""
        self.b_location.update_g_time()
        self._check_db_status()
        self.b_time = self._set_b_time()

    def _check_db_status(self):
        """Rebuild the database if moon has recently renewed
        or if no database exists, or if it's been more than 1
        day since last modification."""
        m_phase = self.b_location.location.moon_phase(
            date=datetime.datetime.now())
        logging.debug('current m_phase at time of test is %s', m_phase)

        if m_phase <= 2:
            combine_data()
        elif DB_EXISTS is False:
            combine_data()
        # Only renew database if it's been more than one day since last mod.
        elif datetime.datetime.now() - DB_MOD_TIME > datetime.timedelta(
                days=1):
            combine_data()

    def _set_b_time(self):
        """Tries to calculate the biblical time."""

        lmoon = last_moon_check()
        last_moon = lmoon[0]
        last_moon_key = lmoon[1]

        def _calc_b_weekday():
            """Tries to calculate the day of week.
            Since the biblical day starts in the
            evening, 1 needs to be added if sun
            has set.
            """
            if self.b_location.sun_info['daylight'] is None:
                self.b_location.sun_status()
            b_weekday_index = self.b_location.g_time.weekday()
            sun_has_set = self.b_location.sun_info['has_set']

            if sun_has_set is not None:
                if sun_has_set is True:
                    b_weekday_index += 1
                    b_weekday = BIB_WEEKDAYS[b_weekday_index]
                else:
                    b_weekday = BIB_WEEKDAYS[b_weekday_index]
            else:
                b_weekday = BIB_WEEKDAYS[b_weekday_index]

            return b_weekday

        def _get_moon_phases():
            logging.debug('Entering the "_test_current" function.')
            # Test wether or not we are looking for a current date.
            today = datetime.datetime.now(self.b_location.location.tz).replace(
                tzinfo=self.b_location.location.tzinfo).date()
            date_to_test = self.b_location.g_time.date()
            m_phase_today = self.b_location.location.moon_phase(date=today)
            m_phase_date_to_test = self.b_location.location.moon_phase(
                date=date_to_test)
            return (today, m_phase_today, date_to_test, m_phase_date_to_test)

        def _test_current():
            m_phases = _get_moon_phases()
            today = m_phases[0]
            m_phase_today = m_phases[1]
            date_to_test = m_phases[2]
            m_phase_date_to_test = m_phases[3]

            cur = None

            if today < date_to_test:
                if m_phase_today > m_phase_date_to_test:
                    cur = False
            elif today > date_to_test:
                if m_phase_today > m_phase_date_to_test:
                    cur = False
            elif today - date_to_test > datetime.timedelta(days=29):
                cur = False
            elif date_to_test - today > datetime.timedelta(days=29):
                cur = False
            else:
                cur = True

            return cur

        current = _test_current()
        logging.debug('current is now %s', current)

        def _find_month(unknown_moon):
            i = 0
            potential_keys = []
            for key in sorted(list(MOONS.keys())):
                known_moon = datetime.date(MOONS[key][2], MOONS[key][3],
                                           MOONS[key][4])
                i += 1
                logging.debug('unknown_moon is %s', unknown_moon)
                if unknown_moon == known_moon:
                    logging.debug('stage 1')
                    logging.debug('known_moon is %s', known_moon)
                    logging.debug('unknown_moon is %s', unknown_moon)
                    logging.debug('known_moon equals unknown_moon')
                    logging.debug('returning key %s', key)
                    return key
                elif unknown_moon < known_moon:
                    logging.debug('stage 2')
                    logging.debug('known_moon is %s', known_moon)
                    logging.debug('unknown_moon is %s', unknown_moon)
                    logging.debug('known_moon is later than unknown_moon')
                    continue
                elif unknown_moon > known_moon:
                    logging.debug('stage 3')
                    logging.debug('known_moon is %s', known_moon)
                    logging.debug('unknown_moon is %s', unknown_moon)
                    delta = unknown_moon - known_moon
                    logging.debug('delta is %s', delta)
                    if delta <= datetime.timedelta(days=29):
                        logging.debug('stage 5')
                        logging.debug('saving potential key %s', key)
                        potential_keys.insert(0, key)
                        continue
                    elif delta == datetime.timedelta(days=30):
                        logging.debug('stage 6')
                        logging.debug('saving potential key %s', key)
                        potential_keys.insert(0, key)
                        continue
                    elif delta > datetime.timedelta(days=30):
                        logging.debug('stage 7')
                        logging.debug('delta (%s) is greater than 30', delta)
                        continue
                    continue
                logging.debug('potential key = %s', potential_keys[0])
            if potential_keys[0]:
                logging.debug('returning previously tested potential key %s',
                              potential_keys[0])
                return potential_keys[0]
            logging.debug('entering last fallback "else"')
            key = None
            return key

        def _get_moon_from_date():
            # If current is True, then try to find out the gregorian date of
            # the month using the last_moon_key.
            if current is True:
                g_month = datetime_from_key(last_moon_key)
                # If no such month exists in the database we need to try to
                # find the one that it most likely is.
                year = last_moon[last_moon_key][0]
                month = last_moon[last_moon_key][1]
                if g_month is None:
                    unknown_moon = self.b_location.g_time.date()
                    logging.debug('g_month is None, trying unknown_moon. '
                                  'unknown_moon is %s', unknown_moon)
                    u_key = _find_month(unknown_moon)
                    logging.debug('u_key is now %s', u_key)
                    g_month = datetime_from_key(u_key)
                    tmpstring = str(u_key)
                    year = int(tmpstring[0:4])
                    month = int(tmpstring[4::])
                return (g_month, year, month)

            else:
                unknown_moon = self.b_location.g_time.date()
                logging.debug('unknown_moon is %s', unknown_moon)
                u_key = _find_month(unknown_moon)
                logging.debug('u_key is now %s', u_key)
                g_month = datetime_from_key(u_key)
                tmpstring = str(u_key)
                year = int(tmpstring[0:4])
                month = int(tmpstring[4::])
                return (g_month, year, month)

        x_month = _get_moon_from_date()
        is_known = x_month[0][1]
        b_year = x_month[1]
        b_month = x_month[2]

        x_month_year = x_month[0][0].year
        logging.debug('x_month_year is %s', x_month_year)
        x_month_month = x_month[0][0].month
        logging.debug('x_month_month is %s', x_month_month)
        x_month_day = x_month[0][0].day
        logging.debug('x_month_day is %s', x_month_day)

        def _set_month_start_time(year, month, day):
            month_start_time = datetime.datetime(year, month, day).replace(
                tzinfo=self.b_location.location.tzinfo, microsecond=0)
            return month_start_time

        def _set_day_of_month(month_start_time):
            time_lapsed = self.b_location.g_time - month_start_time
            day = time_lapsed.days
            if self.b_location.sun_info['has_set'] is True:
                day += 1
            return day

        # TODO: Month start time should take sunset time into consideration
        # to give a more exact datetime.datetime object.
        month_start_time = _set_month_start_time(x_month_year, x_month_month,
                                                 x_month_day)
        b_day = _set_day_of_month(month_start_time)

        if b_day > 30:
            raise Exception('Error: Day of Month greater than 30.')

        b_day_name = BIB_DAY_OF_MONTH[b_day - 1]
        b_month_name = BIB_DAY_OF_MONTH[b_month - 1]
        b_month_trad_name = TRAD_MONTH_NAMES[b_month - 1]

        b_day = _set_day_of_month(month_start_time)

        if b_month >= 11:
            self.aviv_barley = AVIV_BARLEY

        def _get_prev_month_length(b_year, b_month, month_start_time):
            key = int(str(b_year) + '{0:0=2d}'.format(b_month))
            p_month = datetime_from_key(key)
            p_month = datetime.datetime(
                p_month[0].year, p_month[0].month, p_month[0].day).replace(
                    tzinfo=self.b_location.location.tzinfo, microsecond=0)
            delta = month_start_time - p_month
            logging.debug('delta is %s', delta)
            return delta.days

        if b_month == 10:
            p_length = _get_prev_month_length(b_year, 9, month_start_time)
            feast_test = test_is_feast(b_month, b_day, p_length)
        else:
            feast_test = test_is_feast(b_month, b_day, None)

        is_hfd = feast_test[0]
        is_hfs = feast_test[1]

        feast_day = is_hfd
        feast_name = feast_test[2]

        b_weekday = _calc_b_weekday()
        is_ws = True if b_weekday == '7th' else False

        if is_hfs is True:  # hfs stands for high feast sabbath
            b_sabbath = is_hfs
        else:
            b_sabbath = is_ws

        class BibSabbath:
            def __init__(self, b_sabbath, is_hfd, is_hfs, is_ws, feast_name):
                self.sabbath = b_sabbath
                self.high_feast_day = is_hfd
                self.holy_day_of_rest = is_hfs
                self.weekly_sabbath = is_ws
                if self.high_feast_day is True:
                    self.feast_name = feast_name

        class BibDay:
            def __init__(self, b_year, b_month, b_month_name,
                         b_month_trad_name, b_day, b_day_name, b_weekday,
                         month_start_time):
                self.year = b_year
                self.month = b_month
                self.month_name = b_month_name
                self.month_trad_name = b_month_trad_name
                self.day = b_day
                self.day_name = b_day_name
                self.weekday = b_weekday
                self.month_start_time = month_start_time

        b_time = BibDay(b_year, b_month, b_month_name, b_month_trad_name,
                        b_day, b_day_name, b_weekday, month_start_time)
        b_time.sabbath = BibSabbath(b_sabbath, is_hfd, is_hfs, is_ws,
                                    feast_name)
        return b_time


if __name__ == '__main__':
    main()
