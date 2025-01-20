# -*- coding: utf-8 -*-
"""
Author: guozq

Create Date: 2025/01/19

Description:

"""
import datetime

import talib
import talib as ta

from abc import ABC

from btc_model.core.common.context import Context
from btc_model.indicator.BaseIndicator import BaseIndicator


class IndicatorBollinger(BaseIndicator, ABC):
    params = (
        ('time_period', 300),
        ('stddev_multiple', 1.5)
    )

    def __init__(self):
        super().__init__()

    def compute(self, context: Context):
        pass

    @staticmethod
    def calculate(close_array, window, stddev_multiple):
        upper_band, middle_band, lower_band = talib.BBANDS(close_array,
                                                           timeperiod=window,
                                                           nbdevup=stddev_multiple,
                                                           nbdevdn=stddev_multiple,
                                                           matype=0
                                                           )

        if close_array[-1] > upper_band[-1] and close_array[-2] <= upper_band[-2]:
            return True
        else:
            return False
