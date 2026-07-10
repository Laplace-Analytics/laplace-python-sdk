"""Pydantic models for Laplace API responses."""

from enum import Enum
from typing import Dict, List, Optional, Generic, TypeVar

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

T = TypeVar("T")


class CapitalIncreaseType(str, Enum):
    """Capital increase type options."""

    RIGHTS = "rights"
    BONUS = "bonus"
    BONUS_DIVIDEND = "bonus_dividend"
    EXTERNAL = "external"


class PaginationPageSize(int, Enum):
    """Pagination page size options."""

    PAGE_SIZE_5 = 5
    PAGE_SIZE_10 = 10
    PAGE_SIZE_20 = 20
    PAGE_SIZE_50 = 50


class SearchType(str, Enum):
    """Search type options."""

    STOCK = "stock"
    COLLECTION = "collection"
    SECTOR = "sector"
    INDUSTRY = "industry"


class AssetType(str, Enum):
    """Asset type options."""

    STOCK = "stock"
    FOREX = "forex"
    INDEX = "index"
    ETF = "etf"
    COMMODITY = "commodity"
    STOCK_RIGHTS = "stock_rights"
    FUND = "fund"
    ADR = "adr"


class AssetClass(str, Enum):
    """Asset class options."""

    EQUITY = "equity"
    CRYPTO = "crypto"


class Region(str, Enum):
    """Region options."""

    TR = "tr"
    US = "us"


Locale = Literal[
    "tr",
    "en",
]

class CollectionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Stock(BaseModel):
    """Stock model from the stocks API."""

    id: str
    name: str
    active: bool
    symbol: str
    sector_id: str = Field(alias="sectorId")
    asset_type: AssetType = Field(alias="assetType")
    industry_id: str = Field(alias="industryId")
    updated_date: datetime = Field(alias="updatedDate")

    model_config = {"populate_by_name": True}


class StockDetail(BaseModel):
    """Detailed stock information from stock detail API."""

    id: str
    name: str
    active: bool
    region: Region
    symbol: str
    sector_id: str = Field(alias="sectorId")
    asset_type: AssetType = Field(alias="assetType")
    asset_class: AssetClass = Field(alias="assetClass")
    industry_id: str = Field(alias="industryId")
    description: str
    updated_date: datetime = Field(alias="updatedDate")
    short_description: str = Field(alias="shortDescription")
    localized_description: Dict[str, str] = Field(alias="localized_description")
    localized_short_description: Dict[str, str] = Field(alias="localizedShortDescription")
    markets: Optional[List[str]] = None

    model_config = {"populate_by_name": True}


class PriceCandle(BaseModel):
    """Individual price candle data."""

    close: float = Field(alias="c")
    date: int = Field(alias="d")
    high: float = Field(alias="h")
    low: float = Field(alias="l")
    open: float = Field(alias="o")

    unadjusted_open: Optional[float] = Field(default=None, alias="uo")
    unadjusted_high: Optional[float] = Field(default=None, alias="uh")
    unadjusted_low: Optional[float] = Field(default=None, alias="ul")
    unadjusted_close: Optional[float] = Field(default=None, alias="uc")

    volume: Optional[float] = Field(default=None, alias="v")
    unadjusted_volume: Optional[float] = Field(default=None, alias="uv")


class StockPriceData(BaseModel):
    """Stock price data with different time intervals."""

    symbol: str
    one_day: List[PriceCandle] = Field(default_factory=list, alias="1D")
    one_week: List[PriceCandle] = Field(default_factory=list, alias="1W")
    one_month: List[PriceCandle] = Field(default_factory=list, alias="1M")
    three_months: List[PriceCandle] = Field(default_factory=list, alias="3M")
    one_year: List[PriceCandle] = Field(default_factory=list, alias="1Y")
    two_years: List[PriceCandle] = Field(default_factory=list, alias="2Y")
    three_years: List[PriceCandle] = Field(default_factory=list, alias="3Y")
    five_years: List[PriceCandle] = Field(default_factory=list, alias="5Y")

    model_config = {"populate_by_name": True}


class TickRule(BaseModel):
    """Tick rule for stock pricing."""

    price_from: float = Field(alias="priceFrom")
    price_to: float = Field(alias="priceTo")
    tick_size: float = Field(alias="tickSize")

    model_config = {"populate_by_name": True}


class StockRules(BaseModel):
    """Stock tick rules and price limits."""

    rules: List[TickRule]
    base_price: float = Field(alias="basePrice")
    additional_price: int = Field(alias="additionalPrice")
    lower_price_limit: float = Field(alias="lowerPriceLimit")
    upper_price_limit: float = Field(alias="upperPriceLimit")

    model_config = {"populate_by_name": True}


class StockRestriction(BaseModel):
    """Stock restriction information."""

    id: int
    title: str
    symbol: Optional[str] = None
    market: Optional[str] = None
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    description: str

    model_config = {"populate_by_name": True}


class CollectionStock(BaseModel):
    id: str
    asset_type: str = Field(alias="assetType")
    name: str
    symbol: str
    sector_id: str = Field(alias="sectorId")
    industry_id: str = Field(alias="industryId")
    updated_date: datetime = Field(alias="updatedDate")
    daily_change: Optional[float] = Field(alias="dailyChange", default=None)
    active: bool

    model_config = {"populate_by_name": True}


class Collection(BaseModel):
    id: str
    title: str
    region: Optional[List[str]] = None
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")
    asset_class: Optional[str] = Field(alias="assetClass", default=None)

    # Custom theme fields
    description: Optional[str] = None
    image: Optional[str] = None
    order: Optional[int] = None
    status: Optional[str] = None
    meta_data: Optional[dict] = Field(alias="metaData", default=None)

    model_config = {"populate_by_name": True}


class CollectionDetail(Collection):
    """Detailed collection information."""

    stocks: List[CollectionStock]

    model_config = {"populate_by_name": True}

class RatioComparisonPeerType(str, Enum):
    """Peer type for ratio comparison."""

    INDUSTRY = "industry"
    SECTOR = "sector"


class HistoricalRatiosFormat(str, Enum):
    """Format for historical ratios."""

    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    DECIMAL = "decimal"


class FinancialSheetType(str, Enum):
    """Type of financial sheet."""

    INCOME_STATEMENT = "incomeStatement"
    BALANCE_SHEET = "balanceSheet"
    CASH_FLOW = "cashFlowStatement"


class FinancialSheetPeriod(str, Enum):
    """Period type for financial sheets."""

    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    CUMULATIVE = "cumulative"


class Currency(str, Enum):
    """Currency code."""

    USD = "USD"
    TRY = "TRY"
    EUR = "EUR"


class StockPeerFinancialRatioComparisonData(BaseModel):
    """Peer financial ratio comparison data."""

    slug: str
    value: float
    average: float

    model_config = {"populate_by_name": True}


class StockPeerFinancialRatioComparison(BaseModel):
    """Stock peer financial ratio comparison."""

    metric_name: str = Field(alias="metricName")
    normalized_value: float = Field(alias="normalizedValue")
    data: List[StockPeerFinancialRatioComparisonData]

    model_config = {"populate_by_name": True}


class StockHistoricalRatiosData(BaseModel):
    """Stock historical ratios data."""

    period: str
    value: float
    sector_mean: float = Field(alias="sectorMean")

    model_config = {"populate_by_name": True}


class StockHistoricalRatios(BaseModel):
    """Stock historical ratios."""

    slug: str
    final_value: float = Field(alias="finalValue")
    three_year_growth: float = Field(alias="threeYearGrowth")
    year_growth: float = Field(alias="yearGrowth")
    final_sector_value: float = Field(alias="finalSectorValue")
    currency: Currency
    format: HistoricalRatiosFormat
    name: str
    items: List[StockHistoricalRatiosData]

    model_config = {"populate_by_name": True}


class StockHistoricalRatiosDescription(BaseModel):
    """Stock historical ratios description."""

    id: int
    format: str
    currency: Currency
    slug: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    name: str
    description: str
    locale: Locale
    is_realtime: bool = Field(alias="isRealtime")

    model_config = {"populate_by_name": True}


class HistoricalFinancialSheetRow(BaseModel):
    """Historical financial sheet row."""

    description: str
    value: float
    line_code_id: int = Field(alias="lineCodeId")
    indent_level: int = Field(alias="indentLevel")

    model_config = {"populate_by_name": True}


class HistoricalFinancialSheet(BaseModel):
    """Historical financial sheet."""

    period: str
    items: List[HistoricalFinancialSheetRow]

    model_config = {"populate_by_name": True}


class HistoricalFinancialSheets(BaseModel):
    """Historical financial sheets."""

    sheets: List[HistoricalFinancialSheet]

    model_config = {"populate_by_name": True}


class FinancialSheetDate(BaseModel):
    """Financial sheet date."""

    day: int
    month: int
    year: int

    model_config = {"populate_by_name": True}


class MessageType(str, Enum):
    """Message type."""

    PRICE = "pr"
    STATE_CHANGE = "state_change"
    HEARTBEAT = "heartbeat"
    ORDERBOOK = "ob"


class LiveMessageV2(BaseModel, Generic[T]):
    """Live price message model."""

    data: T
    symbol: str
    type: MessageType


class BISTStockLiveData(BaseModel):
    """BIST (Turkish) stock live data model."""

    symbol: str = Field(alias="s")
    daily_percent_change: float = Field(alias="ch")
    close_price: float = Field(alias="p")
    date: int = Field(alias="d")

    model_config = {"populate_by_name": True}


class USStockLiveData(BaseModel):
    """US stock live data model."""

    symbol: str = Field(alias="s")
    price: float = Field(alias="p")
    percent_change: float = Field(alias="pc")
    amount_change: float = Field(alias="ac")
    date: int = Field(alias="d")

    model_config = {"populate_by_name": True}


class LevelSide(str, Enum):
    """Level side."""

    BID = "bid"
    ASK = "ask"


class OrderbookLevel(BaseModel):
    """Orderbook level."""

    id: int = Field(alias="level")
    side: LevelSide = Field(alias="side")
    price: float = Field(alias="price")
    size: float = Field(alias="size")


class OrderbookDeletedLevel(BaseModel):
    """Orderbook deleted level."""

    id: int = Field(alias="level")
    side: LevelSide = Field(alias="side")


class BISTStockOrderBookData(BaseModel):
    """BIST stock order book data."""

    updated: List[OrderbookLevel] = Field(alias="updated")
    deleted: List[OrderbookDeletedLevel] = Field(alias="deleted")
    symbol: str = Field(alias="s")


class BISTBidAskData(BaseModel):
    """BIST (Turkish) stock bid/ask live data model."""

    symbol: str = Field(alias="s")
    date: int = Field(alias="d")
    ask: float
    bid: float

class Politician(BaseModel):
    """Politician information."""

    id: int
    politician_name: str = Field(alias="politicianName")
    total_holdings: int = Field(alias="totalHoldings")
    last_updated: datetime = Field(alias="lastUpdated")

    model_config = {"populate_by_name": True}


class Holding(BaseModel):
    """Holding information for a specific politician."""

    politician_name: str = Field(alias="politicianName")
    symbol: str
    company: str
    holding: str
    allocation: str
    last_updated: datetime = Field(alias="lastUpdated")


class HoldingShort(BaseModel):
    """Short holding information for a specific politician."""

    symbol: str
    company: str
    holding: str
    allocation: str

    model_config = {"populate_by_name": True}


class TopHoldingPolitician(BaseModel):
    """Top holding politician information."""

    name: str
    holding: str
    allocation: str

    model_config = {"populate_by_name": True}


class TopHolding(BaseModel):
    """Top holding information."""

    symbol: str
    company: str
    politicians: List[TopHoldingPolitician]
    count: int

    model_config = {"populate_by_name": True}


class PoliticianDetail(BaseModel):
    """Complete information for a specific politician."""

    id: int
    name: str
    holdings: List[HoldingShort]
    total_holdings: int = Field(alias="totalHoldings")
    last_updated: datetime = Field(alias="lastUpdated")

    model_config = {"populate_by_name": True}


class TopMover(BaseModel):
    """Top mover stock model."""

    change: float
    symbol: str
    asset_type: Optional[AssetType] = Field(alias="assetType", default=None)
    asset_class: Optional[AssetClass] = Field(alias="assetClass", default=None)

    model_config = {"populate_by_name": True}


class Dividend(BaseModel):
    """Stock dividend model."""

    date: datetime
    currency: Currency
    net_ratio: float = Field(alias="netRatio")
    net_amount: float = Field(alias="netAmount")
    price_then: float = Field(alias="priceThen")
    gross_ratio: float = Field(alias="grossRatio")
    gross_amount: float = Field(alias="grossAmount")
    stoppage_ratio: float = Field(alias="stoppageRatio")
    stoppage_amount: float = Field(alias="stoppageAmount")

    model_config = {"populate_by_name": True}


class StockStats(BaseModel):
    """Stock statistics model."""

    eps: Optional[float] = None
    day_low: float = Field(alias="dayLow")
    symbol: str
    day_high: float = Field(alias="dayHigh")
    day_open: float = Field(alias="dayOpen")
    pb_ratio: float = Field(alias="pbRatio")
    pe_ratio: float = Field(alias="peRatio")
    year_low: float = Field(alias="yearLow")
    year_high: float = Field(alias="yearHigh")
    market_cap: float = Field(alias="marketCap")
    ytd_return: float = Field(alias="ytdReturn")
    three_year_return: float = Field(alias="3YearReturn")
    five_year_return: float = Field(alias="5YearReturn")
    daily_change: float = Field(alias="dailyChange")
    latest_price: float = Field(alias="latestPrice")
    three_month_return: float = Field(alias="3MonthReturn")
    weekly_return: float = Field(alias="weeklyReturn")
    yearly_return: float = Field(alias="yearlyReturn")
    monthly_return: float = Field(alias="monthlyReturn")
    previous_close: float = Field(alias="previousClose")
    lower_price_limit: Optional[float] = Field(alias="lowerPriceLimit", default=None)
    upper_price_limit: Optional[float] = Field(alias="upperPriceLimit", default=None)

    model_config = {"populate_by_name": True}


class AggregateGraphData(BaseModel):
    """Aggregate graph data model."""

    graph: List[PriceCandle]
    previous_close: float = Field(alias="previous_close")

    model_config = {"populate_by_name": True}


class KeyInsight(BaseModel):
    """Key insight model."""

    symbol: str
    insight: str

    model_config = {"populate_by_name": True}


class FundStats(BaseModel):
    """Fund statistics model."""

    year_beta: float = Field(alias="yearBeta")
    year_stdev: float = Field(alias="yearStdev")
    ytd_return: float = Field(alias="ytdReturn")
    year_momentum: float = Field(alias="yearMomentum")
    yearly_return: float = Field(alias="yearlyReturn")
    monthly_return: float = Field(alias="monthlyReturn")
    five_year_return: float = Field(alias="fiveYearReturn")
    six_month_return: float = Field(alias="sixMonthReturn")
    three_year_return: float = Field(alias="threeYearReturn")
    three_month_return: float = Field(alias="threeMonthReturn")

    model_config = {"populate_by_name": True}


class FundPriceData(BaseModel):
    """Fund price data model."""

    aum: float
    date: datetime
    price: float
    share_count: float = Field(alias="shareCount")
    investor_count: int = Field(alias="investorCount")

    model_config = {"populate_by_name": True}


class FundAsset(BaseModel):
    """Fund asset model."""

    type: str
    symbol: str
    whole_percentage: float = Field(alias="wholePercentage")
    category_percentage: float = Field(alias="categoryPercentage")

    model_config = {"populate_by_name": True}


class FundCategory(BaseModel):
    """Fund category model."""

    category: str
    percentage: float
    assets: Optional[List[FundAsset]] = None

    model_config = {"populate_by_name": True}


class Fund(BaseModel):
    """Fund model."""

    name: str
    active: bool
    symbol: str
    fund_type: str = Field(alias="fundType")
    asset_type: AssetType = Field(alias="assetType")
    risk_level: int = Field(alias="riskLevel")
    owner_symbol: str = Field(alias="ownerSymbol")
    management_fee: float = Field(alias="managementFee")

    model_config = {"populate_by_name": True}


class FundDistribution(BaseModel):
    """Fund distribution model."""

    categories: List[FundCategory]

    model_config = {"populate_by_name": True}


class Broker(BaseModel):
    """Broker information model."""

    id: int
    logo: str
    name: str
    symbol: str
    long_name: str = Field(alias="longName")
    supported_asset_classes: Optional[List[AssetClass]] =  Field(alias="supportedAssetClasses", default=None)

    model_config = {"populate_by_name": True}

class BrokerStock(BaseModel):
    id: str
    symbol: str
    name: str
    asset_type: str = Field(alias="assetType")
    asset_class: str = Field(alias="assetClass")
    logo_url: Optional[str] = Field(alias="logoUrl", default=None)
    exchange: Optional[str] = Field(alias="exchange", default=None)

    model_config = {"populate_by_name": True}

class BrokerStats(BaseModel):
    total_buy_amount: float = Field(alias="totalBuyAmount")
    total_sell_amount: float = Field(alias="totalSellAmount")
    net_amount: float = Field(alias="netAmount")
    total_buy_volume: float = Field(alias="totalBuyVolume")
    total_sell_volume: float = Field(alias="totalSellVolume")
    total_volume: float = Field(alias="totalVolume")
    total_amount: float = Field(alias="totalAmount")
    average_cost: Optional[float] = Field(alias="averageCost", default=None)

    model_config = {"populate_by_name": True}

class BrokerItem(BrokerStats):
    broker: Optional[Broker] = None
    stock: Optional[BrokerStock] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    record_count: int = Field(alias="recordCount")
    items: List[T]

    model_config = {"populate_by_name": True}

class BrokerList(PaginatedResponse[BrokerItem]):
    total_stats: BrokerStats = Field(alias="totalStats")

    model_config = {"populate_by_name": True}

class BrokerSort(str, Enum):
    """Broker sort options."""

    NET_AMOUNT = "netAmount"
    TOTAL_AMOUNT = "totalAmount"
    TOTAL_VOLUME = "totalVolume"
    TOTAL_BUY_AMOUNT = "totalBuyAmount"
    TOTAL_BUY_VOLUME = "totalBuyVolume"
    TOTAL_SELL_AMOUNT = "totalSellAmount"
    TOTAL_SELL_VOLUME = "totalSellVolume"


class SortDirection(str, Enum):
    """Broker sort direction options."""

    DESC = "desc"
    ASC = "asc"


class CapitalIncrease(BaseModel):
    """Capital increase model."""

    id: int
    types: List[CapitalIncreaseType] = Field(default_factory=list, alias="types")
    symbol: str
    bonus_rate: str = Field(alias="bonusRate")
    rights_rate: str = Field(alias="rightsRate")
    payment_date: Optional[datetime] = Field(alias="paymentDate", default=None)
    rights_price: str = Field(alias="rightsPrice")
    rights_end_date: Optional[datetime] = Field(alias="rightsEndDate", default=None)
    target_capital: str = Field(alias="targetCapital")
    bonus_start_date: Optional[datetime] = Field(alias="bonusStartDate", default=None)
    current_capital: str = Field(alias="currentCapital")
    rights_start_date: Optional[datetime] = Field(alias="rightsStartDate", default=None)
    spk_approval_date: Optional[datetime] = Field(alias="spkApprovalDate", default=None)
    bonus_total_amount: str = Field(alias="bonusTotalAmount")
    registration_date: Optional[datetime] = Field(alias="registrationDate", default=None)
    board_decision_date: Optional[datetime] = Field(alias="boardDecisionDate", default=None)
    bonus_dividend_rate: str = Field(alias="bonusDividendRate")
    rights_total_amount: str = Field(alias="rightsTotalAmount")
    specified_currency: str = Field(alias="specifiedCurrency")
    rights_last_sell_date: Optional[datetime] = Field(alias="rightsLastSellDate", default=None)
    spk_application_date: Optional[datetime] = Field(alias="spkApplicationDate", default=None)
    related_disclosure_ids: List[int] = Field(alias="relatedDisclosureIds")
    spk_application_result: Optional[str] = Field(alias="spkApplicationResult", default=None)
    bonus_dividend_total_amount: str = Field(alias="bonusDividendTotalAmount")
    registered_capital_ceiling: str = Field(alias="registeredCapitalCeiling")
    external_capital_increase_rate: str = Field(alias="externalCapitalIncreaseRate")
    external_capital_increase_amount: str = Field(alias="externalCapitalIncreaseAmount")

    model_config = {"populate_by_name": True}


class SearchResultStock(BaseModel):
    """Search result stock model."""

    id: str
    name: str
    title: str
    region: Region
    asset_type: AssetType = Field(alias="assetType")
    type: Optional[str] = None

    model_config = {"populate_by_name": True}


class SearchResultCollection(BaseModel):
    """Search result collection model."""

    id: str
    title: str
    region: List[Region]
    asset_class: Optional[str] = Field(
        alias="assetClass", default=None
    )  # Can be empty string or AssetClass value
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")

    model_config = {"populate_by_name": True}


class EarningsTranscriptListItem(BaseModel):
    """Earnings transcript list item model."""

    symbol: str
    year: int
    quarter: int
    fiscal_year: int

    model_config = {"populate_by_name": True}


class EarningsTranscriptWithSummary(BaseModel):
    """Earnings transcript with summary model."""

    symbol: str
    year: int
    quarter: int
    content: str
    summary: Optional[str] = None
    has_summary: bool

    model_config = {"populate_by_name": True}


class MarketState(BaseModel):
    """Market state model."""

    id: int
    market_symbol: Optional[str] = Field(alias="marketSymbol", default=None)
    state: str
    last_timestamp: datetime = Field(alias="lastTimestamp")
    stock_symbol: Optional[str] = Field(alias="stockSymbol", default=None)

    model_config = {"populate_by_name": True}


class SearchData(BaseModel):
    """Search data model."""

    stocks: List[SearchResultStock]
    collections: List[SearchResultCollection]
    sectors: List[SearchResultCollection]
    industries: List[SearchResultCollection]

    model_config = {"populate_by_name": True}

class NewsType(str, Enum):
    """News type options."""

    BRIEFS = "briefs"
    BLOOMBERG = "bloomberg"
    FDA = "fda"
    REUTERS = "reuters"

class NewsOrderBy(str, Enum):
    """News order by options."""

    TIMESTAMP = "timestamp"
    QUALITY_SCORE = "quality_score"


class NewsLane(str, Enum):
    """News lane options for the filter-news and stream-news endpoints.

    Lanes are surface-scoped: ``GLOBAL_MACRO`` and ``FAST_MOVERS`` belong to the
    ``us`` region, while ``TR_EKONOMI`` and ``BIST`` belong to the ``tr`` region.
    """

    GLOBAL_MACRO = "global_macro"
    TR_EKONOMI = "tr_ekonomi"
    BIST = "bist"
    FAST_MOVERS = "fast_movers"


class NewsTicker(BaseModel):
    id: str
    name: str
    symbol: Optional[str] = None

    model_config = {"populate_by_name": True}

class NewsPublisher(BaseModel):
    name: str
    logo_url: Optional[str] = Field(alias="logoUrl")

    model_config = {"populate_by_name": True}

class NewsIndustry(BaseModel):
    id: str
    name: str

    model_config = {"populate_by_name": True}

class NewsSector(BaseModel):
    id: str
    name: str

    model_config = {"populate_by_name": True}

class NewsCategory(BaseModel):
    id: str
    name: str
    category_type: Optional[str] = Field(alias="categoryType", default=None)

    model_config = {"populate_by_name": True}

class NewsCategoryListItem(BaseModel):
    """A canonical news category as returned by /api/v1/news/categories.

    The numeric ``id`` is the exact value accepted by the ``categoryIds``
    filter of the filter-news and stream-news endpoints; ``name`` is the
    display name for dropdowns.
    """

    id: str
    name: str

    model_config = {"populate_by_name": True}


class NewsLaneListItem(BaseModel):
    """A news lane as returned by /api/v1/news/lanes.

    The ``id`` is the exact value accepted by the ``lane`` filter of the
    filter-news and stream-news endpoints (see :class:`NewsLane`).
    """

    id: str
    label: str

    model_config = {"populate_by_name": True}


class NewsApiSourceListItem(BaseModel):
    """A configured news source as returned by /api/v1/news/api-source-names.

    The ``id`` is the exact value accepted by the ``apiSource`` filter of the
    filter-news and stream-news endpoints (comma-separated for multiple);
    ``name`` is the display name (e.g. "BBC Business").
    """

    id: str
    name: str

    model_config = {"populate_by_name": True}

class NewsContent(BaseModel):
    title: str
    description: str
    content: List[str]
    summary: List[str]
    investor_insight: str = Field(alias="investorInsight")

    model_config = {"populate_by_name": True}

class News(BaseModel):
    id: str
    created_at: datetime = Field(alias="createdAt")
    url: str
    image_url: str = Field(alias="imageUrl")
    timestamp: datetime
    publisher_url: str = Field(alias="publisherUrl")

    publisher: NewsPublisher
    related_tickers: Optional[List[NewsTicker]] = Field(alias="relatedTickers", default=None)

    tickers: Optional[List[NewsTicker]] = None
    categories: Optional[NewsCategory] = None
    sectors: Optional[NewsSector] = None
    content: Optional[NewsContent] = None
    industries: Optional[NewsIndustry] = None

    quality_score: int = Field(alias="qualityScore")

    model_config = {"populate_by_name": True}

class NewsV2(BaseModel):
    id: str
    created_at: datetime = Field(alias="createdAt")
    url: str
    image_url: str = Field(alias="imageUrl")
    timestamp: datetime
    publisher_url: str = Field(alias="publisherUrl")

    publisher: NewsPublisher

    tickers: Optional[List[NewsTicker]] = None
    categories: Optional[NewsCategory] = None
    sectors: Optional[NewsSector] = None
    content: Optional[NewsContent] = None
    industries: Optional[NewsIndustry] = None

    quality_score: int = Field(alias="qualityScore")

    model_config = {"populate_by_name": True}
class NewsHighlight(BaseModel):
    """A daily categorized news highlight as returned by /api/v1/news/highlights."""

    id: str
    created_at: datetime = Field(alias="createdAt")
    consumer: List[str]
    energy_and_utilities: List[str] = Field(alias="energyAndUtilities")
    finance: List[str]
    healthcare: List[str]
    industrials_and_materials: List[str] = Field(alias="industrialsAndMaterials")
    tech: List[str]
    other: List[str]

    model_config = {"populate_by_name": True}

class ScreenerLetterGrade(str, Enum):
    """Letter grades (A-E) used by the SMR and A/D ratings."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class ScreenerRangeFilter(BaseModel):
    """Min/max numeric range filter for the screener.

    Both bounds are optional and inclusive. If both are set, ``min`` must be
    <= ``max`` (otherwise the API returns 400). Rows whose value is NULL in the
    filtered column are excluded by any range filter touching it.
    """

    min: Optional[float] = None
    max: Optional[float] = None


class ScreenerFilters(BaseModel):
    """Filters accepted by the screener endpoint.

    Three filter types are supported:

    - Range filters: an optional ``{min, max}`` pair per field.
    - Letter-grade list filters: ``smr_rating`` and ``ad_rating`` accept a list
      of grades ``A``-``E`` (IN match).
    - Boolean filter: ``eps_acceleration`` accepts ``True``/``False``.
    """

    # Range filters
    price: Optional[ScreenerRangeFilter] = None
    daily_change: Optional[ScreenerRangeFilter] = Field(default=None, alias="dailyChange")
    pe_ratio: Optional[ScreenerRangeFilter] = Field(default=None, alias="peRatio")
    pb_ratio: Optional[ScreenerRangeFilter] = Field(default=None, alias="pbRatio")
    market_cap: Optional[ScreenerRangeFilter] = Field(default=None, alias="marketCap")
    weekly_return: Optional[ScreenerRangeFilter] = Field(default=None, alias="weeklyReturn")
    monthly_return: Optional[ScreenerRangeFilter] = Field(default=None, alias="monthlyReturn")
    three_month_return: Optional[ScreenerRangeFilter] = Field(default=None, alias="threeMonthReturn")
    yearly_return: Optional[ScreenerRangeFilter] = Field(default=None, alias="yearlyReturn")
    three_year_return: Optional[ScreenerRangeFilter] = Field(default=None, alias="threeYearReturn")
    five_year_return: Optional[ScreenerRangeFilter] = Field(default=None, alias="fiveYearReturn")
    ytd_return: Optional[ScreenerRangeFilter] = Field(default=None, alias="ytdReturn")
    composite_rating: Optional[ScreenerRangeFilter] = Field(default=None, alias="compositeRating")
    composite_score: Optional[ScreenerRangeFilter] = Field(default=None, alias="compositeScore")
    rs_rating: Optional[ScreenerRangeFilter] = Field(default=None, alias="rsRating")
    rs_score: Optional[ScreenerRangeFilter] = Field(default=None, alias="rsScore")
    perf_q1: Optional[ScreenerRangeFilter] = Field(default=None, alias="perfQ1")
    perf_q2: Optional[ScreenerRangeFilter] = Field(default=None, alias="perfQ2")
    perf_q3: Optional[ScreenerRangeFilter] = Field(default=None, alias="perfQ3")
    perf_q4: Optional[ScreenerRangeFilter] = Field(default=None, alias="perfQ4")
    eps_rating: Optional[ScreenerRangeFilter] = Field(default=None, alias="epsRating")
    eps_score: Optional[ScreenerRangeFilter] = Field(default=None, alias="epsScore")
    eps_growth_yoy: Optional[ScreenerRangeFilter] = Field(default=None, alias="epsGrowthYoy")
    eps_growth_qoq: Optional[ScreenerRangeFilter] = Field(default=None, alias="epsGrowthQoq")
    eps_trailing_4q: Optional[ScreenerRangeFilter] = Field(default=None, alias="epsTrailing4q")
    ad_score: Optional[ScreenerRangeFilter] = Field(default=None, alias="adScore")
    up_volume_ratio: Optional[ScreenerRangeFilter] = Field(default=None, alias="upVolumeRatio")
    volume_trend: Optional[ScreenerRangeFilter] = Field(default=None, alias="volumeTrend")
    smr_score: Optional[ScreenerRangeFilter] = Field(default=None, alias="smrScore")
    sales_growth_2q: Optional[ScreenerRangeFilter] = Field(default=None, alias="salesGrowth2q")
    gross_margin: Optional[ScreenerRangeFilter] = Field(default=None, alias="grossMargin")
    net_margin: Optional[ScreenerRangeFilter] = Field(default=None, alias="netMargin")
    roe: Optional[ScreenerRangeFilter] = None
    sma20: Optional[ScreenerRangeFilter] = None
    sma50: Optional[ScreenerRangeFilter] = None
    sma150: Optional[ScreenerRangeFilter] = None
    sma200: Optional[ScreenerRangeFilter] = None
    volume_sma50: Optional[ScreenerRangeFilter] = Field(default=None, alias="volumeSma50")
    price_vs_sma20: Optional[ScreenerRangeFilter] = Field(default=None, alias="priceVsSma20")
    price_vs_sma50: Optional[ScreenerRangeFilter] = Field(default=None, alias="priceVsSma50")
    price_vs_sma150: Optional[ScreenerRangeFilter] = Field(default=None, alias="priceVsSma150")
    price_vs_sma200: Optional[ScreenerRangeFilter] = Field(default=None, alias="priceVsSma200")
    high_52w: Optional[ScreenerRangeFilter] = Field(default=None, alias="high52w")
    low_52w: Optional[ScreenerRangeFilter] = Field(default=None, alias="low52w")
    off_high_pct: Optional[ScreenerRangeFilter] = Field(default=None, alias="offHighPct")
    volume_vs_avg50: Optional[ScreenerRangeFilter] = Field(default=None, alias="volumeVsAvg50")
    price_change_pct: Optional[ScreenerRangeFilter] = Field(default=None, alias="priceChangePct")
    price_change_amount: Optional[ScreenerRangeFilter] = Field(
        default=None, alias="priceChangeAmount"
    )
    ytd_change_pct: Optional[ScreenerRangeFilter] = Field(default=None, alias="ytdChangePct")

    # Letter-grade list filters
    smr_rating: Optional[List[ScreenerLetterGrade]] = Field(default=None, alias="smrRating")
    ad_rating: Optional[List[ScreenerLetterGrade]] = Field(default=None, alias="adRating")

    # Boolean filter
    eps_acceleration: Optional[bool] = Field(default=None, alias="epsAcceleration")

    model_config = {"populate_by_name": True}


class ScreenerSortBy(str, Enum):
    """Sort fields supported by the screener endpoint."""

    SYMBOL = "symbol"
    PRICE = "price"
    DAILY_CHANGE = "dailyChange"
    MARKET_CAP = "marketCap"
    PE_RATIO = "peRatio"
    PB_RATIO = "pbRatio"
    WEEKLY_RETURN = "weeklyReturn"
    MONTHLY_RETURN = "monthlyReturn"
    THREE_MONTH_RETURN = "threeMonthReturn"
    YEARLY_RETURN = "yearlyReturn"
    THREE_YEAR_RETURN = "threeYearReturn"
    FIVE_YEAR_RETURN = "fiveYearReturn"
    YTD_RETURN = "ytdReturn"
    COMPOSITE_RATING = "compositeRating"
    COMPOSITE_SCORE = "compositeScore"
    RS_RATING = "rsRating"
    RS_SCORE = "rsScore"
    PERF_Q1 = "perfQ1"
    PERF_Q2 = "perfQ2"
    PERF_Q3 = "perfQ3"
    PERF_Q4 = "perfQ4"
    EPS_RATING = "epsRating"
    EPS_SCORE = "epsScore"
    EPS_GROWTH_YOY = "epsGrowthYoy"
    EPS_GROWTH_QOQ = "epsGrowthQoq"
    EPS_TRAILING_4Q = "epsTrailing4q"
    EPS_ACCELERATION = "epsAcceleration"
    AD_RATING = "adRating"
    AD_SCORE = "adScore"
    UP_VOLUME_RATIO = "upVolumeRatio"
    VOLUME_TREND = "volumeTrend"
    SMR_RATING = "smrRating"
    SMR_SCORE = "smrScore"
    SALES_GROWTH_2Q = "salesGrowth2q"
    GROSS_MARGIN = "grossMargin"
    NET_MARGIN = "netMargin"
    ROE = "roe"
    SMA20 = "sma20"
    SMA50 = "sma50"
    SMA150 = "sma150"
    SMA200 = "sma200"
    VOLUME_SMA50 = "volumeSma50"
    PRICE_VS_SMA20 = "priceVsSma20"
    PRICE_VS_SMA50 = "priceVsSma50"
    PRICE_VS_SMA150 = "priceVsSma150"
    PRICE_VS_SMA200 = "priceVsSma200"
    HIGH_52W = "high52w"
    LOW_52W = "low52w"
    OFF_HIGH_PCT = "offHighPct"
    VOLUME_VS_AVG50 = "volumeVsAvg50"
    PRICE_CHANGE_PCT = "priceChangePct"
    PRICE_CHANGE_AMOUNT = "priceChangeAmount"
    YTD_CHANGE_PCT = "ytdChangePct"


class ScreenerStock(BaseModel):
    """A single stock entry returned by the screener endpoint.

    Decimal fields return 0 when there is no data. Rating integers
    (``composite_rating``, ``rs_rating``, ``eps_rating``), letter grades
    (``ad_rating``, ``smr_rating``) and ``eps_acceleration`` may be ``None``
    when absent.
    """

    symbol: str
    price: Optional[float] = None
    daily_change: Optional[float] = Field(default=None, alias="dailyChange")
    market_cap: Optional[float] = Field(default=None, alias="marketCap")
    pe_ratio: Optional[float] = Field(default=None, alias="peRatio")
    pb_ratio: Optional[float] = Field(default=None, alias="pbRatio")
    weekly_return: Optional[float] = Field(default=None, alias="weeklyReturn")
    monthly_return: Optional[float] = Field(default=None, alias="monthlyReturn")
    three_month_return: Optional[float] = Field(default=None, alias="threeMonthReturn")
    yearly_return: Optional[float] = Field(default=None, alias="yearlyReturn")
    three_year_return: Optional[float] = Field(default=None, alias="threeYearReturn")
    five_year_return: Optional[float] = Field(default=None, alias="fiveYearReturn")
    ytd_return: Optional[float] = Field(default=None, alias="ytdReturn")
    composite_rating: Optional[int] = Field(default=None, alias="compositeRating")
    composite_score: Optional[float] = Field(default=None, alias="compositeScore")
    rs_rating: Optional[int] = Field(default=None, alias="rsRating")
    rs_score: Optional[float] = Field(default=None, alias="rsScore")
    perf_q1: Optional[float] = Field(default=None, alias="perfQ1")
    perf_q2: Optional[float] = Field(default=None, alias="perfQ2")
    perf_q3: Optional[float] = Field(default=None, alias="perfQ3")
    perf_q4: Optional[float] = Field(default=None, alias="perfQ4")
    eps_rating: Optional[int] = Field(default=None, alias="epsRating")
    eps_score: Optional[float] = Field(default=None, alias="epsScore")
    eps_growth_yoy: Optional[float] = Field(default=None, alias="epsGrowthYoy")
    eps_growth_qoq: Optional[float] = Field(default=None, alias="epsGrowthQoq")
    eps_trailing_4q: Optional[float] = Field(default=None, alias="epsTrailing4q")
    eps_acceleration: Optional[bool] = Field(default=None, alias="epsAcceleration")
    ad_rating: Optional[str] = Field(default=None, alias="adRating")
    ad_score: Optional[float] = Field(default=None, alias="adScore")
    up_volume_ratio: Optional[float] = Field(default=None, alias="upVolumeRatio")
    volume_trend: Optional[float] = Field(default=None, alias="volumeTrend")
    smr_rating: Optional[str] = Field(default=None, alias="smrRating")
    smr_score: Optional[float] = Field(default=None, alias="smrScore")
    sales_growth_2q: Optional[float] = Field(default=None, alias="salesGrowth2q")
    gross_margin: Optional[float] = Field(default=None, alias="grossMargin")
    net_margin: Optional[float] = Field(default=None, alias="netMargin")
    roe: Optional[float] = None
    sma20: Optional[float] = None
    sma50: Optional[float] = None
    sma150: Optional[float] = None
    sma200: Optional[float] = None
    volume_sma50: Optional[float] = Field(default=None, alias="volumeSma50")
    price_vs_sma20: Optional[float] = Field(default=None, alias="priceVsSma20")
    price_vs_sma50: Optional[float] = Field(default=None, alias="priceVsSma50")
    price_vs_sma150: Optional[float] = Field(default=None, alias="priceVsSma150")
    price_vs_sma200: Optional[float] = Field(default=None, alias="priceVsSma200")
    high_52w: Optional[float] = Field(default=None, alias="high52w")
    low_52w: Optional[float] = Field(default=None, alias="low52w")
    off_high_pct: Optional[float] = Field(default=None, alias="offHighPct")
    volume_vs_avg50: Optional[float] = Field(default=None, alias="volumeVsAvg50")
    price_change_pct: Optional[float] = Field(default=None, alias="priceChangePct")
    price_change_amount: Optional[float] = Field(default=None, alias="priceChangeAmount")
    ytd_change_pct: Optional[float] = Field(default=None, alias="ytdChangePct")

    model_config = {"populate_by_name": True}


class WebsocketMonthlyUsageDataResponse(BaseModel):
    external_user_id: str = Field(alias="externalUserID")
    first_connection_time: datetime = Field(alias="firstConnectionTime")
    unique_device_count: int = Field(alias="uniqueDeviceCount")

    model_config = {"populate_by_name": True}
