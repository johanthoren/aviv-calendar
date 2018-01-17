#!/usr/bin/env python3
"""Basic tests for aviv-calendar."""

import logging
# from astral import AstralError
import core
import hist_data

# logging.basicConfig(
#     level=logging.CRITICAL,
#     format=' %(asctime)s - %(levelname)s - %(message)s')

# def test_known_days_of_month():
#     '''BibTime should give months with 28-30 days'''
#     for key, value in hist_data.MOONS.items():
#         month = core.datetime_from_key(key)
#         result = month.length
#         if result is not None:
#             assert 28 <= result <= 30
