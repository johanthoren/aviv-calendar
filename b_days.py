#!/usr/bin/env python3

# Aviv Calendar, a small program to find out what day it is according
# to the Biblical calendar. Also attempts to let you know about
# the Feasts of the Lord as well as the Sabbath.

# Copyright (C) 2017 Johan Thorén <johan@thoren.xyz>

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

# Define the year. I'm starting at 2017, because I see no urgent use
# to keep track of old dates. This is first of all a tool to calculate
# the current time and holidays. Might be a future project to expand on
# this.
jewish_years = tuple(range(5777, 6761))
biblical_years = tuple(range(6017, 7001))

# Define the traditional names of the biblical months of the year.
jewish_months = {
    1: 'Nisan',
    2: 'Iyyar',
    3: 'Sivan',
    4: 'Tammuz',
    5: 'Av',
    6: 'Elul',
    7: 'Tishri',
    8: 'Marẖeshvan',
    9: 'Kislev',
    10: 'Tevet',
    11: 'Shvat',
    12: 'Adar',
    13: 'Adar (2)'
}

# Define the biblical months.
biblical_months = {
    1: '1st',
    2: '2nd',
    3: '3rd',
    4: '4th',
    5: '5th',
    6: '6th',
    7: '7th',
    8: '8th',
    9: '9th',
    10: '10th',
    11: '11th',
    12: '12th',
    13: '13th'
}

# Define the gregorian weekdays.
gregorian_weekday = {
    1: 'Sunday',
    2: 'Monday',
    3: 'Tuesday',
    4: 'Wednesday',
    5: 'Thursday',
    6: 'Friday',
    7: 'Saturday'
}

# Define the biblical weekdays. Wraps around inside
# the tuple to allow for gregorian day + 2 in calculation.
b_weekday = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '1st', '2nd')

# Define the biblical days of the months.
day_of_month = {
    1: '1st',
    2: '2nd',
    3: '3rd',
    4: '4th',
    5: '5th',
    6: '6th',
    7: '7th',
    8: '8th',
    9: '9th',
    10: '10th',
    11: '11th',
    12: '12th',
    13: '13th',
    14: '14th',
    15: '15th',
    16: '16th',
    17: '17th',
    18: '18th',
    19: '19th',
    20: '20th',
    21: '21st',
    22: '22nd',
    23: '23rd',
    24: '24th',
    25: '25th',
    26: '26th',
    27: '27th',
    28: '28th',
    29: '29th',
    30: '30th'
}
