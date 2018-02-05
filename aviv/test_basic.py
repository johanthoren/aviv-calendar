#!/usr/bin/env python3
"""Basic tests for aviv-calendar."""

# -- BEGINNING OF INTRO: -- #

# A SHORT DESCRIPTION:
# Tests for aviv-calendar.

# CURRENT STATUS:
# Simple tests. Need more...

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

import datetime
import logging
# from astral import AstralError
import core

logging.basicConfig(
    level=logging.CRITICAL,
    format=' %(asctime)s - %(levelname)s - %(message)s')


def test_known_reference_days():
    '''Testing against a few known days.'''
    known_reference_days = {
        # date id, g_year, g_month, g_day, 'Weekday', 'G Weekday',
        # Sabbath, Feast day.
        (2012, 12, 16): ((6012, 10, 3), (2012, 12, 14), '2nd', 6, False, True),
        (2013, 3, 13): ((6013, 1, 1), (2013, 3, 13), '5th', 2, False, True),
        (2017, 2, 17): ((6016, 11, 20), (2017, 1, 29), '7th', 4, True, False),
        (2017, 12, 30): ((6017, 10, 11), (2017, 12, 20), '1st', 5, False,
                         False)
    }
    for key, value in known_reference_days.items():
        logging.debug('key is %s', key)

        # Adding the hour 22 to test after sundown.
        d = core.BibTime('Jerusalem', 'astral', key[0], key[1], key[2], 22)
        logging.debug('d is %s', d)

        result_b_year = d.b_time.year
        result_b_month = d.b_time.month
        result_b_day = d.b_time.day
        result_month_start_date = d.b_time.month_start_time
        result_weekday = d.b_time.weekday
        result_g_weekday = d.b_location.g_time.weekday()
        result_sabbath = d.b_time.sabbath.sabbath
        result_feast_day = d.b_time.sabbath.high_feast_day

        ref_b_year = value[0][0]
        ref_b_month = value[0][1]
        ref_b_day = value[0][2]
        ref_month_start_date = datetime.datetime(*value[1]).replace(
            tzinfo=d.b_location.location.tzinfo)
        ref_weekday = value[2]
        ref_g_weekday = value[3]
        ref_sabbath = value[4]
        ref_feast_day = value[5]

        assert result_b_year == ref_b_year
        assert result_b_month == ref_b_month
        assert result_b_day == ref_b_day
        assert result_month_start_date == ref_month_start_date
        assert result_weekday == ref_weekday
        assert result_g_weekday == ref_g_weekday
        assert result_sabbath == ref_sabbath
        assert result_feast_day == ref_feast_day


if __name__ == '__main__':
    test_known_reference_days()
