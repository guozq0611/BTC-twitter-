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
from btc_model.indicator.indicator_pi_cycle import IndicatorPiCycle
from btc_model.indicator.indicator_bollinger import IndicatorBollinger


class EscapeModel:
    def __init__(self, **kwargs):
        self.pi_short_window = kwargs.get('short_window', 111)
        self.pi_long_window = kwargs.get('long_window', 350)

        self.bollinger_window = kwargs.get('bollinger_window', 100)
        self.bollinger_nbdev = kwargs.get('bollinger_nbdev', 2.5)

        self.kline_data = None

        setting = get_settings('cex.okx')
        self._limit = setting['limit']
        self._apikey = setting['apikey']
        self._secretkey = setting['secretkey']
        self._passphrase = setting['passphrase']

        self.OKxApi = OKxApiWrapper.get_instance(apikey=self._apikey,
                                                 secretkey=self._secretkey,
                                                 passphrase=self._passphrase)

    def prepare_data(self):
        current_date = datetime.datetime.today()
        start_dt = current_date - datetime.timedelta(days=self.pi_long_window)

        self.kline_data = self.OKxApi.get_kline(symbol_id='BTC-USD',
                                                interval='1d',
                                                start_dt=start_dt,
                                                end_dt=current_date
                                                )

    def calculate_pi(self):
        indicator = IndicatorPiCycle()
        result = indicator.calculate(close_array=self.kline_data['close'].to_numpy(),
                                     short_window=self.pi_short_window,
                                     long_window=self.pi_long_window
                                     )
        return result

    def calculate_bollinger(self):
        indicator = IndicatorBollinger()
        result = indicator.calculate(close_array=self.kline_data['close'].to_numpy(),
                                     window=self.bollinger_window,
                                     stddev_multiple=self.bollinger_nbdev
                                     )
        return result


if __name__ == "__main__":
    model = EscapeModel(short_window=111, long_window=350)
    model.prepare_data()
    escape_flag_pi_cycle = model.calculate_pi()
    escape_flag_bollinger = model.calculate_bollinger()
    print('ok')
