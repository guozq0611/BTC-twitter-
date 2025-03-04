from dataclasses import field
from typing import Dict

from btc_model.core.common.object import PositionData, AccountData


class PositionHolder:
    """
    Position holder is used for tracking all positions and accounts.
    """
    positions: Dict[str, PositionData] = field(default_factory=dict)

    def add_position(self, symbol: str, quantity: float, entry_price: float) -> None:
        """添加新的仓位"""
        if symbol in self.positions:
            # 如果仓位已存在，更新数量和开仓价格
            existing_position = self.positions[symbol]
            existing_position.quantity += quantity
            existing_position.entry_price = (existing_position.entry_price * existing_position.quantity + entry_price * quantity) / (existing_position.quantity + quantity)
        else:
            # 创建新的仓位
            self.positions[symbol] = PositionData(symbol, quantity, entry_price)

    def remove_position(self, symbol: str, quantity: float) -> None:
        """移除仓位"""
        if symbol in self.positions:
            existing_position = self.positions[symbol]
            if existing_position.quantity >= quantity:
                existing_position.quantity -= quantity
                if existing_position.quantity == 0:
                    del self.positions[symbol]  # 如果数量为0，删除仓位
            else:
                raise ValueError("移除的数量超过现有仓位")
        else:
            raise ValueError("该仓位不存在")

    def get_position_value(self, symbol: str, current_price: float) -> float:
        """获取特定仓位的当前价值"""
        if symbol in self.positions:
            return self.positions[symbol].current_value(current_price)
        else:
            raise ValueError("该仓位不存在")

    def total_value(self, current_prices: Dict[str, float]) -> float:
        """计算所有仓位的总价值"""
        total = 0.0
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                total += position.current_value(current_prices[symbol])
            else:
                raise ValueError(f"当前价格中缺少仓位 {symbol} 的价格")
        return total