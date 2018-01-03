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

# The format for the value is a tuple of the following:
# BIBLICAL year, BIBLICAL month, GREGORIAN year of the first day of the
# BIBLICAL month (the GREGORIAN day on which the sunset signaled the new
# day), GREGORIAN month of that same day, GREGORIAN day of said day.

known_months = {
    # The following dates are based on observations from:
    # http://www.renewedmoon.com/archived-reports/
    601105: (6011, 5, 2011, 8, 1),
    601106: (6011, 6, 2011, 8, 31),
    601107: (6011, 7, 2011, 9, 29),
    601108: (6011, 8, 2011, 10, 28),
    601109: (6011, 9, 2011, 11, 26),
    # Missing months.
    601201: (6012, 1, 2012, 3, 23),
    601202: (6012, 2, 2012, 4, 22),
    601203: (6012, 3, 2012, 5, 22),
    601204: (6012, 4, 2012, 6, 21),
    # Missing month.
    601206: (6012, 6, 2012, 8, 19),
    601207: (6012, 7, 2012, 9, 17),
    601208: (6012, 8, 2012, 10, 17),
    601209: (6012, 9, 2012, 11, 15),
    601210: (6012, 10, 2012, 12, 14),
    601211: (6012, 11, 2013, 1, 13),
    601212: (6012, 12, 2013, 2, 11),
    601301: (6013, 1, 2013, 3, 13),
    601302: (6013, 2, 2013, 4, 11),
    601303: (6013, 3, 2013, 5, 11),
    601304: (6013, 4, 2013, 6, 10),
    601305: (6013, 5, 2013, 7, 10),
    601306: (6013, 6, 2013, 8, 8),
    601307: (6013, 7, 2013, 9, 7),
    601308: (6013, 8, 2013, 10, 6),
    601309: (6013, 9, 2013, 11, 5),
    601310: (6013, 10, 2013, 12, 4),
    601311: (6013, 11, 2014, 1, 2),
    601312: (6013, 12, 2014, 2, 1),
    601313: (6013, 13, 2014, 3, 3),
    601401: (6014, 1, 2014, 3, 31),
    601402: (6014, 2, 2014, 4, 30),
    601403: (6014, 3, 2014, 5, 30),
    # Missing months.
    601406: (6014, 6, 2014, 8, 27),
    601407: (6014, 7, 2014, 9, 26),
    601408: (6014, 8, 2014, 10, 25),
    601409: (6014, 9, 2014, 11, 24),
    601410: (6014, 10, 2014, 12, 23),
    601411: (6014, 11, 2015, 1, 21),
    601412: (6014, 12, 2015, 2, 20),
    # Missing months.
    601509: (6015, 9, 2015, 11, 13),
    601510: (6015, 10, 2015, 12, 13),
    601511: (6015, 11, 2016, 1, 11),
    601512: (6015, 12, 2016, 2, 9),
    601513: (6015, 13, 2016, 3, 10),
    # Missing months.
    601609: (6016, 9, 2016, 11, 30),
    601610: (6016, 10, 2016, 12, 30),
    601611: (6016, 11, 2017, 1, 29),
    601612: (6016, 12, 2017, 2, 27)
    # END of dates from Renewed Moon.
}
