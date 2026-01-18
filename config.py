import os

# CONFIGURATION
# -----------------------------------------------------------------------------
# 配置文件 (Configuration)
# 本文件定义了 News_Engine 的所有抓取目标和分类。
# 目标被分为两大组：
# 1. ENGLISH_SOURCES: 走 YFinance 和 OpenBB 渠道 (美股、越南、大宗商品、全球宏观英文)。
# 2. CHINESE_SOURCES: 走 Akshare 渠道 (A股、港股、国内宏观中文)。
#
# 每项包含:
# - value: 代码 (Ticker) 或 关键词 (Keyword)
# - name: 显示名称
# - type: 类型 (stock_us, stock_hk, stock_vn, stock_zh_a, etf_zh, future_foreign, keyword)
#   - stock_... / future_... : 会尝试通过 API 获取新闻 (YF, OpenBB, Akshare)
#   - keyword : 会通过 Google RSS (mass coverage) 和 Guardian (quality) 获取新闻
# -----------------------------------------------------------------------------

CONFIG = {
    "DAYS_BACK": 7,  # 回溯天数
    "OUTPUT_FILE": "news_result.json",
    # [NEW] Feature Flag
    "ENABLE_GOOGLE_RSS": True, # [OPTIMIZED] Re-enabled with Concurrent scraping + Date Filtering
    "SERP_API_KEY": os.getenv("Serp_API_KEY"),
    
    # ---------------------------------------------------
    # Data Cleaning / Deduplication Configuration
    # ---------------------------------------------------
    "CLEANING": {
        "ENABLED": True,
        
        "ENGLISH": {
            # Options: "all-MiniLM-L6-v2" (Fast/Eng), "paraphrase-multilingual-MiniLM-L12-v2" (Multi)
            "MODEL_NAME": "paraphrase-multilingual-MiniLM-L12-v2", 
            "SIMILARITY_THRESHOLD": 0.85, 
        },
        
        "CHINESE": {
            # Options: "shibing624/text2vec-base-chinese", "BAAI/bge-large-zh-v1.5", "paraphrase-multilingual-MiniLM-L12-v2"
            "MODEL_NAME": "paraphrase-multilingual-MiniLM-L12-v2", 
            "SIMILARITY_THRESHOLD": 0.85, 
        }
    },

    "GROUPS": {
        
        # =========================================================================
        # 1. ENGLISH SOURCES (英文源)
        # 渠道: YFinance, OpenBB
        # =========================================================================
        "ENGLISH_SOURCES": {
            
            # ---------------------------------------------------------------------
            # (1) US Market: Technology & AI (美股科技与AI)
            # ---------------------------------------------------------------------
            "US_MARKET_TECH": {
                # 描述: 纳指、标普、七巨头、芯片股及AI相关概念
                # Note: Items of type 'keyword' will be processed by GoogleRSS/Guardian
                "desc": "US Tech Giants, Chips, and AI related keywords",
                "items": [
                    # --- Tickers (代码) ---
                    {"value": "^NDX", "name": "Nasdaq 100", "type": "index_us"},
                    {"value": "^GSPC", "name": "S&P 500", "type": "index_us"},
                    {"value": "^SOX", "name": "PHLX Semiconductor", "type": "index_us"}, # 费半指数
                    
                    {"value": "NVDA", "name": "Nvidia", "type": "stock_us"},       # 英伟达
                    {"value": "AAPL", "name": "Apple", "type": "stock_us"},        # 苹果
                    {"value": "GOOGL", "name": "Google", "type": "stock_us"},      # 谷歌
                    {"value": "META", "name": "Meta", "type": "stock_us"},         # Meta
                    {"value": "TSLA", "name": "Tesla", "type": "stock_us"},        # 特斯拉
                    {"value": "MSFT", "name": "Microsoft", "type": "stock_us"},    # 微软
                    {"value": "AMZN", "name": "Amazon", "type": "stock_us"},       # 亚马逊
                    {"value": "AVGO", "name": "Broadcom", "type": "stock_us"},     # 博通
                    {"value": "TSM", "name": "TSMC", "type": "stock_us"},          # 台积电 (ADR)
                    {"value": "MU", "name": "Micron", "type": "stock_us"},         # 美光
                    {"value": "SMCI", "name": "Super Micro", "type": "stock_us"},  # 超微电脑

                    # --- User Provided List (Ticker & Keywords Mixed) ---
                    # 注意: 中文关键词设为 keyword，避免传入 YFinance 报错
                    {"value": "英伟达", "name": "英伟达(CN)", "type": "keyword"},
                    {"value": "苹果", "name": "苹果(CN)", "type": "keyword"},
                    {"value": "谷歌", "name": "谷歌(CN)", "type": "keyword"},
                    {"value": "Alphabet", "name": "Alphabet", "type": "keyword"},
                    {"value": "博通", "name": "博通(CN)", "type": "keyword"},
                    {"value": "台积电", "name": "台积电(CN)", "type": "keyword"},
                    {"value": "TSMC", "name": "TSMC", "type": "keyword"}, # Duplicate but keeping for fullness
                    {"value": "美光", "name": "美光(CN)", "type": "keyword"},
                    
                    # AI Concepts
                    {"value": "AGI", "name": "AGI", "type": "keyword"},
                    {"value": "通用人工智能", "name": "通用人工智能", "type": "keyword"},
                    {"value": "物理AI", "name": "物理AI", "type": "keyword"},
                    {"value": "Physical AI", "name": "Physical AI", "type": "keyword"},
                    {"value": "代理智能", "name": "代理智能", "type": "keyword"},
                    {"value": "Agentic AI", "name": "Agentic AI", "type": "keyword"},
                    {"value": "Blackwell", "name": "Blackwell Chip", "type": "keyword"},
                    {"value": "Rubin", "name": "Rubin Chip", "type": "keyword"},
                    {"value": "HBM4", "name": "HBM4 Memory", "type": "keyword"},
                    {"value": "CoWoS", "name": "CoWoS Packaging", "type": "keyword"},
                    {"value": "先进封装", "name": "先进封装", "type": "keyword"},
                    {"value": "TPU v7", "name": "TPU v7", "type": "keyword"},
                    {"value": "SMR", "name": "SMR (Nuclear)", "type": "keyword"},
                    {"value": "小型模块化反应堆", "name": "小型模块化反应堆", "type": "keyword"},
                    {"value": "核能", "name": "核能", "type": "keyword"},
                    {"value": "数据中心资本开支", "name": "数据中心资本开支", "type": "keyword"},
                    {"value": "AI Capex", "name": "AI Capex", "type": "keyword"},
                    {"value": "H200", "name": "H200", "type": "keyword"},
                    {"value": "H20", "name": "H20", "type": "keyword"},
                    {"value": "Revenue Sharing", "name": "Revenue Sharing", "type": "keyword"},
                    {"value": "收入分成模式", "name": "收入分成模式", "type": "keyword"},
                    {"value": "Foundry Capacity", "name": "Foundry Capacity", "type": "keyword"},
                    {"value": "晶圆代工产能", "name": "晶圆代工产能", "type": "keyword"},
                    {"value": "Gamma Flip", "name": "Gamma Flip", "type": "keyword"},
                    {"value": "伽马翻转点", "name": "伽马翻转点", "type": "keyword"},
                    {"value": "CTA Trend Followers", "name": "CTA Trend Followers", "type": "keyword"},
                    {"value": "趋势跟踪基金", "name": "趋势跟踪基金", "type": "keyword"},
                    {"value": "Trigger Levels", "name": "Trigger Levels", "type": "keyword"},
                    {"value": "系统性触发位", "name": "系统性触发位", "type": "keyword"},
                    {"value": "Buyback Blackout", "name": "Buyback Blackout", "type": "keyword"},
                    {"value": "回购禁默期", "name": "回购禁默期", "type": "keyword"},
                    {"value": "Inference Costs", "name": "Inference Costs", "type": "keyword"},
                    {"value": "推理成本", "name": "推理成本", "type": "keyword"},
                    {"value": "Sovereign AI", "name": "Sovereign AI", "type": "keyword"},
                    {"value": "主权AI", "name": "主权AI", "type": "keyword"},
                    {"value": "硅谷", "name": "硅谷", "type": "keyword"},
                    {"value": "Silicon Valley", "name": "Silicon Valley", "type": "keyword"},
                    {"value": "费城半导体", "name": "费城半导体", "type": "keyword"},
                    {"value": "半导体板块指数", "name": "半导体板块指数", "type": "keyword"},
                    {"value": "SMCI", "name": "超微电脑(Ticker/Key)", "type": "stock_us"}, # Also a ticker
                    {"value": "超微电脑", "name": "超微电脑(CN)", "type": "keyword"},
                    {"value": "OBBBA", "name": "OBBBA", "type": "keyword"},
                    {"value": "OBBBA法案", "name": "OBBBA法案", "type": "keyword"},
                    {"value": "大而美法案", "name": "大而美法案", "type": "keyword"},
                    {"value": "Busan Consensus", "name": "Busan Consensus", "type": "keyword"},
                    {"value": "釜山协议", "name": "釜山协议", "type": "keyword"},
                ]
            },

            # ---------------------------------------------------------------------
            # (2) Global Commodities (全球大宗商品)
            # ---------------------------------------------------------------------
            "COMMODITIES_EN": {
                # 描述: 黄金、白银、铜、原油及相关宏观指标
                "desc": "Gold, Precious Metals, and Energy (English Context)",
                "items": [
                    # --- Tickers ---
                    {"value": "GC=F", "name": "Gold (COMEX)", "type": "future_foreign"},   # 黄金
                    {"value": "SI=F", "name": "Silver (COMEX)", "type": "future_foreign"}, # 白银
                    {"value": "HG=F", "name": "Copper (COMEX)", "type": "future_foreign"}, # 铜
                    {"value": "CL=F", "name": "Crude Oil (WTI)", "type": "future_foreign"},# 原油
                    {"value": "URA", "name": "Uranium ETF", "type": "stock_us"},           # 铀矿ETF
                    
                    # --- Keywords (CN/EN Mixed from user list) ---
                    {"value": "黄金", "name": "黄金(CN)", "type": "keyword"},
                    {"value": "Gold", "name": "Gold", "type": "keyword"},
                    {"value": "TIPS Bond", "name": "TIPS Bond", "type": "keyword"},
                    {"value": "实际利率", "name": "实际利率", "type": "keyword"},
                    {"value": "美元指数", "name": "美元指数", "type": "keyword"},
                    {"value": "DXY", "name": "DXY", "type": "keyword"},
                    {"value": "SGE Premium", "name": "SGE Premium", "type": "keyword"},
                    {"value": "上海金溢价", "name": "上海金溢价", "type": "keyword"},
                    {"value": "伦敦金", "name": "伦敦金", "type": "keyword"},
                    {"value": "LBMA", "name": "LBMA", "type": "keyword"},
                    {"value": "纽约金", "name": "纽约金", "type": "keyword"},
                    {"value": "COMEX", "name": "COMEX", "type": "keyword"},
                    {"value": "央行购金", "name": "央行购金", "type": "keyword"},
                    {"value": "Central Bank Gold Reserves", "name": "Central Bank Buying", "type": "keyword"},
                    {"value": "去美元化", "name": "去美元化", "type": "keyword"},
                    {"value": "De-dollarization", "name": "De-dollarization", "type": "keyword"},
                    {"value": "金砖国家", "name": "金砖国家", "type": "keyword"},
                    {"value": "BRICS", "name": "BRICS", "type": "keyword"},
                    {"value": "mBridge", "name": "mBridge", "type": "keyword"},
                    {"value": "货币桥", "name": "货币桥", "type": "keyword"},
                    {"value": "地缘政治溢价", "name": "地缘政治溢价", "type": "keyword"},
                    {"value": "信用货币贬值", "name": "信用货币贬值", "type": "keyword"},
                    {"value": "财政主导", "name": "财政主导", "type": "keyword"},
                    {"value": "Fiscal Dominance", "name": "Fiscal Dominance", "type": "keyword"},
                    {"value": "金银比", "name": "金银比", "type": "keyword"},
                    {"value": "Gold Silver Ratio", "name": "Gold Silver Ratio", "type": "keyword"},
                    {"value": "金铜比", "name": "金铜比", "type": "keyword"},
                    {"value": "Gold Copper Ratio", "name": "Gold Copper Ratio", "type": "keyword"},
                    {"value": "银色奇点", "name": "银色奇点", "type": "keyword"},
                    {"value": "Silver Singularity", "name": "Silver Singularity", "type": "keyword"},
                    {"value": "光伏需求", "name": "光伏需求", "type": "keyword"},
                    {"value": "Photovoltaic Demand", "name": "Photovoltaic Demand", "type": "keyword"},
                    {"value": "TOPCon", "name": "TOPCon", "type": "keyword"},
                    {"value": "HJT", "name": "HJT", "type": "keyword"},
                    {"value": "AI导电散热", "name": "AI导电散热", "type": "keyword"},
                    {"value": "AI Heat Dissipation", "name": "AI Heat Dissipation", "type": "keyword"},
                    {"value": "上海金折价", "name": "上海金折价", "type": "keyword"},
                    {"value": "SGE Discount", "name": "SGE Discount", "type": "keyword"},
                    {"value": "增值税改革", "name": "增值税改革", "type": "keyword"},
                    {"value": "VAT Reform", "name": "VAT Reform", "type": "keyword"},
                    {"value": "印度进口关税", "name": "印度进口关税", "type": "keyword"},
                    {"value": "India Import Duty", "name": "India Import Duty", "type": "keyword"},
                    {"value": "保证金强平抛售", "name": "保证金强平抛售", "type": "keyword"},
                    {"value": "Margin Call Selling", "name": "Margin Call Selling", "type": "keyword"},
                    {"value": "GVZ", "name": "GVZ", "type": "keyword"},
                    {"value": "黄金波动率指数", "name": "黄金波动率指数", "type": "keyword"},
                    {"value": "跨资产相关性", "name": "跨资产相关性", "type": "keyword"},
                    {"value": "Cross-Asset Correlation", "name": "Cross-Asset Correlation", "type": "keyword"},
                    {"value": "中国央行购金", "name": "中国央行购金", "type": "keyword"},
                    {"value": "PBOC Gold Buying", "name": "PBOC Gold Buying", "type": "keyword"},
                    {"value": "波兰央行", "name": "波兰央行", "type": "keyword"},
                    {"value": "Poland Central Bank", "name": "Poland Central Bank", "type": "keyword"},
                    {"value": "主权基金", "name": "主权基金", "type": "keyword"},
                    {"value": "Sovereign Wealth Funds", "name": "Sovereign Wealth Funds", "type": "keyword"},
                    {"value": "10年期盈亏平衡通胀率", "name": "10年期盈亏平衡通胀率", "type": "keyword"},
                    {"value": "10-Year Breakeven Inflation Rate", "name": "10-Year Breakeven Inflation Rate", "type": "keyword"},
                    {"value": "成本推动型通胀", "name": "成本推动型通胀", "type": "keyword"},
                    {"value": "Cost-Push Inflation", "name": "Cost-Push Inflation", "type": "keyword"},
                    {"value": "伦敦库存倒挂", "name": "伦敦库存倒挂", "type": "keyword"},
                    {"value": "Inventory Inversion", "name": "Inventory Inversion", "type": "keyword"},
                    {"value": "USD/CNY", "name": "USD/CNY", "type": "keyword"},
                    {"value": "离岸人民币", "name": "离岸人民币", "type": "keyword"},
                    {"value": "汇率套保成本", "name": "汇率套保成本", "type": "keyword"},
                    {"value": "AISC", "name": "AISC", "type": "keyword"},
                    {"value": "黄金全维持成本", "name": "黄金全维持成本", "type": "keyword"},
                    {"value": "金矿产能限制", "name": "金矿产能限制", "type": "keyword"},
                    {"value": "COT Report", "name": "COT Report", "type": "keyword"},
                    {"value": "CFTC持仓报告", "name": "CFTC持仓报告", "type": "keyword"},
                    {"value": "非商业净多头", "name": "非商业净多头", "type": "keyword"},
                    {"value": "Managed Money Net Longs", "name": "Managed Money Net Longs", "type": "keyword"},
                    {"value": "持仓拥挤度", "name": "持仓拥挤度", "type": "keyword"},
                    {"value": "筹码分布", "name": "筹码分布", "type": "keyword"},
                    {"value": "Gold-to-Oil Ratio", "name": "Gold-to-Oil Ratio", "type": "keyword"},
                    {"value": "金油比", "name": "金油比", "type": "keyword"},
                    {"value": "Real Yields", "name": "Real Yields", "type": "keyword"},
                    {"value": "名义利率减通胀", "name": "名义利率减通胀", "type": "keyword"},
                    {"value": "Gold Swap", "name": "Gold Swap", "type": "keyword"},
                    {"value": "黄金掉期", "name": "黄金掉期", "type": "keyword"},
                ]
            },

            # ---------------------------------------------------------------------
            # (3) Vietnam Market (越南市场)
            # ---------------------------------------------------------------------
            "VIETNAM_EN": {
                # 描述: 越南 VN30 成分股与经济指标
                "desc": "Vietnam Stocks, ETFs and Economy (English/Mixed Context)",
                "items": [
                    # --- Tickers ---
                    {"value": "VNM", "name": "VanEck Vietnam ETF", "type": "stock_us"},
                    {"value": "VPB.VN", "name": "VPBank", "type": "stock_vn"},
                    {"value": "MBB.VN", "name": "MBBank", "type": "stock_vn"},
                    {"value": "HPG.VN", "name": "Hoa Phat Group", "type": "stock_vn"},
                    {"value": "MWG.VN", "name": "Mobile World", "type": "stock_vn"},
                    {"value": "FPT.VN", "name": "FPT Corp", "type": "stock_vn"},
                    {"value": "STB.VN", "name": "Sacombank", "type": "stock_vn"},
                    {"value": "HDB.VN", "name": "HDBank", "type": "stock_vn"},
                    {"value": "TCB.VN", "name": "Techcombank", "type": "stock_vn"},
                    {"value": "VIC.VN", "name": "Vingroup", "type": "stock_vn"},
                    {"value": "VHM.VN", "name": "Vinhomes", "type": "stock_vn"},
                    
                    # --- Keywords ---
                    {"value": "越南股市", "name": "越南股市", "type": "keyword"},
                    {"value": "VN-Index", "name": "VN-Index", "type": "keyword"},
                    {"value": "越南繁荣银行", "name": "越南繁荣银行(CN)", "type": "keyword"},
                    {"value": "VPB", "name": "VPB", "type": "keyword"},
                    {"value": "军队银行", "name": "军队银行", "type": "keyword"},
                    {"value": "MBB", "name": "MBB", "type": "keyword"},
                    {"value": "和发集团", "name": "和发集团(CN)", "type": "keyword"},
                    {"value": "HPG", "name": "HPG", "type": "keyword"},
                    {"value": "FPT", "name": "FPT", "type": "keyword"},
                    {"value": "移动世界", "name": "移动世界", "type": "keyword"},
                    {"value": "MWG", "name": "MWG", "type": "keyword"},
                    {"value": "Vingroup", "name": "Vingroup", "type": "keyword"},
                    {"value": "VIC", "name": "VIC", "type": "keyword"},
                    {"value": "Vinhomes", "name": "Vinhomes", "type": "keyword"},
                    {"value": "VHM", "name": "VHM", "type": "keyword"},
                    {"value": "USD VND", "name": "USD VND", "type": "keyword"},
                    {"value": "越南盾汇率", "name": "越南盾汇率", "type": "keyword"},
                    {"value": "越南制造业PMI", "name": "越南制造业PMI", "type": "keyword"},
                    {"value": "越南出口增速", "name": "越南出口增速", "type": "keyword"},
                    {"value": "FTSE升级", "name": "FTSE升级", "type": "keyword"},
                    {"value": "Emerging Market Upgrade", "name": "Emerging Market Upgrade", "type": "keyword"},
                    {"value": "黄金背离", "name": "黄金背离", "type": "keyword"},
                    {"value": "500kV输电线路", "name": "500kV输电线路", "type": "keyword"},
                    {"value": "KRX交易系统", "name": "KRX交易系统", "type": "keyword"},
                    {"value": "Novaland", "name": "Novaland", "type": "keyword"},
                    {"value": "VinFast", "name": "VinFast", "type": "keyword"},
                    {"value": "越南房企债", "name": "越南房企债", "type": "keyword"},
                    {"value": "Foreign Net Buy", "name": "Foreign Net Buy", "type": "keyword"},
                    {"value": "Foreign Net Sell", "name": "Foreign Net Sell", "type": "keyword"},
                    {"value": "外资净买入", "name": "外资净买入", "type": "keyword"},
                    {"value": "外资净卖出", "name": "外资净卖出", "type": "keyword"},
                    {"value": "Market Breadth", "name": "Market Breadth", "type": "keyword"},
                    {"value": "市场广度", "name": "市场广度", "type": "keyword"},
                    {"value": "Liquidity", "name": "Liquidity", "type": "keyword"},
                    {"value": "成交量", "name": "成交量", "type": "keyword"},
                    {"value": "流动性", "name": "流动性", "type": "keyword"},
                    {"value": "Retail Participation", "name": "Retail Participation", "type": "keyword"},
                    {"value": "散户参与度", "name": "散户参与度", "type": "keyword"},
                    {"value": "Power Shortage", "name": "Power Shortage", "type": "keyword"},
                    {"value": "电力短缺", "name": "电力短缺", "type": "keyword"},
                    {"value": "Northern Industrial Zones", "name": "Northern Industrial Zones", "type": "keyword"},
                    {"value": "北部工业区", "name": "北部工业区", "type": "keyword"},
                    {"value": "Marginal Lending", "name": "Marginal Lending", "type": "keyword"},
                    {"value": "融资融券", "name": "融资融券", "type": "keyword"},
                    {"value": "VSD", "name": "VSD", "type": "keyword"},
                    {"value": "越南证券登记结算中心", "name": "越南证券登记结算中心", "type": "keyword"},
                    {"value": "Force Sell", "name": "Force Sell", "type": "keyword"},
                    {"value": "强制平仓", "name": "强制平仓", "type": "keyword"},
                    {"value": "Binh Duong", "name": "Binh Duong", "type": "keyword"},
                    {"value": "平阳省", "name": "平阳省", "type": "keyword"},
                    {"value": "Dong Nai", "name": "Dong Nai", "type": "keyword"},
                    {"value": "同奈省", "name": "同奈省", "type": "keyword"},
                    {"value": "Vietnam CPI", "name": "Vietnam CPI", "type": "keyword"},
                    {"value": "SBV", "name": "SBV", "type": "keyword"},
                    {"value": "越南央行", "name": "越南央行", "type": "keyword"},
                    {"value": "越南通胀", "name": "越南通胀", "type": "keyword"},
                    {"value": "南部工业区", "name": "南部工业区", "type": "keyword"},
                    {"value": "Margin Call", "name": "Margin Call", "type": "keyword"},
                    {"value": "Burning Furnace", "name": "Burning Furnace", "type": "keyword"},
                    {"value": "熔炉行动", "name": "熔炉行动", "type": "keyword"},
                    {"value": "反腐运动", "name": "反腐运动", "type": "keyword"},
                    {"value": "SBV Credit Room", "name": "SBV Credit Room", "type": "keyword"},
                    {"value": "信达额度", "name": "信达额度", "type": "keyword"},
                    {"value": "VND Devaluation", "name": "VND Devaluation", "type": "keyword"},
                    {"value": "汇率贬值预期", "name": "汇率贬值预期", "type": "keyword"},
                    {"value": "FTSE Decision Window", "name": "FTSE Decision Window", "type": "keyword"},
                    {"value": "FTSE 审核窗口期", "name": "FTSE 审核窗口期", "type": "keyword"},
                    {"value": "Remittance", "name": "Remittance", "type": "keyword"},
                    {"value": "海外侨汇", "name": "海外侨汇", "type": "keyword"},
                ]
            },

            # ---------------------------------------------------------------------
            # (4) Global Macro & Risks (全球宏观风险 - 英文/混排)
            # ---------------------------------------------------------------------
            "GLOBAL_MACRO_RISKS": {
                # 描述: 宏观经济数据、美联储政策、地缘政治
                "desc": "Fed Policy, US Macro, and Geopolitics (English Context)",
                "items": [
                     # --- Keywords ---
                    {"value": "美联储", "name": "美联储", "type": "keyword"},
                    {"value": "Fed", "name": "Fed", "type": "keyword"},
                    {"value": "鲍威尔", "name": "鲍威尔", "type": "keyword"},
                    {"value": "Jerome Powell", "name": "Jerome Powell", "type": "keyword"},
                    {"value": "降息路径", "name": "降息路径", "type": "keyword"},
                    {"value": "点阵图", "name": "点阵图", "type": "keyword"},
                    {"value": "Dot Plot", "name": "Dot Plot", "type": "keyword"},
                    {"value": "10年期美债收益率", "name": "10年期美债收益率", "type": "keyword"},
                    {"value": "期限溢价", "name": "期限溢价", "type": "keyword"},
                    {"value": "Term Premium", "name": "Term Premium", "type": "keyword"},
                    {"value": "赤字率", "name": "赤字率", "type": "keyword"},
                    {"value": "关税", "name": "关税", "type": "keyword"},
                    {"value": "Tariffs", "name": "Tariffs", "type": "keyword"},
                    {"value": "USTR", "name": "USTR", "type": "keyword"},
                    {"value": "美国商务部", "name": "美国商务部", "type": "keyword"},
                    {"value": "BIS", "name": "BIS", "type": "keyword"},
                    {"value": "ON RRP", "name": "ON RRP", "type": "keyword"},
                    {"value": "隔夜逆回购", "name": "隔夜逆回购", "type": "keyword"},
                    {"value": "TGA账户", "name": "TGA账户", "type": "keyword"},
                    {"value": "SOFR", "name": "SOFR", "type": "keyword"},
                    {"value": "准备金", "name": "准备金", "type": "keyword"},
                    {"value": "Reserves", "name": "Reserves", "type": "keyword"},
                    {"value": "LCLOR", "name": "LCLOR", "type": "keyword"},
                    {"value": "最低舒适准备金水平", "name": "最低舒适准备金水平", "type": "keyword"},
                    {"value": "VIX", "name": "VIX", "type": "keyword"},
                    {"value": "波动率指数", "name": "波动率指数", "type": "keyword"},
                    {"value": "GEX", "name": "GEX", "type": "keyword"},
                    {"value": "伽马敞口", "name": "伽马敞口", "type": "keyword"},
                    {"value": "Zero Gamma", "name": "Zero Gamma", "type": "keyword"},
                    {"value": "0DTE", "name": "0DTE", "type": "keyword"},
                    {"value": "SKEW", "name": "SKEW", "type": "keyword"},
                    {"value": "NAAIM", "name": "NAAIM", "type": "keyword"},
                    {"value": "内部人买卖比率", "name": "内部人买卖比率", "type": "keyword"},
                    {"value": "Insider Buy Sell Ratio", "name": "Insider Buy Sell Ratio", "type": "keyword"},
                    {"value": "QT", "name": "QT", "type": "keyword"},
                    {"value": "量化紧缩", "name": "量化紧缩", "type": "keyword"},
                    {"value": "Treasury Buyback", "name": "Treasury Buyback", "type": "keyword"},
                    {"value": "财政部回购", "name": "财政部回购", "type": "keyword"},
                    {"value": "Debt Ceiling", "name": "Debt Ceiling", "type": "keyword"},
                    {"value": "债务上限", "name": "债务上限", "type": "keyword"},
                    {"value": "GDI", "name": "GDI", "type": "keyword"},
                    {"value": "国内总收入", "name": "国内总收入", "type": "keyword"},
                    {"value": "GDP裂口", "name": "GDP裂口", "type": "keyword"},
                    {"value": "Birth-Death Model", "name": "Birth-Death Model", "type": "keyword"},
                    {"value": "出生-死亡模型", "name": "出生-死亡模型", "type": "keyword"},
                    {"value": "Seasonally Adjusted", "name": "Seasonally Adjusted", "type": "keyword"},
                    {"value": "季节性调整", "name": "季节性调整", "type": "keyword"},
                    {"value": "萨姆规则", "name": "萨姆规则", "type": "keyword"},
                    {"value": "Sahm Rule", "name": "Sahm Rule", "type": "keyword"},
                    {"value": "初请失业金人数", "name": "初请失业金人数", "type": "keyword"},
                    {"value": "Initial Jobless Claims", "name": "Initial Jobless Claims", "type": "keyword"},
                    {"value": "非农就业", "name": "非农就业", "type": "keyword"},
                    {"value": "NFP", "name": "NFP", "type": "keyword"},
                    {"value": "Non-Farm Payrolls", "name": "Non-Farm Payrolls", "type": "keyword"},
                    {"value": "美债波动率指数", "name": "美债波动率指数", "type": "keyword"},
                    {"value": "MOVE Index", "name": "MOVE Index", "type": "keyword"},
                    {"value": "高收益债利差", "name": "高收益债利差", "type": "keyword"},
                    {"value": "HY OAS", "name": "HY OAS", "type": "keyword"},
                    {"value": "经济意外指数", "name": "经济意外指数", "type": "keyword"},
                    {"value": "Economic Surprise Index", "name": "Economic Surprise Index", "type": "keyword"},
                    {"value": "CESI", "name": "CESI", "type": "keyword"},
                    {"value": "存储芯片现货价", "name": "存储芯片现货价", "type": "keyword"},
                    {"value": "DRAM Spot Price", "name": "DRAM Spot Price", "type": "keyword"},
                    {"value": "NAND Flash", "name": "NAND Flash", "type": "keyword"},
                    {"value": "ASML订单", "name": "ASML订单", "type": "keyword"},
                    {"value": "ASML Orders", "name": "ASML Orders", "type": "keyword"},
                    {"value": "市场广度", "name": "市场广度", "type": "keyword"},
                    {"value": "Market Breadth", "name": "Market Breadth", "type": "keyword"},
                    {"value": "集中度风险", "name": "集中度风险", "type": "keyword"},
                    {"value": "Concentration Risk", "name": "Concentration Risk", "type": "keyword"},
                    {"value": "盈利修正利差", "name": "盈利修正利差", "type": "keyword"},
                    {"value": "Earnings Revision Spread", "name": "Earnings Revision Spread", "type": "keyword"},
                    {"value": "比特币", "name": "比特币", "type": "keyword"},
                    {"value": "Bitcoin", "name": "Bitcoin", "type": "keyword"},
                    {"value": "BTC", "name": "BTC", "type": "keyword"},
                    {"value": "Put/Call Ratio", "name": "Put/Call Ratio", "type": "keyword"},
                    {"value": "看跌/看涨期权比率", "name": "看跌/看涨期权比率", "type": "keyword"},
                    {"value": "Vanna", "name": "Vanna", "type": "keyword"},
                    {"value": "Charm", "name": "Charm", "type": "keyword"},
                    {"value": "ISM New Orders minus Inventories", "name": "ISM New Orders minus Inventories", "type": "keyword"},
                    {"value": "ISM新订单与库存差", "name": "ISM新订单与库存差", "type": "keyword"},
                    {"value": "基差交易", "name": "基差交易", "type": "keyword"},
                    {"value": "Basis Trade", "name": "Basis Trade", "type": "keyword"},
                    {"value": "MOVE指数", "name": "MOVE指数", "type": "keyword"},
                    {"value": "eSLR改革", "name": "eSLR改革", "type": "keyword"},
                    {"value": "财政部买回", "name": "财政部买回", "type": "keyword"},
                    {"value": "Treasury Buybacks", "name": "Treasury Buybacks", "type": "keyword"},
                    {"value": "铜价", "name": "铜价", "type": "keyword"},
                    {"value": "Copper Price", "name": "Copper Price", "type": "keyword"},
                    {"value": "铀现货", "name": "铀现货", "type": "keyword"},
                    {"value": "Uranium Spot", "name": "Uranium Spot", "type": "keyword"},
                    {"value": "SCFI", "name": "SCFI", "type": "keyword"},
                    {"value": "运价指数", "name": "运价指数", "type": "keyword"},
                    {"value": "BDI", "name": "BDI", "type": "keyword"},
                    {"value": "波罗的海干散货指数", "name": "波罗的海干散货指数", "type": "keyword"},
                    {"value": "Yen Carry Trade", "name": "Yen Carry Trade", "type": "keyword"},
                    {"value": "日元套息交易", "name": "日元套息交易", "type": "keyword"},
                    {"value": "JGB 10Y", "name": "JGB 10Y", "type": "keyword"},
                    {"value": "日债10年收益率", "name": "日债10年收益率", "type": "keyword"},
                    {"value": "High Yield Option-Adjusted Spread", "name": "High Yield Option-Adjusted Spread", "type": "keyword"},
                    {"value": "Citigroup Economic Surprise Index", "name": "Citigroup Economic Surprise Index", "type": "keyword"},
                    {"value": "花旗经济意外指数", "name": "花旗经济意外指数", "type": "keyword"},
                    {"value": "Financial Conditions Index", "name": "Financial Conditions Index", "type": "keyword"},
                    {"value": "FCI", "name": "FCI", "type": "keyword"},
                    {"value": "金融条件指数", "name": "金融条件指数", "type": "keyword"},
                    {"value": "NFCI", "name": "NFCI", "type": "keyword"},
                    {"value": "Bear Steepening", "name": "Bear Steepening", "type": "keyword"},
                    {"value": "熊市陡峭化", "name": "熊市陡峭化", "type": "keyword"},
                    {"value": "Oil Price Shock", "name": "Oil Price Shock", "type": "keyword"},
                    {"value": "原油价格冲击", "name": "原油价格冲击", "type": "keyword"},
                    {"value": "Red Sea", "name": "Red Sea", "type": "keyword"},
                    {"value": "红海", "name": "红海", "type": "keyword"},
                    {"value": "苏伊士运河", "name": "苏伊士运河", "type": "keyword"},
                    {"value": "LCR", "name": "LCR", "type": "keyword"},
                    {"value": "流动性覆盖率", "name": "流动性覆盖率", "type": "keyword"},
                    {"value": "Stagflation", "name": "Stagflation", "type": "keyword"},
                    {"value": "滞胀", "name": "滞胀", "type": "keyword"},
                    {"value": "Debt-to-GDP Ratio", "name": "Debt-to-GDP Ratio", "type": "keyword"},
                    {"value": "债务杠杆率", "name": "债务杠杆率", "type": "keyword"},
                    {"value": "Geopolitical Fragmentation", "name": "Geopolitical Fragmentation", "type": "keyword"},
                    {"value": "地缘碎片化", "name": "地缘碎片化", "type": "keyword"},
                    {"value": "物价冲击", "name": "物价冲击", "type": "keyword"},
                    {"value": "DR007", "name": "DR007", "type": "keyword"},
                    {"value": "银行间7天回购利率", "name": "银行间7天回购利率", "type": "keyword"},
                    {"value": "M1-M2 剪刀差", "name": "M1-M2 剪刀差", "type": "keyword"},
                    {"value": "M1-M2 Growth Gap", "name": "M1-M2 Growth Gap", "type": "keyword"},
                    {"value": "EPU Index", "name": "EPU Index", "type": "keyword"},
                    {"value": "经济政策不确定性指数", "name": "经济政策不确定性指数", "type": "keyword"},
                ]
            }
        },

        # =========================================================================
        # 2. CHINESE SOURCES (中文源)
        # 渠道: Akshare (东方财富, 财联社)
        # =========================================================================
        "CHINESE_SOURCES": {
            
            # ---------------------------------------------------------------------
            # (1) HK Tech (港股科技 - 中文)
            # ---------------------------------------------------------------------
            "HK_TECH_CN": {
                "desc": "Hang Seng Tech Key Assets (Domestic View)",
                "items": [
                    # --- Tickers ---
                    {"value": "^HSTECH", "name": "恒生科技指数", "type": "index_hk"},
                    {"value": "HSTECH", "name": "HSTECH", "type": "index_hk"},
                    
                    {"value": "0700.HK", "name": "腾讯控股", "type": "stock_hk"},
                    {"value": "9988.HK", "name": "阿里巴巴", "type": "stock_hk"},
                    {"value": "3690.HK", "name": "美团", "type": "stock_hk"},
                    {"value": "1810.HK", "name": "小米集团", "type": "stock_hk"},
                    {"value": "1024.HK", "name": "快手", "type": "stock_hk"},
                    {"value": "9618.HK", "name": "京东集团", "type": "stock_hk"},
                    {"value": "9999.HK", "name": "网易", "type": "stock_hk"},
                    {"value": "9888.HK", "name": "百度集团", "type": "stock_hk"},
                    {"value": "0981.HK", "name": "中芯国际(港)", "type": "stock_hk"},
                    
                    # --- Keywords ---
                    {"value": "恒生科技", "name": "恒生科技", "type": "keyword"},
                    {"value": "腾讯", "name": "腾讯", "type": "keyword"},
                    {"value": "Tencent", "name": "Tencent", "type": "keyword"},
                    {"value": "阿里巴巴", "name": "阿里巴巴", "type": "keyword"},
                    {"value": "Alibaba", "name": "Alibaba", "type": "keyword"},
                    {"value": "美团", "name": "美团", "type": "keyword"},
                    {"value": "Meituan", "name": "Meituan", "type": "keyword"},
                    {"value": "小米", "name": "小米", "type": "keyword"},
                    {"value": "Xiaomi", "name": "Xiaomi", "type": "keyword"},
                    {"value": "快手", "name": "快手", "type": "keyword"},
                    {"value": "Kuaishou", "name": "Kuaishou", "type": "keyword"},
                    {"value": "京东", "name": "京东", "type": "keyword"},
                    {"value": "JD.com", "name": "JD.com", "type": "keyword"},
                    {"value": "网易", "name": "网易", "type": "keyword"},
                    {"value": "NetEase", "name": "NetEase", "type": "keyword"},
                    {"value": "中芯国际", "name": "中芯国际", "type": "keyword"},
                    {"value": "SMIC", "name": "SMIC", "type": "keyword"},
                    {"value": "百度", "name": "百度", "type": "keyword"},
                    {"value": "Baidu", "name": "Baidu", "type": "keyword"},
                    {"value": "南向资金", "name": "南向资金", "type": "keyword"},
                    {"value": "Southbound Flow", "name": "Southbound Flow", "type": "keyword"},
                    {"value": "红利税减免", "name": "红利税减免", "type": "keyword"},
                    {"value": "回购墙", "name": "回购墙", "type": "keyword"},
                    {"value": "Buyback Wall", "name": "Buyback Wall", "type": "keyword"},
                    {"value": "AH股溢价", "name": "AH股溢价", "type": "keyword"},
                    {"value": "反内卷", "name": "反内卷", "type": "keyword"},
                    {"value": "Anti-Involution", "name": "Anti-Involution", "type": "keyword"},
                    {"value": "H200", "name": "H200", "type": "keyword"},
                    {"value": "250-day Moving Average", "name": "250-day Moving Average", "type": "keyword"},
                    {"value": "250日年线", "name": "250日年线", "type": "keyword"},
                    {"value": "PS Ratio", "name": "PS Ratio", "type": "keyword"},
                    {"value": "市销率", "name": "市销率", "type": "keyword"},
                    {"value": "Earnings Yield", "name": "Earnings Yield", "type": "keyword"},
                    {"value": "盈利收益率", "name": "盈利收益率", "type": "keyword"},
                    {"value": "Short Selling Ratio", "name": "Short Selling Ratio", "type": "keyword"},
                    {"value": "卖空成交比例", "name": "卖空成交比例", "type": "keyword"},
                    {"value": "ADR Pay-up", "name": "ADR Pay-up", "type": "keyword"},
                    {"value": "ADR溢价", "name": "ADR溢价", "type": "keyword"},
                    {"value": "HIBOR", "name": "HIBOR", "type": "keyword"},
                    {"value": "香港银行同业拆息", "name": "香港银行同业拆息", "type": "keyword"},
                    {"value": "Supply-side Reform", "name": "Supply-side Reform", "type": "keyword"},
                    {"value": "供给侧改革", "name": "供给侧改革", "type": "keyword"},
                    {"value": "Opex Optimization", "name": "Opex Optimization", "type": "keyword"},
                    {"value": "运营成本优化", "name": "运营成本优化", "type": "keyword"},
                    {"value": "Take-rate", "name": "Take-rate", "type": "keyword"},
                    {"value": "货币化率", "name": "货币化率", "type": "keyword"},
                    {"value": "Tariff Exclusion", "name": "Tariff Exclusion", "type": "keyword"},
                    {"value": "关税豁免", "name": "关税豁免", "type": "keyword"},
                    {"value": "Local Manufacturing", "name": "Local Manufacturing", "type": "keyword"},
                    {"value": "本地化生产", "name": "本地化生产", "type": "keyword"},
                    {"value": "EV Tariffs", "name": "EV Tariffs", "type": "keyword"},
                    {"value": "电动车关税", "name": "电动车关税", "type": "keyword"},
                    {"value": "Design-in China Tariffs", "name": "Design-in China Tariffs", "type": "keyword"},
                    {"value": "USD/HKD", "name": "USD/HKD", "type": "keyword"},
                    {"value": "美金港元汇率", "name": "美金港元汇率", "type": "keyword"},
                    {"value": "Golden Dragon Index", "name": "Golden Dragon Index", "type": "keyword"},
                    {"value": "金龙指数", "name": "金龙指数", "type": "keyword"},
                    {"value": "HXC", "name": "HXC", "type": "keyword"},
                    {"value": "弱方兑换保证", "name": "弱方兑换保证", "type": "keyword"},
                    {"value": "Platform Economy Guidelines", "name": "Platform Economy Guidelines", "type": "keyword"},
                    {"value": "平台监管细则", "name": "平台监管细则", "type": "keyword"},
                    {"value": "RMB Counter", "name": "RMB Counter", "type": "keyword"},
                    {"value": "双柜台交易", "name": "双柜台交易", "type": "keyword"},
                    {"value": "H-Share Index", "name": "H-Share Index", "type": "keyword"},
                    {"value": "国企指数联动", "name": "国企指数联动", "type": "keyword"},
                    {"value": "30大中城市成交面积", "name": "30大中城市成交面积", "type": "keyword"},
                    {"value": "Real Estate Transaction Volume", "name": "Real Estate Transaction Volume", "type": "keyword"},
                    {"value": "十五五规划", "name": "十五五规划", "type": "keyword"},
                    {"value": "15th Five-Year Plan", "name": "15th Five-Year Plan", "type": "keyword"},
                    {"value": "反内卷供给侧改革", "name": "反内卷供给侧改革", "type": "keyword"},
                ]
            },

            # ---------------------------------------------------------------------
            # (2) HK Biotech (港股创新药 - 中文)
            # ---------------------------------------------------------------------
            "HK_PHARMA_CN": {
                "desc": "HK Biotech Companies & Policies",
                "items": [
                    # --- Tickers ---
                    {"value": "1801.HK", "name": "信达生物", "type": "stock_hk"},
                    {"value": "6160.HK", "name": "百济神州", "type": "stock_hk"},
                    {"value": "2269.HK", "name": "药明生物", "type": "stock_hk"},
                    {"value": "9926.HK", "name": "康方生物", "type": "stock_hk"},
                    {"value": "2359.HK", "name": "药明康德", "type": "stock_hk"},
                    {"value": "6990.HK", "name": "科伦博泰", "type": "stock_hk"},
                    
                    # --- Keywords ---
                    {"value": "港股创新药", "name": "港股创新药", "type": "keyword"},
                    {"value": "信达生物", "name": "信达生物(Kw)", "type": "keyword"},
                    {"value": "百济神州", "name": "百济神州(Kw)", "type": "keyword"},
                    {"value": "Beigene", "name": "Beigene", "type": "keyword"},
                    {"value": "药明生物", "name": "药明生物(Kw)", "type": "keyword"},
                    {"value": "WuXi Biologics", "name": "WuXi Biologics", "type": "keyword"},
                    {"value": "康方生物", "name": "康方生物(Kw)", "type": "keyword"},
                    {"value": "药明康德", "name": "药明康德(Kw)", "type": "keyword"},
                    {"value": "WuXi AppTec", "name": "WuXi AppTec", "type": "keyword"},
                    {"value": "科伦博泰", "name": "科伦博泰(Kw)", "type": "keyword"},
                    {"value": "生物安全法案", "name": "生物安全法案", "type": "keyword"},
                    {"value": "Biosecure Act", "name": "Biosecure Act", "type": "keyword"},
                    {"value": "1260H名单", "name": "1260H名单", "type": "keyword"},
                    {"value": "CDMO", "name": "CDMO", "type": "keyword"},
                    {"value": "NRDL", "name": "NRDL", "type": "keyword"},
                    {"value": "医保谈判", "name": "医保谈判", "type": "keyword"},
                    {"value": "依沃西", "name": "依沃西", "type": "keyword"},
                    {"value": "AK112", "name": "AK112", "type": "keyword"},
                    {"value": "PD-1", "name": "PD-1", "type": "keyword"},
                    {"value": "VEGF", "name": "VEGF", "type": "keyword"},
                    {"value": "ADC", "name": "ADC", "type": "keyword"},
                    {"value": "抗体偶联药物", "name": "抗体偶联药物", "type": "keyword"},
                    {"value": "BD出海", "name": "BD出海", "type": "keyword"},
                    {"value": "License-out", "name": "License-out", "type": "keyword"},
                    {"value": "FDA审批", "name": "FDA审批", "type": "keyword"},
                    {"value": "现金跑道", "name": "现金跑道", "type": "keyword"},
                    {"value": "Cash Runway", "name": "Cash Runway", "type": "keyword"},
                    {"value": "恒生医疗保健指数", "name": "恒生医疗保健指数", "type": "keyword"},
                    {"value": "HSHCI", "name": "HSHCI", "type": "keyword"},
                    {"value": "XBI", "name": "XBI", "type": "keyword"},
                    {"value": "NMPA", "name": "NMPA", "type": "keyword"},
                    {"value": "国家药监局", "name": "国家药监局", "type": "keyword"},
                    {"value": "集采", "name": "集采", "type": "keyword"},
                    {"value": "VBP", "name": "VBP", "type": "keyword"},
                    {"value": "创新药进院", "name": "创新药进院", "type": "keyword"},
                    {"value": "华大基因", "name": "华大基因", "type": "keyword"},
                    {"value": "BGI", "name": "BGI", "type": "keyword"},
                    {"value": "华大智造", "name": "华大智造", "type": "keyword"},
                    {"value": "MGI", "name": "MGI", "type": "keyword"},
                    {"value": "金斯瑞", "name": "金斯瑞", "type": "keyword"},
                    {"value": "Genscript", "name": "Genscript", "type": "keyword"},
                    {"value": "美债收益率", "name": "美债收益率", "type": "keyword"},
                    {"value": "Treasury Yields", "name": "Treasury Yields", "type": "keyword"},
                    {"value": "降息", "name": "降息", "type": "keyword"},
                    {"value": "Rate Cut", "name": "Rate Cut", "type": "keyword"},
                    {"value": "M&A", "name": "M&A", "type": "keyword"},
                    {"value": "GLP-1", "name": "GLP-1", "type": "keyword"},
                    {"value": "减肥药", "name": "减肥药", "type": "keyword"},
                    {"value": "ASCO", "name": "ASCO", "type": "keyword"},
                    {"value": "ESMO", "name": "ESMO", "type": "keyword"},
                    {"value": "核药", "name": "核药", "type": "keyword"},
                    {"value": "Radiopharmaceutical", "name": "Radiopharmaceutical", "type": "keyword"},
                    {"value": "细胞治疗", "name": "细胞治疗", "type": "keyword"},
                    {"value": "Cell Therapy", "name": "Cell Therapy", "type": "keyword"},
                    {"value": "CAR-T", "name": "CAR-T", "type": "keyword"},
                    {"value": "UFLPA", "name": "UFLPA", "type": "keyword"},
                    {"value": "维吾尔强迫劳动预防法", "name": "维吾尔强迫劳动预防法", "type": "keyword"},
                    {"value": "Clinical Hold", "name": "Clinical Hold", "type": "keyword"},
                    {"value": "临床暂停", "name": "临床暂停", "type": "keyword"},
                    {"value": "CRL", "name": "CRL", "type": "keyword"},
                    {"value": "完整回复函", "name": "完整回复函", "type": "keyword"},
                    {"value": "拒绝信", "name": "拒绝信", "type": "keyword"},
                    {"value": "Fast Track", "name": "Fast Track", "type": "keyword"},
                    {"value": "快速通道", "name": "快速通道", "type": "keyword"},
                    {"value": "Breakthrough Therapy", "name": "Breakthrough Therapy", "type": "keyword"},
                    {"value": "突破性疗法", "name": "突破性疗法", "type": "keyword"},
                    {"value": "CDE", "name": "CDE", "type": "keyword"},
                    {"value": "药品审评中心", "name": "药品审评中心", "type": "keyword"},
                    {"value": "Clinical Data Readout", "name": "Clinical Data Readout", "type": "keyword"},
                    {"value": "临床数据披露", "name": "临床数据披露", "type": "keyword"},
                    {"value": "CRO Capacity Utilization", "name": "CRO Capacity Utilization", "type": "keyword"},
                    {"value": "CRO产能利用率", "name": "CRO产能利用率", "type": "keyword"},
                ]
            },

            # ---------------------------------------------------------------------
            # (3) A-Shares: STAR 50 (科创50 - 中文)
            # ---------------------------------------------------------------------
            "A_SHARES_STAR50": {
                "desc": "STAR 50 ETF and Holdings",
                "items": [
                    # --- Tickers ---
                    {"value": "588000", "name": "科创50ETF", "type": "etf_zh"},
                    {"value": "688981", "name": "中芯国际(A)", "type": "stock_zh_a"},
                    {"value": "688041", "name": "海光信息", "type": "stock_zh_a"},
                    {"value": "688256", "name": "寒武纪", "type": "stock_zh_a"},
                    {"value": "688008", "name": "澜起科技", "type": "stock_zh_a"},
                    {"value": "688012", "name": "中微公司", "type": "stock_zh_a"},
                    {"value": "688271", "name": "联影医疗", "type": "stock_zh_a"},
                    {"value": "688111", "name": "金山办公", "type": "stock_zh_a"},
                    {"value": "688036", "name": "传音控股", "type": "stock_zh_a"},
                    {"value": "688169", "name": "石头科技", "type": "stock_zh_a"},
                    {"value": "688521", "name": "芯原股份", "type": "stock_zh_a"},
                    
                    # --- Keywords ---
                     {"value": "科创50", "name": "科创50", "type": "keyword"},
                     {"value": "STAR 50", "name": "STAR 50", "type": "keyword"},
                     {"value": "海光信息", "name": "海光信息(Kw)", "type": "keyword"},
                     {"value": "寒武纪", "name": "寒武纪(Kw)", "type": "keyword"},
                     {"value": "中微公司", "name": "中微公司(Kw)", "type": "keyword"},
                     {"value": "金山办公", "name": "金山办公(Kw)", "type": "keyword"},
                     {"value": "澜起科技", "name": "澜起科技(Kw)", "type": "keyword"},
                     {"value": "传音控股", "name": "传音控股(Kw)", "type": "keyword"},
                     {"value": "石头科技", "name": "石头科技(Kw)", "type": "keyword"},
                     {"value": "芯原股份", "name": "芯原股份(Kw)", "type": "keyword"},
                     {"value": "联影医疗", "name": "联影医疗(Kw)", "type": "keyword"},
                     {"value": "国产替代", "name": "国产替代", "type": "keyword"},
                     {"value": "18A制程", "name": "18A制程", "type": "keyword"},
                     {"value": "羲之光刻机", "name": "羲之光刻机", "type": "keyword"},
                     {"value": "EBL", "name": "EBL", "type": "keyword"},
                     {"value": "自主可控", "name": "自主可控", "type": "keyword"},
                     {"value": "大基金三期", "name": "大基金三期", "type": "keyword"},
                     {"value": "设备国产化率", "name": "设备国产化率", "type": "keyword"},
                     {"value": "融资余额", "name": "融资余额", "type": "keyword"},
                     {"value": "Margin Balance", "name": "Margin Balance", "type": "keyword"},
                     {"value": "合同负债", "name": "合同负债", "type": "keyword"},
                     {"value": "并购重组", "name": "并购重组", "type": "keyword"},
                     {"value": "科创板八条", "name": "科创板八条", "type": "keyword"},
                     {"value": "转融通余额", "name": "转融通余额", "type": "keyword"},
                     {"value": "Securities Lending", "name": "Securities Lending", "type": "keyword"},
                     {"value": "解禁压力", "name": "解禁压力", "type": "keyword"},
                     {"value": "Unlock Pressure", "name": "Unlock Pressure", "type": "keyword"},
                     {"value": "EDA", "name": "EDA", "type": "keyword"},
                     {"value": "电子设计自动化", "name": "电子设计自动化", "type": "keyword"},
                     {"value": "光刻胶", "name": "光刻胶", "type": "keyword"},
                     {"value": "Photoresist", "name": "Photoresist", "type": "keyword"},
                     {"value": "先进封装", "name": "先进封装", "type": "keyword"},
                     {"value": "Advanced Packaging", "name": "Advanced Packaging", "type": "keyword"},
                     {"value": "Chiplet", "name": "Chiplet", "type": "keyword"},
                     {"value": "芯粒", "name": "芯粒", "type": "keyword"},
                     {"value": "HBM国产化", "name": "HBM国产化", "type": "keyword"},
                     {"value": "韩国半导体出口", "name": "韩国半导体出口", "type": "keyword"},
                     {"value": "Korea Semiconductor Exports", "name": "Korea Semiconductor Exports", "type": "keyword"},
                     {"value": "DRAM Spot Price", "name": "DRAM Spot Price", "type": "keyword"},
                     {"value": "存储芯片现货价", "name": "存储芯片现货价", "type": "keyword"},
                     {"value": "NAND Flash", "name": "NAND Flash", "type": "keyword"},
                     {"value": "北美半导体设备出货额", "name": "北美半导体设备出货额", "type": "keyword"},
                     {"value": "North America Billing Report", "name": "North America Billing Report", "type": "keyword"},
                     {"value": "实体清单", "name": "实体清单", "type": "keyword"},
                     {"value": "Entity List", "name": "Entity List", "type": "keyword"},
                     {"value": "瓦森纳协定", "name": "瓦森纳协定", "type": "keyword"},
                     {"value": "Wassenaar Arrangement", "name": "Wassenaar Arrangement", "type": "keyword"},
                     {"value": "出口管制修正案", "name": "出口管制修正案", "type": "keyword"},
                     {"value": "FDPR", "name": "FDPR", "type": "keyword"},
                     {"value": "IP授权", "name": "IP授权", "type": "keyword"},
                     {"value": "Wafer Fab", "name": "Wafer Fab", "type": "keyword"},
                     {"value": "晶圆厂建厂节奏", "name": "晶圆厂建厂节奏", "type": "keyword"},
                     {"value": "Utilization Rate", "name": "Utilization Rate", "type": "keyword"},
                     {"value": "产能利用率", "name": "产能利用率", "type": "keyword"},
                     {"value": "Equity Incentives", "name": "Equity Incentives", "type": "keyword"},
                     {"value": "股权激励计划", "name": "股权激励计划", "type": "keyword"},
                     {"value": "RISC-V", "name": "RISC-V", "type": "keyword"},
                     {"value": "开源架构", "name": "开源架构", "type": "keyword"},
                     {"value": "ASIC", "name": "ASIC", "type": "keyword"},
                     {"value": "专用集成电路", "name": "专用集成电路", "type": "keyword"},
                     {"value": "GPGPU", "name": "GPGPU", "type": "keyword"},
                     {"value": "通用图形处理器", "name": "通用图形处理器", "type": "keyword"},
                     {"value": "CPO", "name": "CPO", "type": "keyword"},
                     {"value": "共封装光学", "name": "共封装光学", "type": "keyword"},
                     {"value": "STAR Market ETF Flow", "name": "STAR Market ETF Flow", "type": "keyword"},
                     {"value": "科创50ETF资金流向", "name": "科创50ETF资金流向", "type": "keyword"},
                     {"value": "Extreme UV", "name": "Extreme UV", "type": "keyword"},
                     {"value": "EUV国产化", "name": "EUV国产化", "type": "keyword"},
                     {"value": "STIB IPO Guidance", "name": "STIB IPO Guidance", "type": "keyword"},
                     {"value": "科创板IPO节奏", "name": "科创板IPO节奏", "type": "keyword"},
                ]
            }
        }
    }
}
