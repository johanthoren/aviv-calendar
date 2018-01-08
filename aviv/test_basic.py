#!/usr/bin/env python3

import logging
import core
import hist_data
import datetime


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


def test_known_reference_days():
    '''Testing against a few known days.'''
    known_reference_days = {
        # date id, g_year, g_month, g_day, 'Weekday', 'G Weekday',
        # Sabbath, Feast day.
        (6013, 1, 1): ((2013, 3, 13), '5th', 'Wednesday', False, True),
        (6016, 11, 20): ((2017, 2, 17), '7th', 'Friday', True, False),
        (6017, 10, 11): ((2017, 12, 30), '1st', 'Saturday', False, False)
    }

    for key, value in known_reference_days.items():
        logging.debug('key is {}'.format(key))
        d = core.BibDay(*key)

        result_g_date = d.start_g_date
        result_weekday = d.weekday
        result_g_weekday = d.g_weekday
        result_sabbath = d.sabbath
        result_feast_day = d.is_hfd

        ref_g_date = datetime.date(*value[0])
        ref_weekday = value[1]
        ref_g_weekday = value[2]
        ref_sabbath = value[3]
        ref_feast_day = value[4]

        assert result_g_date == ref_g_date
        assert result_weekday == ref_weekday
        assert result_g_weekday == ref_g_weekday
        assert result_sabbath == ref_sabbath
        assert result_feast_day == ref_feast_day


# def test_stockholm_today():
#     s = core.BibLocation('Stockholm')
#     time = datetime.datetime.now(s.astral_city.tz).replace(microsecond=0)

def test_get_latest_data():
    core.get_latest_data()
    import latest_data
    assert latest_data.last_known_moon is not None
    assert latest_data.next_estimated_moon is not None
    assert latest_data.aviv_barley is not None
