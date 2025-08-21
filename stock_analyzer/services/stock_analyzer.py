"""
股票分析服務模組
"""
import pandas as pd
from typing import Optional, Tuple, List

from ..core.stock_data import StockData
from ..core.stock_visualizer import StockDataVisualizer
from ..services.line_notifier import LineNotifier
from ..utils.config import Config
from ..utils.logger import setup_logger


class StockAnalyzer:
    """主要股票分析服務類"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化股票分析器
        
        Args:
            config: 配置對象
        """
        self.config = config or Config()
        self.logger = setup_logger(self.__class__.__name__)
        
        # 初始化服務組件
        self.stock_data = StockData(self.config)
        self.line_notifier = LineNotifier(self.config)
        
        self.logger.info("股票分析器初始化完成")
    
    def get_stock_screening_conditions(self) -> dict:
        """
        獲取股票篩選條件
        
        Returns:
            篩選條件字典
        """
        return {
            '合計買賣超張數': 0,  # 法人買超
            '外資連續買賣日數': 5,  # 外資連續買入天數
            '自營商連續買賣日數': 3,  # 自營商連續買入天數  
            '投信連續買賣日數': 3,  # 投信連續買入天數
            '漲跌幅': 0,  # 當日上漲
            '成交張數': 5000,  # 最小成交量
            '5日均線大於20日均線': True,  # 短期均線在上
            '20日均線大於60日均線': True   # 長期趨勢向上
        }
    
    def screen_stocks(self, custom_conditions: Optional[dict] = None) -> Tuple[pd.DataFrame, List[str]]:
        """
        執行股票篩選
        
        Args:
            custom_conditions: 自定義篩選條件
            
        Returns:
            篩選結果DataFrame和合格股票代號列表
        """
        try:
            self.logger.info("開始執行股票篩選...")
            
            # 獲取所有數據
            self.stock_data.get_co_data()
            self.stock_data.get_co_revenue_data()  
            self.stock_data.get_co_ma_data()
            self.stock_data.get_co_macd_data()
            self.stock_data.get_co_cons_data()
            matched_df, revenue_columns = self.stock_data.match_data()
            
            if matched_df.empty:
                self.logger.warning("未獲取到股票數據")
                return pd.DataFrame(), []
            
            # 套用篩選條件
            conditions = custom_conditions or self.get_stock_screening_conditions()
            
            selected_stocks = matched_df[
                (matched_df['合計買賣超張數'] > conditions.get('合計買賣超張數', 0)) & 
                ((matched_df['外資連續買賣日數'] >= conditions.get('外資連續買賣日數', 5)) | 
                 (matched_df['自營商連續買賣日數'] >= conditions.get('自營商連續買賣日數', 3)) | 
                 (matched_df['投信連續買賣日數'] >= conditions.get('投信連續買賣日數', 3))) & 
                (matched_df['漲跌幅'] > conditions.get('漲跌幅', 0)) & 
                (matched_df['5日均線'] > matched_df['20日均線']) &
                (matched_df['成交張數'] >= conditions.get('成交張數', 5000)) & 
                (matched_df['20日均線'] > matched_df['60日均線'])
            ]
            
            # 篩選有效股票代號
            stock_ids = selected_stocks[
                selected_stocks['代號'].str.match(r'^\d{4}$')
            ]['代號'].tolist()
            
            self.logger.info(f"股票篩選完成，找到 {len(selected_stocks)} 支符合條件的股票")
            return selected_stocks, stock_ids
            
        except Exception as e:
            self.logger.error(f"股票篩選失敗: {str(e)}")
            return pd.DataFrame(), []
    
    def analyze_individual_stock(self, stock_id: str) -> Tuple[bool, str]:
        """
        分析個別股票
        
        Args:
            stock_id: 股票代號
            
        Returns:
            是否符合買入條件和分析結果
        """
        try:
            self.logger.info(f"開始分析股票 {stock_id}")
            
            stock_visualizer = StockDataVisualizer(stock_id, self.config)
            stock_visualizer.fetch_data()
            stock_visualizer.clean_daily_data()
            
            # 判斷是否符合買入條件
            is_bullish = stock_visualizer.is_stock_bullish()
            
            if is_bullish:
                # 清理月線數據並生成圖表
                stock_visualizer.clean_monthly_data()
                # stock_visualizer.plot_stock_price()
                # stock_visualizer.plot_closing_price()
                # stock_visualizer.plot_foreign_investment()
                # stock_visualizer.plot_revenue_growth()
                
                # 獲取AI分析
                analysis = stock_visualizer.chatgpt_analysis()
                
                self.logger.info(f"股票 {stock_id} 符合買入條件")
                return True, analysis
            else:
                self.logger.info(f"股票 {stock_id} 不符合買入條件")
                return False, "不符合技術面買入條件"
                
        except Exception as e:
            self.logger.error(f"分析股票 {stock_id} 失敗: {str(e)}")
            return False, f"分析失敗: {str(e)}"
    
    def run_daily_analysis(self, send_notification: bool = True) -> dict:
        """
        執行每日股票分析
        
        Args:
            send_notification: 是否發送LINE通知
            
        Returns:
            分析結果摘要
        """
        try:
            self.logger.info("開始執行每日股票分析")
            
            # 篩選股票
            selected_stocks, stock_ids = self.screen_stocks()
            
            analysis_results = {
                'total_screened': len(selected_stocks),
                'qualified_stocks': [],
                'analysis_results': {},
                'notification_sent': False
            }
            
            # 發送篩選摘要
            if send_notification and not selected_stocks.empty:
                stock_date = selected_stocks.iloc[0].get('法人買賣日期', 'N/A')
                analysis_results['notification_sent'] = self.line_notifier.send_stock_summary(
                    selected_stocks, stock_date
                )
            
            # 分析個別股票
            for stock_id in stock_ids:
                is_bullish, analysis = self.analyze_individual_stock(stock_id)
                
                if is_bullish:
                    analysis_results['qualified_stocks'].append(stock_id)
                    analysis_results['analysis_results'][stock_id] = analysis
                    
                    # 發送個別股票分析
                    if send_notification:
                        self.line_notifier.send_stock_analysis(stock_id, analysis)
            
            self.logger.info(f"每日分析完成，共分析 {len(stock_ids)} 支股票，"
                           f"{len(analysis_results['qualified_stocks'])} 支符合買入條件")
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"每日股票分析失敗: {str(e)}")
            return {'error': str(e)}
    
    def get_analysis_summary(self, results: dict) -> str:
        """
        生成分析摘要報告
        
        Args:
            results: 分析結果字典
            
        Returns:
            摘要報告文字
        """
        if 'error' in results:
            return f"分析過程發生錯誤: {results['error']}"
        
        summary = f"""
=== 每日股票分析報告 ===

📊 篩選結果:
• 符合初步條件股票: {results['total_screened']} 支
• 符合買入條件股票: {len(results['qualified_stocks'])} 支

🎯 推薦買入股票:
{', '.join(results['qualified_stocks']) if results['qualified_stocks'] else '無'}

📱 通知狀態:
{'已發送LINE通知' if results['notification_sent'] else '未發送通知'}

=========================
        """
        
        return summary.strip()