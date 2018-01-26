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
import datetime
import logging
import urllib.request
import os
import sys
import getopt
import shelve
import time
# Uncomment the following line to use the astral builtin geocoder.
# Se Astral documentation for alternatives.
from astral import Astral
# Using GoogleGeocoder requires you to accept their licenses and terms
# of service.
from astral import GoogleGeocoder
from astral import AstralError
import hist_data

_DEBUG = False


def main(argv):
    geocoder = 'astral'
    location = 'Jerusalem'
    try:
        opts, args = getopt.getopt(argv, "hgl:d",
                                   ["help", "geocoder=", "location="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt == '-d':
            global _DEBUG
            _DEBUG = True
        elif opt in ("-g", "--geocoder"):
            if opt == 'astral':
                geocoder = Astral
            elif opt == 'google':
                geocoder = GoogleGeocoder
            # else:
            #     usage()
            #     sys.exit()
        elif opt in ("-l", "--location"):
            location = arg

    b = BibTime(location, geocoder)
    print('The biblical date in {} is now {}{}{}'.format(
        b.b_location.city, b.b_time.year, b.b_time.month, b.b_time.day))


def usage():
    """Prints a useful message."""
    # TODO: Create useful message.
    print("""Useful message.""")


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
FIXED_FEAST_DAYS = {(9, 25), ('1st day of Hanukkah', False), (12, 14),
                    ('Purim', False)}
# TODO: Feast days that are relative to weekday, or that span over
# months (like Hanukkah).

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
    # TODO: This needs error handling.
    url = 'https://www.avivcalendar.com/latest-data'
    latest_file = os.path.join(sys.path[0], 'latest_data.py')
    with urllib.request.urlopen(url) as response, open(latest_file,
                                                       'wb') as out_file:
        data = response.read()
        out_file.write(data)
        out_file.close()


# Working with a DB_FILE since we will be joining dictionaries from both git
# synced sources, as well as the latest_data.py that is retrieved from
# online.
DB_FILE = os.path.join(sys.path[0], 'current_data')
DB_ACTUAL_FILE = os.path.join(sys.path[0], 'current_data.DB')
DB_EXISTS = os.path.exists(DB_ACTUAL_FILE)
DB_MOD_TIME = datetime.datetime.fromtimestamp(os.path.getmtime(DB_ACTUAL_FILE))


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
def test_is_feast(month, day):
    """Tests if a day is a High Feast Day.

    Needs 2 integers as arguments: Month, Day.
    Example: 1, 15"""
    potential_feast = (month, day)
    try:
        if FIXED_HIGH_FEAST_DAYS[potential_feast]:
            is_hfd = True
            is_hfs = FIXED_HIGH_FEAST_DAYS[potential_feast][1]
            feast_name = FIXED_HIGH_FEAST_DAYS[potential_feast][0]
    except KeyError:
        is_hfd = False
        is_hfs = False
        feast_name = None
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
                 year=1,
                 month=1,
                 day=1,
                 hour=1):
        try:
            r"""Creates an object using the Astral or Google Geocoder.

            You need to choose whether to use Astral or Google Geocoder.
            To use the GoogleGeocoder you have to agree to GoogleGeocoder
            terms and license found here:
            https://developers.google.com/maps/documentation/geocoding/usage-limits#terms-of-use-restrictions"""

            if geocoder == 'astral':
                geo = Astral()
            elif geocoder == 'google':
                geo = GoogleGeocoder()
            else:
                raise Exception('Error: Unknown geocoder: {}'.format(geocoder))

            geo.solar_depression = 'civil'
            logging.debug('city_name is %s', city_name)
            logging.debug('trying to find the coordinates for %s', city_name)
            try:
                location = geo[city_name]
            except AstralError:
                print('Please wait...')
                time.sleep(2)
                try:
                    location = geo[city_name]
                except AstralError:
                    print('Please wait some more...')
                    time.sleep(2)
                    try:
                        location = geo[city_name]
                    except AstralError:
                        raise Exception(
                            'The Geocoder ({}) is having a fit.'
                            # 'GoogleGeocoder is having a fit. '
                            "Or the location really can't be found.".format(
                                geo))
        except KeyError:
            raise Exception(
                'Error: That city is not found. Please try another.')
        self.location = location

        # If no date input it given, defaults to the current date and time.
        if year == month == day == hour == 1:
            logging.debug('No date input given.')
            self.g_time = self._set_g_time_now()
        else:
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
            astral_geo = Astral()
            # google_geo = GoogleGeocoder()
            astral_geo.solar_depression = 'civil'
            # google_geo.solar_depression = 'civil'
            location = astral_geo[city_name]
            # location = google_geo[city_name]
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
                if unknown_moon == known_moon:
                    logging.debug('stage 1')
                    logging.debug('known_moon equals unknown_moon')
                    logging.debug('returning key %s', key)
                    return key
                elif unknown_moon < known_moon:
                    logging.debug('stage 2')
                    logging.debug('known_moon is later than unknown_moon')
                    continue
                elif unknown_moon > known_moon:
                    logging.debug('stage 3')
                    delta = unknown_moon - known_moon
                    logging.debug('delta is %s', delta)
                    if delta > datetime.timedelta(days=30):
                        logging.debug('stage 4')
                        logging.debug('delta (%s) is greater than 30', delta)
                        continue
                    elif delta <= datetime.timedelta(days=30):
                        logging.debug('stage 5')
                        logging.debug('saving potential key %s', key)
                        potential_keys.append(key)
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
        else:
            self.aviv_barley = None

        # Find out if it's a High Feast Day or a Sabbath.
        feast_test = test_is_feast(b_month, b_day)

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


def demo():
    """Gets the current information of a city. Format: 'City, Country'."""
    try:
        print('Please enter the name of the city and the country. '
              'Example: Jerusalem, Israel')
        entry = input()
        if not entry:
            raise ValueError('Error: Empty string')
    except ValueError:
        print('You failed to provide your location.')
        print('Try again.')
        print('Example: Manila')
    else:
        logging.debug('entry is %s', entry)
        try:
            city = BibTime(entry)
        except AstralError:
            print('Please wait.', end='')
            time.sleep(2)
            try:
                city = BibTime(entry)
            except AstralError:
                print('.', end='')
                time.sleep(2)
                try:
                    city = BibTime(entry)
                except AstralError:
                    print('.')
                    time.sleep(2)
                    try:
                        city = BibTime(entry)
                    except AstralError:
                        raise Exception(
                            'Error: Still not working. '
                            'Please try again if you are certain of the '
                            'spelling.\n'
                            'Otherwise, please try another location.')
        c_loc = city.b_location
        c_btime = city.b_time
        logging.debug('Creating object %s', entry)
        print('\nThe chosen location is {}'.format(entry))
        print('The gregorian date in {} is now {}'.format(
            entry, c_loc.g_time.strftime('%Y-%m-%d')))
        print('The gregorian time in {} is now {}'.format(
            entry, c_loc.g_time.strftime('%H:%M')))
        if c_loc.sun_info['has_set'] is True:
            print('The sun is down')
            print('The sunset was at {}'.format(
                c_loc.sun_info['has_set'].strftime('%H:%M')))
        if c_loc.sun_info['has_risen'] is False:
            print('The sun has not yet risen')
            print('The sunrise will be at {}'.format(
                c_loc.sun_info['sunrise'].strftime('%H:%M')))
        # If sun_has_set is None, it should be in the morning. Therefore, check
        # if the sun has risen.
        if c_loc.sun_info['has_set'] is None and c_loc.sun_info['has_risen'] is True:
            print('The sun is still up')
            print('The sunset will be at {}'.format(
                c_loc.sun_info['sunset'].strftime('%H:%M')))
        # If sun_info['has_risen'] is None it should be in the afternoon. Therefore,
        # check if the sun has set.
        if c_loc.sun_info['has_risen'] is None and c_loc.sun_info['has_set'] is False:
            print('The sun is still up')
            print('The sunset will be at {}'.format(
                c_loc.sun_info['sunset'].strftime('%H:%M')))
        print('Today is the {} day of the week'.format(c_btime.weekday))
        print('The biblical date in {} is now:\n'
              'The {} day of the {} month in the year {}.'.format(
                  entry, c_btime.day_name, c_btime.month_name, c_btime.year))
        # if x.is_estimated is True:
        #     print('The date and time is estimated'
        #           ' and is NOT based on actual observations')
        # if x.is_known is True:
        #     print('The date and time is certain'
        #           ' and is based on actual observations')
        if c_btime.sabbath.sabbath is True:
            if c_btime.sabbath.weekly_sabbath is True:
                print('It is now the weekly Sabbath')
            elif c_btime.sabbath.holy_day_of_rest is True:
                print('It is now a High Feast Sabbath.')
            else:
                print('Error: Unkown Sabbath')
        if c_btime.sabbath.high_feast_day is True:
            print('It is now the {}'.format(c_btime.sabbath.feast_name))
            if c_btime.sabbath.holy_day_of_rest is True:
                print('It is a Holy Day of Convocation where no work '
                      'shall be done.')
            elif c_btime.sabbath.holy_day_of_rest is False:
                print('It is not a Holy Day of Convocation.')
        if c_btime.month == 12:
            if city.aviv_barley is True:
                print('The barley in the land of Israel is aviv!')
                print('The next new moon will begin the new year.')
            else:
                print('The barley in the land of Israel is NOT yet aviv.')
                print('There will be a 13th month if it is not aviv before '
                      'the end of the month.')


if __name__ == '__main__':
    main(sys.argv[1:])
