import pandas as pd
import threading
import queue
import asyncio
import ccxt.pro as ccxtpro
from btc_model.core.util.log_util import Logger
from btc_model.strategy.exchange_arbitrage.pairs_monitor import PairsMonitor
from btc_model.core.common.object import PositionData
from btc_model.core.util.crypto_util import get_position_data


class ExchangeArbitrageStrategy:
    def __init__(self, exchange_1: ccxtpro.Exchange, exchange_2: ccxtpro.Exchange, pairs: list):
        self.exchange_1 = exchange_1
        self.exchange_2 = exchange_2
        self.pairs = pairs

        self.pair_monitor = PairsMonitor(self.exchange_1, self.exchange_2, self.pairs)
        self.pair_monitor.add_arbitrage_opportunity_event(self.on_arbitrage_opportunity)

        self.lock = threading.Lock()
        # 通过队列保存接收到的套利机会，并通过其他线程处理队列中的数据
        self.queue = queue.Queue()
        # 套利机会事件列表
        self.on_arbitrage_event_list = []
        self.websocket_manager = None

    # def start(self):
    #     try:
    #         t = threading.Thread(target=self.run, daemon=True)
    #         t.start()
    #         return True
    #     except Exception as e:
    #         logger.error(f"启动ExchangeArbitrageStrategy失败,错误信息:{e}", exc_info=True)
    #         return False


    async def run_monitor(self):
        await self.exchange_1.load_markets()
        await self.exchange_2.load_markets()

        self.pair_monitor.start()
        
        try:
            while True:
                await asyncio.sleep(1)
        except:
            self.pair_monitor.stop()
            print("监控已停止")
        
    def execute(self):
        try:
            asyncio.run(self.run_monitor())
        except KeyboardInterrupt:
            print("程序已终止")


    def load_positions(self):
        """刷新两个交易所的持仓数据（现货和永续合约）"""
        try:
            # 刷新第一个交易所的持仓数据
            # 获取现货持仓
            spot_balance1 = self.exchange1.fetch_balance()
            if spot_balance1:
                for currency, balance in spot_balance1['total'].items():
                    if balance > 0:
                        self.position_holder1.add_position(
                            f"{currency}/USDT", 
                            balance,
                            0  # 现货没有entry_price概念
                        )

            # 获取永续合约持仓
            futures_positions1 = self.exchange1.fetch_positions()
            if futures_positions1:
                for position in futures_positions1:
                    if float(position['contracts']) != 0:
                        self.position_holder1.add_position(
                            position['symbol'],
                            float(position['contracts']),
                            float(position['entryPrice'])
                        )

            # 刷新第二个交易所的持仓数据
            # 获取现货持仓
            spot_balance2 = self.exchange2.fetch_balance()
            if spot_balance2:
                for currency, balance in spot_balance2['total'].items():
                    if balance > 0:
                        self.position_holder2.add_position(
                            f"{currency}/USDT", 
                            balance,
                            0  # 现货没有entry_price概念
                        )

            # 获取永续合约持仓
            futures_positions2 = self.exchange2.fetch_positions()
            if futures_positions2:
                for position in futures_positions2:
                    if float(position['contracts']) != 0:
                        self.position_holder2.add_position(
                            position['symbol'],
                            float(position['contracts']),
                            float(position['entryPrice'])
                        )

            self.logger.info("持仓数据刷新成功")

        except Exception as e:
            self.logger.error(f"刷新持仓数据失败: {str(e)}")
            raise

    def send_order(self, order):
        pass

    def cancel_order(self, order):
        pass

    def on_arbitrage_opportunity(self, pair_key, data):
        """处理套利机会""" 
        Logger.info(f"套利信号触发: {'-'.join(pair_key) :<10} 价差: {data['spread']:>6.2%}, {data['comment']}"
)
       

    async def start(self):
        # 启动 WebSocket 服务器
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)

    def get_exchange_a_price(self):
        # 实现获取交易所A价格的方法
        pass

    def get_exchange_b_price(self):
        # 实现获取交易所B价格的方法
        pass

    def get_price_diff(self):
        # 实现获取价差的方法
        pass

    def get_diff_percentage(self):
        # 实现获取价差百分比的方法
        pass


if __name__ == "__main__":
    from btc_model.setting.setting import get_settings

    params = {
        'enableRateLimit': True,
        'proxies': {
            'http': get_settings('common')['proxies']['http'],
            'https': get_settings('common')['proxies']['https'],
        },
        'aiohttp_proxy': get_settings('common')['proxies']['http'],
        'ws_proxy': get_settings('common')['proxies']['http']
    }


    try:
        pairs_df = pd.read_csv("normal_pairs.csv")
        pairs_dif = pairs_df[pairs_df['quote'] == "USDT"]
        required_cols = ['base', 'quote', 'symbol_a', 'symbol_b']
        if not all(col in pairs_df.columns for col in required_cols):
            raise ValueError("CSV文件缺少必要列")
        pairs = pairs_df[required_cols].to_dict('records')
    except Exception as e:
        print(f"配置加载失败: {str(e)}")
        exit(1)

    # 交易所初始化
    exchange_1 = ccxtpro.binance(params)
    exchange_2 = ccxtpro.okx(params)
    
    strategy = ExchangeArbitrageStrategy(exchange_1, exchange_2, pairs)
    Logger.info("跨交易所套利监控程序已启动")
    strategy.execute()
    print("程序已终止")
