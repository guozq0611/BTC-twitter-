import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

import sys
sys.path.append('/Users/Jason/work/source/03_ThorpAI')

from btc_model.core.util.log_util import Logger
from btc_model.core.update_data.okx_downloader import OKxDownloader

from btc_model.setting.setting import get_settings
from btc_model.core.common.const import PROJECT_NAME, Interval
from btc_model.core.util.file_util import FileUtil
from btc_model.core.common.const import (Exchange,
                                         Interval,
                                         InstrumentType,
                                         Product,
                                         EntityType,
                                         ProviderType
                                         )

from btc_model.core.data_loader.crypto_data_loader import CryptoDataLoader



# 读入日线行情
data_dir = FileUtil.get_project_dir(project_name=PROJECT_NAME, sub_dir='data')

data_loader = CryptoDataLoader(data_dir)

Logger.info('loading indicators of exchange okx')
df_indicator = data_loader.load_indicator_data(Exchange.OKX, Interval.DAILY, ProviderType.OKX)
df_indicator = df_indicator[df_indicator['symbol_id'] == 'BTC-USDT']
df_indicator['date'] = pd.to_datetime(df_indicator['datetime']).dt.date
df_indicator = df_indicator[[x for x in df_indicator.columns if x not in ['symbol_id', 'datetime','insert_timestamp',
       'modify_timestamp', 's2f_14_value']]]
df_indicator.set_index('date', inplace=True)


# df_indicator.to_csv('output/indicator.csv', index=False)

df_other_indicator = pd.DataFrame()
for provider_type in [ProviderType.ALTERNATIVE, ProviderType.BITCOIN_DATA]:
    Logger.info(f'loading indicators of data provider {provider_type.value.lower()}')
    data = data_loader.load_indicator_data(Exchange.NONE, Interval.DAILY, provider_type=provider_type)
    data['date'] = pd.to_datetime(data['date']).dt.date
    data.set_index('date', inplace=True)
    df_other_indicator = pd.concat([df_other_indicator, data], axis=1, ignore_index=False, join='outer')

# 排序索引，确保按日期对齐
df_other_indicator.sort_index(inplace=True)

df_final = pd.concat([df_indicator, df_other_indicator], axis=1, ignore_index=False).sort_index().dropna()

# --- 费舍尔变换函数 (保持不变) ---
def fisher_transform(price, period=10):
    price_range = price.rolling(window=period).max() - price.rolling(window=period).min()
    relative_price = (price - price.rolling(window=period).min()) / price_range
    relative_price = np.clip(relative_price, 0, 1)
    fisher = 0.5 * np.log((1 + relative_price) / (1 - relative_price))
    return fisher

# 标题
st.title('技术指标交互图表')

# 子图选择
selected_plots = st.multiselect(
    '选择要显示的子图:',
    ['Close Price & Bollinger Bands', 'Fisher Transform', 'MACD', 'Mayer Multiple', 'Pi Cycle MA', 'RSI', 'Fear & Greed Index', 'STH MVRV', 'MVRV Z-Score'],
    default=['Close Price & Bollinger Bands', 'Fisher Transform', 'MACD', 'RSI'] # 默认选择
)

df = df_final.copy() # 复制数据，防止修改原始数据

# 计算 Fisher 变换 (确保在绘图前计算)
df['fisher'] = fisher_transform(df['close'], period=20)

# --- 创建子图 ---
num_plots = len(selected_plots)
fig, axs = plt.subplots(num_plots, 1, figsize=(14, 6 * num_plots), sharex=True) # 根据选择的图表数量动态调整高度
axs = [axs] if num_plots == 1 else axs # 当只有一个子图时，确保 axs 是列表

plot_index = 0 # 用于追踪当前绘制的子图索引

# --- 绘制 Close Price 和 Bollinger Bands ---
if 'Close Price & Bollinger Bands' in selected_plots:
    ax1 = axs[plot_index]

    ax1.plot(df.index, df['close'], label='Close Price', color='blue')
    ax1.plot(df.index, df['boll_100_2@5_upper'], label='Bollinger Upper Band', color='red', linestyle='--')
    ax1.plot(df.index, df['boll_100_2@5_middle'], label='Bollinger Middle Band', color='green', linestyle='--')
    ax1.plot(df.index, df['boll_100_2@5_lower'], label='Bollinger Lower Band', color='orange', linestyle='--')

    last_break_index_bb = None
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['boll_100_2@5_upper'].iloc[i] and df['close'].iloc[i-1] <= df['boll_100_2@5_upper'].iloc[i-1]:
            ax1.axvline(x=df.index[i], color='lightgray', linestyle='--')
            last_break_index_bb = i

    if last_break_index_bb is not None:
        ax1.axvline(x=df.index[last_break_index_bb], color='lightgray', linestyle='--', label='BB Break')

    # 叠加 Fisher Transform 信号
    last_signal_index_fisher = None
    for i in range(1, len(df)):
        if (df['fisher'].iloc[i] > 0 and df['fisher'].iloc[i-1] <= 0) or (df['fisher'].iloc[i] < 0 and df['fisher'].iloc[i-1] >= 0):
            ax1.axvline(x=df.index[i], color='lightblue', linestyle='--', alpha=0.7)
            last_signal_index_fisher = i

    if last_signal_index_fisher is not None:
        ax1.axvline(x=df.index[last_signal_index_fisher], color='lightblue', linestyle='--', alpha=0.7, label='Fisher Signal')

    ax1.set_title('Close Price and Bollinger Bands with Fisher Transform Signals')
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')
    ax1.grid(True)
    plot_index += 1

# --- 绘制 Fisher Transform ---
if 'Fisher Transform' in selected_plots:
    ax2 = axs[plot_index]

    ax2.plot(df.index, df['fisher'], label='Fisher Transform', color='purple')
    ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8)

    last_signal_index_fisher = None
    for i in range(1, len(df)):
        if (df['fisher'].iloc[i] > 0 and df['fisher'].iloc[i-1] <= 0) or (df['fisher'].iloc[i] < 0 and df['fisher'].iloc[i-1] >= 0):
             ax2.axvline(x=df.index[i], color='lightblue', linestyle='--', alpha=0.7)
             last_signal_index_fisher = i

    if last_signal_index_fisher is not None:
        ax2.axvline(x=df.index[last_signal_index_fisher], color='lightblue', linestyle='--', alpha=0.7, label='Fisher Signal')

    ax2.set_title('Fisher Transform')
    ax2.set_ylabel('Fisher Value')
    ax2.legend(loc='upper left')
    ax2.grid(True)
    plot_index += 1

# --- 绘制 MACD 指标 ---
if 'MACD' in selected_plots:
    ax3 = axs[plot_index]

    ax3.plot(df.index, df['macd_16_26_9_dif'], label='MACD DIF', color='blue')
    ax3.plot(df.index, df['macd_16_26_9_dea'], label='MACD DEA', color='red', linestyle='--')
    ax3.bar(df.index, df['macd_16_26_9_hist'], label='MACD Histogram', color='gray', alpha=0.5)

    ax3.set_title('MACD Indicator')
    ax3.set_ylabel('MACD Value')
    ax3.legend(loc='upper left')
    ax3.grid(True)
    plot_index += 1

# --- 绘制 Mayer Multiple ---
if 'Mayer Multiple' in selected_plots:
    ax4 = axs[plot_index]

    ax4.plot(df.index, df['mayer_multiple_200_value'], label='Mayer Multiple', color='green')
    ax4.axhline(1, color='gray', linestyle='--', linewidth=0.8)

    ax4.set_title('Mayer Multiple 200')
    ax4.set_ylabel('Mayer Multiple')
    ax4.legend(loc='upper left')
    ax4.grid(True)
    plot_index += 1

# --- 绘制 Pi Cycle MA ---
if 'Pi Cycle MA' in selected_plots:
    ax5 = axs[plot_index]

    ax5.plot(df.index, df['pi_cycle_111_350__ma_short'], label='Pi Cycle MA Short', color='orange')
    ax5.plot(df.index, df['pi_cycle_111_350_ma_long'], label='Pi Cycle MA Long', color='purple')

    ax5.set_title('Pi Cycle Moving Averages')
    ax5.set_ylabel('MA Value')
    ax5.legend(loc='upper left')
    ax5.grid(True)
    plot_index += 1

# --- 绘制 RSI ---
if 'RSI' in selected_plots:
    ax6 = axs[plot_index]

    ax6.plot(df.index, df['rsi_14_value'], label='RSI 14', color='blue')
    ax6.axhline(70, color='red', linestyle='--', linewidth=0.8)
    ax6.axhline(30, color='green', linestyle='--', linewidth=0.8)

    ax6.set_title('RSI 14')
    ax6.set_xlabel('Date')
    ax6.set_ylabel('RSI Value')
    ax6.legend(loc='upper left')
    ax6.grid(True)
    plot_index += 1

# --- 绘制 Fear & Greed Index (FGI) ---
if 'Fear & Greed Index' in selected_plots:
    ax7 = axs[plot_index]
    ax7.plot(df.index, df['fgi'], label='FGI', color='orange')
    ax7.set_title('Fear & Greed Index (FGI)')
    ax7.set_ylabel('Index Value')
    ax7.legend(loc='upper left')
    ax7.grid(True)
    plot_index += 1

# --- 绘制 STH MVRV ---
if 'STH MVRV' in selected_plots:
    ax8 = axs[plot_index]
    ax8.plot(df.index, df['sth_mvrv'], label='STH MVRV', color='green')
    ax8.set_title('STH MVRV')
    ax8.set_ylabel('STH MVRV Value')
    ax8.legend(loc='upper left')
    ax8.grid(True)
    plot_index += 1

# --- 绘制 MVRV Z-Score ---
if 'MVRV Z-Score' in selected_plots:
    ax9 = axs[plot_index]
    ax9.plot(df.index, df['mvrv_zscore'], label='MVRV Z-Score', color='purple')
    ax9.set_title('MVRV Z-Score')
    ax9.set_xlabel('Date')
    ax9.set_ylabel('Z-Score')
    ax9.legend(loc='upper left')
    plot_index += 1

# 调整子图布局
plt.tight_layout()

# 在 Streamlit 中显示 Matplotlib 图表
st.pyplot(fig)