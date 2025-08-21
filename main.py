"""
股票分析系統主程序
"""
import argparse
import sys
from stock_analyzer import StockAnalyzer, Config
from stock_analyzer.utils.logger import setup_logger


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='股票分析系統')
    parser.add_argument(
        '--stock-id', 
        type=str, 
        help='分析特定股票代號'
    )
    parser.add_argument(
        '--no-notification', 
        action='store_true', 
        help='不發送LINE通知'
    )
    parser.add_argument(
        '--config', 
        type=str, 
        help='配置文件路径'
    )
    parser.add_argument(
        '--log-level', 
        type=str, 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        default='INFO',
        help='日誌級別'
    )
    
    args = parser.parse_args()
    
    # 設置日誌
    import logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logger('main', log_level)
    
    try:
        # 載入配置
        config = Config(args.config)
        
        # 驗證配置
        if not config.validate():
            logger.error("配置驗證失敗，請檢查環境變數或配置文件")
            return 1
        
        # 初始化分析器
        analyzer = StockAnalyzer(config)
        
        if args.stock_id:
            # 分析特定股票
            logger.info(f"開始分析股票 {args.stock_id}")
            is_bullish, analysis = analyzer.analyze_individual_stock(args.stock_id)
            
            print(f"\n=== 股票 {args.stock_id} 分析結果 ===")
            print(f"買入建議: {'推薦買入' if is_bullish else '不建議買入'}")
            print(f"分析結果:\n{analysis}")
            
            if is_bullish and not args.no_notification:
                analyzer.line_notifier.send_stock_analysis(args.stock_id, analysis)
                
        else:
            # 執行每日分析
            logger.info("開始執行每日股票分析")
            results = analyzer.run_daily_analysis(
                send_notification=not args.no_notification
            )
            
            # 顯示摘要
            summary = analyzer.get_analysis_summary(results)
            print(summary)
        
        logger.info("程序執行完成")
        return 0
        
    except KeyboardInterrupt:
        logger.info("程序被用戶中斷")
        return 0
    except Exception as e:
        logger.error(f"程序執行失敗: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())