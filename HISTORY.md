# Project History

## v2.0.1 (2026-01-17) - Quality & Format Fixes
- **Fix**: **Data Quality**. Implemented strict validation in `DataCleaner` and `GoogleNews_RSS_Fetcher` to remove "garbage" items (generic "Google News" titles, empty content).
- **Refinement**: **Email Output**. Removed verbose stats, added "Raw Data" section to email body.
- **Fix**: Corrected return values of Collectors to ensure `raw_data` is passed to reports.
- **Config**: Refined "TIPS" keyword to "TIPS Bond" to reduce noise in Commodities group.

## v2.0.0 (2026-01-17) - 7-Layer Architecture Refactoring
**Major architectural overhaul to improve scalability and maintainability.**
- **Refactoring**: Split monolithic scripts into 7 layers (`DataSources`, `Collectors`, `Processors`, `Formatters`, `Core`, `Dispatchers`).
- **New Feature**: **Email Integration**. Automated HTML reports sent via SMTP (MarketRadar port).
- **New Feature**: **Modular CLI**. Run specific collectors via `python main.py --collector=NAME`.
- **Optimization**: Fixed Google RSS Fetcher (Concurrent fetching + Date filtering).
- **Fix**: Resolved OpenBB API initialization errors.
- **Documentation**: Updated `README.md` and `walkthrough.md`.

## v1.5.0 (2026-01-15) - Optimization & Robustness
- **Feature**: Google RSS concurrency (ThreadPoolExecutor).
- **Feature**: Global concurrency for Index/Stock fetchers.
- **Fix**: Added "Safe Mode" to handle `FileNotFoundError` in CI/CD.
- **Config**: Split configuration for English/Chinese semantic models.

## v1.0.0 (2026-01-10) - Initial Release
- **Core**: Basic fetching from YFinance, Akshare, and Google RSS.
- **Processing**: Initial Semantic Deduplication using `sentence-transformers`.
- **CI/CD**: Basic GitHub Actions workflow.
