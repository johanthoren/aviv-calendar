#!/usr/bin/env python3

# Aviv Calendar, a small program to find out what day it is according
# to the Biblical calendar. Also attempts to let you know about
# the Feasts of the Lord as well as the Sabbath.

# Copyright (C) 2017 - 2018 Johan Thorén <johan@thoren.xyz>

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
from astral import Astral  # Using the builtin geocoder. Se Astral
                           # documentation for alternatives.
import logging

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


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
        daily_sun = self.astral_city.sun(
            date=datetime.datetime.now(self.astral_city.tz), local=True)
        # Get the relevant data.
        daily_sunset = daily_sun['sunset']
        daily_sunrise = daily_sun['sunrise']
        # Before I set microsecond=0 I had trouble comparing the time_now
        # with daily_sunset below.
        time_now = datetime.datetime.now(self.astral_city.tz).replace(
            tzinfo=self.astral_city.tzinfo, microsecond=0)

        # TODO: Check if it's past midnight but before noon. If TRUE, then
        #       the time for the sunset should be adjusted and set at the
        #       time of the previous days' sunset.

        # Check if the sun has set.
        if time_now > daily_sunset:
            self.sun_has_set = True
        else:
            self.sun_has_set = False
        # Misc. attributes.
        self.sunset_hour = daily_sunset.hour
        self.sunset_minute = daily_sunset.minute
        self.sunset_second = daily_sunset.second
        self.sunset_timezone = daily_sunset.tzname()
        self.sunset_time = daily_sunset.strftime("%H:%M")
        self.current_time = time_now.strftime("%H:%M")
        self.is_ws = False  # ws stands for weekly sabbath
        self.is_hs = False  # hs stands for high sabbath

    def weekday(self):
        # Get the current weekday from datetime. Monday is 0, Sunday is 6.
        self.sun()
        b_weekday_index = datetime.datetime.now(self.astral_city.tz).weekday()

        # Tuple containing the biblical weekday names. Simply refered to by
        # their number.
        b_weekdays = ('2nd', '3rd', '4th', '5th', '6th', '7th', '1st', '2nd')

        if self.sun_has_set is True:
            b_weekday_index += 1
            b_weekday_today = b_weekdays[b_weekday_index]
        else:
            b_weekday_today = b_weekdays[b_weekday_index]

        # Return the weekday string.
        self.weekday = b_weekday_today

    def weekly_sabbath(self):
        self.weekday()
        if self.weekday == '7th':
            self.is_ws = True  # ws stands for weekly Sabbath.
        else:
            self.is_ws = False
        # Check for high Sabbath and override to True if that's the case.
        if self.is_hs is True:
            self.sabbath = self.is_hs
        else:
            self.sabbath = self.is_ws

    def high_sabbath(self):
        self.weekday()
        logging.debug('It is a high sabbath.')
        self.sabbath = True

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
        print('The time in {} is now {}'.format(location.city_name,
                                                location.current_time))
        if location.sun_has_set is True:
            print('The sun is down')
            print('The sunset was at {}'.format(location.sunset_time))
        print('Today is the {} day of the week.'.format(location.weekday))
        if location.sabbath is True:
            if location.is_ws is True:
                print('It is now the weekly Sabbath')
            elif location.is_hs is True:
                print('It is now a high Sabbath')
            else:
                print('Error: Unkown Sabbath.')
