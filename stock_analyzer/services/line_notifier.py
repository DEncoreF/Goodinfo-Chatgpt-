"""
LINE Bot 通知服務模組
"""
import ssl
import certifi
from typing import Optional, List
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, TextMessage
from linebot.v3 import WebhookHandler
from linebot.v3.messaging.models import PushMessageRequest

from ..utils.config import Config
from ..utils.logger import setup_logger


class LineNotifier:
    """LINE Bot 通知服務類"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化 LINE 通知服務
        
        Args:
            config: 配置對象
        """
        self.config = config or Config()
        self.logger = setup_logger(self.__class__.__name__)
        
        # 設置 SSL 上下文
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # 配置 LINE Bot
        configuration = Configuration(access_token=self.config.line.channel_access_token)
        self.handler = WebhookHandler(self.config.line.channel_secret)
        
        api_client = ApiClient(configuration)
        api_client.rest_client.pool_manager.connection_pool_kw['ssl_context'] = ssl_context
        self.messaging_api = MessagingApi(api_client)
        
        self.logger.info("LINE Bot 初始化完成")
    
    def send_message(self, message: str, user_id: Optional[str] = None) -> bool:
        """
        發送訊息給指定用戶
        
        Args:
            message: 要發送的訊息
            user_id: 目標用戶ID，若為None則使用默認用戶
            
        Returns:
            發送成功返回True，失敗返回False
        """
        try:
            target_user = user_id or self.config.line.user_id
            
            if not target_user:
                self.logger.error("未設置目標用戶ID")
                return False
            
            push_message_request = PushMessageRequest(
                to=target_user,
                messages=[TextMessage(text=message)]
            )
            
            self.messaging_api.push_message(push_message_request)
            self.logger.info(f"成功發送訊息給用戶 {target_user}")
            return True
            
        except Exception as e:
            self.logger.error(f"發送LINE訊息失敗: {str(e)}")
            return False
    
    def send_stock_summary(self, selected_stocks, stock_date: str) -> bool:
        """
        發送股票摘要訊息
        
        Args:
            selected_stocks: 選中的股票DataFrame
            stock_date: 股票日期
            
        Returns:
            發送成功返回True，失敗返回False
        """
        try:
            if selected_stocks.empty:
                message = "⚠️ 今日沒有符合條件的股票"
                return self.send_message(message)
            
            message = f"📈 {stock_date} 符合條件的股票:\n\n"
            
            for index, row in selected_stocks.iterrows():
                message += (
                    f"🔢 代號: {row['代號']}\n"
                    f"📊 名稱: {row['名稱']}\n" 
                    f"💰 成交: {row['成交']}\n"
                    f"📈 漲跌幅: {row['漲跌幅']}%\n"
                    f"💼 成交量: {row['成交張數']} 張\n"
                    f"🏛️ 法人買超: {row['合計買賣超張數']} 張\n\n"
                )
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"發送股票摘要失敗: {str(e)}")
            return False
    
    def send_stock_analysis(self, stock_id: str, analysis: str) -> bool:
        """
        發送股票分析結果
        
        Args:
            stock_id: 股票代號
            analysis: 分析結果文字
            
        Returns:
            發送成功返回True，失敗返回False
        """
        try:
            message = f"📊 股票 {stock_id} 詳細分析\n\n{analysis}"
            
            # LINE 訊息長度限制處理
            if len(message) > 2000:
                # 分割長訊息
                messages = [message[i:i+2000] for i in range(0, len(message), 2000)]
                for msg in messages:
                    if not self.send_message(msg):
                        return False
                return True
            else:
                return self.send_message(message)
                
        except Exception as e:
            self.logger.error(f"發送股票分析失敗: {str(e)}")
            return False