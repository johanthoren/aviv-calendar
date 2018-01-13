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
# and sunrise and wether or not is is a weekly sabbath.

# COPYRIGHT:
# Copyright (C) 2017 - 2018 Johan Thorén <johan@thoren.xyz>

# LICENSE:
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# -- END OF INTRO -- #
import datetime
# Using the builtin geocoder. Se Astral documentation for alternatives.
import logging
import urllib.request
import os
import sys
import shelve
from astral import Astral
import hist_data

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

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
    '9, 25', ('1st day of Hanukkah', False), '12, 14', ('Purim', False)
}
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
DB_MOD_TIME = os.path.getmtime(DB_ACTUAL_FILE)


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
if not os.path.exists(DB_FILE):
    combine_data()

# Get the database in order.
DB = shelve.open(DB_FILE)
MOONS = DB['MOONS']
AVIV_BARLEY = DB['AVIV_BARLEY']
DB.close()


# Creates a datetime object from key (k). First tries to find the month in the
# ´MOONS´. Also sets the value of the attribute is_known to reflect wether or
# not it was based on observation (and therefore confirmed) or if it's an
# estimated guess.
# Note that most historical MOONS before 6001 will always be estimated.
# Keys need to be in the form of YYYYMM (example: 600101).
def datetime_from_key(k):
    """Tries to find the key in dictionary 'MOONS'."""
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


# This function tests to see if a year is within the given range of this
# program.
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


# This function tests to see if a month is within the given range of a year.
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


# This function tests to see if a day is within the given range of a month.
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


# This function tests to see if a day is a feast day.
# TODO: Work in progress.
def test_is_feast(month, day):
    """Tests if a day is a High Feast Day."""
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


# This function tests to see if a day of the week is the weekly sabbath.
# Hint: Only tests if it's the 7th day.
def test_is_sabbath(weekday):
    """Tests if a weekday is the 7th, and thus a weekly sabbath."""
    weekly_sabbath = False
    if weekday == '7th':
        weekly_sabbath = True
    return weekly_sabbath


# g_time_now = datetime.datetime.now().replace(microsecond=0)


class BibTime():
    """Define biblical time and date. Takes city_name and optional time."""
    def __init__(self, city_name, gyear=2018, gmonth=1, gday=1, ghour=12):
        try:
            location = Astral()[city_name]
        except KeyError:
            raise Exception(
                'Error: That city is not found. Please try another.')
        self.location = location

        time = datetime.datetime(gyear, gmonth, gday,
                                 ghour).replace(tzinfo=self.location.tzinfo)

        self.set_g_time(time)
        self.bdate()
        self.bweekday()

    def set_g_time(self, time):
        """Puts the different arguments into attributes."""
        self.g_year = time.year
        self.g_month = time.month
        self.g_day = time.day
        self.g_hour = time.hour
        self.g_datetime = time

    def get_g_datetime_now(self):
        t = datetime.datetime.now(
            self.location.tz).replace(tzinfo=self.location.tzinfo)
        self.set_g_time(t)
        return t

    def sun_status(self):
        sun = self.location.sun(date=self.g_datetime, local=True)
        sunrise = sun['sunrise']
        sunset = sun['sunset']

        if self.g_hour >= 12:
            after_noon = True
        elif self.g_hour < 12:
            after_noon = False

        sun_has_set = None
        sun_has_risen = None

        if after_noon is True:
            if self.g_datetime >= sunset:
                sun_has_set = True
            elif self.g_datetime < sunset:
                sun_has_set = False
            else:
                raise Exception('Error: Unable to tell if the sun has set.')

        elif after_noon is False:
            if self.g_datetime >= sunrise:
                sun_has_risen = True
            elif self.g_datetime < sunrise:
                sun_has_risen = False
            else:
                raise Exception('Error: Unable to tell if the sun has risen.')

        if sun_has_set is not None:
            if sun_has_set is True:
                daylight = False
            elif sun_has_set is False:
                daylight = True
        if sun_has_risen is not None:
            if sun_has_risen is True:
                daylight = True
            elif sun_has_risen is False:
                daylight = False

        self.sunrise = sunrise
        self.sunset = sunset
        self.sun_has_set = sun_has_set
        self.sun_has_risen = sun_has_risen
        self.daylight = daylight

    def sun_status_now(self):
        self.g_datetime = self.get_g_datetime_now()
        self.sun_status()

    def bweekday(self):
        self.sun_status()
        bwi = self.g_datetime.weekday()  # biblical weekday index
        ss = self.sun_has_set

        if ss is not None:
            if ss is True:
                bwi += 1
                bweekday = BIB_WEEKDAYS[bwi]
            else:
                bweekday = BIB_WEEKDAYS[bwi]
        elif ss is None:
            bweekday = BIB_WEEKDAYS[bwi]

        self.weekday = bweekday

    def bweekday_now(self):
        self.g_datetime = self.get_g_datetime_now()
        self.bweekday()

    def bdate(self):
        # Update the needed data.
        self.sun_status()
        m_phase = self.location.moon_phase(date=self.g_datetime.date())

        if m_phase <= 2:
            combine_data()
        elif DB_EXISTS is False:
            combine_data()
        elif DB_MOD_TIME > 86400:
            combine_data()

        def get_moon_phases():
            logging.debug('Entering the "test_current" function.')
            # Test wether or not we are looking for a current date.
            today = datetime.datetime.now(
                self.location.tz).replace(tzinfo=self.location.tzinfo).date()
            date_to_test = self.g_datetime.date()
            m_phase_today = self.location.moon_phase(date=today)
            m_phase_date_to_test = self.location.moon_phase(date=date_to_test)
            return (today, m_phase_today, date_to_test, m_phase_date_to_test)

        def test_current():
            m = get_moon_phases()
            today = m[0]
            m_phase_today = m[1]
            date_to_test = m[2]
            m_phase_date_to_test = m[3]

            current = False
            if today < date_to_test:
                logging.debug('%s (today) is lesser than %s (date_to_test)' %
                              (today, date_to_test))
                if m_phase_today > m_phase_date_to_test:
                    logging.debug('%s (m_phase_today)is greater '
                                  'than %s(m_phase_date_to_test)' %
                                  (m_phase_today, m_phase_date_to_test))
                    current = False
            elif today > date_to_test:
                logging.debug('%s (today) is greater than %s (date_to_test)' %
                              (today, date_to_test))
                if m_phase_today > m_phase_date_to_test:
                    logging.debug('%s (m_phase_today)is greater '
                                  'than %s(m_phase_date_to_test)' %
                                  (m_phase_today, m_phase_date_to_test))
                    current = False
            elif today - date_to_test > datetime.timedelta(days=29):
                current = False
                logging.debug('current is %s' % current)
            elif date_to_test - today > datetime.timedelta(days=29):
                current = False
                logging.debug('current is %s' % current)
            else:
                current = True
                logging.debug('current is %s' % current)
            return current

        # Import latest_data and initialize the database.
        import latest_data
        LAST_MOON = latest_data.LAST_MOON
        last_moon_key = list(LAST_MOON.keys())[0]

        def find_month(m):
            i = 0
            x_MOONS = {**MOONS}
            m_phase = self.location.moon_phase(date=m)
            list_of_tested_known_MOONS = []
            logging.debug('created empty list list_of_MOONS')
            list_of_tested_keys = []
            logging.debug('created empty list list_of_keys')
            for key in sorted(list(x_MOONS.keys())):
                logging.debug(
                    'there are %s more items to try' % len(x_MOONS.keys()))
                known_moon = datetime.date(x_MOONS[key][2], x_MOONS[key][3],
                                           x_MOONS[key][4])
                x_phase = self.location.moon_phase(date=known_moon)
                list_of_tested_keys.append(key)
                list_of_tested_known_MOONS.append(known_moon)
                i += 1
                if m == known_moon:
                    logging.debug('stage 1')
                    return key
                elif m > known_moon:
                    logging.debug('stage 2')
                    logging.debug('removing %s from the dictionary' % key)
                    del x_MOONS[key]
                    continue
                elif m < known_moon:
                    logging.debug('stage 3')
                    delta = m - known_moon
                    logging.debug('delta is %s' % delta)
                    if delta > datetime.timedelta(days=30):
                        logging.debug('stage 4')
                        logging.debug('delta (%s) is greater than 30' % delta)
                        logging.debug('removing %s from the dictionary' % key)
                        del x_MOONS[key]
                        continue
                    if m.month == known_moon.month:
                        logging.debug('stage 5')
                        logging.debug(
                            'm.month equals known_moon.month (%s and %s)' %
                            (m.month, known_moon.month))
                        if m_phase < x_phase:
                            logging.debug('stage 6')
                            logging.debug(
                                'm_phase is NOT greater than x_phase (%s and %s)'
                                % (m_phase, x_phase))
                            logging.debug('returning %s' % key)
                            return key
                        else:
                            logging.debug('stage 7')
                            logging.debug(
                                'm_phase is greater than x_phase (%s and %s)' %
                                (m_phase, x_phase))
                            x_key = list_of_tested_keys[i - 2]
                            return x_key
                    elif m.month - 1 == known_moon.month:
                        logging.debug('stage 8')
                        logging.debug(
                            'm.month - 1 is equal to known_moon.month (%s and %s)'
                            % (m.month - 1, known_moon.month))
                        if m_phase > x_phase:
                            logging.debug('stage 9')
                            logging.debug(
                                'm_phase is greater than x_phase (%s and %s)' %
                                (m_phase, x_phase))
                            logging.debug('returning %s' % key)
                            return key
                        else:
                            logging.debug('stage 10')
                            logging.debug(
                                'm_phase is NOT greater than x_phase (%s and %s)'
                                % (m_phase, x_phase))
                            continue
                else:
                    key = None
                    return key

        def get_month_key(year, month):
            moon_key = int(str(year) + '{0:0=2d}'.format(month))
            return moon_key

        current = test_current()

        def get_moon_from_date():
            # If current is True, then try to find out the gregorian date of
            # the month using the last_moon_key.
            g_month = None
            if current is True:
                g_month = datetime_from_key(last_moon_key)
                # If no such month exists in the database we need to try to
                # find the one that it most likely is.
                self.year = LAST_MOON[last_moon_key][0]
                self.month = LAST_MOON[last_moon_key][1]
                if g_month is None:
                    q = self.g_datetime.date()
                    print('g_month is None, trying q. q is {}'.format(q))
                    q_key = find_month(q)
                    logging.debug('q_key is now {}'.format(q_key))
                    g_month = datetime_from_key(q_key)
                    tmpstring = str(q_key)
                    self.year = int(tmpstring[0:4])
                    self.month = int(tmpstring[4::])

            else:
                q = self.g_datetime.date()
                print('q is {}'.format(q))
                q_key = find_month(q)
                logging.debug('q_key is now {}'.format(q_key))
                g_month = datetime_from_key(q_key)
                tmpstring = str(q_key)
                self.year = int(tmpstring[0:4])
                self.month = int(tmpstring[4::])

            return g_month

        g_month = get_moon_from_date()
        self.is_known = g_month[1]

        g_month_year = g_month[0].year
        logging.debug('g_month_year is %s' % g_month_year)
        g_month_month = g_month[0].month
        logging.debug('g_month_month is %s' % g_month_month)
        g_month_day = g_month[0].day
        logging.debug('g_month_day is %s' % g_month_day)

        def set_month_start_time(y, m, d):
            month_start_time = datetime.datetime(y, m, d).replace(
                tzinfo=self.location.tzinfo, microsecond=0)
            return month_start_time

        def set_time_lapsed(t):
            time_lapsed = self.g_datetime - t
            d = time_lapsed.days  # day of month
            if self.sun_has_set is True:
                d += 1
            return d

        month_start_time = set_month_start_time(g_month_year, g_month_month,
                                                g_month_day)
        dom = set_time_lapsed(month_start_time)
        if dom > 30:
            raise Exception('Error: Day of Month greater than 30.')

        # Catch any false positives.
        def catch_false_postitive(year, month):
            if month <= 12:
                mk = get_month_key(year, month)
                mk = mk + 1
            elif month == 13:
                mk = int(str(year + 1) + '01')
            try:
                if MOONS[mk]:
                    logging.debug('%s (mk) found in MOONS' % mk)
                    bm = datetime_from_key(mk)
                    y = bm[0].year
                    m = bm[0].month
                    d = bm[0].day
                    return (y, m, d)
            except KeyError:
                pass

        def set_month_attributes(dom):
            self.day = dom
            self.day_name = BIB_DAY_OF_MONTH[dom - 1]
            self.month_trad_name = TRAD_MONTH_NAMES[self.month - 1]

        set_month_attributes(dom)

        if 2 < m_phase <= 27:
            confident = True
        elif m_phase <= 2:
            confident = False

        if confident is False:
            g_month = catch_false_postitive(self.year, self.month)
            month_start_time = set_month_start_time(g_month_year,
                                                    g_month_month, g_month_day)
            dom = set_time_lapsed(month_start_time)

        self.confident = confident

        if self.month >= 11:
            self.AVIV_BARLEY = AVIV_BARLEY
        else:
            self.AVIV_BARLEY = None

        # Find out if it's a High Feast Day or a Sabbath.
        f = test_is_feast(self.month, self.day)

        self.is_hfd = f[0]
        self.is_hfs = f[1]

        self.feast_day = self.is_hfd
        self.feast_name = f[2]

        self.bweekday()
        self.is_ws = test_is_sabbath(self.weekday)

        if self.is_hfs is True:  # hfs stands for high feast sabbath
            self.sabbath = self.is_hfs
        else:
            self.sabbath = self.is_ws

    def bdate_now(self):
        self.sun_status_now()
        self.bweekday_now()
        self.bdate()


def main():
    try:
        print('Please enter the name of the city.')
        entry = input()
        if not entry:
            raise ValueError('Error: Empty string')
    except ValueError:
        print('You failed to provide your location.')
        print('Try again.')
        print('Example: Manila')
    else:
        logging.debug('entry is %s' % entry)
        x = BibTime(entry)
        logging.debug('Creating object %s' % x)
        print('The chosen location is {}'.format(x))
        print('The gregorian date in {} is now {}'.format(
            x.location.name, x.g_datetime.strftime('%Y-%m-%d')))
        print('The time in {} is now {}'.format(
            x.location.name, x.g_datetime.strftime('%H:%M')))
        if x.sun_has_set is True:
            print('The sun is down')
            print('The sunset was at {}'.format(x.sunset.strftime('%H:%M')))
        if x.sun_has_risen is False:
            print('The sun has not yet risen')
            print('The sunrise will be at {}'.format(
                x.sunrise.strftime('%H:%M')))
        # If sun_has_set is None, it should be in the morning. Therefore, check
        # if the sun has risen.
        if x.sun_has_set is None and x.sun_has_risen is True:
            print('The sun is still up')
            print('The sunset will be at {}'.format(
                x.sunset.strftime('%H:%M')))
        # If sun_has_risen is None it should be in the afternoon. Therefore,
        # check if the sun has set.
        if x.sun_has_risen is None and x.sun_has_set is False:
            print('The sun is still up')
            print('The sunset will be at {}'.format(
                x.sunset.strftime('%H:%M')))
        print('Today is the {} day of the week'.format(x.weekday))
        print('The biblical date in {} is now:\n'
              'The {} day of the {} month in the year {}.'.format(
                  x.location.name, x.day_name, x.month, x.year))
        # if x.is_estimated is True:
        #     print('The date and time is estimated'
        #           ' and is NOT based on actual observations')
        # if x.is_known is True:
        #     print('The date and time is certain'
        #           ' and is based on actual observations')
        if x.sabbath is True:
            if x.is_ws is True:
                print('It is now the weekly Sabbath')
            elif x.is_hfs is True:
                print('It is now a High Feast Sabbath.')
            else:
                print('Error: Unkown Sabbath')
        if x.feast_day is True:
            print('It is now the {}'.format(x.feast_name))
            if x.is_hfs is True:
                print('It is a Holy Day of Convocation where no work '
                      'shall be done.')
            elif x.is_hfs is False:
                print('It is not a Holy Day of Convocation.')
        if x.month == 12:
            if x.AVIV_BARLEY is False:
                print('The barley in the land of Israel is NOT yet aviv.')
                print('There will be a 13th month if it is not aviv before '
                      'the end of the month.')
            if x.AVIV_BARLEY is True:
                print('The barley in the land of Israel is aviv!')
                print('The next new moon will begin the new year.')


if __name__ == '__main__':
    main()
