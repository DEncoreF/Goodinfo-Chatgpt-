"""
股票數據視覺化模組
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import openai as OpenAI
from IPython.display import display, Markdown
import seaborn as sns
from io import StringIO
from datetime import datetime, timedelta
import talib
from typing import Tuple, Optional

from ..utils.config import Config
from ..utils.logger import setup_logger


class StockDataVisualizer:
    """股票數據視覺化類"""
    
    def __init__(self, stock_id: str, config: Optional[Config] = None):
        """
        初始化股票視覺化器
        
        Args:
            stock_id: 股票代號
            config: 配置對象
        """
        self.stock_id = stock_id
        self.config = config or Config()
        self.logger = setup_logger(f"{self.__class__.__name__}_{stock_id}")
        
        # 數據存儲
        self.daily_df = None
        self.monthly_df = None
        self.yearly_df = None
        self.stock_name = None
    
    def fetch_data(self, days: int = 365) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        獲取股票數據
        
        Args:
            days: 獲取天數
            
        Returns:
            日線、月線、年線數據
        """
        try:
            headers = self.config.stock.headers
            today = datetime.now()
            start_date = today - timedelta(days=days)
            
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = today.strftime('%Y-%m-%d')
            
            # 獲取日線數據
            daily_url = (f'https://goodinfo.tw/tw/ShowK_Chart.asp?STOCK_ID={self.stock_id}'
                        f'&CHT_CAT=DATE&PRICE_ADJ=F&START_DT={start_date_str}&END_DT={end_date_str}')
            daily_res = requests.get(daily_url, headers=headers)
            daily_res.encoding = 'utf-8'
            daily_soup = BeautifulSoup(daily_res.text, 'lxml')
            daily_data = daily_soup.select_one('#tblDetail')
            
            if daily_data:
                daily_html_string = daily_data.prettify()
                self.daily_df = pd.read_html(StringIO(daily_html_string))[0]
                
                # 提取股票名稱
                title = daily_soup.find('title')
                if title:
                    self.stock_name = title.text.split(' ')[1] if len(title.text.split(' ')) > 1 else self.stock_id
                else:
                    self.stock_name = self.stock_id
            
            # 獲取月線數據
            monthly_url = f'https://goodinfo.tw/tw/ShowSaleMonChart.asp?STOCK_ID={self.stock_id}'
            monthly_res = requests.get(monthly_url, headers=headers)
            monthly_res.encoding = 'utf-8'
            monthly_soup = BeautifulSoup(monthly_res.text, 'lxml')
            monthly_data = monthly_soup.select_one('#tblDetail')
            
            if monthly_data:
                monthly_html_string = monthly_data.prettify()
                self.monthly_df = pd.read_html(StringIO(monthly_html_string))[0]
            else:
                self.logger.warning(f"股票代號 {self.stock_id} 無月線數據")
            
            # 獲取年線數據
            yearly_url = f'https://goodinfo.tw/tw/StockBzPerformance.asp?STOCK_ID={self.stock_id}'
            yearly_res = requests.get(yearly_url, headers=headers)
            yearly_res.encoding = 'utf-8'
            yearly_soup = BeautifulSoup(yearly_res.text, 'lxml')
            yearly_data = yearly_soup.select_one('#txtFinDetailData')
            
            if yearly_data:
                yearly_html_string = yearly_data.prettify()
                self.yearly_df = pd.read_html(StringIO(yearly_html_string))[0]
            
            self.logger.info(f"成功獲取股票 {self.stock_id} 的數據")
            return self.monthly_df, self.daily_df, self.yearly_df
            
        except Exception as e:
            self.logger.error(f"獲取股票 {self.stock_id} 數據失敗: {str(e)}")
            return None, None, None
    
    def clean_daily_data(self) -> Optional[pd.DataFrame]:
        """清理日線數據"""
        if self.daily_df is None:
            return None
            
        try:
            # 清理列名
            self.daily_df.columns = ['_'.join(col).strip() for col in self.daily_df.columns]
            
            cleaned_cols = []
            for col in self.daily_df.columns:
                parts = col.split('_')
                unique_parts = list(dict.fromkeys(parts))
                cleaned_col = ''.join(unique_parts)
                cleaned_cols.append(cleaned_col)
            
            self.daily_df.columns = cleaned_cols
            self.daily_df.columns = self.daily_df.columns.str.strip().str.replace('  ', '')
            
            # 轉換數據類型
            for col in self.daily_df.columns:
                if col != '交易日期': 
                    self.daily_df[col] = pd.to_numeric(self.daily_df[col], errors='coerce')
            
            # 處理日期
            self.daily_df = self.daily_df.drop_duplicates(keep=False)
            self.daily_df['交易日期'] = (self.daily_df['交易日期']
                                    .astype(str)
                                    .str.replace("'", ""))
            self.daily_df['交易日期'] = pd.to_datetime(
                self.daily_df['交易日期'], 
                format='%y/%m/%d', 
                dayfirst=True, 
                errors='coerce'
            )
            self.daily_df = self.daily_df.sort_values(by='交易日期', ascending=True)
            
            # 計算技術指標
            if '收盤' in self.daily_df.columns:
                self.daily_df['MA5'] = talib.SMA(self.daily_df['收盤'], timeperiod=5)
                self.daily_df['MA20'] = talib.SMA(self.daily_df['收盤'], timeperiod=20)
                
                self.daily_df['dif'], self.daily_df['signal'], self.daily_df['macd'] = talib.MACD(
                    self.daily_df['收盤'], fastperiod=12, slowperiod=26, signalperiod=9
                )
                self.daily_df['osc'] = self.daily_df['dif'] - self.daily_df['macd']
            
            self.daily_df = self.daily_df.sort_values(by='交易日期', ascending=False)
            self.logger.info(f"日線數據清理完成，共 {len(self.daily_df)} 筆記錄")
            return self.daily_df
            
        except Exception as e:
            self.logger.error(f"清理日線數據失敗: {str(e)}")
            return None
    
    def clean_monthly_data(self) -> Optional[pd.DataFrame]:
        """清理月線數據"""
        if self.monthly_df is None:
            return None
            
        try:
            # 清理列名
            self.monthly_df.columns = ['_'.join(col).strip() for col in self.monthly_df.columns]
            
            month_col = [col for col in self.monthly_df.columns if '月別' in col]
            if month_col:
                self.monthly_df = self.monthly_df[
                    ~self.monthly_df[month_col[0]].isin(['月別'])
                ].reset_index(drop=True)
            
            self.monthly_df.columns = self.monthly_df.columns.str.strip()
            
            # 標準化列名
            cols = [
                '月別', '當月股價_開盤', '當月股價_收盤', '當月股價_最高', '當月股價_最低', 
                '當月股價_漲跌(元)', '當月股價_漲跌(%)', '營業收入_單月_營收(億)', 
                '營業收入_單月_月增(%)', '營業收入_單月_年增(%)', '營業收入_累計_營收(億)', 
                '營業收入_累計_年增(%)', '合併營業收入_單月_營收(億)', '合併營業收入_單月_月增(%)', 
                '合併營業收入_單月_年增(%)', '合併營業收入_累計_營收(億)', '合併營業收入_累計_年增(%)'
            ]
            
            if len(self.monthly_df.columns) == len(cols):
                self.monthly_df.columns = cols
            
            # 轉換數據類型
            for col in self.monthly_df.columns:
                if col != '月別':
                    self.monthly_df[col] = pd.to_numeric(self.monthly_df[col], errors='coerce')
            
            self.monthly_df = self.monthly_df.drop_duplicates(keep=False)
            
            if '月別' in self.monthly_df.columns:
                self.monthly_df['月別'] = pd.to_datetime(self.monthly_df['月別'], format='%Y/%m')
            
            self.logger.info(f"月線數據清理完成，共 {len(self.monthly_df)} 筆記錄")
            return self.monthly_df
            
        except Exception as e:
            self.logger.error(f"清理月線數據失敗: {str(e)}")
            return None
    
    def is_stock_bullish(self) -> bool:
        """
        判斷股票是否符合買入條件
        
        Returns:
            True if 符合買入條件
        """
        if self.daily_df is None or self.daily_df.empty:
            return False
            
        try:
            latest_data = self.daily_df.iloc[0]
            
            # 檢查所需欄位是否存在
            required_cols = ['MA5', 'MA20', 'dif', 'signal', 'macd', 'osc', '收盤']
            if not all(col in latest_data.index for col in required_cols):
                self.logger.warning("缺少必要的技術指標欄位")
                return False
            
            # 篩選條件
            condition1 = latest_data['MA5'] > latest_data['MA20']
            condition2 = latest_data['dif'] > latest_data['signal']
            condition3 = latest_data['macd'] > 0
            condition4 = latest_data['osc'] > 0
            condition5 = latest_data['收盤'] > latest_data['MA20']
            
            result = all([condition1, condition2, condition3, condition4, condition5])
            self.logger.info(f"股票 {self.stock_id} 買入條件判斷: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"判斷買入條件失敗: {str(e)}")
            return False
    
    def plot_closing_price(self):
        """繪製收盤價圖表"""
        if self.daily_df is None or '收盤' not in self.daily_df.columns:
            self.logger.warning("無法繪製收盤價圖表：缺少數據")
            return
            
        try:
            plt.figure(figsize=(10, 5))
            plt.rcParams['font.sans-serif'] = ['苹方', 'Arial Unicode Ms']
            plt.plot(self.daily_df['交易日期'], self.daily_df['收盤'], 
                    color='#1f77b4', label='收盤價')
            plt.title(f'股票號碼: {self.stock_id} {self.stock_name} - 收盤價', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('交易日期')
            plt.ylabel('收盤價')
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            self.logger.error(f"繪製收盤價圖表失敗: {str(e)}")
    
    def plot_foreign_investment(self):
        """繪製外資持股圖表"""
        if self.daily_df is None or '外資持股(%)' not in self.daily_df.columns:
            self.logger.warning("無法繪製外資持股圖表：缺少數據")
            return
            
        try:
            plt.figure(figsize=(10, 5))
            plt.rcParams['font.sans-serif'] = ['苹方', 'Arial Unicode Ms']
            plt.plot(self.daily_df['交易日期'], self.daily_df['外資持股(%)'], 
                    color='#9467bd', label='外資持股 (%)')
            plt.title(f'股票號碼: {self.stock_id} {self.stock_name} - 外資持股 (%)', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('交易日期')
            plt.ylabel('外資持股 (%)')
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            self.logger.error(f"繪製外資持股圖表失敗: {str(e)}")
    
    def plot_stock_price(self):
        """繪製月線股價圖表"""
        if self.monthly_df is None:
            self.logger.warning("無法繪製月線股價圖表：缺少數據")
            return
            
        try:
            plt.figure(figsize=(12, 6))
            plt.rcParams['font.sans-serif'] = ['苹方', 'Arial Unicode Ms']
            
            price_cols = ['當月股價_開盤', '當月股價_收盤', '當月股價_最高', '當月股價_最低']
            labels = ['開盤價', '收盤價', '最高價', '最低價']
            
            for col, label in zip(price_cols, labels):
                if col in self.monthly_df.columns:
                    plt.plot(self.monthly_df['月別'], self.monthly_df[col], 
                           label=label, linewidth=2, markersize=4)
            
            plt.title(f'股票號碼: {self.stock_id} {self.stock_name} - 當月股價', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('月別', fontsize=14)
            plt.ylabel('股價', fontsize=14)
            plt.xticks(rotation=45)
            plt.legend(loc='upper left')
            plt.grid(linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            self.logger.error(f"繪製月線股價圖表失敗: {str(e)}")
    
    def plot_revenue_growth(self):
        """繪製營收成長圖表"""
        if self.monthly_df is None:
            self.logger.warning("無法繪製營收成長圖表：缺少數據")
            return
            
        try:
            plt.figure(figsize=(12, 6))
            plt.rcParams['font.sans-serif'] = ['苹方', 'Arial Unicode Ms']
            
            # 篩選最近一年數據
            last_year = self.monthly_df[
                self.monthly_df['月別'] >= (self.monthly_df['月別'].max() - pd.DateOffset(years=1))
            ]
            
            ax1 = plt.subplot(1, 1, 1)
            
            # 營收條形圖
            if '營業收入_單月_營收(億)' in last_year.columns:
                ax1.bar(last_year['月別'].dt.strftime('%Y-%m'), 
                       last_year['營業收入_單月_營收(億)'], 
                       color='cornflowerblue', label='營業收入', alpha=0.6)
            
            ax1.set_xlabel('月份', fontsize=14)
            ax1.set_ylabel('營業收入 (億元)', fontsize=14)
            
            # 成長率線圖
            ax2 = ax1.twinx()
            if '營業收入_單月_月增(%)' in last_year.columns:
                ax2.plot(last_year['月別'].dt.strftime('%Y-%m'), 
                        last_year['營業收入_單月_月增(%)'], 
                        color='orange', marker='o', label='成長率', linewidth=2)
            
            ax2.set_ylabel('成長率 (%)', fontsize=14)
            
            plt.title(f'股票號碼: {self.stock_id} {self.stock_name} - 營業收入與成長率 (最近一年)', fontsize=16)
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            ax1.grid(linestyle='--', alpha=0.7)
            plt.xticks(rotation=45)
            ax1.invert_xaxis()
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            self.logger.error(f"繪製營收成長圖表失敗: {str(e)}")
    
    def chatgpt_analysis(self) -> str:
        """
        使用ChatGPT分析股票數據
        
        Returns:
            分析結果文字
        """
        if self.daily_df is None:
            return "無法分析：缺少股票數據"
            
        try:
            OpenAI.api_key = self.config.openai.api_key
            OpenAI.base_url = self.config.openai.base_url
            OpenAI.default_headers = {"x-foo": "true"}
            
            response = OpenAI.chat.completions.create(
                model=self.config.openai.model,
                messages=[
                    {
                        'role': 'system', 
                        'content': '使用繁體中文回答：你是個一位專業股票分析師，請幫我解讀以下技術面訊息和月盈利狀況，並幫我針對長期(約半年)及短期(約一個月)提供交易策略'
                    },
                    {
                        'role': 'user', 
                        'content': f'{self.daily_df.to_string()}'
                    }
                ],
                temperature=1,
                max_tokens=4096,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            content = response.choices[0].message.content
            self.logger.info(f"股票 {self.stock_id} ChatGPT 分析完成")
            return str(content)
            
        except Exception as e:
            self.logger.error(f"股票 {self.stock_id} ChatGPT 分析失敗: {str(e)}")
            return "分析服務暫時無法使用"