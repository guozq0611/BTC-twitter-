import numpy as np
import pandas as pd
import datetime
import abc

from btc_model.core.common.const import Interval

class BaseDownloader(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def download_history_kline_data(self, symbol_id, start_dt, end_dt, interval: Interval, **kwargs):
        pass

