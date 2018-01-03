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
    # 6005
    600501: (6005, 1, 2005, 3, 11),    # karaite korner newsletter #197
    600502: (6005, 2, 2005, 4, 10),    # karaite korner newsletter #210
    600503: (6005, 3, 2005, 5, 9),     # karaite korner newsletter #215
    600504: (6005, 4, 2005, 6, 8),     # karaite korner newsletter #219
    600505: (6005, 5, 2005, 7, 7),     # karaite korner newsletter #223
    600506: (6005, 6, 2005, 8, 6),     # karaite korner newsletter #228
    600507: (6005, 7, 2005, 9, 5),     # karaite korner newsletter #235
    600508: (6005, 8, 2005, 10, 5),    # karaite korner newsletter #245
    600509: (6005, 9, 2005, 11, 3),    # karaite korner newsletter #246
    600510: (6005, 10, 2005, 12, 3),   # karaite korner newsletter #248
    600511: (6005, 11, 2006, 1, 2),    # karaite korner newsletter #249
    600512: (6005, 12, 2006, 1, 30),   # karaite korner newsletter #251
    600513: (6005, 13, 2006, 3, 1),    # karaite korner newsletter #256
    # 6006
    600601: (6006, 1, 2006, 3, 30),    # karaite korner newsletter #261
    600602: (6006, 2, 2006, 4, 29),    # karaite korner newsletter #266
    600603: (6006, 3, 2006, 5, 28),    # karaite korner newsletter #267
    600604: (6006, 4, 2006, 6, 26),    # karaite korner newsletter #268
    600605: (6006, 5, 2006, 7, 26),    # karaite korner newsletter #271
    600606: (6006, 6, 2006, 8, 25),    # karaite korner newsletter #275
    600607: (6006, 7, 2006, 9, 24),    # karaite korner newsletter #278
    600608: (6006, 8, 2006, 10, 24),   # karaite korner newsletter #282
    600609: (6006, 9, 2006, 11, 22),   # karaite korner newsletter #283
    600610: (6006, 10, 2006, 12, 22),  # karaite korner newsletter #284
    600611: (6006, 11, 2007, 1, 21),   # karaite korner newsletter #285
    600612: (6006, 12, 2007, 2, 19),   # karaite korner newsletter #288
    # 6007
    600701: (6007, 1, 2007, 3, 20),    # karaite korner newsletter #292
    600702: (6007, 2, 2007, 4, 18),    # karaite korner newsletter #297
    600703: (6007, 3, 2007, 5, 17),    # karaite korner newsletter #298
    600704: (6007, 4, 2007, 6, 16),    # karaite korner newsletter #300
    600705: (6007, 5, 2007, 7, 15),    # karaite korner newsletter #301
    600706: (6007, 6, 2007, 8, 14),    # karaite korner newsletter #304
    600707: (6007, 7, 2007, 9, 13),    # karaite korner newsletter #308
    600708: (6007, 8, 2007, 10, 13),   # karaite korner newsletter #309
    600709: (6007, 9, 2007, 11, 12),   # karaite korner newsletter #311
    600710: (6007, 10, 2007, 12, 11),  # karaite korner newsletter #313
    600711: (6007, 11, 2008, 1, 10),   # karaite korner newsletter #315
    600712: (6007, 12, 2008, 2, 8),    # karaite korner newsletter #317
    600713: (6007, 13, 2008, 3, 9),    # karaite korner newsletter #324
    # 6008
    600801: (6008, 1, 2008, 4, 7),     # karaite korner newsletter #327
    600802: (6008, 2, 2008, 5, 6),     # karaite korner newsletter #330
    600803: (6008, 3, 2008, 6, 4),     # karaite korner newsletter #331
    600804: (6008, 4, 2008, 7, 4),     # karaite korner newsletter #336
    600805: (6008, 5, 2008, 8, 2),     # karaite korner newsletter #340
    600806: (6008, 6, 2008, 9, 1),     # karaite korner newsletter #344
    600807: (6008, 7, 2008, 10, 1),    # karaite korner newsletter #353
    600808: (6008, 8, 2008, 10, 31),   # karaite korner newsletter #357
    600809: (6008, 9, 2008, 11, 29),   # karaite korner newsletter #359
    600810: (6008, 10, 2008, 12, 29),  # karaite korner newsletter #361
    600811: (6008, 11, 2009, 1, 27),   # karaite korner newsletter #363
    600812: (6008, 12, 2009, 2, 26),   # karaite korner newsletter #366
    # 6009
    600901: (6009, 1, 2009, 3, 27),    # karaite korner newsletter #376
    600902: (6009, 2, 2009, 4, 26),    # karaite korner newsletter #380
    600903: (6009, 3, 2009, 5, 25),    # karaite korner newsletter #383
    600904: (6009, 4, 2009, 6, 23),    # karaite korner newsletter #392
    600905: (6009, 5, 2009, 7, 23),    # karaite korner newsletter #398
    600906: (6009, 6, 2009, 8, 22),    # karaite korner newsletter #409
    600907: (6009, 7, 2009, 9, 20),    # karaite korner newsletter #416
    600908: (6009, 8, 2009, 10, 20),   # karaite korner newsletter #418
    600909: (6009, 9, 2009, 11, 18),   # karaite korner newsletter #425
    600910: (6009, 10, 2009, 12, 18),  # karaite korner newsletter #435
    600911: (6009, 11, 2010, 1, 16),   # karaite korner newsletter #440
    600912: (6009, 12, 2010, 2, 15),   # karaite korner newsletter #447
    # 6010
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
    # 6011
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
    # 6012
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
    # 6013
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
    # 6014
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
    # 6015
    601509: (6015, 9, 2015, 11, 13),   # renewedmoon.com
    601510: (6015, 10, 2015, 12, 13),  # renewedmoon.com
    601511: (6015, 11, 2016, 1, 11),   # renewedmoon.com
    601512: (6015, 12, 2016, 2, 9),    # renewedmoon.com
    601513: (6015, 13, 2016, 3, 10),   # renewedmoon.com
    # Missing months.
    # 6016
    601609: (6016, 9, 2016, 11, 30),   # renewedmoon.com
    601610: (6016, 10, 2016, 12, 30),  # renewedmoon.com
    601611: (6016, 11, 2017, 1, 29),   # renewedmoon.com
    601612: (6016, 12, 2017, 2, 27)    # renewedmoon.com
}

if __name__ == '__main__':
    # Run a simple example for testing purposes.
    from core import BibMonth
    month = BibMonth(*known_months[600502])
    print('The {} month of the year {} started at sunset '
          'on the gregorian date {}'.format(month.name, month.year,
                                            month.start_g_date))
    try:
        if month.last_name:
            print('The {}, and last day of the month, '
                  'started on the gregorian date {}'.format(
                      month.last_name, month.end_g_date))
    except AttributeError:
        print('Unable to say anything about the end of the month right now')
        print(
            'This might be because the following month is not in the database')
    print('The traditional name of the {} month is {}'.format(
        month.name, month.trad_name))
