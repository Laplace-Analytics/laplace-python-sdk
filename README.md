# Laplace Python SDK

[![PyPI version](https://badge.fury.io/py/laplace-python-sdk.svg)](https://badge.fury.io/py/laplace-python-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/laplace-python-sdk.svg)](https://pypi.org/project/laplace-python-sdk/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for the Laplace stock data platform. Get easy access to stock data, collections, financials, funds, and AI-powered insights.

## Features

- 🚀 **Easy to use**: Simple, intuitive API
- 📊 **Comprehensive data**: Stocks, collections, financials, funds, and AI insights
- 🔧 **Well-typed**: Full TypeScript-style typing with Pydantic models
- 🧪 **Well-tested**: Comprehensive test coverage with real API integration
- 🌍 **Multi-region**: Support for US and Turkish markets
- ⚡ **Fast**: Built on httpx for high performance
- 🔌 **Real-time**: WebSocket support for live price data

## Installation

```bash
pip install laplace-python-sdk
```

## Quick Start

```python
from laplace import LaplaceClient

# Initialize the client
client = LaplaceClient(api_key="your-api-key")

# Get stock details
stock = client.stocks.get_detail_by_symbol(symbol="AAPL", region="us")
print(f"{stock.name}: {stock.description}")

# Get all stocks in a region
stocks = client.stocks.get_all(region="us", page=1, page_size=10)
for stock in stocks:
    print(f"{stock.symbol}: {stock.name}")

# Get collections
collections = client.collections.get_collections(region="tr", locale="en")
for collection in collections:
    print(f"{collection.title}: {collection.num_stocks} stocks")

# Get collection details
collection_detail = client.collections.get_collection_detail(
    collection_id="620f455a0187ade00bb0d55f",
    region="tr"
)
print(f"Stocks in {collection_detail.title}:")
for stock in collection_detail.stocks:
    print(f"  {stock.symbol}: {stock.name}")

# Get politicians and their holdings
politicians = client.politicians.get_politicians()
for politician in politicians:
    print(f"{politician.politician_name}: {politician.total_holdings} holdings")

# Get holdings for a specific stock
holdings = client.politicians.get_politician_holdings_by_symbol("AAPL")
for holding in holdings:
    print(f"{holding.politician_name}: {holding.holding} ({holding.allocation})")
```

## API Reference

### Stocks Client

```python
# Get all stocks with pagination
stocks = client.stocks.get_all(region="us", page=1, page_size=10)

# Get stock detail by symbol
stock = client.stocks.get_detail_by_symbol(symbol="AAPL", region="us", asset_class="equity")

# Get stock detail by ID
stock = client.stocks.get_detail_by_id(stock_id="stock-id", locale="en")

# Get historical prices
prices = client.stocks.get_price(region="us", symbols=["AAPL", "GOOGL"], keys=["1D", "1W"])

# Get historical prices with custom interval
from datetime import datetime
from laplace.stocks import HistoricalPriceInterval

prices = client.stocks.get_price_with_interval(
    symbol="AAPL",
    region="us",
    from_date=datetime(2024, 1, 1),
    to_date=datetime(2024, 1, 31),
    interval=HistoricalPriceInterval.ONE_DAY
)

# Get tick rules (Turkey only)
rules = client.stocks.get_tick_rules(region="tr")

# Get restrictions (Turkey only)
restrictions = client.stocks.get_restrictions(region="tr")
```

### Collections Client

```python
# Get all collections
collections = client.collections.get_collections(region="tr", locale="en")

# Get collection detail
detail = client.collections.get_collection_detail(collection_id="id", region="tr")

# Get themes
themes = client.collections.get_themes(region="tr", locale="en")

# Get theme detail
theme_detail = client.collections.get_theme_detail(theme_id="id", region="tr")

# Get industries
industries = client.collections.get_industries(region="tr", locale="en")

# Get industry detail
industry_detail = client.collections.get_industry_detail(industry_id="id", region="tr")

# Get sectors
sectors = client.collections.get_sectors(region="tr", locale="en")

# Get sector detail
sector_detail = client.collections.get_sector_detail(sector_id="id", region="tr")
```

### Politicians Client

```python
# Get all politicians
politicians = client.politicians.get_politicians()

# Get politician detail
politician = client.politicians.get_politician_detail(id=1)

# Get holdings by stock symbol
holdings = client.politicians.get_politician_holdings_by_symbol(symbol="AAPL")

# Get top holdings
top_holdings = client.politicians.get_top_holdings()
```

### News Client

`get_news_v2` returns a `NewsV2Page`: a `PaginatedResponse[NewsV2]` with `next_cursor` and `publisher_cap` added. Multi-value filters take a list or a comma-separated string, and enum values and plain strings can be mixed. Filters you don't set aren't sent.

```python
from laplace.models import NewsEventType, NewsOrderBy, NewsTickerRelevance, Region, SortDirection

# News about one company: drop table-only mentions and market wraps,
# cap any publisher at 25% of the result and show each story once.
page = client.news.get_news_v2(
    locale="tr",
    region=Region.TR,
    symbols=["THYAO"],
    ticker_relevance=[NewsTickerRelevance.PRIMARY, NewsTickerRelevance.MENTIONED],
    exclude_list_articles=True,
    collapse_clusters=True,
    max_publisher_share=25,
    event_types=[NewsEventType.FINANCIAL_RESULTS, NewsEventType.DIVIDEND],
    order_by=[
        (NewsOrderBy.QUALITY_SCORE_V2, SortDirection.DESC),
        (NewsOrderBy.PUBLISHED_AT, SortDirection.DESC),
    ],
    page_size=50,  # any value from 1 to 100
)
for item in page.items:
    print(item.primary_ticker, item.content.title, item.event_type, item.cluster_size)
```

```python
# Cursor paging: iter_news_v2 follows next_cursor until the last page and
# sends include_total=False. It takes the same arguments as get_news_v2,
# except page.
for item in client.news.iter_news_v2(
    "tr", Region.TR, symbols="THYAO", page_size=100, published_from="2026-11-01"
):
    handle(item)
```

```python
from datetime import timedelta

# Incremental sync: upsert by id, then store the largest updated_at minus
# 5 minutes as the next updated_since. quality_score_min=0 makes articles
# whose score is later lowered still arrive as updates.
latest = None
for item in client.news.iter_news_v2(
    "tr",
    Region.TR,
    updated_since=last_sync,  # datetime or RFC3339 string
    quality_score_min=0,
    page_size=100,
):
    store.upsert(item.id, item)
    if item.updated_at and (latest is None or item.updated_at > latest):
        latest = item.updated_at
if latest is not None:
    last_sync = latest - timedelta(minutes=5)
```

`record_count` is `None` when `include_total=False` (and in `iter_news_v2`). `published_at` and `content_updated_at` are `None` when unknown. `timestamp`, `timestamp_from` and `timestamp_to` are deprecated: use `published_at` and `published_from` / `published_to`.

The API rejects unknown values with a `400`, raised as `LaplaceAPIError`. The API's message is in `error.response["message"]`.

```python
# Lookups
event_types = client.news.get_news_event_types(locale="tr")
categories = client.news.get_news_categories(locale="tr")  # ids for category_ids
lanes = client.news.get_news_lanes(region=Region.TR)

# Live news with the same content filters
stream = await client.news.get_news_stream(
    locale="tr",
    region=Region.TR,
    symbols=["THYAO", "GARAN"],
    exclude_list_articles=True,
    event_types=[NewsEventType.FINANCIAL_RESULTS],
)
async for result in stream:
    if result.data:
        for item in result.data:
            print(item.primary_ticker, item.published_at)
```

### WebSocket Client (Live Price Data)

```python
import asyncio
from laplace import LaplaceClient, LivePriceFeed, WebSocketOptions, LogLevel

# Initialize the client
client = LaplaceClient(api_key="your-api-key")

# Create WebSocket options
options = WebSocketOptions(
    enable_logging=True,
    log_level=LogLevel.INFO,
    reconnect_attempts=5,
    reconnect_delay=5000,
    max_reconnect_delay=30000,
)

# Create WebSocket client
websocket_client = client.create_websocket_client(
    feeds=[LivePriceFeed.LIVE_BIST, LivePriceFeed.LIVE_US],
    external_user_id="your-user-id",
    options=options,
)

# Define callback function for price updates
def on_price_update(data):
    print(f"Price update for {data.symbol}: {data.close_price}")
    if hasattr(data, 'percent_change'):
        print(f"  Change: {data.percent_change}%")
    print(f"  Timestamp: {data.timestamp}")

async def main():
    # Connect to WebSocket
    await websocket_client.connect()

    # Subscribe to symbols
    symbols_bist = ["THYAO", "GARAN", "AKBNK"]
    symbols_us = ["AAPL", "GOOGL", "MSFT"]

    # Subscribe to BIST symbols
    unsubscribe_bist = websocket_client.subscribe(
        symbols=symbols_bist,
        feed=LivePriceFeed.LIVE_BIST,
        handler=on_price_update
    )

    # Subscribe to US symbols
    unsubscribe_us = websocket_client.subscribe(
        symbols=symbols_us,
        feed=LivePriceFeed.LIVE_US,
        handler=on_price_update
    )

    # Keep connection alive
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Cleanup
        unsubscribe_bist()
        unsubscribe_us()
        await websocket_client.close()

# Run the WebSocket client
asyncio.run(main())
```

### Available WebSocket Feeds

- `LivePriceFeed.LIVE_BIST`: Live BIST (Turkish) stock prices
- `LivePriceFeed.LIVE_US`: Live US stock prices
- `LivePriceFeed.DELAYED_BIST`: Delayed BIST stock prices
- `LivePriceFeed.DEPTH_TR`: Depth data for TR (commented out, available if needed)

## Supported Regions

- **US**: United States stock market
- **TR**: Turkey stock market (Borsa Istanbul)

## Error Handling

```python
from laplace import LaplaceClient, LaplaceAPIError

client = LaplaceClient(api_key="your-api-key")

try:
    stock = client.stocks.get_detail_by_symbol(symbol="INVALID", region="us")
except LaplaceAPIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Response: {e.response}")
```

## Authentication

Get your API key from the Laplace platform and initialize the client:

```python
client = LaplaceClient(api_key="your-api-key-here")
```

## Development

### Setup

```bash
git clone https://github.com/Laplace-Analytics/laplace-python-sdk.git
cd laplace-python-sdk
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=laplace

# Run integration tests (requires API key)
LAPLACE_API_KEY=your-key pytest -m integration
```

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0
- websocket-client >= 1.8.0

## Documentation

Full API documentation is available at [laplace.finfree.co/en/docs](https://laplace.finfree.co/en/docs)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
