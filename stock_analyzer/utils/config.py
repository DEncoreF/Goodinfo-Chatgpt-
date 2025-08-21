"""
配置管理模組
"""
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class LineConfig:
    """LINE Bot 配置"""
    user_id: str
    channel_secret: str  
    channel_access_token: str


@dataclass
class OpenAIConfig:
    """OpenAI API 配置"""
    api_key: str
    base_url: str
    model: str = "gpt-4o-mini"


@dataclass
class StockConfig:
    """股票分析配置"""
    headers: Dict[str, str]
    default_days: int = 365


class Config:
    """應用程式配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """載入配置"""
        # LINE Bot 配置
        self.line = LineConfig(
            user_id=os.getenv('LINE_USER_ID', 'Uf8b404295d8f02bc60b06dca2ddfa954'),
            channel_secret=os.getenv('LINE_CHANNEL_SECRET', '7f4e86c32d8871f2fe5e19ea7b954c2f'),
            channel_access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 
                                         'g7zAdJ6MQDd69p7ir+2zv9cTsxGqFVyfVswr+rNIEU5jJl8ihu97M8DlRwaLvUDpRjq5DGIOc/z8Sn/bhapwSLzwoa9IcP4Lax06zZhnOytDsGNQbsEmxj0+JFu7xT8CExBKaqDbUB+JagBvvBvYqAdB04t89/1O/w1cDnyilFU=')
        )
        
        # OpenAI 配置
        self.openai = OpenAIConfig(
            api_key=os.getenv('OPENAI_API_KEY', 'sk-tB0P16DBqnPLex85A9EdAeB107D34439AcA3B129DaD0135e'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://free.v36.cm/v1/'),
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        )
        
        # 股票數據配置
        self.stock = StockConfig(
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Cookie': 'IS_TOUCH_DEVICE=F; _ga=GA1.1.181317566.1718532079; CLIENT%5FID=20240616180126875%5F36%2E229%2E52%2E63; TW_STOCK_BROWSE_LIST=6163; SCREEN_SIZE=WIDTH=2048&HEIGHT=1280; _ga_0LP5MLQS7E=GS1.1.1718532079.1.1.1718533794.55.0.0; FCNEC=%5B%5B%22AKsRol9SI_2fTGHpemG9YsrULojLbIxof0jMpZlU9D2QhtEJ1tcsb7DWXrxdOxPSr3M34xBLTu5R1-X5Y5YFzqjc7X5yv7XuyUZOC5efVbCaLev18nmzd81fN_QEOIPMrcGqwcyKtTt2dh-E6WHKVn-mBCwQQatztA%3D%3D%22%5D%5D'
            },
            default_days=365
        )
    
    def validate(self) -> bool:
        """驗證配置是否完整"""
        required_configs = [
            self.line.user_id,
            self.line.channel_secret, 
            self.line.channel_access_token,
            self.openai.api_key
        ]
        
        return all(config for config in required_configs)
    
    def get_revenue_columns(self) -> list:
        """取得營收欄位列表"""
        return [
            '2024年6月營收 (億)',
            '2024年7月營收 (億)', 
            '2024年8月營收 (億)', 
            '2024年9月營收 (億)', 
            '2024年10月營收 (億)',
            '2024年11月營收 (億)', 
            '2024年12月營收 (億)', 
            '2025年1月營收 (億)', 
            '2025年2月營收 (億)',
            '2025年3月營收 (億)', 
            '2025年4月營收 (億)', 
            '2025年5月營收 (億)'
        ]