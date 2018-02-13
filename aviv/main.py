#!/usr/bin/env python3
"""A simple program to find out the biblical date."""
# -- BEGINNING OF INTRO: -- #

# A SHORT DESCRIPTION:
# Aviv Calendar, a small program to find out what day it is according
# to the Biblical calendar. Also attempts to let you know about
# the Feasts of the Lord as well as the Sabbath.

# CURRENT STATUS:
# Currently, it only decides what day of week, month and year it is according
# to biblical timekeeping. It will also tell you some details about sunset
# and sunrise and wether or not is is a weekly sabbath or a feast day.

# COPYRIGHT:
# Copyright (C) 2017 - 2018 Johan Thorén <johan@thoren.xyz>

# LICENSE:
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# -- END OF INTRO -- #
import argparse
import re
import Aviv


def main():
    """Find out the biblical calendar data for a
    given location.
    """
    parser = argparse.ArgumentParser(
        description='Find out the biblical time for a given location.')
    parser.add_argument(
        '--debug',
        type=bool,
        default=False,
        nargs='?',
        help='show debug messages')
    parser.add_argument(
        '--country',
        metavar='C',
        type=str,
        nargs='?',
        help='specify the country where the location is located')
    parser.add_argument(
        '--location',
        metavar='L',
        default='Jerusalem',
        type=str,
        nargs='?',
        help='specify the location where the time will be calculated')
    parser.add_argument(
        '--geocoder',
        metavar='G',
        default='astral',
        type=str,
        nargs='?',
        help='specify the geocoder to use for calculating the location')
    parser.add_argument(
        '--year', metavar='Y', type=int, nargs='?', help='specify the year')
    parser.add_argument(
        '--month', metavar='M', type=int, nargs='?', help='specify the month')
    parser.add_argument(
        '--day',
        metavar='D',
        type=int,
        nargs='?',
        help='specify the day of month')
    parser.add_argument(
        '--hour',
        metavar='H',
        type=int,
        nargs='?',
        help='specify the hour of the day')

    args = parser.parse_args()

    # Check for the --debug flag and set the corresponding debug settings.
    Aviv.debug(args.debug)

    # Since the --geocoder 'astral' does not work with the --country option,
    # check if --country has been used and ignore it with a message to the user.
    if args.country:
        if args.geocoder == 'astral':
            print(
                'Astral Geocoder does not like to have the country specified.')
            print('Ignoring "--country {}"'.format(args.country))
            print('To use "--country {}", please specify "--geocoder google".'.
                  format(args.country))
        elif args.geocoder == 'google':
            args.location = str(args.location + ', ' + args.country)

    # Put everything together and create the main object that _info will be
    # based on.
    main_city = Aviv.BibTime(args.location, args.geocoder, args.year,
                             args.month, args.day, args.hour)
    _info(main_city)


def _info(loc):
    """Prints information about the given location and it's calendar data."""

    # To shorten all the references to loc.b_location.location.name, which is so
    # long it tends to mess up rows just a bit too much.
    city_re = re.compile(r'[^\s\d]+')
    match_obj = city_re.findall(loc.b_location.location.name)
    city_name = ' '.join(match_obj)

    def _location_info():
        # Print information about the location.
        print('Location '.ljust(40, '.'))
        print('{:20s}{:>20s}'.format('City:', city_name))
        print('{:20s}{:>20s}'.format('Country:',
                                     loc.b_location.location.region))
        print('{:20s}{:>20f}'.format('Latitude:',
                                     loc.b_location.location.latitude))
        print('{:20s}{:>20f}'.format('Longitude:',
                                     loc.b_location.location.longitude))
        print('')

    def _bib_info():
        # Print information about the biblical calendar data.
        print('Biblical '.ljust(40, '.'))
        # Create a string in the format 'YYYY-MM-DD' using the biblical
        # calendar data.
        bib_date_str = str(loc.b_time.year) + '-' + '{0:02d}'.format(
            loc.b_time.month) + '-' + '{0:02d}'.format(loc.b_time.day)
        print('{:20s}{:>20s}'.format('Short (ISO) Date:', bib_date_str))
        print('')
        print('{:20s}{:>20d}'.format('Year:', loc.b_time.year))
        print('{:20s}{:>20s}'.format('Month:', loc.b_time.month_name))
        print('{:25s}{:>15s}'.format('Month (traditional name):',
                                     loc.b_time.month_trad_name))
        print('{:20s}{:>20s}'.format('Day of month:', loc.b_time.day_name))
        print('')
        print('{:20s}{:>20s}'.format('Weekday:', loc.b_time.weekday))
        print('')

        ws_print = 'Yes' if loc.b_time.sabbath.weekly_sabbath is True else 'No'
        fd_print = 'Yes' if loc.b_time.sabbath.high_feast_day is True else 'No'
        hd_print = 'Yes' if loc.b_time.sabbath.holy_day_of_rest is True else 'No'
        print('{:20s}{:>20s}'.format('Weekly Sabbath:', ws_print))
        print('{:20s}{:>20s}'.format('Feast Day:', fd_print))
        print('{:20s}{:>20s}'.format('Holy Day of rest:', hd_print))
        print('')
        if loc.b_time.sabbath.high_feast_day is True:
            if len(loc.b_time.sabbath.feast_name) >= 28:
                name_re_1 = re.compile(r"^([^/]*)/*")
                name_mo_1 = name_re_1.search(loc.b_time.sabbath.feast_name)
                name_part_1 = name_mo_1.group()
                name_part_2 = loc.b_time.sabbath.feast_name[len(name_part_1):]
                print('{:12s}{:>28s}'.format('Feast name:', name_part_1))
                print('{:>40s}'.format(name_part_2))
                print('')
            else:
                print('{:12}{:>28s}'.format('Feast name:',
                                            loc.b_time.sabbath.feast_name))
                print('')
        if loc.aviv_barley is not None:
            if loc.aviv_barley is True:
                barley_statement = 'The barley IS Aviv'
            elif loc.aviv_barley is False:
                barley_statement = 'The barley is NOT Aviv'
            print('{:12s}{:>28s}'.format('Barley:', barley_statement))
            print('')

        if loc.b_time.sabbath.omer_count is not None:
            print('{:35s}{:>5s}'.format('Day of the Omer count:',
                                        loc.b_time.sabbath.omer_count))
            print('')

    def _greg_info():
        # Print information about the gregorian calendar data.
        print('Gregorian '.ljust(40, '.'))
        print('{:20s}{:>20s}'.format(
            'Short (ISO) Date:',
            loc.b_location.g_time.date().strftime('%Y-%m-%d')))
        print('')
        print('{:20s}{:>20s}'.format('Year:',
                                     loc.b_location.g_time.strftime('%Y')))
        print('{:20s}{:>20s}'.format('Month:',
                                     loc.b_location.g_time.strftime('%B')))
        print('{:20s}{:>20s}'.format('Day of month:',
                                     loc.b_location.g_time.strftime('%d')))
        print('')
        print('{:20s}{:>20s}'.format(
            'Weekday:', Aviv.GREG_WEEKDAYS[loc.b_location.g_time.weekday()]))
        print('')
        print('{:20s}{:>20s}'.format(
            'Time:', loc.b_location.g_time.strftime('%H:%M:%S')))
        print('')

    def _solar_info():
        # Print information about the sun, such as daylight, sunset and
        # sunrise etc.
        print('Solar info '.ljust(40, '.'))
        if loc.b_location.sun_info['has_set'] is True:
            print('{:20s}{:>20s}'.format('Daylight:', 'No'))
            print('{:20s}{:>20s}'.format('Sun has set:', 'Yes'))
            sunset_time = loc.b_location.sun_info['sunset'].strftime(
                '%H:%M:%S')
            print('{:20s}{:>20s}'.format('Time of sunset:', sunset_time))
        elif loc.b_location.sun_info['has_risen'] is False:
            print('{:20s}{:>20s}'.format('Daylight:', 'No'))
            print('{:20s}{:>20s}'.format('Sun has risen:', 'No'))
            sunrise_time = loc.b_location.sun_info['sunrise'].strftime(
                '%H:%M:%S')
            print('{:20s}{:>20s}'.format('Time of sunrise:', sunrise_time))
        else:
            print('{:20s}{:>20s}'.format('Daylight:', 'Yes'))
            sunrise_time = loc.b_location.sun_info['sunrise'].strftime(
                '%H:%M:%S')
            sunset_time = loc.b_location.sun_info['sunset'].strftime(
                '%H:%M:%S')
            print('{:20s}{:>20s}'.format('Time of sunrise:', sunrise_time))
            print('{:20s}{:>20s}'.format('Time of sunset:', sunset_time))

    _location_info()
    _bib_info()
    _greg_info()
    _solar_info()


if __name__ == '__main__':
    main()
