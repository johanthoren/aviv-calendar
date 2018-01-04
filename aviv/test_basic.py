#!/usr/bin/env python3

import core
import hist_data


def test_days_of_month():
    '''BibMonth should give months with 28-30 days'''
    for key, value in hist_data.known_months.items():
        month = core.month_from_key(key)
        result = month.length
        if result is not None:
            assert 28 <= result <= 30
