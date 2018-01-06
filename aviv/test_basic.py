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


def test_est_is_known():
    '''Any BibCalItem should have a value for being known or estimated'''
    for key, value in hist_data.estimated_moons.items():
        y = core.bibitem_from_key(key)
        result1 = y.is_known
        result2 = y.is_estimated
        assert result1 is not None
        assert result2 is not None


def test_is_known():
    '''Any BibCalItem should have a value for being known or estimated'''
    for key, value in hist_data.known_moons.items():
        y = core.bibitem_from_key(key)
        result1 = y.is_known
        result2 = y.is_estimated
        assert result1 is not None
        assert result2 is not True
        assert result2 is not None
