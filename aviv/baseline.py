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
trad_months = ('Nisan', 'Iyyar', 'Sivan', 'Tammuz', 'Av', 'Elul', 'Tishri',
               'Marẖeshvan', 'Kislev', 'Tevet', 'Shvat', 'Adar', 'Adar (2)')

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
    def __init__(self, year, month, start_g_year, start_g_month, start_g_day,
                 length):
        # Make integers from the input.
        self.year = int(year)
        self.month = int(month)
        self.length = int(length)
        # Define the traditional name of the month.
        self.trad_month = trad_months[self.month - 1]
        # Make a datetime.date object from the gregorian integers.
        self.start_g_date = datetime.date(start_g_year, start_g_month,
                                          start_g_day)
        self.start_g_year = self.start_g_date.year
        self.start_g_month = self.start_g_date.month
        self.start_g_day = self.start_g_date.day
