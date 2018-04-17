#!/usr/bin/env python3
"""Historical data to act as reference in aviv-calendar."""

# -- BEGINNING OF INTRO: -- #

# A SHORT DESCRIPTION:
# Aviv Calendar, a small program to find out what day it is according
# to the Biblical calendar. Also attempts to let you know about
# the Feasts of the Lord as well as the Sabbath.

# CURRENT STATUS:
# Currently, it only decides what day of week it is according to
# biblical timekeeping. It will also tell you some details about
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

# This file contains some baseline months where gregorian time and
# biblical time can be defined for sure based on real observations.

# It also contains months where the moon has been estimated because no
# actual observation is available. Known moons should always take
# priority and any months added to known_moons should be removed from
# the list of estimated_moons.

# The format for the value is a tuple of the following:
# BIBLICAL year, BIBLICAL month, GREGORIAN year of the first day of the
# BIBLICAL month (the GREGORIAN day on which the sunset signaled the new
# day), GREGORIAN month of that same day, GREGORIAN day of said day.
# True or False is to reflect on confidence.

MOONS = {
    # 5999
    # Missing months.
    599905: (5999, 5, 1999, 8, 12, True),     # karaite korner newsletter #5
    599906: (5999, 6, 1999, 9, 11, True),     # karaite korner newsletter #10
    599907: (5999, 7, 1999, 10, 10, True),    # karaite korner newsletter #14
    599908: (5999, 8, 1999, 11, 9, True),     # karaite korner newsletter #15
    599909: (5999, 9, 1999, 12, 9, True),     # karaite korner newsletter #17
    599910: (5999, 10, 2000, 1, 8, True),     # karaite korner newsletter #21
    599911: (5999, 11, 2000, 2, 7, True),     # karaite korner newsletter #25
    599912: (5999, 12, 2000, 3, 7, True),     # karaite korner newsletter #29
    # 6000
    600001: (6000, 1, 2000, 4, 6, True),      # karaite korner newsletter #33
    600002: (6000, 2, 2000, 5, 5, True),      # karaite korner newsletter #35
    600003: (6000, 3, 2000, 6, 3, True),      # karaite korner newsletter #39
    600004: (6000, 4, 2000, 7, 3, True),      # karaite korner newsletter #44
    600005: (6000, 5, 2000, 8, 1, True),      # karaite korner newsletter #48
    600006: (6000, 6, 2000, 8, 30, True),     # karaite korner newsletter #50
    600007: (6000, 7, 2000, 9, 28, True),     # karaite korner newsletter #53
    600008: (6000, 8, 2000, 10, 28, True),    # karaite korner newsletter #56
    600009: (6000, 9, 2000, 11, 27, True),    # karaite korner newsletter #58
    600010: (6000, 10, 2000, 12, 27, True),   # karaite korner newsletter #60
    600011: (6000, 11, 2001, 1, 25, True),    # karaite korner newsletter #62
    600012: (6000, 12, 2001, 2, 24, True),    # karaite korner newsletter #64
    # 6001
    600101: (6001, 1, 2001, 3, 26, True),     # karaite korner newsletter #69
    600102: (6001, 2, 2001, 4, 24, True),     # karaite korner newsletter #74
    600103: (6001, 3, 2001, 5, 24, True),     # karaite korner newsletter #75
    600104: (6001, 4, 2001, 6, 22, True),     # karaite korner newsletter #76
    600105: (6001, 5, 2001, 7, 21, True),     # karaite korner newsletter #77
    600106: (6001, 6, 2001, 8, 20, True),     # karaite korner newsletter #79
    600107: (6001, 7, 2001, 9, 18, True),     # karaite korner newsletter #82
    600108: (6001, 8, 2001, 10, 18, True),    # karaite korner newsletter #84
    600109: (6001, 9, 2001, 11, 16, True),    # karaite korner newsletter #86
    600110: (6001, 10, 2001, 12, 16, True),   # karaite korner newsletter #88
    600111: (6001, 11, 2002, 1, 15, True),    # karaite korner newsletter #91
    600112: (6001, 12, 2002, 2, 13, True),    # karaite korner newsletter #92
    # 6002
    600201: (6002, 1, 2002, 3, 15, True),     # karaite korner newsletter #99
    600202: (6002, 2, 2002, 4, 14, True),     # karaite korner newsletter #103
    600203: (6002, 3, 2002, 5, 14, True),     # karaite korner newsletter #106
    600204: (6002, 4, 2002, 6, 12, True),     # karaite korner newsletter #107
    600205: (6002, 5, 2002, 7, 11, True),     # karaite korner newsletter #108
    600206: (6002, 6, 2002, 8, 9, True),      # karaite korner newsletter #110
    600207: (6002, 7, 2002, 9, 8, True),      # karaite korner newsletter #113
    600208: (6002, 8, 2002, 10, 7, True),     # karaite korner newsletter #115
    600209: (6002, 9, 2002, 11, 6, True),     # karaite korner newsletter #117
    600210: (6002, 10, 2002, 12, 5, True),    # karaite korner newsletter #119
    600211: (6002, 11, 2003, 1, 4, True),     # karaite korner newsletter #120
    600212: (6002, 12, 2003, 2, 3, True),     # karaite korner newsletter #122
    600213: (6002, 13, 2003, 3, 4, True),     # karaite korner newsletter #125
    # 6003
    600301: (6003, 1, 2003, 4, 3, True),      # karaite korner newsletter #127
    600302: (6003, 2, 2003, 5, 2, True),      # karaite korner newsletter #130
    600303: (6003, 3, 2003, 6, 1, True),      # karaite korner newsletter #131
    600304: (6003, 4, 2003, 7, 1, True),      # karaite korner newsletter #133
    600305: (6003, 5, 2003, 7, 30, True),     # karaite korner newsletter #134
    600306: (6003, 6, 2003, 8, 29, True),     # karaite korner newsletter #137
    600307: (6003, 7, 2003, 9, 27, True),     # karaite korner newsletter #139
    600308: (6003, 8, 2003, 10, 26, True),    # karaite korner newsletter #141
    600309: (6003, 9, 2003, 11, 25, True),    # karaite korner newsletter #142
    600310: (6003, 10, 2003, 12, 24, True),   # karaite korner newsletter #144
    600311: (6003, 11, 2004, 1, 23, True),    # karaite korner newsletter #147
    600312: (6003, 12, 2004, 2, 21, True),    # karaite korner newsletter #148
    # 6004
    600401: (6004, 1, 2004, 3, 22, True),     # karaite korner newsletter #155
    600402: (6004, 2, 2004, 4, 21, True),     # karaite korner newsletter #158
    600403: (6004, 3, 2004, 5, 20, True),     # karaite korner newsletter #160
    600404: (6004, 4, 2004, 6, 19, True),     # karaite korner newsletter #162
    600405: (6004, 5, 2004, 7, 18, True),     # karaite korner newsletter #163
    600406: (6004, 6, 2004, 8, 17, True),     # karaite korner newsletter #164
    600407: (6004, 7, 2004, 9, 15, True),     # karaite korner newsletter #170
    600408: (6004, 8, 2004, 10, 15, True),    # karaite korner newsletter #171
    600409: (6004, 9, 2004, 11, 13, True),    # karaite korner newsletter #173
    600410: (6004, 10, 2004, 12, 13, True),   # karaite korner newsletter #179
    600411: (6004, 11, 2005, 1, 11, True),    # karaite korner newsletter #185
    600412: (6004, 12, 2005, 2, 10, True),    # karaite korner newsletter #189
    # 6005
    600501: (6005, 1, 2005, 3, 11, True),     # karaite korner newsletter #197
    600502: (6005, 2, 2005, 4, 10, True),     # karaite korner newsletter #210
    600503: (6005, 3, 2005, 5, 9, True),      # karaite korner newsletter #215
    600504: (6005, 4, 2005, 6, 8, True),      # karaite korner newsletter #219
    600505: (6005, 5, 2005, 7, 7, True),      # karaite korner newsletter #223
    600506: (6005, 6, 2005, 8, 6, True),      # karaite korner newsletter #228
    600507: (6005, 7, 2005, 9, 5, True),      # karaite korner newsletter #235
    600508: (6005, 8, 2005, 10, 5, True),     # karaite korner newsletter #245
    600509: (6005, 9, 2005, 11, 3, True),     # karaite korner newsletter #246
    600510: (6005, 10, 2005, 12, 3, True),    # karaite korner newsletter #248
    600511: (6005, 11, 2006, 1, 2, True),     # karaite korner newsletter #249
    600512: (6005, 12, 2006, 1, 30, True),    # karaite korner newsletter #251
    600513: (6005, 13, 2006, 3, 1, True),     # karaite korner newsletter #256
    # 6006
    600601: (6006, 1, 2006, 3, 30, True),     # karaite korner newsletter #261
    600602: (6006, 2, 2006, 4, 29, True),     # karaite korner newsletter #266
    600603: (6006, 3, 2006, 5, 28, True),     # karaite korner newsletter #267
    600604: (6006, 4, 2006, 6, 26, True),     # karaite korner newsletter #268
    600605: (6006, 5, 2006, 7, 26, True),     # karaite korner newsletter #271
    600606: (6006, 6, 2006, 8, 25, True),     # karaite korner newsletter #275
    600607: (6006, 7, 2006, 9, 24, True),     # karaite korner newsletter #278
    600608: (6006, 8, 2006, 10, 24, True),    # karaite korner newsletter #282
    600609: (6006, 9, 2006, 11, 22, True),    # karaite korner newsletter #283
    600610: (6006, 10, 2006, 12, 22, True),   # karaite korner newsletter #284
    600611: (6006, 11, 2007, 1, 21, True),    # karaite korner newsletter #285
    600612: (6006, 12, 2007, 2, 19, True),    # karaite korner newsletter #288
    # 6007
    600701: (6007, 1, 2007, 3, 20, True),     # karaite korner newsletter #292
    600702: (6007, 2, 2007, 4, 18, True),     # karaite korner newsletter #297
    600703: (6007, 3, 2007, 5, 17, True),     # karaite korner newsletter #298
    600704: (6007, 4, 2007, 6, 16, True),     # karaite korner newsletter #300
    600705: (6007, 5, 2007, 7, 15, True),     # karaite korner newsletter #301
    600706: (6007, 6, 2007, 8, 14, True),     # karaite korner newsletter #304
    600707: (6007, 7, 2007, 9, 13, True),     # karaite korner newsletter #308
    600708: (6007, 8, 2007, 10, 13, True),    # karaite korner newsletter #309
    600709: (6007, 9, 2007, 11, 12, True),    # karaite korner newsletter #311
    600710: (6007, 10, 2007, 12, 11, True),   # karaite korner newsletter #313
    600711: (6007, 11, 2008, 1, 10, True),    # karaite korner newsletter #315
    600712: (6007, 12, 2008, 2, 8, True),     # karaite korner newsletter #317
    600713: (6007, 13, 2008, 3, 9, True),     # karaite korner newsletter #324
    # 6008
    600801: (6008, 1, 2008, 4, 7, True),      # karaite korner newsletter #327
    600802: (6008, 2, 2008, 5, 6, True),      # karaite korner newsletter #330
    600803: (6008, 3, 2008, 6, 4, True),      # karaite korner newsletter #331
    600804: (6008, 4, 2008, 7, 4, True),      # karaite korner newsletter #336
    600805: (6008, 5, 2008, 8, 2, True),      # karaite korner newsletter #340
    600806: (6008, 6, 2008, 9, 1, True),      # karaite korner newsletter #344
    600807: (6008, 7, 2008, 10, 1, True),     # karaite korner newsletter #353
    600808: (6008, 8, 2008, 10, 31, True),    # karaite korner newsletter #357
    600809: (6008, 9, 2008, 11, 29, True),    # karaite korner newsletter #359
    600810: (6008, 10, 2008, 12, 29, True),   # karaite korner newsletter #361
    600811: (6008, 11, 2009, 1, 27, True),    # karaite korner newsletter #363
    600812: (6008, 12, 2009, 2, 26, True),    # karaite korner newsletter #366
    # 6009
    600901: (6009, 1, 2009, 3, 27, True),     # karaite korner newsletter #376
    600902: (6009, 2, 2009, 4, 26, True),     # karaite korner newsletter #380
    600903: (6009, 3, 2009, 5, 25, True),     # karaite korner newsletter #383
    600904: (6009, 4, 2009, 6, 23, True),     # karaite korner newsletter #392
    600905: (6009, 5, 2009, 7, 23, True),     # karaite korner newsletter #398
    600906: (6009, 6, 2009, 8, 22, True),     # karaite korner newsletter #409
    600907: (6009, 7, 2009, 9, 20, True),     # karaite korner newsletter #416
    600908: (6009, 8, 2009, 10, 20, True),    # karaite korner newsletter #418
    600909: (6009, 9, 2009, 11, 18, True),    # karaite korner newsletter #425
    600910: (6009, 10, 2009, 12, 18, True),   # karaite korner newsletter #435
    600911: (6009, 11, 2010, 1, 16, True),    # karaite korner newsletter #440
    600912: (6009, 12, 2010, 2, 15, True),    # karaite korner newsletter #447
    # 6010
    601001: (6010, 1, 2010, 3, 17, True),     # karaite korner newsletter #454
    601002: (6010, 2, 2010, 4, 15, True),     # karaite korner newsletter #461
    601003: (6010, 3, 2010, 5, 15, True),     # karaite korner newsletter #466
    601004: (6010, 4, 2010, 6, 13, True),     # karaite korner newsletter #468
    601005: (6010, 5, 2010, 7, 13, True),     # karaite korner newsletter #470
    601006: (6010, 6, 2010, 8, 11, True),     # karaite korner newsletter #472
    601007: (6010, 7, 2010, 9, 10, True),     # karaite korner newsletter #477
    601008: (6010, 8, 2010, 10, 9, True),     # karaite korner newsletter #480
    601009: (6010, 9, 2010, 11, 7, True),     # karaite korner newsletter #483
    601010: (6010, 10, 2010, 12, 7, True),    # karaite korner newsletter #490
    601011: (6010, 11, 2011, 1, 5, True),     # karaite korner newsletter #492
    601012: (6010, 12, 2011, 2, 4, True),     # karaite korner newsletter #494
    601013: (6010, 13, 2011, 3, 6, True),     # karaite korner newsletter #500
    # 6011
    601101: (6011, 1, 2011, 4, 4, True),      # karaite korner newsletter #506
    601102: (6011, 2, 2011, 5, 4, True),      # karaite korner newsletter #512
    601103: (6011, 3, 2011, 6, 3, True),      # karaite korner newsletter #516
    601104: (6011, 4, 2011, 7, 2, True),      # karaite korner newsletter #521
    601105: (6011, 5, 2011, 8, 1, True),      # renewedmoon.com
    601106: (6011, 6, 2011, 8, 31, True),     # renewedmoon.com
    601107: (6011, 7, 2011, 9, 29, True),     # renewedmoon.com
    601108: (6011, 8, 2011, 10, 28, True),    # renewedmoon.com
    601109: (6011, 9, 2011, 11, 26, True),    # renewedmoon.com
    601110: (6011, 10, 2011, 12, 26, True),   # karaite korner newsletter #540
    601111: (6011, 11, 2012, 1, 25, True),    # karaite korner newsletter #543
    601112: (6011, 12, 2012, 2, 23, True),    # karaite korner newsletter #545
    # 6012
    601201: (6012, 1, 2012, 3, 23, True),     # renewedmoon.com
    601202: (6012, 2, 2012, 4, 22, True),     # renewedmoon.com
    601203: (6012, 3, 2012, 5, 22, True),     # renewedmoon.com
    601204: (6012, 4, 2012, 6, 21, True),     # renewedmoon.com
    601205: (6012, 5, 2012, 7, 21, True),     # karaite korner newsletter #559
    601206: (6012, 6, 2012, 8, 19, True),     # renewedmoon.com
    601207: (6012, 7, 2012, 9, 17, True),     # renewedmoon.com
    601208: (6012, 8, 2012, 10, 17, True),    # renewedmoon.com
    601209: (6012, 9, 2012, 11, 15, True),    # renewedmoon.com
    601210: (6012, 10, 2012, 12, 14, True),   # renewedmoon.com
    601211: (6012, 11, 2013, 1, 13, True),    # renewedmoon.com
    601212: (6012, 12, 2013, 2, 11, True),    # renewedmoon.com
    # 6013
    601301: (6013, 1, 2013, 3, 13, True),     # renewedmoon.com
    601302: (6013, 2, 2013, 4, 11, True),     # renewedmoon.com
    601303: (6013, 3, 2013, 5, 11, True),     # renewedmoon.com
    601304: (6013, 4, 2013, 6, 10, True),     # renewedmoon.com
    601305: (6013, 5, 2013, 7, 10, True),     # renewedmoon.com
    601306: (6013, 6, 2013, 8, 8, True),      # renewedmoon.com
    601307: (6013, 7, 2013, 9, 7, True),      # renewedmoon.com
    601308: (6013, 8, 2013, 10, 6, True),     # renewedmoon.com
    601309: (6013, 9, 2013, 11, 5, True),     # renewedmoon.com
    601310: (6013, 10, 2013, 12, 4, True),    # renewedmoon.com
    601311: (6013, 11, 2014, 1, 2, True),     # renewedmoon.com
    601312: (6013, 12, 2014, 2, 1, True),     # renewedmoon.com
    601313: (6013, 13, 2014, 3, 3, True),     # renewedmoon.com
    # 6014
    601401: (6014, 1, 2014, 3, 31, True),     # renewedmoon.com
    601402: (6014, 2, 2014, 4, 30, True),     # renewedmoon.com
    601403: (6014, 3, 2014, 5, 30, True),     # renewedmoon.com
    601404: (6014, 4, 2014, 6, 29, True),     # whenisthenewmoon.com
    601405: (6014, 5, 2014, 7, 28, True),     # whenisthenewmoon.com
    601406: (6014, 6, 2014, 8, 27, True),     # renewedmoon.com
    601407: (6014, 7, 2014, 9, 26, True),     # renewedmoon.com
    601408: (6014, 8, 2014, 10, 25, True),    # renewedmoon.com
    601409: (6014, 9, 2014, 11, 24, True),    # renewedmoon.com
    601410: (6014, 10, 2014, 12, 23, True),   # renewedmoon.com
    601411: (6014, 11, 2015, 1, 21, True),    # renewedmoon.com
    601412: (6014, 12, 2015, 2, 20, True),    # renewedmoon.com
    # 6015
    601501: (6015, 1, 2015, 3, 21, True),     # whenisthenewmoon.com
    601502: (6015, 2, 2015, 4, 20, True),     # whenisthenewmoon.com
    601503: (6015, 3, 2015, 5, 19, True),     # whenisthenewmoon.com
    601504: (6015, 4, 2015, 6, 18, True),     # whenisthenewmoon.com
    601505: (6015, 5, 2015, 7, 17, True),     # whenisthenewmoon.com
    601506: (6015, 6, 2015, 8, 16, True),     # whenisthenewmoon.com
    601507: (6015, 7, 2015, 9, 15, True),     # whenisthenewmoon.com
    601508: (6015, 8, 2015, 10, 14, True),    # whenisthenewmoon.com
    601509: (6015, 9, 2015, 11, 13, True),    # renewedmoon.com
    601510: (6015, 10, 2015, 12, 13, True),   # renewedmoon.com
    601511: (6015, 11, 2016, 1, 11, True),    # renewedmoon.com
    601512: (6015, 12, 2016, 2, 9, True),     # renewedmoon.com
    601513: (6015, 13, 2016, 3, 10, True),    # renewedmoon.com
    # 6016
    601601: (6016, 1, 2016, 4, 9, True),      # whenisthenewmoon.com
    601602: (6016, 2, 2016, 5, 7, True),      # whenisthenewmoon.com
    601603: (6016, 3, 2016, 6, 6, True),      # whenisthenewmoon.com
    601604: (6016, 4, 2016, 7, 5, True),      # whenisthenewmoon.com
    601605: (6016, 5, 2016, 8, 4, True),      # whenisthenewmoon.com
    601606: (6016, 6, 2016, 9, 2, True),      # renewedmoon twitter
    601607: (6016, 7, 2016, 10, 2, True),     # karaite korner newsletter
    601608: (6016, 8, 2016, 11, 1, True),     # 31st day since last moon
    601609: (6016, 9, 2016, 11, 30, True),    # renewedmoon.com
    601610: (6016, 10, 2016, 12, 30, True),   # renewedmoon.com
    601611: (6016, 11, 2017, 1, 29, True),    # renewedmoon.com
    601612: (6016, 12, 2017, 2, 27, True),    # renewedmoon.com
    # 6017
    601701: (6017, 1, 2017, 3, 29, True),     # renewedmoon.com
    601702: (6017, 2, 2017, 4, 27, True),     # renewedmoon twitter
    601703: (6017, 3, 2017, 5, 27, True),     # jerusalemsaints facebook
    601704: (6017, 4, 2017, 6, 25, True),     # jerusalemsaints facebook
    601705: (6017, 5, 2017, 7, 25, True),     # whenisthenewmoon.com
    601706: (6017, 6, 2017, 8, 23, True),     # whenisthenewmoon.com
    601707: (6017, 7, 2017, 9, 21, True),     # renewedmoon twitter
    601708: (6017, 8, 2017, 10, 21, True),    # whenisthenewmoon.com
    601709: (6017, 9, 2017, 11, 20, True),    # renewedmoon.com
    601710: (6017, 10, 2017, 12, 20, True),   # a rood awakening / michael rood
    601711: (6017, 11, 2018, 1, 18, True),    # goo.gl/dftVJ9
    601712: (6017, 12, 2018, 2, 17, True),    # 30 day rule
    # 6018
    601801: (6018, 1, 2018, 3, 18, True),     # renewedmoon.com
    601802: (6018, 2, 2018, 4, 17, True)      # Devorah's date tree.
}
