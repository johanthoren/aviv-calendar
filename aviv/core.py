#!/usr/bin/env python3

# -- BEGINNING OF INTRO: -- #

# A SHORT DESCRIPTION:
# Aviv Calendar, a small program to find out what day it is according
# to the Biblical calendar. Also attempts to let you know about
# the Feasts of the Lord as well as the Sabbath.

# CURRENT STATUS:
# Currently, it only decides what day of week it is according to
# biblical timekeeping. It will also tell you some details about
# sunset and sunrise and wether or not is is a weekly sabbath.

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

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

# Define the traditional names of the biblical months of the year.
trad_month_names = ('Nisan', 'Iyyar', 'Sivan', 'Tammuz', 'Av', 'Elul',
                    'Tishri', 'Marheshvan', 'Kislev', 'Tevet', 'Shvat', 'Adar',
                    'Adar (2)')

# Define the biblical months.
bib_months = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th',
              '10th', '11th', '12th', '13th')

# Define the gregorian weekdays.
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

# List of feast days that are not biblically commanded to keep.
fixed_feast_days = {
    '9, 25', ('1st day of Hanukkah', False), '12, 14', ('Purim', False)
}
# TODO: Feast days that are relative to weekday, or that span over
# months (like Hanukkah).
# List of high feast days. True if they are considered
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
    # Download the file from `https://www.avivcalendar.com/latest_data`
    # and save it locally under `latest_data.py`:
    url = 'https://www.avivcalendar.com/latest-data'
    file = os.path.join(sys.path[0], 'latest_data.py')
    with urllib.request.urlopen(url) as response, open(file, 'wb') as out_file:
        d = response.read()
        out_file.write(d)
        out_file.close()


db_file = os.path.join(sys.path[0], 'current_data')


def combine_data():
    get_latest_data()
    import latest_data
    import hist_data
    db = shelve.open(db_file)
    db.clear()

    def merge_two_dicts(x, y):
        z = x.copy()  # start with x's keys and values
        z.update(y)  # modifies z with y's keys and values & returns None
        return z

    now_known_moons = merge_two_dicts(latest_data.last_known_moon,
                                      hist_data.known_moons)
    now_estimated_moons = merge_two_dicts(latest_data.next_estimated_moon,
                                          hist_data.estimated_moons)
    db['known_moons'] = now_known_moons
    db['estimated_moons'] = now_estimated_moons
    db['aviv_barley'] = latest_data.aviv_barley
    db.close()


combine_data()

db = shelve.open(db_file)
known_moons = db['known_moons']
estimated_moons = db['estimated_moons']
aviv_barley = db['aviv_barley']


# Creates a datetime object from key (k). First tries to find the month in the
# hist_data.known_moons and tries hist_data.estimated_moons as backup. Also
# sets the value of the attribute is_known to reflect wether or not it was
# found among the known (and therefore confirmed) moons or if it's an
# estimated guess.
# Note that most historical moons will always be estimated.
# Keys need to be in the form of YYYYMM (example: 600101).
def datetime_from_key(k):
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


# This function attempts to create a BibDay object given a gregorian
# date. Example d = 2017, 1, 1
def bibday_from_g_date(year, month, day):
    if year <= 4000:
        print('Error: Year value lower than 4000. Not searchable.')
        raise IndexError


def test_year(year):
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


def test_month(month):
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


def test_day(day, length):
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


def test_is_feast(month, day):
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


def test_is_sabbath(weekday):
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


class BibMonth(BibCalItem):
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

    def is_aviv(self):
        if self.end_g_date.year == datetime.datetime.now().year:
            if self.month >= 11:
                pass


class BibDay(BibCalItem):
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


class BibHour(BibCalItem):
    def __init__(self, year, month, day, hour):
        pass


# Creates the object BibLocation which takes the argument of a city name
# as a string. Note that only major capitals and some cities in U.S will work.
# Example: 'sthlm = BibLocation('Stockholm)' <- Creates an object with the name
# 'sthlm'.
# Example usage: 'sthlm.weekday' <- Gives back the day of week as a string.
# Example usage: 'sthlm.sabbath' <- Gives back if it's a sabbath as boolean.
class BibLocation:
    def __init__(self, city_name):
        self.city_name = city_name
        self.astral_city = Astral()[city_name]
        #  The number of degrees the sun must be below the horizon for the
        #  dawn/dusk calculation. Can either be set as a number of degrees
        #  below the horizon or as one of the following strings:
        #  'civil', 'nautical' or 'astronomical'. Can also be set to a
        #  floating number, representing the degrees of depression below
        #  the horizon.
        self.solar_depression = 'civil'

        #    def sun(self):
        # Uses the timezone of the given location to fetch the solar data.
        # This solution could probably be prettier. By default astral uses
        # UTC (I think...) as timezone.
        self.daily_sun = self.astral_city.sun(
            date=datetime.datetime.now(self.astral_city.tz), local=True)
        # Get the relevant data.
        self.daily_sunset = self.daily_sun['sunset']
        self.daily_sunrise = self.daily_sun['sunrise']
        # Before I set microsecond=0 I had trouble comparing the time_now
        # with daily_sunset below.
        self.time_now = datetime.datetime.now(self.astral_city.tz).replace(
            tzinfo=self.astral_city.tzinfo, microsecond=0)

        # DONE: Check if it's past midnight but before noon. If TRUE, then
        #       the time for the sunset should be adjusted and set at the
        #       time of the previous days' sunset.
        # TODO: Needs more testing.

        self.sun_has_set = None
        self.sun_has_risen = None

        # Check if it's past noon.
        if self.time_now.hour >= 12:
            self.after_noon = True
        elif self.time_now.hour < 12:
            self.after_noon = False
        else:
            raise Exception('Neither before or after 12.')

        # If after noon, Check if the sun has set.
        if self.after_noon is True:
            if self.time_now >= self.daily_sunset:
                self.sun_has_set = True
            elif self.time_now < self.daily_sunset:
                self.sun_has_set = False
            else:
                raise Exception('Unable to tell if the sun has set.')

        # If NOT in the afternoon, check if the sun has risen.
        elif self.after_noon is False:
            if self.time_now >= self.daily_sunrise:
                self.sun_has_risen = True
            elif self.time_now < self.daily_sunrise:
                self.sun_has_risen = False
            else:
                raise Exception('Unable to tell if the sun has risen.')

        else:
            raise Exception('Unable to tell if it is after noon or not.')

        # Now create a value to give to the weekday function.
        if self.sun_has_set is not None:
            if self.sun_has_set is True:
                self.daylight = False
            elif self.sun_has_set is False:
                self.daylight = True

        if self.sun_has_risen is not None:
            if self.sun_has_risen is True:
                self.daylight = True
            elif self.sun_has_risen is False:
                self.daylight = False

        # Misc. attributes.
        self.sunrise_hour = self.daily_sunrise.hour
        self.sunrise_minute = self.daily_sunrise.minute
        self.sunrise_second = self.daily_sunrise.second
        self.sunrise_timezone = self.daily_sunrise.tzname()
        self.sunrise_time = self.daily_sunrise.strftime("%H:%M")
        self.sunset_hour = self.daily_sunset.hour
        self.sunset_minute = self.daily_sunset.minute
        self.sunset_second = self.daily_sunset.second
        self.sunset_timezone = self.daily_sunset.tzname()
        self.sunset_time = self.daily_sunset.strftime("%H:%M")
        self.current_time = self.time_now.strftime("%H:%M")
        self.current_date = self.time_now.strftime("%Y-%m-%d")

        # Get the current weekday from datetime. Monday is 0, Sunday is 6.
        b_weekday_index = datetime.datetime.now(self.astral_city.tz).weekday()

        # Check if the sun has set and add 1 to get the correct day.
        if self.sun_has_set is not None:
            if self.sun_has_set is True:
                b_weekday_index += 1
                b_weekday_today = bib_weekdays[b_weekday_index]
            else:
                b_weekday_today = bib_weekdays[b_weekday_index]
        elif self.sun_has_set is None:
            b_weekday_today = bib_weekdays[b_weekday_index]
        else:
            raise Exception('''Unable to tell what day of week it is.
                Unclear if the sun has set.''')

        # Return the weekday string.
        self.weekday = b_weekday_today

        f = test_is_feast(self.time_now.month, self.time_now.day)

        self.is_hfd = f[0]
        self.is_hfs = f[1]
        self.feast_name = f[2]

        self.is_ws = test_is_sabbath(self.weekday)

        if self.is_hfs is True:  # hfs stands for high feast sabbath
            self.sabbath = self.is_hfs
        else:
            self.sabbath = self.is_ws


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
        location = BibLocation(entry)
        logging.debug('Creating object %s' % location)
        print('The chosen location is {}'.format(location.city_name))
        print('The gregorian date in {} is now {}'.format(
            location.city_name, location.current_date))
        print('The time in {} is now {}'.format(location.city_name,
                                                location.current_time))
        if location.sun_has_set is True:
            print('The sun is down')
            print('The sunset was at {}'.format(location.sunset_time))
        if location.sun_has_risen is False:
            print('The sun has not yet risen')
            print('The sunrise will be at {}'.format(location.sunrise_time))
        # If sun_has_set is None, it should be in the morning. Therefore, check
        # if the sun has risen.
        if location.sun_has_set is None and location.sun_has_risen is True:
            print('The sun is still up')
            print('The sunset will be at {}'.format(location.sunset_time))
        # If sun_has_risen is None it should be in the afternoon. Therefore,
        # check if the sun has set.
        if location.sun_has_risen is None and location.sun_has_set is False:
            print('The sun is still up')
            print('The sunset will be at {}'.format(location.sunset_time))
        print('Today is the {} day of the week'.format(location.weekday))
        if location.sabbath is True:
            if location.is_ws is True:
                print('It is now the weekly Sabbath')
            elif location.is_hfs is True:
                print('It is now a High Feast Sabbath.')
            else:
                print('Error: Unkown Sabbath')
    db.close()
