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

# TODO: not finish
class IndicatorSTHMVRV(BaseIndicator, ABC):
    def __init__(self):
        super().__init__()

    def compute(self, context: Context):
        pass



