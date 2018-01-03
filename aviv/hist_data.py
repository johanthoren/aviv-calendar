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
    601105: (6011, 5, 2011, 8, 1),
    601106: (6011, 6, 2011, 8, 31),
    601609: (6016, 9, 2016, 11, 30)
}
