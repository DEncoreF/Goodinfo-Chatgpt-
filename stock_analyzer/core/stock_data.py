"""
股票數據獲取和處理模組
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
import openai as OpenAI
from IPython.display import display, Markdown
from io import StringIO
from markdown import markdown
import re
from typing import Tuple, List, Optional

from ..utils.config import Config
from ..utils.logger import setup_logger


class StockData:
    """股票數據獲取和處理類"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化股票數據處理器
        
        Args:
            config: 配置對象，若為None則使用默認配置
        """
        self.config = config or Config()
        self.logger = setup_logger(self.__class__.__name__)
        self.headers = self.config.stock.headers
        
        # 數據框存儲
        self.co_df = None
        self.co_ma_df = None
        self.co_revenue_df = None
        self.co_macd_df = None
        self.co_cons_df = None
        self.matched_df = None
        self.revenue_columns = None
    
    def _fetch_corporation_data(self, sheet_type: str) -> pd.DataFrame:
        """
        獲取法人數據
        
        Args:
            sheet_type: 數據表類型
            
        Returns:
            DataFrame: 處理後的數據
        """
        try:
            url = (f'https://goodinfo.tw/tw2/StockList.asp?SEARCH_WORD=&MARKET_CAT='
                  f'%E6%99%BA%E6%85%A7%E9%81%B8%E8%82%A1&INDUSTRY_CAT='
                  f'%E4%B8%89%E5%A4%A7%E6%B3%95%E4%BA%BA%E9%80%A3%E8%B2%B7+'
                  f'%E2%80%93+%E6%97%A5%40%40%E4%B8%89%E5%A4%A7%E6%B3%95%E4%BA%BA'
                  f'%E9%80%A3%E7%BA%8C%E8%B2%B7%E8%B6%85%40%40%E4%B8%89%E5%A4%A7'
                  f'%E6%B3%95%E4%BA%BA%E9%80%A3%E7%BA%8C%E8%B2%B7%E8%B6%85+'
                  f'%E2%80%93+%E6%97%A5&STOCK_CODE=&RANK=0&STEP=DATA&SHEET={sheet_type}')
            
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            data = soup.select_one('#tblStockList')
            
            if data is None:
                self.logger.warning(f"無法獲取數據，sheet_type: {sheet_type}")
                return pd.DataFrame()
            
            html_string = data.prettify()
            df = pd.read_html(StringIO(html_string))[0]
            df.columns = df.columns.str.strip().str.replace('  ', '')
            df = df.drop_duplicates(keep=False)
            
            self.logger.info(f"成功獲取 {sheet_type} 數據，共 {len(df)} 筆記錄")
            return df
            
        except Exception as e:
            self.logger.error(f"獲取 {sheet_type} 數據失敗: {str(e)}")
            return pd.DataFrame()
    
    def get_co_data(self) -> pd.DataFrame:
        """獲取法人買賣數據"""
        self.co_df = self._fetch_corporation_data('%E6%B3%95%E4%BA%BA%E8%B2%B7%E8%B3%A3_%E4%B8%89%E5%A4%A7')
        return self.co_df
    
    def get_co_ma_data(self) -> pd.DataFrame:
        """獲取移動平均數據"""
        self.co_ma_df = self._fetch_corporation_data('%E7%A7%BB%E5%8B%95%E5%9D%87%E7%B7%9A')
        return self.co_ma_df
    
    def get_co_revenue_data(self) -> pd.DataFrame:
        """獲取營收數據"""
        self.co_revenue_df = self._fetch_corporation_data('%E7%87%9F%E6%94%B6%E7%8B%80%E6%B3%81_%E8%BF%91N%E5%80%8B%E6%9C%88%E4%B8%80%E8%A6%BD')
        return self.co_revenue_df
    
    def get_co_macd_data(self) -> pd.DataFrame:
        """獲取MACD數據"""
        self.co_macd_df = self._fetch_corporation_data('MACD')
        return self.co_macd_df
    
    def get_co_cons_data(self) -> pd.DataFrame:
        """獲取法人連續買賣數據"""
        try:
            url = ('https://goodinfo.tw/tw2/StockList.asp?SEARCH_WORD=&SHEET='
                  '%E6%B3%95%E4%BA%BA%E8%B2%B7%E8%B3%A3%5F%E4%B8%89%E5%A4%A7&'
                  'MARKET_CAT=%E6%99%BA%E6%85%A7%E9%81%B8%E8%82%A1&INDUSTRY_CAT='
                  '%E4%B8%89%E5%A4%A7%E6%B3%95%E4%BA%BA%E9%80%A3%E8%B2%B7+'
                  '%E2%80%93+%E6%97%A5%40%40%E4%B8%89%E5%A4%A7%E6%B3%95%E4%BA%BA'
                  '%E9%80%A3%E7%BA%8C%E8%B2%B7%E8%B6%85%40%40%E4%B8%89%E5%A4%A7'
                  '%E6%B3%95%E4%BA%BA%E9%80%A3%E7%BA%8C%E8%B2%B7%E8%B6%85+'
                  '%E2%80%93+%E6%97%A5&STOCK_CODE=&RANK=0&STEP=DATA&SHEET2='
                  '%E6%B3%95%E4%BA%BA%E9%80%A3%E8%B2%B7%E9%80%A3%E8%B3%A3'
                  '%E7%B5%B1%E8%A8%88(%E6%97%A5)')
            
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            data = soup.select_one('#tblStockList')
            
            if data is None:
                self.logger.warning("無法獲取法人連續買賣數據")
                return pd.DataFrame()
            
            html_string = data.prettify()
            self.co_cons_df = pd.read_html(StringIO(html_string))[0]
            self.co_cons_df.columns = self.co_cons_df.columns.str.strip().str.replace('  ', '')
            self.co_cons_df = self.co_cons_df.drop_duplicates(keep=False)
            
            self.logger.info(f"成功獲取法人連續買賣數據，共 {len(self.co_cons_df)} 筆記錄")
            return self.co_cons_df
            
        except Exception as e:
            self.logger.error(f"獲取法人連續買賣數據失敗: {str(e)}")
            return pd.DataFrame()
    
    def _modify_all_titles(self, columns: List[str]) -> List[str]:
        """
        修改營收欄位標題格式
        
        Args:
            columns: 原始欄位列表
            
        Returns:
            修改後的欄位列表
        """
        modified_columns = []
        for col in columns:
            if col.endswith("營收(億)") and col[:2].isdigit() and col[2] == 'M':
                year_prefix = col[:2]
                month = col[3:5]
                year = f"20{year_prefix}"
                modified_columns.append(f"{year}年{int(month)}月營收 (億)")
            else:
                modified_columns.append(col)
        return modified_columns
    
    def match_data(self) -> Tuple[pd.DataFrame, List[str]]:
        """
        合併所有數據並進行清理
        
        Returns:
            合併後的DataFrame和營收欄位列表
        """
        try:
            # 合併數據
            self.matched_df = pd.merge(
                self.co_df, self.co_ma_df, 
                on=['代號', '名稱', '成交', '漲跌價', '漲跌幅', '成交張數'], 
                how='left'
            )
            self.matched_df = pd.merge(
                self.matched_df, self.co_cons_df, 
                on=['法人買賣日期', '代號', '名稱', '成交', '漲跌價', '漲跌幅'], 
                how='left'
            )
            self.matched_df = pd.merge(
                self.matched_df, self.co_revenue_df, 
                on=['代號', '名稱', '成交', '漲跌價', '漲跌幅'], 
                how='left'
            )
            self.matched_df = pd.merge(
                self.matched_df, self.co_macd_df, 
                on=['代號', '名稱', '成交', '漲跌價', '漲跌幅'], 
                how='left'
            )
            
            # 清理數據
            cols_to_process = [
                '合計買賣超張數', '成交張數', '漲跌幅', '三大法人連續買賣日數',
                '外資連續買賣日數', '自營商連續買賣日數', '投信連續買賣日數',
                '5日均線', '10日均線', '15日均線', '20日均線', '50日均線', 
                '60日均線', '100日均線', '120日均線', '200日均線', '240日均線', 
                'DIF(日)', 'MACD(日)', 'OSC(日)', 'DIF(週)', 'MACD(週)', 
                'OSC(週)', 'DIF(月)', 'MACD(月)', 'OSC(月)'
            ]
            
            for col in cols_to_process:
                if col in self.matched_df.columns and not self.matched_df[col].empty:
                    # 清理特殊符號
                    self.matched_df[col] = (
                        self.matched_df[col]
                        .astype(str)
                        .str.replace('↗', '', regex=False)
                        .str.replace('↘', '', regex=False)
                        .str.replace('→', '', regex=False)
                    )
                    # 轉換為數值
                    self.matched_df[col] = pd.to_numeric(self.matched_df[col], errors='coerce')
            
            # 修改欄位標題
            self.matched_df.columns = self._modify_all_titles(self.matched_df.columns.tolist())
            
            # 處理營收欄位
            self.revenue_columns = self.config.get_revenue_columns()
            for col in self.revenue_columns:
                if col in self.matched_df.columns:
                    self.matched_df[col] = pd.to_numeric(self.matched_df[col], errors='coerce')
            
            # 移除不需要的欄位
            cols_to_drop = ['100日均線', '15日均線', '50日均線', '200日均線', '法人買賣超註記']
            cols_to_drop = [col for col in cols_to_drop if col in self.matched_df.columns]
            if cols_to_drop:
                self.matched_df = self.matched_df.drop(columns=cols_to_drop)
            
            self.logger.info(f"數據合併完成，共 {len(self.matched_df)} 筆記錄")
            return self.matched_df, self.revenue_columns
            
        except Exception as e:
            self.logger.error(f"數據合併失敗: {str(e)}")
            return pd.DataFrame(), []
    
    def chatgpt_analysis(self) -> str:
        """
        使用ChatGPT分析股票數據
        
        Returns:
            分析結果文字
        """
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
                        'content': f'{self.matched_df.to_string()}'
                    }
                ],
                temperature=1,
                max_tokens=4096,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            content = response.choices[0].message.content
            self.logger.info("ChatGPT 分析完成")
            return str(content)
            
        except Exception as e:
            self.logger.error(f"ChatGPT 分析失敗: {str(e)}")
            return "分析服務暫時無法使用"