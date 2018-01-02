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

# This file contains some baseline months where gregorian time and
# biblical time can be defined for sure based on real observations.
import datetime

trad_years = tuple(range(5777, 6761))
bib_years = tuple(range(6017, 7001))

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

# Here follows a dictionary with some known months.
# The format for the key is YYYYMM where Y and M represents the Year
# and Month of the BIBLICAL month in question.

# The format for the value is a tuple of the following:
# BIBLICAL year, BIBLICAL month, GREGORIAN year of the first day of the
# BIBLICAL month (the GREGORIAN day on which the sunset signaled the new
# day), GREGORIAN month of that same day, GREGORIAN day of said day, the
# length of the BIBLICAL month in days.
known_months = {
    601609: (6016, 9, 2016, 11, 30, 30)
}

# Define a new BaselineMonth, needs the biblical year as integer,
# the biblical month number (starting on 1) as integer, gregorian year as
# integer, gregorian month as integer (starting on 1), gregorian day of month,
# as integer (starting on 1) as well as the length in number of days.
# Example: bm_6017_10 = BaselineMonth(6017, 10, 2017, 12, 20, 29)
class BaselineMonth:
    def __init__(self, year, month, start_g_year, start_g_month, start_g_day,
                 length):
        # Make integers from the input.
        try:
            self.year = int(year)
            self.month = int(month)
            self.start_g_year = int(start_g_year)
            self.start_g_month = int(start_g_month)
            self.start_g_day = int(start_g_day)
            self.length = int(length)
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
            if self.length <= 27:
                print('Error: Length of month value lower than 28.')
                raise IndexError
            elif self.length > 30:
                print('Error: Length of month value higher than 30.')
                raise IndexError
        except ValueError:
            print('Error: Could not convert the value to an integer.')
        except IndexError:
            print('Error: The specified value is out of the allowed range.')
        # Define the traditional name of the month.
        self.name = bib_months[self.month - 1]
        self.trad_name = trad_month_names[self.month - 1]
        self.first_name = bib_day_of_month[0]
        self.last_name = bib_day_of_month[self.length - 1]
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

        # The first day of the biblical month equals to the gregorian day when
        # the sunset signaled the start of the biblical day. To keep
        # consistancy the last day of the month should therefore equal to the
        # gregorian day when the last day started. This way, there is no
        # overlap.
        # Example: The 9th month of 6016 ended Nov 30 of 2016. The last
        # day then continued until the sunset of Dec 1. But since the biblical
        # day starts with sunset, the gregorian date to be marked as the last
        # end date will be Nov 30.
        self.end_g_date = self.start_g_date + datetime.timedelta(
            days=self.length - 1)



bm = BaselineMonth(*known_months[601609])
print(bm)

if __name__ == '__main__':
    # Run a simple example for testing purposes.
    bm_6016_09 = BaselineMonth(6016, 9, 2016, 11, 30, 30)
    month = bm_6016_09
    print('The {} month of the year {} started at sunset '
          'on the gregorian date {}'.format(month.name, month.year,
                                            month.start_g_date))
    print('The {}, and last day of the month, '
          'started on the gregorian date {}'.format(month.last_name,
                                                    month.end_g_date))
    print('The traditional name of the {} month is {}'.format(
        month.name, month.trad_name))
