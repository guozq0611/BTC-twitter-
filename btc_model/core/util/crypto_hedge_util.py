import ccxt
import numpy as np
from typing import Dict, List
from btc_model.core.util.crypto_util import CryptoUtil

class CryptoHedgeUtil:
    """永续合约对冲工具类"""
    
    __instance = None
    
    def __init__(self):
        self.crypto_util = CryptoUtil.get_instance()
        
    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance
        
    def analyze_hedge_opportunity(self, exchange_a: ccxt.Exchange, exchange_b: ccxt.Exchange,
                                symbol: str, window: int = 30) -> Dict:
        """
        分析两个交易所间的永续合约对冲机会
        
        Args:
            exchange_a: 第一个交易所实例
            exchange_b: 第二个交易所实例
            symbol: 合约交易对
            window: 回看窗口（天数）
            
        Returns:
            Dict: {
                'funding_analysis': {
                    'rate_diff': {
                        'mean': 资金费率差均值,
                        'std': 资金费率差标准差,
                        'annualized_return': 年化收益率预期
                    },
                    'correlation': 两个交易所资金费率相关性,
                    'optimal_side': {
                        'exchange_a': '做多/做空',
                        'exchange_b': '做多/做空'
                    }
                },
                'cost_analysis': {...},
                'risk_metrics': {...},
                'recommendation': {...}
            }
        """
        try:
            # 1. 获取历史资金费率数据
            funding_a = self.crypto_util.analyze_funding_history(exchange_a, symbol, limit=window*8)
            funding_b = self.crypto_util.analyze_funding_history(exchange_b, symbol, limit=window*8)
            
            # 2. 计算资金费率差异统计
            rate_diff_analysis = self._analyze_funding_rate_difference(funding_a, funding_b, window)
            
            # 3. 分析交易成本
            cost_analysis = self._analyze_hedge_costs(exchange_a, exchange_b, symbol, rate_diff_analysis)
            
            # 4. 评估风险指标
            risk_metrics = self._evaluate_hedge_risks(exchange_a, exchange_b, symbol, rate_diff_analysis)
            
            # 5. 生成建议
            recommendation = self._generate_hedge_recommendation(
                rate_diff_analysis, cost_analysis, risk_metrics
            )
            
            return {
                'funding_analysis': rate_diff_analysis,
                'cost_analysis': cost_analysis,
                'risk_metrics': risk_metrics,
                'recommendation': recommendation
            }
            
        except Exception as e:
            raise Exception(f"分析对冲机会失败: {str(e)}")
            
  
            
    def calculate_funding_statistics(self, rates: List[Dict], window: int = 30) -> Dict:
        """
        计算资金费率统计指标
        
        Args:
            rates: 资金费率历史数据
            window: 滚动窗口大小
            
        Returns:
            Dict: {
                'current': 当前费率,
                'rolling_mean': 滚动平均,
                'rolling_std': 滚动标准差,
                'annualized_return': 年化收益,
                'volatility': 波动率,
                'trend': 趋势分析
            }
        """
        try:
            if not rates:
                raise ValueError("没有资金费率数据")
                
            # 提取费率数据
            funding_rates = [r['fundingRate'] for r in rates]
            timestamps = [r['timestamp'] for r in rates]
            
            # 计算统计指标
            current_rate = funding_rates[-1]
            rolling_mean = np.convolve(funding_rates, np.ones(window)/window, mode='valid')
            rolling_std = np.array([np.std(funding_rates[i:i+window]) 
                                  for i in range(len(funding_rates)-window+1)])
            
            # 计算年化收益
            annual_multiplier = 365 * 8  # 每天8次资金费率
            annualized_return = rolling_mean[-1] * annual_multiplier
            
            # 分析趋势
            recent_trend = np.polyfit(range(min(len(funding_rates), window)), 
                                    funding_rates[-window:], 1)[0]
            trend = 'up' if recent_trend > 0.0001 else 'down' if recent_trend < -0.0001 else 'stable'
            
            return {
                'current': float(current_rate),
                'rolling_mean': rolling_mean.tolist(),
                'rolling_std': rolling_std.tolist(),
                'annualized_return': float(annualized_return),
                'volatility': float(np.std(funding_rates)),
                'trend': trend,
                'timestamps': timestamps
            }
            
        except Exception as e:
            raise Exception(f"计算资金费率统计失败: {str(e)}")
            
   

    def analyze_spot_futures_hedge(self, exchange: ccxt.Exchange, symbol: str, window: int = 30) -> Dict:
        """
        分析现货多头+永续合约空头的资金费率收益
        
        Args:
            exchange: 交易所实例
            symbol: 合约交易对
            window: 回看窗口（天数）
            
        Returns:
            Dict: {
                'funding_analysis': {
                    'funding_stats': {
                        'mean': 资金费率均值,
                        'std': 资金费率标准差,
                        'annualized_return': 年化资金费率收益
                    },
                    'position_side': {
                        'spot': '多头',
                        'futures': '空头'
                    }
                },
                'cost_analysis': {
                    'spot_trading_fee': 现货交易费率,
                    'futures_trading_fee': 合约交易费率,
                    'estimated_holding_cost': 预计持仓成本
                },
                'risk_metrics': {
                    'funding_volatility': 资金费率波动率,
                    'basis_risk': 基差风险指标,
                    'liquidation_risk': 强平风险评估
                }
            }
        """
        try:
            # 转换为合约符号
            contract_symbol = self.crypto_util.convert_symbol_to_contract(exchange, symbol)
            
            # 1. 获取永续合约历史资金费率数据
            history = exchange.fetch_funding_rate_history(contract_symbol, limit=window*8)
            
            # 转换为所需的格式
            funding_rates = [
                {
                    'timestamp': x['timestamp'],
                    'fundingRate': x['fundingRate']
                }
                for x in history if x['fundingRate'] is not None
            ]
            
            # 2. 计算资金费率统计
            funding_stats = self.calculate_funding_statistics(funding_rates, window)
            
            # 3. 分析交易成本
            cost_analysis = {
                'spot_trading_fee': exchange.fees['trading'].get('taker', 0.001),
                'futures_trading_fee': exchange.fees['trading'].get('taker', 0.0005),
                'estimated_holding_cost': self._calculate_holding_cost(
                    funding_stats['annualized_return'],
                    exchange.fees['trading'].get('taker', 0.001)
                )
            }
            
            # 4. 评估风险指标
            risk_metrics = {
                'funding_volatility': funding_stats['volatility'],
                'basis_risk': self._calculate_basis_risk(exchange, symbol),
                'liquidation_risk': self._assess_liquidation_risk(exchange, symbol)
            }
            
            return {
                'funding_analysis': {
                    'funding_stats': {
                        'mean': funding_stats['rolling_mean'][-1],
                        'std': funding_stats['rolling_std'][-1],
                        'annualized_return': funding_stats['annualized_return']
                    },
                    'position_side': {
                        'spot': '多头',
                        'futures': '空头'
                    }
                },
                'cost_analysis': cost_analysis,
                'risk_metrics': risk_metrics
            }
            
        except Exception as e:
            raise Exception(f"分析现货永续对冲策略失败: {str(e)}")
            
    def _calculate_holding_cost(self, annualized_funding: float, trading_fee: float) -> float:
        """计算预计持仓成本"""
        # 考虑开仓和平仓的交易费用，以及预期的资金费率收益
        total_trading_fee = trading_fee * 4  # 现货和合约各需要开仓和平仓
        return total_trading_fee - annualized_funding  # 资金费率为正时付费，为负时收费

    def _calculate_basis_risk(self, exchange: ccxt.Exchange, symbol: str) -> float:
        """
        计算基差风险指标
        
        Args:
            exchange: 交易所实例
            symbol: 交易对
            
        Returns:
            float: 基差风险指标值 (0-1之间，越大风险越高)
        """
        try:
            # 获取现货价格
            spot_ticker = exchange.fetch_ticker(symbol)
            spot_price = spot_ticker['last']
            
            # 获取永续合约价格
            contract_symbol = self.crypto_util.convert_symbol_to_contract(exchange, symbol)
            futures_ticker = exchange.fetch_ticker(contract_symbol)
            futures_price = futures_ticker['last']
            
            # 计算基差率
            basis_rate = abs(futures_price - spot_price) / spot_price
            
            # 将基差率标准化到0-1之间
            # 假设基差率超过1%则风险较高
            normalized_risk = min(basis_rate * 100, 1.0)

            # # 使用sigmoid函数进行标准化
            # # 基差率在0.5%时对应风险值0.5
            # # 基差率在2%时对应风险值约0.88
            # # 基差率在3%时对应风险值约0.95
            # k = 400  # 斜率参数
            # x0 = 0.005  # 中点参数（0.5%基差率）
            # normalized_risk = 1 / (1 + np.exp(-k * (basis_rate - x0)))
            
            
            return normalized_risk
            
        except Exception as e:
            # 如果无法获取数据，返回较高的风险值
            return 0.8
            
    def _assess_liquidation_risk(self, exchange: ccxt.Exchange, symbol: str) -> float:
        """
        评估强平风险
        
        Args:
            exchange: 交易所实例
            symbol: 交易对
            
        Returns:
            float: 强平风险指标值 (0-1之间，越大风险越高)
        """
        try:
            # 获取24小时价格波动数据
            ticker = exchange.fetch_ticker(symbol)
            
            # 计算24小时波动率
            high = ticker['high']
            low = ticker['low']
            current = ticker['last']
            
            if not all([high, low, current]):
                return 0.5
                
            volatility = (high - low) / current
            
            # 将波动率标准化到0-1之间
            # 假设24小时波动超过10%则风险较高
            normalized_risk = min(volatility * 10, 1.0)
            
            return normalized_risk
            
        except Exception as e:
            # 如果无法获取数据，返回中等风险值
            return 0.5


if __name__ == "__main__":
    import ccxt
    from btc_model.setting.setting import get_settings

    # 获取设置
    setting = get_settings('cex.okx')

    apikey = setting['apikey']
    secretkey = setting['secretkey']
    passphrase = setting['passphrase']
    proxy = setting['proxy']

    # 初始化币安交易所
    params = {
        'enableRateLimit': True,
        'proxies': {
            'http': proxy,                  
            'https': proxy,
        },
        'apiKey': apikey,          
        'secret': secretkey,  
        'password': passphrase,     
        'options': {
            'defaultType': 'spot',  # 可选：'spot', 'margin', 'future'
        },
        'headers': {
            'x-simulated-trading': '1'
        }
    }

    exchange = ccxt.okx(params)
    exchange.set_sandbox_mode(True)

    crypto_hedge_util = CryptoHedgeUtil.get_instance()
    
    print(crypto_hedge_util.analyze_spot_futures_hedge(exchange, 'BTC/USDT'))