# 📈 台灣股票分析系統 (Stock Analyzer)

一個完整的台灣股市技術分析和自動選股系統，支援LINE Bot通知功能。

## ✨ 主要功能

- 🔍 **自動選股**: 根據技術指標和法人動向篩選潛力股票
- 📊 **技術分析**: MACD、移動平均線、成交量等技術指標分析
- 📱 **LINE通知**: 自動發送分析結果到LINE群組或個人
- 🎯 **AI分析**: 整合OpenAI GPT進行專業股票分析
- 📈 **視覺化圖表**: 自動生成股價、技術指標、營收圖表
- 🏛️ **法人追蹤**: 監控外資、投信、自營商買賣動向

## 🚀 快速開始

### 環境需求

- Python 3.8+
- pandas, requests, beautifulsoup4
- matplotlib, seaborn
- line-bot-sdk
- openai

### 安裝

1. **Clone 專案**
```bash
git clone https://github.com/yourusername/stock-analyzer.git
cd stock-analyzer
```

2. **安裝依賴**
```bash
pip install -r requirements.txt
```

3. **設置環境變數**
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯環境變數
export LINE_USER_ID="your_line_user_id"
export LINE_CHANNEL_SECRET="your_channel_secret"  
export LINE_CHANNEL_ACCESS_TOKEN="your_access_token"
export OPENAI_API_KEY="your_openai_api_key"
```

### 使用方式

#### 1. 每日自動分析
```bash
python main.py
```

#### 2. 分析特定股票
```bash
python main.py --stock-id 2330
```

#### 3. 不發送LINE通知
```bash
python main.py --no-notification
```

#### 4. 程式化使用
```python
from stock_analyzer import StockAnalyzer

# 初始化分析器
analyzer = StockAnalyzer()

# 執行每日分析
results = analyzer.run_daily_analysis()

# 分析特定股票  
is_bullish, analysis = analyzer.analyze_individual_stock("2330")
```

## 📁 專案結構

```
stock-analyzer/
├── stock_analyzer/           # 主要套件
│   ├── __init__.py
│   ├── core/                 # 核心模組
│   │   ├── stock_data.py     # 股票數據獲取
│   │   └── stock_visualizer.py # 數據視覺化
│   ├── services/             # 服務模組
│   │   ├── line_notifier.py  # LINE通知服務
│   │   └── stock_analyzer.py # 主分析服務
│   └── utils/                # 工具模組
│       ├── config.py         # 配置管理
│       └── logger.py         # 日誌設置
├── main.py                   # 主程序入口
├── requirements.txt          # 依賴列表
├── setup.py                  # 安裝設置
├── .env.example             # 環境變數範本
└── README.md                # 專案說明
```

## ⚙️ 配置說明

### 環境變數

| 變數名 | 說明 | 必需 |
|--------|------|------|
| `LINE_USER_ID` | LINE用戶ID | 是 |
| `LINE_CHANNEL_SECRET` | LINE Bot頻道密鑰 | 是 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot存取權杖 | 是 |
| `OPENAI_API_KEY` | OpenAI API金鑰 | 是 |
| `OPENAI_BASE_URL` | OpenAI API基礎URL | 否 |
| `OPENAI_MODEL` | 使用的模型名稱 | 否 |

### 選股條件

預設的選股條件包括:
- 法人買超張數 > 0
- 外資/投信/自營商連續買入
- 當日股價上漲
- 成交量 >= 5000張
- 5日均線 > 20日均線
- 20日均線 > 60日均線

## 📊 分析指標

### 技術指標
- **移動平均線**: 5日、20日、60日MA
- **MACD指標**: DIF、MACD、OSC
- **成交量分析**: 日成交量變化
- **外資持股**: 外資持股比例變化

### 基本面指標  
- **營收分析**: 月營收成長率
- **法人動向**: 三大法人買賣超
- **連續買賣**: 法人連續買賣天數

## 🔧 開發指南

### 安裝開發環境
```bash
pip install -e ".[dev]"
```

### 運行測試
```bash
pytest
```

### 代碼格式化
```bash
black stock_analyzer/
isort stock_analyzer/
```

### 類型檢查
```bash
flake8 stock_analyzer/
```

## 📝 使用範例

### 自定義選股條件
```python
custom_conditions = {
    '合計買賣超張數': 1000,      # 提高法人買超門檻
    '成交張數': 10000,            # 提高成交量門檻
    '漲跌幅': 2.0                 # 只看漲幅超過2%的股票
}

selected_stocks, stock_ids = analyzer.screen_stocks(custom_conditions)
```

### 批量分析股票
```python
stock_list = ["2330", "2454", "3711"]
results = {}

for stock_id in stock_list:
    is_bullish, analysis = analyzer.analyze_individual_stock(stock_id)
    results[stock_id] = {
        'recommend': is_bullish,
        'analysis': analysis
    }
```

## ⚠️ 注意事項

1. **資料來源**: 本系統從公開網站爬取資料，請遵守網站使用條款
2. **投資風險**: 本系統僅供參考，投資決策請自行承擔風險
3. **API限制**: OpenAI API和LINE Bot有使用限制，請注意配額
4. **資料延遲**: 股票資料可能有延遲，請以官方資料為準

## 🙏 致謝
- 感謝 [goodinfo.tw](https://goodinfo.tw) 提供股票資料
- 感謝開源社群提供的優秀套件
- 感謝所有貢獻者的支持
