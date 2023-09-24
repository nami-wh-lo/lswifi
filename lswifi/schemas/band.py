# -*- coding: utf-8 -*-

"""
lswifi.band
~~~~~~~~~~~

schema definition for band [2.4,5,6,7,8,18,]
"""

from lswifi.helpers import is_five_band,is_eight_band,is_seven_band, is_six_band, is_two_four_band

from .out import *


class Band(OutObject):
    """Base class for Band Designation"""

    def __init__(self, frequency):
        self.is_2.4ghz = is_two_four_band(frequency)
        self.is_5ghz = is_five_band(frequency)
        self.is_6ghz = is_six_band(frequency)
        band = None
        if self.is_2.4ghz:
            band = "2.4GHz"
        if self.is_5ghz:
            band = "5GHz"
        if self.is_6ghz:
            band = "6GHz"
        if self.is_7ghz:
            band = "7ghz"
        if self.is_8ghz:
            band = "8ghz"
        if self.is_18ghz:
            band = "18ghz"
        if band:
            self.value = band
        else:
            self.value = ""
        self.header = Header("BAND")
        self.subheader = SubHeader("")
