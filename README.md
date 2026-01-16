# News Acquisition Engine (新闻采集引擎)

这是一个模块化的新闻聚合系统，集成了多种数据源（YFinance, Akshare, OpenBB, Google News, Guardian等）并具备语义数据清洗功能。

## 核心功能

1.  **多源海量采集 (Mass Acquisition)**
    *   **YFinance**: 获取美股、外汇、大宗商品新闻。
    *   **Akshare**: 获取A股、港股、以及中国宏观经济新闻。
    *   **OpenBB**: 聚合多渠道金融数据。
    *   **Google News RSS**: 针对特定关键词（如“AI Capex”、“Sovereign AI”）进行大规模全文抓取。
    *   **The Guardian**: 获取高质量的深度报道。

2.  **语义数据清洗 (Semantic Data Cleaning)**
    *   利用 BERT 模型 (`sentence-transformers`) 对新闻进行向量化。
    *   **语义去重**: 自动识别并合并跨来源、跨语言的重复报道（例如“英伟达股价上涨”与“Nvidia stock rose”被视为同一事件）。
    *   **中英分治**: 针对中文和英文内容分别加载优化的语言模型进行处理。

3.  **模块化架构**
    *   清洗后的数据统一输出到 `data/` 目录。
    *   代码结构清晰：Fetcher（采集）、Processing（清洗）、Utils（通用）分离。

## 项目结构
```
News_Engine/
├── main.py              # 启动入口
├── config.py            # 全局配置 (目标关键词、API Key、模型参数)
├── requirements.txt     # 依赖包列表
├── data/                # 输出数据 (JSON报告)
├── fetchers/            # 采集脚本 (YFinance, Akshare, OpenBB等)
├── processing/          # 数据处理 (语义清洗)
├── utils/               # 通用工具
└── tests/               # 测试脚本
```

## 部署与运行 (Deployment)

1.  **环境安装**
    ```bash
    pip install -r requirements.txt
    pip install sentence-transformers
    ```

2.  **配置**
    *   修改 `config.py`，填入必要的 API Keys (如 SerpAPI, Guardian API)。
    *   在 `config.py` 的 `CLEANING` 部分调整去重模型参数（可选）。

3.  **运行引擎**
    ```bash
    python main.py
    ```
    *   运行结束后，清洗好的数据将保存在 `data/` 目录下，文件名为 `Cleaned_Report_*.json`。

4.  **测试清洗功能**
    ```bash
    python tests/test_data_cleaner.py
    ```

## 下一步计划 (Roadmap: LLM Integration)

我们将引入大语言模型 (LLM) 以实现更高层级的智能处理：

1.  **智能搜索与API调度 (Agentic Retrieval)**
    *   使用 LLM 动态拼装搜索关键词。
    *   智能调度有次数限制的付费 API (如 SerpAPI, Guardian)，仅在 LLM 判断“值得深入”时才进行调用，节省成本。

2.  **多智能体协作与分析 (Multi-Agent Analysis)**
    *   **新闻研讨会 (Newsroom Discussion)**: 创建多个 Agent 角色（如宏观分析师、科技行业专家、风险控制官）对新闻进行讨论。
    *   **智能评级与分类**:
        *   根据新闻对他资产类别（黄金/美股/基本面）的影响力打分。
        *   自动生成所有重要新闻的简报和深度分析。
