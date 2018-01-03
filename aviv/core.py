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
from hist_data import known_months

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

# Define the traditional names of the biblical months of the year.
trad_month_names = ('Nisan', 'Iyyar', 'Sivan', 'Tammuz', 'Av', 'Elul',
                    'Tishri', 'Marẖeshvan', 'Kislev', 'Tevet', 'Shvat', 'Adar',
                    'Adar (2)')

# Define the biblical months.
bib_months = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th',
              '10th', '11th', '12th', '13th')

# Define the gregorian weekdays.
greg_weekday = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                'Friday', 'Saturday')

# Tuple containing the biblical weekday names. Simply refered to by
# their number.
bib_weekdays = ('2nd', '3rd', '4th', '5th', '6th', '7th', '1st', '2nd')

# Define the biblical days of the months.
bib_day_of_month = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
                    '9th', '10th', '11th', '12th', '13th', '14th', '15th',
                    '16th', '17th', '18th', '19th', '20th', '21st', '22nd',
                    '23rd', '24th', '25th', '26th', '27th', '28th', '29th',
                    '30th')


# Define a new BibMonth, needs the biblical year as integer,
# the biblical month number (starting on 1) as integer, gregorian year as
# integer, gregorian month as integer (starting on 1) and gregorian day of
# month, as integer (starting on 1).
# Example: bm_6017_10 = BibMonth(6017, 10, 2017, 12, 20)
class BibMonth:
    def __init__(self, year, month, start_g_year, start_g_month, start_g_day):
        # Make integers from the input.
        try:
            self.year = int(year)
            self.month = int(month)
            self.start_g_year = int(start_g_year)
            self.start_g_month = int(start_g_month)
            self.start_g_day = int(start_g_day)
            # There has got to be a better way to do this without
            # repeating the 'raise IndexError' for every if statement.
            if self.year <= 6000:
                print('Error: Year value lower than 6000.')
                raise IndexError
            if self.month <= 0:
                print('Error: Month value lower than 1.')
                raise IndexError
            elif self.month > 13:
                print('Error: Month value higher than 13.')
                raise IndexError
            if self.start_g_year <= 2000:
                print('Error: Gregorian Year value lower than 6000.')
                raise IndexError
            if self.start_g_month <= 0:
                print('Error: Starting Month value lower than 1.')
                raise IndexError
            elif self.start_g_month > 12:
                print('Error: Starting Month value higher than 12.')
            if self.start_g_day <= 0:
                print('Error: Starting Day value lower than 1.')
                raise IndexError
            elif self.start_g_day > 31:
                print('Error: Starting Day value higher than 31.')
                raise IndexError
        except ValueError:
            print('Error: Could not convert the value to an integer.')
        except IndexError:
            print('Error: The specified value is out of the allowed range.')
        # Define the traditional name of the month.
        self.name = bib_months[self.month - 1]
        self.trad_name = trad_month_names[self.month - 1]
        self.first_name = bib_day_of_month[0]
        # Make a datetime.date object from the gregorian integers.
        # start_g_date is defined as the gregorian date in which the sunset
        # started the new month.
        # Example: If the 10th month of the years starts on the evening of
        # December 20, 2017 the entry would be as defined in the example above.
        self.start_g_date = datetime.date(start_g_year, start_g_month,
                                          start_g_day)
        self.start_g_year = self.start_g_date.year
        self.start_g_month = self.start_g_date.month
        self.start_g_day = self.start_g_date.day

        def next_month(next_dict_key):
            logging.debug('entering get_next_month function')
            year = known_months[next_dict_key][2]
            logging.debug('year is set to %s' % year)
            month = known_months[next_dict_key][3]
            logging.debug('month is set to %s' % month)
            day = known_months[next_dict_key][4]
            logging.debug('day is set to %s' % day)
            next_month_g_start_date = datetime.date(year, month, day)
            logging.debug('next_month_g_start_date is set to %s' %
                          next_month_g_start_date)
            return next_month_g_start_date

        def get_end_g_date(d):
            self.end_g_date = d - datetime.timedelta(days=1)
            logging.debug('self.end_g_date is set to %s' % self.end_g_date)
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
            logging.debug('entering get_length function')
            self.length = (end_d - start_d).days + 1
            logging.debug('Returning self.length as %s' % self.length)
            return self.length

        # Join the year and the month to create an integer key for the
        # dictionary in hist_data.known_months.
        self.dict_key = int(str(self.year) + '{0:0=2d}'.format(self.month))
        logging.debug('The dictionary key is %s' % self.dict_key)

        # Check if the month is in the database of known_months.
        # Primary reason for doing this is because we want to get the data
        # on the next month so that we can calculate the end date, and thus
        # the length.
        try:
            if known_months[self.dict_key]:
                logging.debug('%s exists in known_months' % self.dict_key)

                if 0 < self.month <= 11:
                    logging.debug(
                        '%s i greater than 0 and lesser than or equal to 11' %
                        self.month)
                    logging.debug('Will try to add 1 to the index')
                    logging.debug('to get the value of the next month')
                    next_dict_key = self.dict_key + 1
                elif self.month == 12:
                    logging.debug('%s i equal to 12' % self.month)
                    logging.debug('Will check if there is a 13th month.')
                    try:
                        if known_months[self.dict_key + 1]:
                            logging.debug('The 13th month exists.')
                            next_dict_key = self.dict_key + 1
                            logging.debug(
                                'The next month key is %s' % next_dict_key)
                    except KeyError:
                        logging.debug('The 13th month does NOT exist.')
                        next_dict_key = int(str(self.year + 1) + '01')
                        logging.debug(
                            'The next month key is %s' % next_dict_key)
                elif self.month == 13:
                    logging.debug('%s is equal to 13' % self.month)
                    logging.debug(
                        '+1 on the year part of the id and reset month to 01')
                    next_dict_key = int(str(self.year + 1) + '01')
                    logging.debug('The next month key is %s' % next_dict_key)
        except KeyError:
            logging.debug('%s does NOT exist in known_months' % self.dict_key)
            logging.debug(
                'Unable to say anything about the next month right now.')
        try:
            if known_months[next_dict_key]:
                next_month_g_start_date = next_month(next_dict_key)
                self.end_g_date = get_end_g_date(next_month_g_start_date)
                self.length = get_length(self.start_g_date, self.end_g_date)
                self.last_name = bib_day_of_month[self.length - 1]
        except KeyError:
            logging.debug('%s does NOT exist in known_months' % next_dict_key)
            logging.debug(
                'Unable to say anything about the next month right now.')


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

    def sun(self):
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

    def weekday(self):
        self.sun()

        self.is_ws = False  # ws stands for weekly sabbath
        self.is_hfd = False  # hs stands for High Feast day

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

    def weekly_sabbath(self):
        self.weekday()
        if self.weekday == '7th':
            self.is_ws = True  # ws stands for weekly Sabbath.
        else:
            self.is_ws = False
        # Check for a High Feast day and override to True if that's the case.
        if self.is_hfd is True:
            self.sabbath = self.is_hfd
        else:
            self.sabbath = self.is_ws

    # The following function is basically just a placeholder for later code.
    def high_feast_day(self):
        self.weekday()
        self.is_hfd = True
        logging.debug('It is a High Feast day.')
        self.sabbath = True

    # The following function is basically just a placeholder for later code.
    def regular_day(self):
        self.weekday()
        logging.debug('It is a regular day.')
        self.sabbath = False


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
        location.weekly_sabbath()
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
            elif location.is_hfd is True:
                print('It is now a High Feast day, and therefore a Sabbath')
            else:
                print('Error: Unkown Sabbath')
