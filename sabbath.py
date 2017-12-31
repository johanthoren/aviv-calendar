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
import datetime
from astral import Astral
import logging

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


# Creates the object BiblicalWeekday which takes the argument of a city name
# as a string. Note that only major capitals and some cities in U.S will work.
# Example: 'sthlm = BiblicalWeekday('Stockholm)' <- Creates the object.
# Example usage: 'sthlm.weekday' <- Gives back the day of week as a string.
# Example usage: 'sthlm.sabbath' <- Gives back if it's a weekly sabbath
# as boolean.
class BiblicalWeekday:
    def __init__(self, city_name):
        self.city_name = city_name
        logging.debug('city_name is set to %s' % city_name)
        a = Astral()
        a.solar_depression = 'civil'
        logging.debug('solar_depression set to %s' % a.solar_depression)
        city = a[self.city_name]
        logging.debug('city object contains %s' % city)
        # Defines the time that the sun sets
        # in the given location.
        daily_sun = city.sun(date=datetime.datetime.now(city.tz), local=True)
        daily_sunset = daily_sun['sunset']
        time_now = datetime.datetime.now(city.tz).replace(
            tzinfo=daily_sunset.tzinfo, microsecond=0)
        logging.debug("The 'time_now' variable is now set to %s" % time_now)
        logging.debug(
            "The 'daily_sunset()' variable is now set to %s" % daily_sunset)

        # TODO: Check if it's past midnight but before noon. If TRUE, then
        #       the time for the sunset should be adjusted and set at the
        #       time of the previous days' sunset.

        # Check if the sun has set.
        if time_now > daily_sunset:
            self.sun_has_set = True
            logging.debug(
                'Setting self.sun_has_set to {}.'.format(self.sun_has_set))
        else:
            self.sun_has_set = False
            logging.debug(
                'Setting self.sun_has_set to {}.'.format(self.sun_has_set))

        self.sunset_hour = daily_sunset.hour
        self.sunset_minute = daily_sunset.minute
        self.sunset_second = daily_sunset.second
        self.sunset_timezone = daily_sunset.tzname()
        self.sunset_time = daily_sunset.strftime("%H:%M")
        self.current_time = time_now.strftime("%H:%M")

        b_weekdays = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '1st',
                      '2nd')

        day_now = datetime.datetime.now(city.tz).weekday()
        b_weekday_index = day_now + 1
        logging.debug('b_weekday_index is now set to %s' % b_weekday_index)

        if self.sun_has_set is True:
            b_weekday_index += 1
            b_weekday_today = b_weekdays[b_weekday_index]
        else:
            b_weekday_today = b_weekdays[b_weekday_index]

        if b_weekday_index == 6:
            is_ws = True
            logging.debug('Setting is_ws to {}.'.format(is_ws))
        else:
            is_ws = False
            logging.debug('Setting is_ws to {}.'.format(is_ws))
        self.weekday = 'Not yet set.'
        logging.debug(
            'Setting weekday of {} to {}'.format(self.city_name, self.weekday))
        self.sabbath = False
        logging.debug('Setting sabbath status of {} to {}'.format(
            self.city_name, self.sabbath))
        self.weekday = b_weekday_today
        self.sabbath = is_ws

    def weekly_sabbath(self):
        logging.debug('It is a weekly sabbath.')
        self.sabbath = True

    def high_sabbath(self):
        logging.debug('It is a high sabbath.')
        self.sabbath = True

    def regular_day(self):
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
        print(
            'Try again with the name of your city as a command line argument.')
        print('Example: sabbath.py Manila')
    else:
        logging.debug('entry is %s' % entry)
        location = BiblicalWeekday(entry)
        logging.debug('Creating object %s' % location)
        print('The chosen location is {}'.format(location.city_name))
        print('The time in {} is now {}'.format(location.city_name,
                                                location.current_time))
        if location.sun_has_set is True:
            print('The sun is down')
            print('The sunset was at {}'.format(location.sunset_time))
        print('Today is the {} day of the week.'.format(location.weekday))
        if location.sabbath is True:
            print('It is now the weekly Sabbath')
