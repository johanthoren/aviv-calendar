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

import logging
import datetime
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


# Define a new BaselineMonth, needs the biblical year as integer,
# the biblical month number (starting on 1) as integer, gregorian year as
# integer, gregorian month as integer (starting on 1), gregorian day of month,
# as integer (starting on 1) as well as the length in number of days.
# Example: bm_6017_10 = BaselineMonth(6017, 10, 2017, 12, 20, 29)
class BaselineMonth:
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

        # Check if the month is known.
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
                    logging.debug('%s i equal to 13' % self.month)
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


if __name__ == '__main__':
    # Run a simple example for testing purposes.
    month = BaselineMonth(*known_months[601412])
    print('The {} month of the year {} started at sunset '
          'on the gregorian date {}'.format(month.name, month.year,
                                            month.start_g_date))
    try:
        if month.last_name:
            print('The {}, and last day of the month, '
                  'started on the gregorian date {}'.format(
                      month.last_name, month.end_g_date))
    except AttributeError:
        print('Unable to say anything about the end of the month right now')
        print(
            'This might be because the following month is not in the database'
        )
    print('The traditional name of the {} month is {}'.format(
        month.name, month.trad_name))
