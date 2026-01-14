import os

# CONFIGURATION
# Categories maps structured groups to list of items.
# Each item has: "value", "name", "type"

CONFIG = {
    "DAYS_BACK": 7,
    "OUTPUT_FILE": "news_result.json",
    "SERP_API_KEY": os.getenv("SERP_API_KEY"),
    
    "CATEGORIES": {
        # ------------------------------------------------
        # 1. US Market (Indices, Mag7, ETFs)
        # ------------------------------------------------
        "US_MARKET": {
            "desc": "US Indices, Mag7, and ETFs",
            "items": [
                # INDICES
                {"value": "^NDX", "name": "Nasdaq 100", "type": "index_us"}, # 纳斯达克100
                {"value": "^GSPC", "name": "S&P 500", "type": "index_us"},   # 标普500
                # ETFS
                {"value": "VNM", "name": "VanEck Vietnam ETF", "type": "stock_us"}, # 越南ETF
                {"value": "XBI", "name": "Biotech ETF", "type": "stock_us"},        # 生物科技ETF
                # MAG 7 & CHIPS
                {"value": "AAPL",  "name": "Apple",         "type": "stock_us"}, # 苹果
                {"value": "MSFT",  "name": "Microsoft",     "type": "stock_us"}, # 微软
                {"value": "GOOGL", "name": "Google",        "type": "stock_us"}, # 谷歌
                {"value": "AMZN",  "name": "Amazon",        "type": "stock_us"}, # 亚马逊
                {"value": "NVDA",  "name": "Nvidia",        "type": "stock_us"}, # 英伟达
                {"value": "META",  "name": "Meta",          "type": "stock_us"}, # Meta
                {"value": "TSLA",  "name": "Tesla",         "type": "stock_us"}, # 特斯拉
                {"value": "TSM",   "name": "TSMC",          "type": "stock_us"}, # 台积电
                {"value": "AVGO",  "name": "Broadcom",      "type": "stock_us"}, # 博通
                {"value": "MU",    "name": "Micron",        "type": "stock_us"}, # 美光
            ]
        },

        # ------------------------------------------------
        # 2. HK Tech (Indices & Top 20)
        # ------------------------------------------------
        "HK_TECH": {
            "desc": "Hang Seng Tech Index & Constituents",
            "items": [
                # INDICES
                {"value": "^HSTECH", "name": "Hang Seng Tech Index", "type": "index_hk"}, # 恒生科技指数
                {"value": "^HSI",    "name": "Hang Seng Index",      "type": "index_hk"}, # 恒生指数
                # STOCKS
                {"value": "3690.HK", "name": "Meituan", "type": "stock_hk"},          # 美团
                {"value": "0700.HK", "name": "Tencent", "type": "stock_hk"},          # 腾讯
                {"value": "1810.HK", "name": "Xiaomi", "type": "stock_hk"},           # 小米
                {"value": "9988.HK", "name": "Alibaba", "type": "stock_hk"},          # 阿里巴巴
                {"value": "2015.HK", "name": "Li Auto", "type": "stock_hk"},          # 理想汽车
                {"value": "1024.HK", "name": "Kuaishou", "type": "stock_hk"},         # 快手
                {"value": "9618.HK", "name": "JD.com", "type": "stock_hk"},           # 京东
                {"value": "9999.HK", "name": "NetEase", "type": "stock_hk"},          # 网易
                {"value": "9888.HK", "name": "Baidu", "type": "stock_hk"},            # 百度
                {"value": "9961.HK", "name": "Trip.com", "type": "stock_hk"},         # 携程
                {"value": "0981.HK", "name": "SMIC", "type": "stock_hk"},             # 中芯国际
                {"value": "6690.HK", "name": "Haier Smart Home", "type": "stock_hk"}, # 海尔智家
                {"value": "0285.HK", "name": "BYD Electronic", "type": "stock_hk"},   # 比亚迪电子
                {"value": "2382.HK", "name": "Sunny Optical", "type": "stock_hk"},    # 舜宇光学
                {"value": "0772.HK", "name": "China Literature", "type": "stock_hk"}, # 阅文集团
                {"value": "0020.HK", "name": "SenseTime", "type": "stock_hk"},        # 商汤
                {"value": "3888.HK", "name": "Kingsoft", "type": "stock_hk"},         # 金山软件
                {"value": "1347.HK", "name": "Hua Hong Semi", "type": "stock_hk"},    # 华虹半导体
                {"value": "0268.HK", "name": "Kingdee", "type": "stock_hk"},          # 金蝶国际
                {"value": "0780.HK", "name": "Tongcheng Travel", "type": "stock_hk"}, # 同程旅行
            ]
        },

        # ------------------------------------------------
        # 3. HK Pharma
        # ------------------------------------------------
        "HK_PHARMA": {
            "desc": "Hong Kong Innovative Pharma",
            "items": [
                {"value": "1801.HK", "name": "Innovent Bio", "type": "stock_hk"},    # 信达生物
                {"value": "6160.HK", "name": "BeiGene", "type": "stock_hk"},         # 百济神州
                {"value": "2269.HK", "name": "WuXi Biologics", "type": "stock_hk"},  # 药明生物
                {"value": "9926.HK", "name": "Akeso", "type": "stock_hk"},           # 康方生物
                {"value": "1177.HK", "name": "Sino Biopharm", "type": "stock_hk"},   # 中国生物制药
                {"value": "1093.HK", "name": "CSPC Pharma", "type": "stock_hk"},     # 石药集团
                {"value": "1530.HK", "name": "3SBio", "type": "stock_hk"},           # 三生制药
                {"value": "2359.HK", "name": "WuXi AppTec", "type": "stock_hk"},     # 药明康德
                {"value": "3692.HK", "name": "Hansoh Pharma", "type": "stock_hk"},   # 翰森制药
                {"value": "6990.HK", "name": "Kelun-Biotech", "type": "stock_hk"},   # 科伦博泰
            ]
        },

        # ------------------------------------------------
        # 4. Emerging Markets (Vietnam)
        # ------------------------------------------------
        "EMERGING_MARKETS": {
            "desc": "Vietnam Top 10 Stocks",
            "items": [
                {"value": "VPB.VN", "name": "VPBank", "type": "stock_vn"},       # 越南繁荣银行
                {"value": "MBB.VN", "name": "MBBank", "type": "stock_vn"},       # 军队商业银行
                {"value": "HPG.VN", "name": "Hoa Phat Group", "type": "stock_vn"}, # 和发集团
                {"value": "MWG.VN", "name": "Mobile World", "type": "stock_vn"},  # 移动世界
                {"value": "FPT.VN", "name": "FPT Corp", "type": "stock_vn"},      # FPT公司
                {"value": "STB.VN", "name": "Sacombank", "type": "stock_vn"},     # 西贡商信
                {"value": "HDB.VN", "name": "HDBank", "type": "stock_vn"},        # 胡志明发展银行
                {"value": "TCB.VN", "name": "Techcombank", "type": "stock_vn"},   # 科技商业银行
                {"value": "VIC.VN", "name": "Vingroup", "type": "stock_vn"},      # Vingroup
                {"value": "VHM.VN", "name": "Vinhomes", "type": "stock_vn"},      # Vinhomes
            ]
        },

        # ------------------------------------------------
        # 5. A-Shares (STAR 50)
        # ------------------------------------------------
        "A_SHARES_STAR50": {
            "desc": "STAR 50 ETF & Holdings",
            "items": [
                # ETF
                {"value": "588000", "name": "STAR 50 ETF", "type": "etf_zh"},         # 科创50ETF
                # HOLDINGS
                {"value": "688981", "name": "SMIC (CN)", "type": "stock_zh_a"},       # 中芯国际
                {"value": "688041", "name": "Hygon Info", "type": "stock_zh_a"},      # 海光信息
                {"value": "688256", "name": "Cambricon", "type": "stock_zh_a"},       # 寒武纪
                {"value": "688008", "name": "Montage Tech", "type": "stock_zh_a"},    # 澜起科技
                {"value": "688012", "name": "AMEC", "type": "stock_zh_a"},            # 中微公司
                {"value": "688271", "name": "United Imaging", "type": "stock_zh_a"},  # 联影医疗
                {"value": "688111", "name": "Kingsoft Office", "type": "stock_zh_a"}, # 金山办公
                {"value": "688521", "name": "VeriSilicon", "type": "stock_zh_a"},     # 芯原股份
                {"value": "688169", "name": "Roborock", "type": "stock_zh_a"},        # 石头科技
                {"value": "688036", "name": "Transsion", "type": "stock_zh_a"},       # 传音控股
                {"value": "688126", "name": "Silicon Industry", "type": "stock_zh_a"},# 沪硅产业
                {"value": "688120", "name": "Hwatsing", "type": "stock_zh_a"},        # 华海清科
                {"value": "688099", "name": "Amlogic", "type": "stock_zh_a"},         # 晶晨股份
                {"value": "688072", "name": "Piotech", "type": "stock_zh_a"},         # 拓荆科技
                {"value": "688608", "name": "Bestechnic", "type": "stock_zh_a"},      # 恒玄科技
                {"value": "688777", "name": "Supcon", "type": "stock_zh_a"},          # 中控技术
                {"value": "688525", "name": "Biwin", "type": "stock_zh_a"},           # 佰维存储
                {"value": "688213", "name": "SmartSens", "type": "stock_zh_a"},       # 思特威
                {"value": "688469", "name": "SMEC", "type": "stock_zh_a"},            # 芯联集成
                {"value": "688506", "name": "Baili Tianheng", "type": "stock_zh_a"},  # 百利天恒
            ]
        },

        # ------------------------------------------------
        # 6. Commodities
        # ------------------------------------------------
        "COMMODITIES": {
            "desc": "Global Commodities (Gold, Silver, Oil, etc.)",
            "items": [
                {"value": "GC=F", "name": "Gold (COMEX)", "type": "future_foreign"},   # 黄金
                {"value": "SI=F", "name": "Silver (COMEX)", "type": "future_foreign"}, # 白银
                {"value": "HG=F", "name": "Copper (COMEX)", "type": "future_foreign"}, # 铜
                {"value": "CL=F", "name": "Crude Oil (WTI)", "type": "future_foreign"},# 原油
                {"value": "URA",  "name": "Uranium ETF",     "type": "stock_us"},      # 铀矿ETF
                {"value": "au0",  "name": "Shanghai Gold",   "type": "future_zh_sina"},# 上海金
            ]
        },

        # ------------------------------------------------
        # 7. Policy & Macro
        # ------------------------------------------------
        "POLICY_MACRO": {
            "desc": "Medical Policies, Acts, and Macro Regulations",
            "items": [
                {"value": "Medical Policy", "name": "Medical Policy", "type": "keyword"},     # 医疗政策
                {"value": "Healthcare Act", "name": "Healthcare Act", "type": "keyword"},     # 医保法案
                {"value": "FDA Approval",   "name": "FDA Approval",   "type": "keyword"},     # FDA批准
                {"value": "CDE Review",     "name": "CDE Review (China)", "type": "keyword"}, # CDE评审
            ]
        }
    }
}
