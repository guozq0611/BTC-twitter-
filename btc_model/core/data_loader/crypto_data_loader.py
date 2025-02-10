import os
import numpy as np
import pandas as pd
import datetime
import pyarrow as pa
import pyarrow.parquet as pq

from btc_model.core.common.const import (Exchange,
                                         Interval,
                                         InstrumentType,
                                         Product,
                                         EntityType,
                                         ProviderType
                                         )
from btc_model.core.wrapper.binance_api_wrapper import BinanceApiWrapper
from btc_model.core.update_data.base_downloader import BaseDownloader
from btc_model.core.util.log_util import Logger
from btc_model.core.util.file_util import FileUtil


class CryptoDataLoader():
    def __init__(self, data_directory):
        """
        初始化 CryptoDataLoader 类的实例。

        参数:
        data_directory (str): 数据文件所在的目录路径。
        """
        self.data_directory = data_directory

    def _internal_load_data(self,
                            exchange: Exchange,
                            entity_type: EntityType,
                            interval: Interval,
                            provider_type: ProviderType
                            ):
        """
        内部方法，用于加载指定交易所、实体类型、时间间隔和数据提供者类型的数据。

        参数:
        exchange (Exchange): 交易所类型。
        entity_type (EntityType): 实体类型，如KLINE、INSTRUMENT等。
        interval (Interval): 时间间隔，如DAILY、HOURLY等。
        provider_type (ProviderType): 数据提供者类型。

        返回:
        pd.DataFrame: 加载的数据，如果文件不存在则返回None。
        """
        # 获取本地实体数据的根路径
        root_path = FileUtil.get_local_entity_root_path(output_dir=self.data_directory,
                                                        entity_type=entity_type,
                                                        interval=interval,
                                                        exchange=exchange,
                                                        provider_type=provider_type
                                                        )
        # 如果路径不存在，返回None
        if not os.path.exists(root_path):
            return None

        # 读取 Parquet 文件
        data = pd.read_parquet(root_path)
        # 重置索引
        data.reset_index(inplace=True)
        return data

    def load_instruments(self, exchange: Exchange):
        return self._internal_load_data(exchange=exchange,
                                        entity_type=EntityType.INSTRUMENT,
                                        interval=Interval.NONE,
                                        provider_type=ProviderType.NONE
                                        )

    def load_kline_data(self, exchange: Exchange, interval: Interval):
        return self._internal_load_data(exchange=exchange,
                                        entity_type=EntityType.KLINE,
                                        interval=interval,
                                        provider_type=ProviderType.NONE
                                        )

    def load_kline_index_data(self, exchange: Exchange, interval: Interval):
        return self._internal_load_data(exchange=exchange,
                                        entity_type=EntityType.KLINE_INDEX,
                                        interval=interval,
                                        provider_type=ProviderType.NONE
                                        )

    def load_indicator_data(self, exchange: Exchange, interval: Interval, provider_type: ProviderType):
        return self._internal_load_data(exchange=exchange,
                                        entity_type=EntityType.INDICATOR,
                                        interval=interval,
                                        provider_type=provider_type
                                        )


if __name__ == "__main__":
    from btc_model.core.common.const import PROJECT_NAME
    from btc_model.core.util.file_util import FileUtil

    output_dir = FileUtil.get_project_dir(project_name=PROJECT_NAME, sub_dir='data')

    data_loader = CryptoDataLoader(output_dir)
    result = data_loader.load_instruments(Exchange.OKX)
    print(result)

    Logger.info('loading kline data of exchange okx')
    result = data_loader.load_kline_data(Exchange.OKX, Interval.DAILY)
    print(result)

    Logger.info('loading index bar data of exchange okx')
    result = data_loader.load_kline_index_data(Exchange.OKX, Interval.DAILY)
    print(result)

    Logger.info('loading indicators of exchange okx')
    result = data_loader.load_indicator_data(Exchange.OKX, Interval.DAILY, ProviderType.OKX)
    print(result)

    for provider_type in [ProviderType.ALTERNATIVE, ProviderType.BITCOIN_DATA]:
        Logger.info(f'loading indicators of data provider {provider_type.value.lower()}')
        result = data_loader.load_indicator_data(Exchange.NONE, Interval.DAILY, provider_type=provider_type)
        print(result)
