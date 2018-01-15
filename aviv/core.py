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
# from astral import Astral
from astral import GoogleGeocoder
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


class BibLocation:
    """Define a location. Takes city_name as argument.
       Also takes optional time as argument (which will
       usually be passed on from BibTime.)
       Arguments: city_name, year, month, day, hour.
       Example: s = BibLocation('Stockholm, Sweden', 2018, 1, 1, 12)"""

    def __init__(self, city_name, year=2018, month=1, day=1, hour=12):
        try:
            # astral_geo = Astral()
            google_geo = GoogleGeocoder()
            # astral_geo.solar_depression = 'civil'
            google_geo.solar_depression = 'civil'
            location = google_geo[city_name]
        except KeyError:
            raise Exception(
                'Error: That city is not found. Please try another.')
        self.location = location

        # The following attributes are set by `set_gtime` or `set_gtime_now`.
        self.gtime = self.set_gtime(year, month, day, hour)

        # The following attributes are set by `sun_status` function.
        self.sunrise = None
        self.sunset = None
        self.sun_has_set = None
        self.sun_has_risen = None
        self.daylight = None

        self.sun_status()

    def _get_entry(self):
        return 'The city name is set to {}'.format(self.location)

    def _set_entry(self, city_name):
        try:
            # astral_geo = Astral()
            google_geo = GoogleGeocoder()
            # astral_geo.solar_depression = 'civil'
            google_geo.solar_depression = 'civil'
            location = google_geo[city_name]
        except KeyError:
            raise Exception(
                'Error: That city is not found. Please try another.')
        self.location = location

    city = property(_get_entry, _set_entry)

    def set_gtime(self, year=2018, month=1, day=1, hour=12):
        """Gives the object a point in time."""
        gtime = datetime.datetime(year, month, day, hour, 0, 0,
                                  0).replace(tzinfo=self.location.tzinfo)
        return gtime

    def set_gtime_now(self):
        """Updates the g_datetime to reflect current time."""
        gtime = datetime.datetime.now(
            self.location.tz).replace(tzinfo=self.location.tzinfo)
        return gtime

    def sun_status(self):
        """Updates the sunrise and sunset status based on location and time."""
        gtime = self.gtime
        sun = self.location.sun(date=gtime, local=True)
        sunrise = sun['sunrise']
        sunset = sun['sunset']

        # The following might be unnecessary code:

        # def check_time_after_noon(gtime):
        #     """Checks if it is after noon or not and returns a boolean."""
        #     after_noon = (gtime.hour >= 12)
        #     return after_noon

        # after_noon = check_time_after_noon(gtime)

        # def sunset_or_sunrise(after_noon, gtime):
        #     """Checks if sun has risen or set depending on time of day."""
        #     sun_has_set, sun_has_risen = False, False
        #     if after_noon is True:
        #         sun_has_set = (gtime >= sunset)
        #         sun_has_risen = (gtime >= sunrise)
        #     elif after_noon is False:
        #         sun_has_risen = (gtime >= sunrise)
        #     return (sun_has_set, sun_has_risen)

        # sun_has_set = sunset_or_sunrise(after_noon, gtime)[0]
        # sun_has_risen = sunset_or_sunrise(after_noon, gtime)[1]

        # Instead just replace with this:
        sun_has_set, sun_has_risen = (gtime >= sunset), (gtime >= sunrise)

        def check_daylight(sun_has_set, sun_has_risen):
            """Checks if there is still daylight."""
            if sun_has_set is not None:
                daylight = not sun_has_set
            if sun_has_risen is not None:
                daylight = sun_has_risen
            return daylight

        daylight = check_daylight(sun_has_set, sun_has_risen)

        self.sunrise = sunrise
        self.sunset = sunset
        self.sun_has_set = sun_has_set
        self.sun_has_risen = sun_has_risen
        self.daylight = daylight

    def sun_status_now(self):
        """Updates the g_datetime to reflect current time and then the sun."""
        self.set_gtime_now()
        self.sun_status()


class BibTime:
    """Define biblical time and date.
       Needs a city name as a string.
       Takes optional time as an argument
       as year, month, day.
       Defaults to 2018, 1, 1.
       Example: m = BibTime('Manila')
       Example: s = BibTime('Skepplanda, Sweden', 2018, 2, 1)"""

    def __init__(self, city, year=2018, month=1, day=1):
        try:
            b_location = BibLocation(str(city), year, month, day)
        except ValueError:
            raise Exception('Error: Not a valid string.')
        b_location.set_gtime()
        b_location.sun_status()
        self.b_location = b_location
        self.b_time = self._set_b_time()

    def _set_b_time(self):
        """Tries to calculate the biblical time."""

        def _check_db_status():
            m_phase = self.b_location.location.moon_phase(
                date=self.b_location.gtime.date())

            if m_phase <= 2:
                combine_data()
            elif DB_EXISTS is False:
                combine_data()
            elif DB_MOD_TIME > 86400:
                combine_data()

        _check_db_status()

        # Import latest_data and initialize the database.
        import latest_data
        last_moon = latest_data.LAST_MOON
        last_moon_key = list(last_moon.keys())[0]

        def _calc_b_weekday():
            """Tries to calculate the day of week.
            Since the biblical day starts in the
            evening, 1 needs to be added if sun
            has set."""
            self.b_location.sun_status()
            b_weekday_index = self.b_location.gtime.weekday()
            sun_has_set = self.b_location.sun_has_set

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
            logging.debug('Entering the "test_current" function.')
            # Test wether or not we are looking for a current date.
            today = datetime.datetime.now(self.b_location.location.tz).replace(
                tzinfo=self.b_location.location.tzinfo).date()
            date_to_test = self.b_location.gtime.date()
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

            if today < date_to_test:
                if m_phase_today > m_phase_date_to_test:
                    current = False
            elif today > date_to_test:
                if m_phase_today > m_phase_date_to_test:
                    current = False
            elif today - date_to_test > datetime.timedelta(days=29):
                current = False
            elif date_to_test - today > datetime.timedelta(days=29):
                current = False
            else:
                current = True

            return current

        def _find_month(unknown_moon):
            i = 0
            x_moons = {**MOONS}
            m_phase = self.b_location.location.moon_phase(date=unknown_moon)
            list_of_tested_known_moons = []
            list_of_tested_keys = []
            for key in sorted(list(x_moons.keys())):
                logging.debug('there are %s more items to try',
                              len(x_moons.keys()))
                known_moon = datetime.date(x_moons[key][2], x_moons[key][3],
                                           x_moons[key][4])
                x_phase = self.b_location.location.moon_phase(date=known_moon)
                list_of_tested_keys.append(key)
                list_of_tested_known_moons.append(known_moon)
                i += 1
                if unknown_moon == known_moon:
                    logging.debug('stage 1')
                    return key
                elif unknown_moon > known_moon:
                    logging.debug('stage 2')
                    logging.debug('removing %s from the dictionary', key)
                    del x_moons[key]
                    continue
                elif unknown_moon < known_moon:
                    logging.debug('stage 3')
                    delta = unknown_moon - known_moon
                    logging.debug('delta is %s', delta)
                    if delta > datetime.timedelta(days=30):
                        logging.debug('stage 4')
                        logging.debug('delta (%s) is greater than 30', delta)
                        logging.debug('removing %s from the dictionary', key)
                        del x_moons[key]
                        continue
                    if unknown_moon.month == known_moon.month:
                        logging.debug('stage 5')
                        logging.debug(
                            'unknown_moon.month equals known_moon.month '
                            '(%s and %s)', unknown_moon.month,
                            known_moon.month)
                        if m_phase < x_phase:
                            logging.debug('stage 6')
                            logging.debug(
                                'm_phase is NOT greater than x_phase '
                                '(%s and %s)', m_phase, x_phase)
                            logging.debug('returning %s', key)
                            return key
                        logging.debug('stage 7')
                        logging.debug('m_phase is greater than x_phase '
                                      '(%s and %s)', m_phase, x_phase)
                        x_key = list_of_tested_keys[i - 2]
                        return x_key
                    elif unknown_moon.month - 1 == known_moon.month:
                        logging.debug('stage 8')
                        logging.debug(
                            'm.month - 1 is equal to known_moon.month '
                            '(%s and %s)', unknown_moon.month - 1,
                            known_moon.month)
                        if m_phase > x_phase:
                            logging.debug('stage 9')
                            logging.debug('m_phase is greater than x_phase '
                                          '(%s and %s)', m_phase, x_phase)
                            logging.debug('returning %s', key)
                            return key
                        logging.debug('stage 10')
                        logging.debug('m_phase is NOT greater than x_phase '
                                      '(%s and %s)', m_phase, x_phase)
                        continue
                    continue
                else:
                    key = None
                    return key

        def _get_moon_key(year, month):
            moon_key = int(str(year) + '{0:0=2d}'.format(month))
            return moon_key

        def _get_moon_from_date():
            current = _test_current()
            # If current is True, then try to find out the gregorian date of
            # the month using the last_moon_key.
            if current is True:
                g_month = datetime_from_key(last_moon_key)
                # If no such month exists in the database we need to try to
                # find the one that it most likely is.
                year = last_moon[last_moon_key][0]
                month = last_moon[last_moon_key][1]
                if g_month is None:
                    unknown_moon = self.b_location.gtime.date()
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
                unknown_moon = self.b_location.gtime.date()
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
            time_lapsed = self.b_location.gtime - month_start_time
            day = time_lapsed.days
            if self.b_location.sun_has_set is True:
                day += 1
            return day

        month_start_time = _set_month_start_time(x_month_year, x_month_month,
                                                 x_month_day)
        b_day = _set_day_of_month(month_start_time)

        if b_day > 30:
            raise Exception('Error: Day of Month greater than 30.')

        # Catch any false positives.
        def _catch_false_postitive(year, month):
            if month <= 12:
                moon_key = _get_moon_key(year, month)
                moon_key += 1
            elif month == 13:
                moon_key = int(str(year + 1) + '01')
            try:
                if MOONS[moon_key]:
                    logging.debug('%s (moon_key) found in MOONS', moon_key)
                    b_moon = datetime_from_key(moon_key)
                    b_year = b_moon[0].year
                    b_month = b_moon[0].month
                    b_day = b_moon[0].day
                    return (b_year, b_month, b_day)
            except KeyError:
                pass
            return None

        b_day_name = BIB_DAY_OF_MONTH[b_day - 1]
        b_month_trad_name = TRAD_MONTH_NAMES[b_month - 1]

        m_phase = self.b_location.location.moon_phase(
            date=self.b_location.gtime.date())
        confident = 2 <= m_phase <= 27

        if confident is False:
            x_month = _catch_false_postitive(b_year, b_month)
            month_start_time = _set_month_start_time(
                x_month[0], x_month[1], x_month[2])
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
        is_ws = test_is_sabbath(b_weekday)

        if is_hfs is True:  # hfs stands for high feast sabbath
            b_sabbath = is_hfs
        else:
            b_sabbath = is_ws

        class BibSabbath:
            def __init__(self, b_sabbath, is_hfd, is_hfs, is_ws):
                self.sabbath = b_sabbath
                self.high_feast_day = is_hfd
                self.holy_day_of_rest = is_hfs
                self.weekly_sabbath = is_ws

        class BibDay:
            def __init__(self, b_year, b_month, b_day, b_weekday):
                self.year = b_year
                self.month = b_month
                self.day = b_day
                self.weekday = b_weekday

        b_time = BibDay(b_year, b_month, b_day, b_weekday)
        b_time.sabbath = BibSabbath(b_sabbath, is_hfd, is_hfs, is_ws)
        return b_time


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
