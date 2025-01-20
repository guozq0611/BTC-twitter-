# -*- coding: utf-8 -*-
"""
Author: guozq

Create Date: 2025/01/19

Description:

"""
import datetime
import talib

from abc import ABC

from btc_model.core.common.context import Context
from btc_model.indicator.BaseIndicator import BaseIndicator


class IndicatorMACD(BaseIndicator, ABC):
    def __init__(self):
        super().__init__()

    def compute(self, context: Context):
        pass

    @staticmethod
    def calculate(close_array, fast_period, slow_period, signal_period):
        macd, signal, hist = talib.MACD(close_array,
                                        fastperiod=fast_period,
                                        slowperiod=slow_period,
                                        signalperiod=signal_period)

        return macd, signal, hist


