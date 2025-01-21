# -*- coding: utf-8 -*-
"""
Author: guozq

Create Date: 2025/01/19

Description:

"""
import datetime
import numpy as np
from abc import ABC
import talib as ta


from btc_model.core.common.context import Context
from btc_model.indicator.BaseIndicator import BaseIndicator


class IndicatorMayerMultiple(BaseIndicator, ABC):
    def __init__(self):
        super().__init__()

    def compute(self, context: Context):
        pass

    @staticmethod
    def calculate(close_array, window):
        ma = ta.SMA(close_array, timeperiod=window)
        mayer_multiple = close_array[-1] / ma[-1]

        if mayer_multiple > 2.4:
            return True
        else:
            return False

