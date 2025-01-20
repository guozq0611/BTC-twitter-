# -*- coding: utf-8 -*-
"""
Author: guozq

Create Date: 2025/01/19

Description:

"""
import datetime

from btc_model.core.wrapper.okx_api_wrapper import OKxApiWrapper
from btc_model.core.wrapper.bitcoin_data_api_wrapper import BitcoinDataApiWrapper
from btc_model.setting.setting import get_settings
from btc_model.indicator.indicator_pi_cycle import IndicatorPiCycle
from btc_model.indicator.indicator_bollinger import IndicatorBollinger
from btc_model.indicator.indicator_rsi import IndicatorRSI
from btc_model.indicator.indicator_macd import IndicatorMACD


class EscapeModel:
    def __init__(self, **kwargs):

        self.pi_short_window = kwargs.get('short_window', 111)
        self.pi_long_window = kwargs.get('long_window', 350)

        self.bollinger_window = kwargs.get('bollinger_window', 100)
        self.bollinger_nbdev = kwargs.get('bollinger_nbdev', 2.5)

        self.rsi_window = kwargs.get('rsi_window', 14)
        self.rsi_upper = kwargs.get('rsi_upper', 70)
        self.rsi_lower = kwargs.get('rsi_lower', 30)

        self.macd_fast_period = kwargs.get('macd_fast_period', 12)
        self.macd_slow_period = kwargs.get('macd_slow_period', 26)
        self.macd_signal_period = kwargs.get('macd_signal_period', 9)

        self.kline_data = None
        self.sth_mvrv_data = None

        setting = get_settings('cex.okx')
        self._limit = setting['limit']
        self._apikey = setting['apikey']
        self._secretkey = setting['secretkey']
        self._passphrase = setting['passphrase']
        self._proxy = setting['proxy']

        self.OKxApi = OKxApiWrapper.get_instance(apikey=self._apikey,
                                                 secretkey=self._secretkey,
                                                 passphrase=self._passphrase,
                                                 proxy=self._proxy
                                                 )

        self.bitcoin_data_api = BitcoinDataApiWrapper.get_instance()

    def prepare_data(self):
        current_date = datetime.datetime.today()
        start_dt = current_date - datetime.timedelta(days=self.pi_long_window)

        self.kline_data = self.OKxApi.get_kline(symbol_id='BTC-USD',
                                                interval='1d',
                                                start_dt=start_dt,
                                                end_dt=current_date
                                                )

        self.sth_mvrv_data = self.bitcoin_data_api.get_sth_mvrv_data(start_dt=start_dt, end_dt=current_date)

    def calculate_pi(self):
        indicator = IndicatorPiCycle()
        result = indicator.calculate(close_array=self.kline_data['close'].to_numpy(),
                                     short_window=self.pi_short_window,
                                     long_window=self.pi_long_window
                                     )
        return result

    def calculate_bollinger(self):
        close_array = self.kline_data['close'].to_numpy()

        indicator = IndicatorBollinger()
        upper_band, middle_band, lower_band = indicator.calculate(close_array=close_array,
                                                                  window=self.bollinger_window,
                                                                  nbdev=self.bollinger_nbdev
                                                                  )

        if close_array[-1] > upper_band[-1] and close_array[-2] <= upper_band[-2]:
            return True
        else:
            return False

    def calculate_rsi(self):
        indicator = IndicatorRSI()
        rsi = indicator.calculate(close_array=self.kline_data['close'].to_numpy(),
                                  window=self.rsi_window,
                                  )

        if len(rsi) > 0 and rsi[-1] > self.rsi_upper:
            return True
        else:
            return False

    def calculate_macd(self):
        indicator = IndicatorMACD()
        dif, dea, hist = indicator.calculate(close_array=self.kline_data['close'].to_numpy(),
                                             fast_period=self.macd_fast_period,
                                             slow_period=self.macd_slow_period,
                                             signal_period=self.macd_signal_period
                                             )

        # 判断是否死叉
        if len(dif) > 2 and dif[-1] < dea[-1] and dif[-2] > dea[-2]:
            return True
        else:
            return False

    def calculate_sth_mvrv(self):
        if self.sth_mvrv_data is not None and len(self.sth_mvrv_data) > 0:
            std_mvrv = self.sth_mvrv_data[-1]

            if std_mvrv > 2:
                return True
            else:
                return False
        else:
            return False

if __name__ == "__main__":
    model = EscapeModel(short_window=111, long_window=350)
    model.prepare_data()
    escape_flag = dict()
    escape_flag['pi_cycle'] = model.calculate_pi()
    escape_flag['boll'] = model.calculate_bollinger()
    escape_flag['rsi'] = model.calculate_rsi()
    escape_flag['macd'] = model.calculate_macd()
    escape_flag['sth_mvrv'] = model.calculate_sth_mvrv()
    print(escape_flag)
