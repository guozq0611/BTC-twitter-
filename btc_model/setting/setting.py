import os
from logging import CRITICAL
from typing import Dict, Any

from btc_model.core.util.file_util import FileUtil

SETTINGS: Dict[str, Any] = {
    # 配置request url需要的proxies，如果网络环境无需代理，注释即可
    "common.proxies": {
        # 'http': 'http://127.0.0.1:52469',
        # 'https': 'http://127.0.0.1:52469'
        'http': 'http://127.0.0.1:7897',
        'https': 'http://127.0.0.1:7897'
    },


    "font.family": "微软雅黑",
    "font.size": 12,

    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # 为避免真实账户信息泄露，这里填写的是模拟账户的apikey和secretkey
    # 如果需要使用实盘账户，请在os.getenv('cex_okx')中填写实盘账户的apikey和secretkey
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # "cex.okx.apikey": "dede12e9-ec61-4212-944e-9ac5138f743b",
    # "cex.okx.secretkey": "E70C2C82FDC68D98DC7252B83745B38F",
    # "cex.okx.passphrase": "Qwe123!@#",

    # "cex.okx.apikey": "19e04efb-e8ee-4ceb-8706-e45815b605f7",
    # "cex.okx.secretkey": "E826805718DA2A9DA8CD1C8882E92B5F",
    # "cex.okx.passphrase": "Qwe123!@#",

    # mail.com
    "cex.okx.apikey": "8731b892-efa3-42f8-993d-4213c2d2e201",
    "cex.okx.secretkey": "23558898E2AC618C0D61CB57EB988CB0",
    "cex.okx.passphrase": "Qwe123!@#",
     # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # 配置okx用的代理，若网络网络无需代理，设置为None
    "cex.okx.proxy": "http://127.0.0.1:7897",
    #"cex.okx.proxy": None,

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # 为避免真实账户信息泄露，这里填写的是模拟账户的apikey和secretkey
    # 如果需要使用实盘账户，请在os.getenv('cex_binance')中填写实盘账户的apikey和secretkey
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    "cex.binance.apikey": "Yef2imrldezU8R6hdgvBFPgMMFnsxG06TvPoQUpwP5UI4jw9XhM4MudQbCFgXVis",
    "cex.binance.secretkey": "66Rc9gtt1OnudixpPKvIuqNL56YSymtfz8WQ6Q9rfw58R2TxAUY3RH4ohjaJkeYu",

    # ------------------------------------------------------
    # 设置逃顶模型各指标的参数
    # ------------------------------------------------------
    "escape_model.indicator.pi_cycle.short_window": 111,
    "escape_model.indicator.pi_cycle.long_window": 350,
    "escape_model.indicator.pi_cycle.threshold": 2,

    "escape_model.indicator.mvrv_zscore.threshold": 8,

    "escape_model.indicator.mayer_multiple.window": 200,
    "escape_model.indicator.mayer_multiple.threshold": 2.4,

    "escape_model.indicator.feargreed.threshold": 80,

    "escape_model.indicator.rsi.window": 14,
    "escape_model.indicator.rsi.upper": 70,
    "escape_model.indicator.rsi.lower": 30,

    "escape_model.indicator.macd.fast_period": 12,
    "escape_model.indicator.macd.slow_period": 26,
    "escape_model.indicator.macd.signal_period": 9,

    "escape_model.indicator.sth_mvrv.threshold": 2,

    "escape_model.indicator.bollinger.window": 100,
    "escape_model.indicator.bollinger.nbdev": 2.5,
    # ------------------------------------------------------

    # ------------------------------------------------------
    # update_manager的参数
    # ------------------------------------------------------
    "update_manager.indicator.use_exchange": 'OKX',
    "update_manager.indicator.symbols": ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'SOL-USDT'],


    "database.uri": "",
    "database.name": "",
    "database.database": "",
    "database.host": "",
    "database.port": 0,
    "database.user": "",
    "database.password": "",
    "database.auth_source": ''
}


# Load global setting from json file.
# SETTING_FILENAME: str = "blockchain_setting.json"
# SETTINGS.update(FileUtil.load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length = len(prefix)
    if prefix_length > 0 and not prefix.endswith('.'):
        prefix = prefix + '.'
        prefix_length += 1

    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}


def get_proxy_settings():
    # 优先使用环境变量
    http_proxy = os.getenv('http_proxy')
    https_proxy = os.getenv('https_proxy')
    
    if http_proxy and https_proxy:
        return {
            "http": http_proxy,
            "https": https_proxy
        }
    
    # 如果环境变量未设置，使用 SETTINGS 中的配置
    return SETTINGS.get("common.proxies", {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    })

