# -*- coding: utf-8 -*-
"""
Author: guozq

Create Date: 2025/01/19

Description:

"""
import datetime
from abc import ABC

import okx.MarketData as MarketData

from btc_model.core.wrapper.okx_api_wrapper import OKxApiWrapper
from btc_model.setting.setting import get_settings

class EscapeModel:
    def __init__(self, **kwargs):
        self.pi_short_window = kwargs.get('short_window', 111)
        self.pi_long_window = kwargs.get('long_window', 350)

        setting = get_settings('dex.okx')
        self._limit = setting['limit']
        self._apikey = setting['apikey']
        self._secretkey = setting['secretkey']
        self._passphrase = setting['passphrase']

        self.OKxApi = OKxApiWrapper.get_instance()

    def prepare_data(self):
        total_loop_count = (self.pi_long_window // self._limit) + 1
        rest_days = self.pi_long_window % self._limit

        all_data = []

        for i in range(total_loop_count):
            if i == 0:
                btc_k_line_100 = marketDataAPI.get_index_candlesticks(instId="BTC-USD", bar="1D")
                btc_k_line_100_df = pd.DataFrame(btc_k_line_100)
                df_size = btc_k_line_100_df['data'].size
                for index in range(df_size):
                    temp_k_line_sum += float(btc_k_line_100_df['data'][index][4])
                    if index == df_size - 1:
                        ts_100 = btc_k_line_100_df['data'][index][0]
            elif i == total_loop_count - 1:
                btc_k_line_100 = marketDataAPI.get_index_candlesticks(instId="BTC-USD", bar="1D",
                                                                      after=ts_100, limit=rest_days)
                btc_k_line_100_df = pd.DataFrame(btc_k_line_100)
                df_size = btc_k_line_100_df['data'].size
                for index in range(df_size):
                    temp_k_line_sum += float(btc_k_line_100_df['data'][index][4])
            else:
                btc_k_line_100 = marketDataAPI.get_index_candlesticks(instId="BTC-USD", bar="1D", after=ts_100)
                btc_k_line_100_df = pd.DataFrame(btc_k_line_100)
                df_size = btc_k_line_100_df['data'].size
                for index in range(df_size):
                    temp_k_line_sum += float(btc_k_line_100_df['data'][index][4])
                    if index == df_size - 1:
                        ts_100 = btc_k_line_100_df['data'][index][0]
        return (temp_k_line_sum)
    def calculate_pi(self):

