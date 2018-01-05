#!/usr/bin/env python3

import core
import hist_data


def test_estimated_days_of_month():
    '''BibMonth should give months with 28-30 days'''
    for key, value in hist_data.estimated_moons.items():
        month = core.bibmonth_from_key(key)
        result = month.length
        if result is not None:
            assert 28 <= result <= 30


def test_known_days_of_month():
    '''BibMonth should give months with 28-30 days'''
    for key, value in hist_data.known_moons.items():
        month = core.bibmonth_from_key(key)
        result = month.length
        if result is not None:
            assert 28 <= result <= 30


def test_estimated_moon_is_known():
    '''Months should be moved from the estimated_moons dict when
    observation is available'''
    for key, value in hist_data.estimated_moons.items():
        assert key not in hist_data.known_moons.keys(
        ), 'the key {} is a duplicate'.format(key)
