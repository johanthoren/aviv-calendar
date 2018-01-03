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
    601001: (6010, 1, 2010, 3, 17),    # karaite korner newsletter #454
    601002: (6010, 2, 2010, 4, 15),    # karaite korner newsletter #461
    601003: (6010, 3, 2010, 5, 15),    # karaite korner newsletter #466
    601004: (6010, 4, 2010, 6, 13),    # karaite korner newsletter #468
    601005: (6010, 5, 2010, 7, 13),    # karaite korner newsletter #470
    601006: (6010, 6, 2010, 8, 11),    # karaite korner newsletter #472
    601007: (6010, 7, 2010, 9, 10),    # karaite korner newsletter #477
    601008: (6010, 8, 2010, 10, 9),    # karaite korner newsletter #480
    601009: (6010, 9, 2010, 11, 7),    # karaite korner newsletter #483
    601010: (6010, 10, 2010, 12, 7),   # karaite korner newsletter #490
    601011: (6010, 11, 2011, 1, 5),    # karaite korner newsletter #492
    601012: (6010, 12, 2011, 2, 4),    # karaite korner newsletter #494
    601013: (6010, 13, 2011, 3, 6),    # karaite korner newsletter #500
    601101: (6011, 1, 2011, 4, 4),     # karaite korner newsletter #506
    601102: (6011, 2, 2011, 5, 4),     # karaite korner newsletter #512
    601103: (6011, 3, 2011, 6, 3),     # karaite korner newsletter #516
    601104: (6011, 4, 2011, 7, 2),     # karaite korner newsletter #521
    601105: (6011, 5, 2011, 8, 1),     # renewedmoon.com
    601106: (6011, 6, 2011, 8, 31),    # renewedmoon.com
    601107: (6011, 7, 2011, 9, 29),    # renewedmoon.com
    601108: (6011, 8, 2011, 10, 28),   # renewedmoon.com
    601109: (6011, 9, 2011, 11, 26),   # renewedmoon.com
    601110: (6011, 10, 2011, 12, 26),  # karaite korner newsletter #540
    601111: (6011, 11, 2012, 1, 25),   # karaite korner newsletter #543
    601112: (6011, 12, 2012, 2, 23),   # karaite korner newsletter #545
    601201: (6012, 1, 2012, 3, 23),    # renewedmoon.com
    601202: (6012, 2, 2012, 4, 22),    # renewedmoon.com
    601203: (6012, 3, 2012, 5, 22),    # renewedmoon.com
    601204: (6012, 4, 2012, 6, 21),    # renewedmoon.com
    601205: (6012, 5, 2012, 7, 21),    # karaite korner newsletter #559
    601206: (6012, 6, 2012, 8, 19),    # renewedmoon.com
    601207: (6012, 7, 2012, 9, 17),    # renewedmoon.com
    601208: (6012, 8, 2012, 10, 17),   # renewedmoon.com
    601209: (6012, 9, 2012, 11, 15),   # renewedmoon.com
    601210: (6012, 10, 2012, 12, 14),  # renewedmoon.com
    601211: (6012, 11, 2013, 1, 13),   # renewedmoon.com
    601212: (6012, 12, 2013, 2, 11),   # renewedmoon.com
    601301: (6013, 1, 2013, 3, 13),    # renewedmoon.com
    601302: (6013, 2, 2013, 4, 11),    # renewedmoon.com
    601303: (6013, 3, 2013, 5, 11),    # renewedmoon.com
    601304: (6013, 4, 2013, 6, 10),    # renewedmoon.com
    601305: (6013, 5, 2013, 7, 10),    # renewedmoon.com
    601306: (6013, 6, 2013, 8, 8),     # renewedmoon.com
    601307: (6013, 7, 2013, 9, 7),     # renewedmoon.com
    601308: (6013, 8, 2013, 10, 6),    # renewedmoon.com
    601309: (6013, 9, 2013, 11, 5),    # renewedmoon.com
    601310: (6013, 10, 2013, 12, 4),   # renewedmoon.com
    601311: (6013, 11, 2014, 1, 2),    # renewedmoon.com
    601312: (6013, 12, 2014, 2, 1),    # renewedmoon.com
    601313: (6013, 13, 2014, 3, 3),    # renewedmoon.com
    601401: (6014, 1, 2014, 3, 31),    # renewedmoon.com
    601402: (6014, 2, 2014, 4, 30),    # renewedmoon.com
    601403: (6014, 3, 2014, 5, 30),    # renewedmoon.com
    # Missing months.
    601406: (6014, 6, 2014, 8, 27),    # renewedmoon.com
    601407: (6014, 7, 2014, 9, 26),    # renewedmoon.com
    601408: (6014, 8, 2014, 10, 25),   # renewedmoon.com
    601409: (6014, 9, 2014, 11, 24),   # renewedmoon.com
    601410: (6014, 10, 2014, 12, 23),  # renewedmoon.com
    601411: (6014, 11, 2015, 1, 21),   # renewedmoon.com
    601412: (6014, 12, 2015, 2, 20),   # renewedmoon.com
    # Missing months.
    601509: (6015, 9, 2015, 11, 13),   # renewedmoon.com
    601510: (6015, 10, 2015, 12, 13),  # renewedmoon.com
    601511: (6015, 11, 2016, 1, 11),   # renewedmoon.com
    601512: (6015, 12, 2016, 2, 9),    # renewedmoon.com
    601513: (6015, 13, 2016, 3, 10),   # renewedmoon.com
    # Missing months.
    601609: (6016, 9, 2016, 11, 30),   # renewedmoon.com
    601610: (6016, 10, 2016, 12, 30),  # renewedmoon.com
    601611: (6016, 11, 2017, 1, 29),   # renewedmoon.com
    601612: (6016, 12, 2017, 2, 27)    # renewedmoon.com
}
