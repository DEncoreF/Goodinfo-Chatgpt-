"""
日誌設置模組
"""
import logging
import os
from datetime import datetime


def setup_logger(name: str = 'stock_analyzer', level: int = logging.INFO) -> logging.Logger:
    """
    設置日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        level: 日誌級別
        
    Returns:
        配置好的日誌記錄器
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    
    # 創建日誌目錄
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 文件處理器
    file_handler = logging.FileHandler(
        f"{log_dir}/{name}_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger