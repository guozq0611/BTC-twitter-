# -*- coding: utf-8 -*-
"""
Author: guozq

Create Date: 2025/01/19

Description:

"""
import datetime
import numpy as np
from abc import ABC


from btc_model.core.common.context import Context
from btc_model.indicator.BaseIndicator import BaseIndicator


class IndicatorPiCycle(BaseIndicator, ABC):
    def __init__(self):
        super().__init__()

    def compute(self, context: Context):

    @staticmethod
    def calculate(close_array, short_window, long_window):
        """
        :param close_array: 包含收盘价的 numpy array
        :param short_window: 短周期
        :param long_window:  长周期
        :return: 包含 pi_cycle 指标的 numpy array
        """
        # 计算移动平均
        ma_short = np.convolve(close_array, np.ones(short_window) / short_window, mode='valid')
        ma_long = np.convolve(close_array, np.ones(long_window) / long_window, mode='valid')

        pi_cycle = ma_short[long_window - short_window:] - ma_long  # 只取长度一致的部分

        return pi_cycle


