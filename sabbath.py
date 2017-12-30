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
from b_days import b_weekday
import datetime
from astral import Astral
import logging

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

# Set to your city.
city_name = 'Chicago'
logging.debug('city_name is set to %s' % city_name)

Astral().solar_depression = 'civil'
logging.debug('solar_depression set to %s' % Astral().solar_depression)

city = Astral()[city_name]
logging.debug('city object contains %s' % city)

# Defines the time that the sun sets
# in the given location.
daily_sun = city.sun(date=datetime.datetime.now(city.tz), local=True)
daily_sunset = daily_sun['sunset']

time_now = datetime.datetime.now(city.tz).replace(
    tzinfo=daily_sunset.tzinfo, microsecond=0)

logging.debug("The 'time_now' variable is now set to %s" % time_now)
logging.debug("The 'daily_sunset()' variable is now set to %s" % daily_sunset)

if time_now > daily_sunset:
    sun_is_down = True
    logging.debug('Setting sun_is_down to {}.'.format(sun_is_down))
else:
    sun_is_down = False
    logging.debug('Setting sun_is_down to {}.'.format(sun_is_down))

# Put the different items in variables for later use.
sunset_hour = daily_sunset.hour
sunset_minute = daily_sunset.minute
sunset_second = daily_sunset.second
sunset_timezone = daily_sunset.tzname()
sunset_time = daily_sunset.strftime("%H:%M")
current_time = time_now.strftime("%H:%M")

day_now = datetime.datetime.now(city.tz).weekday()
b_weekday_index = day_now + 1
logging.debug('b_weekday_index is now set to %s' % b_weekday_index)

if sun_is_down is True:
    b_weekday_index += 1
    b_weekday_today = b_weekday[b_weekday_index]
else:
    b_weekday_today = b_weekday[b_weekday_index]

if b_weekday_index == 6:
    is_ws = True
    logging.debug('Setting is_ws to {}.'.format(is_ws))
else:
    is_ws = False
    logging.debug('Setting is_ws to {}.'.format(is_ws))

if __name__ == '__main__':
    print('The chosen location is {}'.format(city_name))
    print('The time is now {}'.format(current_time))
    if sun_is_down is True:
        print('The sun is down')
        print('The sunset was at {}'.format(sunset_time))
    else:
        print('The sun is up')
        print('The sunset will be at {}'.format(sunset_time))
    print('Today is the %s day of the week' % b_weekday_today)
    if is_ws is True:
        print('It is now the Weekly Sabbath')
    else:
        print('It is not the Weekly Sabbath')
