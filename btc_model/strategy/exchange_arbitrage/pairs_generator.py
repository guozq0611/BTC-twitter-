import os
import ccxt
import pandas as pd
from typing import Dict, List

from btc_model.setting.setting import get_settings


class PairsGenerator:
    def __init__(self, exchange_a, exchange_b):
        self.exchange_a = exchange_a
        self.exchange_b = exchange_b

        
    def load_pairs(self, type_a="spot", subtype_a=None, type_b="spot", subtype_b=None):
        self.exchange_a.load_markets()
        self.exchange_b.load_markets()

        markets_a = {
            (m['base'], m['quote']): m['symbol']
            for m in self.exchange_a.markets.values()
            if m['type'] == type_a and (subtype_a is None or m[subtype_a])
        }
        markets_b = {
            (m['base'], m['quote']): m['symbol']
            for m in self.exchange_b.markets.values()
            if m['type'] == type_b and (subtype_b is None or m[subtype_b])
        }

        pair_keys = set(markets_a.keys()).intersection(set(markets_b.keys()))
        return [
            {
                'base': base,
                'quote': quote,
                'symbol_a': markets_a[(base, quote)],
                'symbol_b': markets_b[(base, quote)],
            }
            for base, quote in pair_keys
        ]

    def detect_abnormal_pairs(self, pairs, threshold=0.05):
        """
        用于检测价差异常的函数
        参数说明：
        :param matched_pairs: load_pairs函数返回的匹配交易对列表
        :param threshold: 视为异常的价格差异比例（0.05表示5%）
        
        返回结构：
        {
            'base': 基准货币,
            'quote': 计价货币,
            'symbol_a': 交易所A交易对,
            'symbol_b': 交易所B交易对,
            'price_a': 原始价格A,
            'price_b': 原始价格B,
            'spread_ratio': 价差比例,
            'is_abnormal': 是否异常
        }
        """
        new_pairs = []
        abonormal_pairs = []
        for pair in pairs:
            try:
                # 获取最新行情数据（单次尝试）
                ticker_a = self.exchange_a.fetch_ticker(pair['symbol_a'])
                ticker_b = self.exchange_b.fetch_ticker(pair['symbol_b'])

                # 获取最后成交价
                price_a = ticker_a.get('last')
                price_b = ticker_b.get('last')

                # 跳过无效价格
                if None in [price_a, price_b]:
                    print(f"价格缺失: {pair['symbol_a']}/{pair['symbol_b']}")
                    continue

                # 计算价差比例（基于较小价格）
                min_price = min(price_a, price_b)
                spread_ratio = abs(price_a - price_b) / min_price
    
                # 构建结果对象
                result = {
                    **pair,
                    'price_a': price_a,
                    'price_b': price_b,
                    'spread_ratio': spread_ratio,
                    'is_abnormal': spread_ratio > threshold
                }

                if result['is_abnormal']:
                    abonormal_pairs.append(result)
                else:
                    new_pairs.append(pair)
            except Exception as e:
                print(f"处理交易对 {pair} 时发生错误: {str(e)}")

        return abonormal_pairs, new_pairs

    def run(self, type_a='swap', subtype_a='linear', type_b='swap', subtype_b='linear'):
        pairs = self.load_pairs(type_a, subtype_a, type_b, subtype_b)
        abnormal_pairs, normal_pairs = self.detect_abnormal_pairs(pairs)
        return abnormal_pairs, normal_pairs


if __name__ == "__main__":
    params = {
            'enableRateLimit': True,
            'proxies': {
                "http": get_settings('common')['proxies']['http'],
                "https": get_settings('common')['proxies']['https'],
            }
        }
            
    binance = ccxt.binance(params)
    okx = ccxt.okx(params)

    pairs_generator = PairsGenerator(binance, okx)
    abnormal_pairs, normal_pairs = pairs_generator.run()
    pd.DataFrame(normal_pairs).to_csv("normal_pairs.csv")
    pd.DataFrame(abnormal_pairs).to_csv("abnormal_pairs.csv")