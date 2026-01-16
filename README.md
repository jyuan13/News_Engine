# News Acquisition Engine (新闻采集引擎)

这是一个模块化的新闻聚合系统，集成了多种数据源（YFinance, Akshare, OpenBB, Google News, Guardian等）并具备语义数据清洗功能。

## 核心功能

1.  **多源海量采集 (Mass Acquisition)**
    *   **YFinance**: 获取美股、外汇、大宗商品新闻。
    *   **Akshare**: 获取A股、港股、以及中国宏观经济新闻。
    *   **OpenBB**: 聚合多渠道金融数据。
    *   **Google News RSS**: 针对特定关键词进行大规模全文抓取（已优化：支持日期预过滤及并发加速）。
    *   **The Guardian**: 获取高质量的深度报道。

2.  **语义数据清洗 (Semantic Data Cleaning)**
    *   利用 BERT 模型 (`sentence-transformers`) 对新闻进行向量化。
    *   **语义去重**: 自动识别并合并跨来源、跨语言的重复报道。
    *   **中英分治**: 针对中文和英文内容分别加载优化的语言模型进行处理。

3.  **高性能 (Performance)**
    *   **并发采集**: 支持多线程并发获取新闻，大幅提升抓取速度。
    *   **智能过滤**: 自动过滤非近期（默认7天外）新闻，减少无效请求。

## 项目结构
```
News_Engine/
├── main.py              # 启动入口 (包含并发调度逻辑)
├── config.py            # 全局配置 (目标关键词、API Key、开关)
├── requirements.txt     # 依赖包列表
├── data/                # 输出数据 (JSON报告)
├── fetchers/            # 采集脚本 (YFinance, Akshare, OpenBB等)
├── processing/          # 数据处理 (语义清洗)
├── utils/               # 通用工具
└── tests/               # 测试脚本
```
*(注：参考文档已移至 Ref/ 目录，不包含在工程源码中)*

## 部署与运行

1.  **环境安装**
    ```bash
    pip install -r requirements.txt
    pip install sentence-transformers
    ```

2.  **配置**
    *   修改 `config.py`，配置 API Keys。
    *   确认 `ENABLE_GOOGLE_RSS = True` 以启用全文抓取。

3.  **运行**
    ```bash
    python main.py
    ```

## 下一步计划 (Roadmap)

1.  **LLM 集成 (智能体)**: 使用大模型自动拼装搜索关键词，并对新闻进行智能摘要和评级。
2.  **多智能体协作**: 引入“分析师”和“风控官”角色 Agent，自动生成投资简报。
