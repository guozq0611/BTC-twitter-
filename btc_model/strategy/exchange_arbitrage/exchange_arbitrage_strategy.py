import pandas as pd
import threading
import queue
import asyncio
import ccxt.pro as ccxtpro
from btc_model.core.util.log_util import Logger
from btc_model.strategy.exchange_arbitrage.pairs_monitor import PairsMonitor


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

    def send_order(self, order):
        pass

    def cancel_order(self, order):
        pass

    def on_arbitrage_opportunity(self, pair_key, data):
        """处理套利机会""" 
        Logger.info(f"套利信号触发: {'-'.join(pair_key) :<10} 价差: {data['spread']:>6.2%}, {data['comment']}"
)
       


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
