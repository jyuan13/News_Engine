# News Acquisition Engine (新闻采集引擎 v2.0)

这是一个基于 **7层架构 (7-Layer Architecture)** 的模块化新闻聚合系统，集成了多种数据源（YFinance, Akshare, Google News等），支持语义清洗，并内置邮件智能投递功能。

## 核心架构 (7-Layer Architecture)
为了实现高内聚低耦合，项目采用以下分层设计：

| 层级 | 模块 | 路径 | 功能描述 |
| :--- | :--- | :--- | :--- |
| **1. DataSources** | 数据源层 | `data_sources/` | 封装底层 API (YFinance, Akshare, GoogleRSS, Guardian, OpenBB)。 |
| **2. Collectors** | 采集层 | `collectors/` | 业务逻辑单元，负责特定板块（如美股科技、大宗商品）的策略性采集。 |
| **3. Processors** | 处理层 | `processors/` | 语义清洗、去重、翻译与摘要。 |
| **4. Formatters** | 格式化层 | `formatters/` | 将清洗后的数据转化为 HTML 报表。 |
| **5. Core** | 消息中心 | `core/` | **MessageBus**: 负责各层之间的消息路由与分发。 |
| **6. Dispatchers** | 分发层 | `dispatchers/` | **EmailDispatcher**: 通过 SMTP 发送最终报表。 |
| **7. Consumers** | 终端层 | `(Future)` | 前端展示或 API 接口。 |

## 核心功能

1.  **板块化采集**: 包含 7 个预置采集器:
    *   `US_TECH`: 美股科技与 AI 巨头
    *   `COMMODITIES`: 全球大宗商品 (黄金/原油等)
    *   `VIETNAM`: 越南市场前沿动态
    *   `MACRO`: 全球宏观风险
    *   `HK_TECH`: 港股科技板块
    *   `HK_PHARMA`: 港股创新药
    *   `STAR50`: A股科创50与芯片

2.  **智能邮件通知**: 采集完成后自动生成 HTML 报表并发送邮件。

3.  **语义去重**: 利用 `sentence-transformers` 进行跨源内容去重。

## 项目结构
```
News_Engine/
├── main.py              # CLI 入口
├── config.py            # 全局配置
├── requirements.txt     # 依赖
├── data_sources/        # [Layer 1] 底层 API
├── collectors/          # [Layer 2] 业务采集器
├── processors/          # [Layer 3] 清洗逻辑
├── formatters/          # [Layer 4] 报表渲染
├── core/                # [Layer 5] 消息总线
├── dispatchers/         # [Layer 6] 邮件发送
├── data/                # 输出数据 (JSON)
└── tests/               # 测试文件
```

## 部署与运行

### 1. 环境安装
```bash
pip install -r requirements.txt
pip install sentence-transformers
```

### 2. 配置环境变量 (用于邮件和部分 API)
请在系统环境变量或 `.env` (需自行加载) 中设置：
*   `SENDER_EMAIL`: 发件人邮箱 (推荐 QQ 邮箱)
*   `SENDER_PASSWORD`: 邮箱授权码 (SMTP)
*   `RECEIVER_EMAIL`: 收件人列表
*   `SERP_API_KEY` / `News_API_KEY`: (可选) 第三方 API 密钥

### 3. 运行 (CLI 模式)

**采集所有板块:**
```bash
python main.py --collector=ALL
```

**采集特定板块:**
```bash
python main.py --collector=US_TECH
python main.py --collector=COMMODITIES
```

## 自动化 (CI/CD)
本项目包含 GitHub Actions 工作流 (`manual_fetch.yml`)，支持在 GitHub 网页端手动选择板块进行云端采集并发送邮件。

