#!/usr/bin/env python3

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
from astral import Astral
import logging
import urllib.request
import os
import sys
import shelve
import hist_data

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

# Define the traditional names of the biblical months of the year.
# These are not per definition biblical, rather they come from the exile
# in Babylon.
trad_month_names = ('Nisan', 'Iyyar', 'Sivan', 'Tammuz', 'Av', 'Elul',
                    'Tishri', 'Marheshvan', 'Kislev', 'Tevet', 'Shvat', 'Adar',
                    'Adar (2)')

# Define the biblical months. 1st month could be named Aviv. Maybe later.
bib_months = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th',
              '10th', '11th', '12th', '13th')

# Define the gregorian weekdays. Wrapping for ease of index reference.
greg_weekday = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                'Saturday', 'Sunday', 'Monday')

# Tuple containing the biblical weekday names. Simply refered to by
# their number.
bib_weekdays = ('2nd', '3rd', '4th', '5th', '6th', '7th', '1st', '2nd')

# Define the biblical days of the months.
bib_day_of_month = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
                    '9th', '10th', '11th', '12th', '13th', '14th', '15th',
                    '16th', '17th', '18th', '19th', '20th', '21st', '22nd',
                    '23rd', '24th', '25th', '26th', '27th', '28th', '29th',
                    '30th')

# List of feast days that are NOT biblically commanded to keep but still
# of interest.
fixed_feast_days = {
    '9, 25', ('1st day of Hanukkah', False), '12, 14', ('Purim', False)
}
# TODO: Feast days that are relative to weekday, or that span over
# months (like Hanukkah).

# List of high feast days. Boolean True if they are considered
# "High days of convocation" where no work shall be done.
fixed_high_feast_days = {
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
    file = os.path.join(sys.path[0], 'latest_data.py')
    with urllib.request.urlopen(url) as response, open(file, 'wb') as out_file:
        d = response.read()
        out_file.write(d)
        out_file.close()


# Working with a db_file since we will be joining dictionaries from both git
# synced sources, as well as the latest_data.py that is retrieved from
# online.
db_file = os.path.join(sys.path[0], 'current_data')
db_actual_file = os.path.join(sys.path[0], 'current_data.db')
db_exists = os.path.exists(db_actual_file)
db_mod_time = os.path.getmtime(db_actual_file)


# Combine the data from hist_data (which is distributed with the source code),
# and data from latest_data, which is synced in get_latest_data above.
def combine_data():
    """Combine data from source code with data fetched online and create db."""
    get_latest_data()
    # I didn't want this import to be at the top of the file, since the
    # latest_data.py file will not exist on first run.
    # TODO: Is that the correct way to do it?
    import latest_data
    db = shelve.open(db_file)

    # Potentially needed clearing of db befor each run. Or is that overkill?
    # TODO: Needs testing.
    # db.clear()

    def merge_two_dicts(x, y):
        """Merges two dictionaries: historical data and latest data."""
        z = x.copy()  # start with x's keys and values
        z.update(y)  # modifies z with y's keys and values & returns None
        return z

    # Combine hist_data and latest_data and stash it in the database.
    now_known_moons = merge_two_dicts(latest_data.last_known_moon,
                                      hist_data.known_moons)
    now_estimated_moons = merge_two_dicts(latest_data.next_estimated_moon,
                                          hist_data.estimated_moons)

    db['known_moons'] = now_known_moons
    db['estimated_moons'] = now_estimated_moons
    db['aviv_barley'] = latest_data.aviv_barley
    db.close()


# Open the database, if none exists run the function to create one.
if not os.path.exists(db_file):
    combine_data()

# Get the database in order.
db = shelve.open(db_file)
known_moons = db['known_moons']
estimated_moons = db['estimated_moons']
aviv_barley = db['aviv_barley']
db.close()


# Creates a datetime object from key (k). First tries to find the month in the
# known_moons and tries estimated_moons as backup. Also sets the value of the
# attribute is_known to reflect wether or not it was found among the known
# (and therefore confirmed) moons or if it's an estimated guess.
# Note that most historical moons before 6001 will always be estimated.
# Keys need to be in the form of YYYYMM (example: 600101).
def datetime_from_key(k):
    """Tries to find the key in dictionaries of known and estimated moons."""
    try:
        if known_moons[k]:
            y = known_moons[k][2]
            m = known_moons[k][3]
            d = known_moons[k][4]
            date = datetime.date(y, m, d)
            is_known = True
            is_estimated = False
            # Returns as a tuple.
            return (is_known, is_estimated, date)
    except KeyError:
        try:
            if estimated_moons[k]:
                y = estimated_moons[k][2]
                m = estimated_moons[k][3]
                d = estimated_moons[k][4]
                date = datetime.date(y, m, d)
                is_known = False
                is_estimated = True
                # Returns as a tuple.
                return (is_known, is_estimated, date)
        except KeyError:
            is_known = False
            is_estimated = False
            # Returns as a tuple.
            return (is_known, is_estimated, None)


# This function tries to create a BibMonth object given a key (k).
# Keys need to be in the form of YYYYMM (example: 600101).
def bibitem_from_key(k):
    """Creates a BibCalItem object from a key (k) in the form YYYYMM."""
    try:
        if known_moons[k]:
            m = BibCalItem(*known_moons[k][0:1])
            return m
    except KeyError:
        try:
            if estimated_moons[k]:
                m = BibCalItem(*estimated_moons[k][0:1])
                return m
        except KeyError:
            return False


# This function tries to create a BibMonth object given a key (k).
# Keys need to be in the form of YYYYMM (example: 600101).
def bibmonth_from_key(k):
    """Creates a BibMonth object from a key (k) in the form of YYYYMM."""
    try:
        if known_moons[k]:
            m = BibMonth(*known_moons[k][0:2])
            return m
    except KeyError:
        try:
            if estimated_moons[k]:
                m = BibMonth(*estimated_moons[k][0:2])
                return m
        except KeyError:
            return None


# This function tests to see if a year is within the given range of this
# program.
def test_year(year):
    """Tests if a year is within the scope of the program. Namely 4001-8001."""
    y = int(year)
    try:
        if y <= 4000:
            print('Error: Year value lower than 4001. Not searchable.')
            raise IndexError
        elif y >= 8001:
            print('Error: Year value higher than 8000. Not searchable.')
        else:
            return y
    except ValueError or TypeError:
        print('Error: Incorrect Type or Value')


# This function tests to see if a month is within the given range of a year.
def test_month(month):
    """Tests if a month is within the range of a biblical year: 1-13."""
    m = int(month)
    try:
        if m <= 0:
            print('Error: Month value lower than 1.')
            raise IndexError
        elif m > 13:
            print('Error: Month value higher than 13.')
            raise IndexError
        else:
            return m
    except ValueError:
        print('Error: Not an integer.')
    except IndexError:
        print('Error: The specified value is out of the allowed range.')


# This function tests to see if a day is within the given range of a month.
def test_day(day, length):
    """Tests if a day is within the range of a biblical month: 1-30"""
    d = int(day)
    l = int(length)
    try:
        if d <= 0:
            print('Error: Day value lower than 1.')
            raise IndexError
        elif d > 30:
            print('Error: Day value higher than 30.')
            raise IndexError
        elif d > l:
            print('Error: The month did not contain that many days.')
            raise IndexError
        else:
            return d
    except ValueError:
        print('Error: Could not convert the value to an integer.')
    except IndexError:
        print('Error: The value is out of the allowed range.')


# This function tests to see if a day is a feast day.
# TODO: Work in progress.
def test_is_feast(month, day):
    """Tests if a day is a High Feast Day."""
    f = (month, day)
    try:
        if fixed_high_feast_days[f]:
            is_hfd = True
            is_hfs = fixed_high_feast_days[f][1]
            feast_name = fixed_high_feast_days[f][0]
    except KeyError:
        is_hfd = False
        is_hfs = False
        feast_name = None
    return (is_hfd, is_hfs, feast_name)


# This function tests to see if a day of the week is the weekly sabbath.
# Hint: Only tests if it's the 7th day.
def test_is_sabbath(weekday):
    """Tests if a weekday is the 7th, and thus a weekly sabbath."""
    try:
        if weekday == '7th':
            ws = True  # ws stands for weekly Sabbath.
        else:
            ws = False
        return ws
    except ValueError:
        print('Error: Wrong kind of input.')


# Base class for other classes.
# Every point in time needs to at least have a year defined.
# I can't imagine using anything larger like decade, century or
# millenia.
class BibCalItem:
    """Base class for date related objects."""

    def __init__(self, year):
        self.year = test_year(year)

        # Generate a yk (year_key) combining the year with 01 to get a
        # searchable key to get the first month.
        yk = int(str(self.year) + '01')

        try:
            d = datetime_from_key(yk)
            self.start_g_year = d[2].year
            self.start_g_month = d[2].month
            self.start_g_day = d[2].day
            self.start_g_date = d[2]
            self.is_known = d[0]
            self.is_estimated = d[1]
        except AttributeError:
            self.is_known = False
            self.is_estimated = False
        db.close()


class BibMonth(BibCalItem):
    """Represents a biblical month."""

    def __init__(self, year, month):
        # Make integers from the input.
        y = BibCalItem(year)
        self.year = y.year
        self.month = test_month(month)

        # ck = current (month) key
        # searchable key to get the month.
        ck = int(str(self.year) + '{0:0=2d}'.format(self.month))

        d = datetime_from_key(ck)

        self.is_known = d[0]
        self.is_estimated = d[1]
        self.start_g_date = d[2]
        self.start_g_day = d[2].day
        self.start_g_month = d[2].month
        self.start_g_year = d[2].year
        # Define the traditional name of the month.
        self.name = bib_months[self.month - 1]
        self.trad_name = trad_month_names[self.month - 1]
        self.first_name = bib_day_of_month[0]

        # nk = next (month) key
        def get_end_g_date(nk):
            """Tries to calculate the end date of self."""
            try:
                if known_moons[nk]:
                    y = known_moons[nk][2]
                    m = known_moons[nk][3]
                    d = known_moons[nk][4]
                    n = datetime.date(y, m, d)
                    self.end_g_date = n - datetime.timedelta(days=1)
                    return self.end_g_date
            except KeyError:
                if estimated_moons[nk]:
                    y = estimated_moons[nk][2]
                    m = estimated_moons[nk][3]
                    d = estimated_moons[nk][4]
                    n = datetime.date(y, m, d)
                    self.end_g_date = n - datetime.timedelta(days=1)
                    return self.end_g_date

        # The first day of the biblical month equals to the gregorian day when
        # the sunset signaled the start of the biblical day. To keep
        # consistancy the last day of the month should therefore equal to the
        # gregorian day when the last day started. This way, there is no
        # overlap.
        # Example: The 9th month of 6016 ended Nov 30 of 2016. The last
        # day then continued until the sunset of Dec 1. But since the biblical
        # day starts with sunset, the gregorian date to be marked as the last
        # end date will be Nov 30.

        def get_length(start_d, end_d):
            """Tries to calculate the length of self in days."""
            self.length = (end_d - start_d).days + 1
            return self.length

        # Check if the month is in the database of known_moons or
        # estimated_moons
        # Primary reason for doing this is because we want to get the data
        # on the next month so that we can calculate the end date, and thus
        # the length.
        if self.is_known is True:
            if 0 < self.month <= 11:
                nk = ck + 1
            elif self.month == 12:
                try:
                    if known_moons[ck + 1]:
                        nk = ck + 1
                except KeyError:
                    try:
                        if estimated_moons[ck + 1]:
                            nk = ck + 1
                    except KeyError:
                        nk = int(str(self.year + 1) + '01')
            if self.month == 13:
                nk = int(str(self.year + 1) + '01')
            try:
                if known_moons[nk]:
                    get_end_g_date(nk)
                    self.length = get_length(self.start_g_date,
                                             self.end_g_date)
                    logging.debug('self.length is %s' % self.length)
                    self.last_name = bib_day_of_month[self.length - 1]
            except KeyError:
                try:
                    if estimated_moons[nk]:
                        get_end_g_date(nk)
                        self.length = get_length(self.start_g_date,
                                                 self.end_g_date)
                        logging.debug('self.length is %s' % self.length)
                except KeyError:
                    self.length = None
        else:
            logging.debug('Unable to set the length.'
                          'Likely because next month is not known.')
            self.length = None
        db.close()

    def is_aviv(self):
        """Reads the latest_data to check if the Barley in Israel is Aviv."""
        if self.end_g_date.year == datetime.datetime.now().year:
            if self.month >= 11:
                pass


class BibDay(BibCalItem):
    """Represents a biblical day."""

    def __init__(self, year, month, day):
        # Make integers from the input.
        m = BibMonth(year, month)
        self.year = m.year
        self.month = m.month
        self.day = test_day(day, m.length)
        self.is_known = m.is_known
        self.is_estimated = m.is_estimated
        self.is_certain = None
        self.date = (self.year, self.month, self.day)
        self.start_g_date = m.start_g_date + datetime.timedelta(
            days=self.day - 1)

        self.is_ws = None  # ws stands for weekly sabbath
        self.is_hfd = None  # hs stands for High Feast day
        self.is_sabbath = None

        # Get the gregorian weekday from datetime. Monday is 0, Sunday is 6.
        y = self.start_g_date.year
        m = self.start_g_date.month
        d = self.start_g_date.day
        weekday_index = datetime.datetime(y, m, d).weekday()
        # +1 Since the day starts in the evening.
        b_weekday_today = bib_weekdays[weekday_index + 1]
        g_weekday_today = greg_weekday[weekday_index]

        # Return the weekday string.
        self.weekday = b_weekday_today
        self.g_weekday = g_weekday_today

        f = test_is_feast(self.month, self.day)

        self.is_hfd = f[0]
        self.is_hfs = f[1]
        self.feast_name = f[2]

        self.is_ws = test_is_sabbath(self.weekday)

        if self.is_hfs is True:  # hfs stands for high feast sabbath
            self.sabbath = self.is_hfs
        else:
            self.sabbath = self.is_ws


now = datetime.datetime.now().replace(microsecond=0)


class BibTime():
    def __init__(self,
                 city_name,
                 gyear=now.year,
                 gmonth=now.month,
                 gday=now.day,
                 ghour=now.hour,
                 gminute=now.minute,
                 gsecond=now.second,
                 gmicrosecond=0):
        location = Astral()[city_name]
        self.location = location
        self.location.solar_depression = 'civil'

        self.gyear = gyear
        self.gmonth = gmonth
        self.gday = gday
        self.ghour = ghour
        self.gminute = gminute
        self.gsecond = gsecond
        self.gmicrosecond = gmicrosecond

        self.gdatetime = datetime.datetime(self.gyear, self.gmonth, self.gday,
                                           self.ghour, self.gsecond,
                                           self.gmicrosecond).replace(
                                               tzinfo=self.location.tzinfo)

    def get_gdatetime_now(self):
        self.gdatetime = datetime.datetime.now(self.location.tz).replace(
            tzinfo=self.location.tzinfo)
        return self.gdatetime

    def sun_status(self):
        sun = self.location.sun(date=self.gdatetime, local=True)
        sunrise = sun['sunrise']
        sunset = sun['sunset']

        h = self.gdatetime.hour

        if h >= 12:
            after_noon = True
        elif h < 12:
            after_noon = False

        t = self.gdatetime

        sun_has_set = None
        sun_has_risen = None

        if after_noon is True:
            if t >= sunset:
                sun_has_set = True
            elif t < sunset:
                sun_has_set = False
            else:
                raise Exception('Error: Unable to tell if the sun has set.')

        elif after_noon is False:
            if t >= sunrise:
                sun_has_risen = True
            elif t < sunrise:
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
        self.gdatetime = self.get_gdatetime_now()
        self.sun_status()

    def bweekday(self):
        self.sun_status()
        bwi = self.gdatetime.weekday()  # biblical weekday index
        ss = self.sun_has_set

        if ss is not None:
            if ss is True:
                bwi += 1
                bweekday = bib_weekdays[bwi]
            else:
                bweekday = bib_weekdays[bwi]
        elif ss is None:
            bweekday = bib_weekdays[bwi]

        self.weekday = bweekday

    def bweekday_now(self):
        self.gdatetime = self.get_gdatetime_now()
        self.bweekday()

    def bdate(self):
        # Update the needed data.
        self.sun_status()
        gdate = self.gdatetime.date()
        mp = self.location.moon_phase(date=gdate)

        if mp <= 1:
            combine_data()
        elif db_exists is False:
            combine_data()
        elif db_mod_time > 86400:
            combine_data()

        # Import latest_data and initialize the database.
        import latest_data
        last_moon = latest_data.last_known_moon
        last_moon_key = list(last_moon.keys())[0]

        def find_month(m):
            i = 0
            list_of_known_moons = []
            logging.debug('created empty list list_of_known_moons')
            list_of_keys = []
            logging.debug('created empty list list_of_keys')
            for k, v in known_moons.items():
                km = datetime.date(v[2], v[3], v[4])
                list_of_known_moons.append(km)
                list_of_keys.append(k)
                i += 1
                if km == m:
                    logging.debug('%s is equal to %s, returning %s' % (km, m,
                                                                       k))
                    return k
                elif km > m:
                    logging.debug('%s (km) is greater than %s (m)' % (km, m))
                    if km.year == m.year:
                        logging.debug('%s is equal to %s' % (km.year, m.year))
                        if km.month == m.month:
                            logging.debug('%s is equal to %s' % (km.month,
                                                                 m.month))
                            pm = list_of_known_moons[i - 2]
                            logging.debug('pm is %s' % pm)
                            pk = list_of_keys[i - 2]
                            logging.debug('pk is %s' % pk)
                            if pm < m:
                                logging.debug('%s is lesser than %s' % (pm, m))
                                logging.debug('returning %s' % pk)
                                return pk
                            else:
                                logging.debug('%s is NOT lesser than %s' % (pm,
                                                                            m))
                                logging.debug('moving on (continue)')
                                continue
                        elif km.month > m.month:
                            logging.debug('%s is greater than %s' % (km.month,
                                                                     m.month))
                            logging.debug('moving on (continue)')
                            continue
                    if km.year > m.year:
                        logging.debug('%s is greater than %s' % (km.year,
                                                                 m.year))
                        logging.debug('moving on (continue)')
                        continue
                elif km < m:
                    logging.debug('%s (km) is lesser than %s (m)' % (km, m))
                    if km.year == m.year:
                        logging.debug('%s is equal to %s' % (km.year, m.year))
                        if km.month == m.month:
                            logging.debug('%s is equal to %s' % (km.month,
                                                                 m.month))
                            pm = list_of_known_moons[i - 2]
                            logging.debug('pm is %s' % pm)
                            pk = list_of_keys[i - 2]
                            logging.debug('pk is %s' % pk)
                            if pm < m:
                                logging.debug('%s is lesser than %s' % (pm, m))
                                logging.debug('returning %s' % pk)
                                return pk
                            else:
                                logging.debug('%s is NOT lesser than %s' % (pm,
                                                                            m))
                                logging.debug('moving on (continue)')
                                continue
                        elif km.month > m.month:
                            logging.debug('%s is greater than %s' % (km.month,
                                                                     m.month))
                            logging.debug('moving on (continue)')
                            continue
                    elif km.year > m.year:
                        logging.debug('%s is greater than %s' % (km.year,
                                                                 m.year))
                        logging.debug('moving on (continue)')
                        continue
                else:
                    logging.debug('%s is NOT lesser than %s' % (km, m))
                    i = 0
                    logging.debug('reset counter i to %s' % i)
                    list_of_estimated_moons = []
                    logging.debug('created empty list list_of_estimated_moons')
                    list_of_ekeys = []
                    logging.debug('created empty list list_of_ekeys')
                    for k, v in known_moons.items():
                        em = datetime.date(v[2], v[3], v[4])
                        list_of_estimated_moons.append(em)
                        list_of_ekeys.append(k)
                        i += 1
                        if km == m:
                            logging.debug('%s is equal to %s, returning %s' %
                                          (km, m, k))
                            return k
                        elif em > m:
                            if em.year == m.year:
                                if em.month == m.month:
                                    pem = list_of_estimated_moons[i - 2]
                                    pek = list_of_ekeys[i - 2]
                                    if pem < m:
                                        return pek
                                    else:
                                        continue
                                elif em.month > m.month:
                                    continue
                            if em.year > m.year:
                                continue
                        elif em < m:
                            if em.year == m.year:
                                if em.month == m.month:
                                    pem = list_of_estimated_moons[i - 2]
                                    pek = list_of_ekeys[i - 2]
                                    if pem < m:
                                        return pek
                                    else:
                                        continue
                                elif em.month > m.month:
                                    continue
                            elif em.year > m.year:
                                continue
                        else:
                            pm = None
                            return pm

        # Test wether or not we are looking for a current date.

        today = datetime.datetime.now(self.location.tz).replace(
            tzinfo=self.location.tzinfo)
        date_to_test = self.gdatetime.date()

        print('year today is {}'.format(today.year))
        print('month today is {}'.format(today.month))
        print('day today is {}'.format(today.day))

        if today.date() - date_to_test > datetime.timedelta(days=29):
            current = False
            logging.debug('current is %s' % current)
        elif date_to_test - today.date() > datetime.timedelta(days=29):
            current = False
            logging.debug('current is %s' % current)
        else:
            current = True
            logging.debug('current is %s' % current)

        def get_month_key(year, month):
            mk = int(str(year) + '{0:0=2d}'.format(month))
            return mk

        if current is True:
            bm = datetime_from_key(last_moon_key)
            if bm is None:
                m = self.gdatetime.date()
                print('bm is None, trying m. m is {}'.format(m))
                pm = find_month(m)
                bm = datetime_from_key(pm)
        elif current is False:
            m = self.gdatetime.date()
            print('m is {}'.format(m))
            pm = find_month(m)
            bm = datetime_from_key(pm)

        self.is_known = bm[0]
        self.is_estimated = bm[1]

        def set_month_start_time(y, m, d):
            month_start_time = datetime.datetime(y, m, d).replace(
                tzinfo=self.location.tzinfo, microsecond=0)
            return month_start_time

        def set_time_lapsed(t):
            time_lapsed = self.gdatetime - t
            d = time_lapsed.days  # day of month
            if self.sun_has_set is True:
                d += 1
            return d

        bm_y = bm[2].year
        logging.debug('bm_y is %s' % bm_y)
        bm_m = bm[2].month
        logging.debug('bm_m is %s' % bm_m)
        bm_d = bm[2].day
        logging.debug('bm_d is %s' % bm_d)

        month_start_time = set_month_start_time(bm_y, bm_m, bm_d)
        dom = set_time_lapsed(month_start_time)

        # Catch any false positives.
        def catch_false_postitive(year, month):
            if month <= 12:
                mk = get_month_key(year, month)
                mk = mk + 1
            elif month == 13:
                mk = int(str(year + 1) + '01')
            try:
                if known_moons[mk]:
                    logging.debug('%s (mk) found in known_moons' % mk)
                    bm = datetime_from_key(mk)
                    y = bm[2].year
                    m = bm[2].month
                    d = bm[2].day
                    return (y, m, d)
            except KeyError:
                try:
                    if estimated_moons[mk]:
                        logging.debug('%s (mk) found in estimated_moons' % mk)
                        bm = datetime_from_key(mk)
                        y = bm[2].year
                        m = bm[2].month
                        d = bm[2].day
                        return (y, m, d)
                except KeyError:
                    pass

        def set_month_attributes(dom, mk):
            self.day = dom
            self.day_name = bib_day_of_month[dom - 1]
            self.month_trad_name = trad_month_names[self.month - 1]

        set_month_attributes(dom, mk)

        if 2 < mp <= 27:
            confident = True
        elif mp <= 2:
            confident = False

        if confident is False:
            bm = catch_false_postitive(self.year, self.month)
            month_start_time = set_month_start_time(bm_y, bm_m, bm_d)
            dom = set_time_lapsed(month_start_time)

        self.confident = confident

        if self.month >= 11:
            self.aviv_barley = aviv_barley
        else:
            self.aviv_barley = None

        # Find out if it's a High Feast Day or a Sabbath.
        f = test_is_feast(self.month, self.day)

        self.is_hfd = f[0]
        self.is_hfs = f[1]

        self.feast_day = self.is_hfd
        self.feast_name = f[2]

        self.weekday = self.bweekday()
        self.is_ws = test_is_sabbath(self.weekday)

        if self.is_hfs is True:  # hfs stands for high feast sabbath
            self.sabbath = self.is_hfs
        else:
            self.sabbath = self.is_ws

    def bdate_now(self):
        self.sun_status_now()
        self.bdate()


if __name__ == '__main__':
    try:
        print('Please enter the name of the city.')
        entry = input()
        if not entry:
            raise ValueError('Empty string')
    except ValueError:
        print('You failed to provide your location.')
        print('Try again.')
        print('Example: Manila')
    else:
        logging.debug('entry is %s' % entry)
        x = BibTime(entry)
        x.bdate_now()
        x.bweekday_now()
        logging.debug('Creating object %s' % x)
        print('The chosen location is {}'.format(x.location.name))
        print('The gregorian date in {} is now {}'.format(
            x.location.name, x.gdatetime.strftime('%Y-%m-%d')))
        print('The time in {} is now {}'.format(x.location.name,
                                                x.gdatetime.strftime('%H:%M')))
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
            print(
                'The sunset will be at {}'.format(x.sunset.strftime('%H:%M')))
        # If sun_has_risen is None it should be in the afternoon. Therefore,
        # check if the sun has set.
        if x.sun_has_risen is None and x.sun_has_set is False:
            print('The sun is still up')
            print(
                'The sunset will be at {}'.format(x.sunset.strftime('%H:%M')))
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
            if x.aviv_barley is False:
                print('The barley in the land of Israel is NOT yet aviv.')
                print('There will be a 13th month if it is not aviv before '
                      'the end of the month.')
            if x.aviv_barley is True:
                print('The barley in the land of Israel is aviv!')
                print('The next new moon will begin the new year.')
