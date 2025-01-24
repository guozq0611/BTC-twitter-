import numpy as np
import pandas as pd
import datetime

from btc_model.core.common.const import Interval
from btc_model.core.wrapper.okx_api_wrapper import OKxApiWrapper

class OKxDownloader:
    def __init__(self, apikey, secretkey, passphrase, proxy):
        self.okx_api_wrapper = OKxApiWrapper.get_instance(apikey, secretkey, passphrase, proxy)

    def download_history_kline_data(self, symbol_id, start_dt, end_dt, interval: Interval, **kwargs):
        kline_data = self.okx_api_wrapper.get_history_kline_data(symbol_id, interval, start_dt, end_dt)

        print(kline_data)



if __name__ == "__main__":
    from btc_model.setting.setting import get_settings

    setting = get_settings('cex.okx')

    apikey = setting['apikey']
    secretkey = setting['secretkey']
    passphrase = setting['passphrase']
    proxy = setting['proxy']

    downloader = OKxDownloader(apikey, secretkey, passphrase, proxy)

    symbol_id = 'BTC-USD'
    start_dt = '2024-01-01 00:00:00'
    end_dt = '2025-01-18 23:59:59'
    result = downloader.download_history_kline_data(symbol_id=symbol_id, interval=Interval.DAILY, start_dt=start_dt, end_dt=end_dt)

    print(result)
