"""
股票分析系統 - Stock Analyzer

一個完整的股票數據分析和LINE通知系統。

主要功能：
- 股票數據爬取和分析
- 技術指標計算
- 自動選股
- LINE Bot 通知
- 圖表視覺化
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .core.stock_data import StockData
from .core.stock_visualizer import StockDataVisualizer
from .services.line_notifier import LineNotifier
from .services.stock_analyzer import StockAnalyzer
from .utils.config import Config

__all__ = [
    'StockData',
    'StockDataVisualizer', 
    'LineNotifier',
    'StockAnalyzer',
    'Config'
]