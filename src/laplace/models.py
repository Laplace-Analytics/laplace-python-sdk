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

    model_config = {"populate_by_name": True}


class PriceCandle(BaseModel):
    """Individual price candle data."""

    close: float = Field(alias="c")
    date: float = Field(alias="d")
    high: float = Field(alias="h")
    low: float = Field(alias="l")
    open: float = Field(alias="o")


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
    """Stock information within a collection."""

    id: str
    name: str
    symbol: str
    sector_id: str = Field(alias="sectorId")
    asset_type: AssetType = Field(alias="assetType")
    industry_id: str = Field(alias="industryId")

    model_config = {"populate_by_name": True}


class Collection(BaseModel):
    """Collection model."""

    id: str
    title: str
    region: List[Region]
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")
    asset_class: AssetClass = Field(alias="assetClass")

    model_config = {"populate_by_name": True}


class CollectionDetail(BaseModel):
    """Detailed collection information."""

    id: str
    title: str
    region: List[Region]
    stocks: List[CollectionStock]
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")
    asset_class: AssetClass = Field(alias="assetClass")

    model_config = {"populate_by_name": True}


class Theme(BaseModel):
    """Theme model."""

    id: str
    title: str
    region: List[Region]
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")
    asset_class: AssetClass = Field(alias="assetClass")

    model_config = {"populate_by_name": True}


class ThemeDetail(BaseModel):
    """Detailed theme information."""

    id: str
    title: str
    region: List[Region]
    stocks: List[CollectionStock]
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")
    asset_class: AssetClass = Field(alias="assetClass")

    model_config = {"populate_by_name": True}


class Industry(BaseModel):
    """Industry model."""

    id: str
    title: str
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")

    model_config = {"populate_by_name": True}


class IndustryDetail(BaseModel):
    """Detailed industry information."""

    id: str
    title: str
    region: List[Region]
    stocks: List[CollectionStock]
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")
    stocks: List[CollectionStock]

    model_config = {"populate_by_name": True}


class Sector(BaseModel):
    """Sector model."""

    id: str
    title: str
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")

    model_config = {"populate_by_name": True}


class SectorDetail(BaseModel):
    """Detailed sector information."""

    id: str
    title: str
    region: List[Region]
    stocks: List[CollectionStock]
    image_url: str = Field(alias="imageUrl")
    avatar_url: str = Field(alias="avatarUrl")
    num_stocks: int = Field(alias="numStocks")

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
    currency: str
    slug: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
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
    asset_type: AssetType = Field(alias="assetType")
    asset_class: AssetClass = Field(alias="assetClass")

    model_config = {"populate_by_name": True}


class Dividend(BaseModel):
    """Stock dividend model."""

    date: datetime
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

    eps: float
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
    latest_price: float = Field(alias="latestPrice")
    three_month_return: float = Field(alias="3MonthReturn")
    weekly_return: float = Field(alias="weeklyReturn")
    yearly_return: float = Field(alias="yearlyReturn")
    monthly_return: float = Field(alias="monthlyReturn")
    previous_close: float = Field(alias="previousClose")
    lower_price_limit: float = Field(alias="lowerPriceLimit")
    upper_price_limit: float = Field(alias="upperPriceLimit")

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
    share_count: int = Field(alias="shareCount")
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

    model_config = {"populate_by_name": True}


class BrokerTradingData(BaseModel):
    """Broker trading data model."""

    broker: Broker
    net_amount: float = Field(alias="netAmount")
    total_amount: float = Field(alias="totalAmount")
    total_volume: int = Field(alias="totalVolume")
    total_buy_amount: float = Field(alias="totalBuyAmount")
    total_buy_volume: int = Field(alias="totalBuyVolume")
    total_sell_amount: float = Field(alias="totalSellAmount")
    total_sell_volume: int = Field(alias="totalSellVolume")

    model_config = {"populate_by_name": True}


class BrokerTotalStats(BaseModel):
    """Broker total statistics model."""

    net_amount: float = Field(alias="netAmount")
    total_amount: float = Field(alias="totalAmount")
    total_volume: int = Field(alias="totalVolume")
    total_buy_amount: float = Field(alias="totalBuyAmount")
    total_buy_volume: int = Field(alias="totalBuyVolume")
    total_sell_amount: float = Field(alias="totalSellAmount")
    total_sell_volume: int = Field(alias="totalSellVolume")

    model_config = {"populate_by_name": True}


class BrokerMarketData(BaseModel):
    """Broker market data model."""

    items: List[BrokerTradingData]
    total_stats: BrokerTotalStats = Field(alias="totalStats")
    record_count: int = Field(alias="recordCount")

    model_config = {"populate_by_name": True}


class StockInfo(BaseModel):
    """Stock information model."""

    id: str
    name: str
    symbol: str
    asset_type: AssetType = Field(alias="assetType")
    asset_class: AssetClass = Field(alias="assetClass")

    model_config = {"populate_by_name": True}


class StockTradingData(BaseModel):
    """Stock trading data model."""

    stock: StockInfo
    net_amount: float = Field(alias="netAmount")
    total_amount: float = Field(alias="totalAmount")
    total_volume: int = Field(alias="totalVolume")
    total_buy_amount: float = Field(alias="totalBuyAmount")
    total_buy_volume: int = Field(alias="totalBuyVolume")
    total_sell_amount: float = Field(alias="totalSellAmount")
    total_sell_volume: int = Field(alias="totalSellVolume")

    model_config = {"populate_by_name": True}


class BrokerStockData(BaseModel):
    """Broker stock data model."""

    items: List[StockTradingData]
    total_stats: BrokerTotalStats = Field(alias="totalStats")
    record_count: int = Field(alias="recordCount")

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
    types: List[CapitalIncreaseType]
    symbol: str
    bonus_rate: Optional[str] = Field(alias="bonusRate")
    rights_rate: Optional[str] = Field(alias="rightsRate")
    payment_date: Optional[datetime] = Field(alias="paymentDate")
    rights_price: Optional[str] = Field(alias="rightsPrice")
    rights_end_date: Optional[datetime] = Field(alias="rightsEndDate")
    target_capital: Optional[str] = Field(alias="targetCapital")
    bonus_start_date: Optional[datetime] = Field(alias="bonusStartDate")
    current_capital: Optional[str] = Field(alias="currentCapital")
    rights_start_date: Optional[datetime] = Field(alias="rightsStartDate")
    spk_approval_date: Optional[str] = Field(alias="spkApprovalDate")
    bonus_total_amount: Optional[str] = Field(alias="bonusTotalAmount")
    registration_date: Optional[datetime] = Field(alias="registrationDate")
    board_decision_date: Optional[datetime] = Field(alias="boardDecisionDate")
    bonus_dividend_rate: Optional[str] = Field(alias="bonusDividendRate")
    rights_total_amount: Optional[str] = Field(alias="rightsTotalAmount")
    specified_currency: Optional[str] = Field(alias="specifiedCurrency")
    rights_last_sell_date: Optional[datetime] = Field(alias="rightsLastSellDate")
    spk_application_date: Optional[datetime] = Field(alias="spkApplicationDate")
    related_disclosure_ids: List[int] = Field(alias="relatedDisclosureIds")
    spk_application_result: Optional[str] = Field(alias="spkApplicationResult")
    bonus_dividend_total_amount: Optional[str] = Field(alias="bonusDividendTotalAmount")
    registered_capital_ceiling: Optional[str] = Field(alias="registeredCapitalCeiling")
    external_capital_increase_rate: Optional[str] = Field(alias="externalCapitalIncreaseRate")
    external_capital_increase_amount: Optional[str] = Field(alias="externalCapitalIncreaseAmount")

    model_config = {"populate_by_name": True}


class SearchResultStock(BaseModel):
    """Search result stock model."""

    id: str
    name: str
    title: str
    region: Region
    asset_type: AssetType = Field(alias="assetType")

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
    fiscal_year: Optional[int] = Field(alias="fiscal_year", default=None)

    model_config = {"populate_by_name": True}


class EarningsTranscriptWithSummary(BaseModel):
    """Earnings transcript with summary model."""

    symbol: str
    year: int
    quarter: int
    content: str
    summary: Optional[str] = None
    has_summary: Optional[bool] = Field(alias="has_summary", default=None)

    model_config = {"populate_by_name": True}


class MarketState(BaseModel):
    """Market state model."""

    id: int
    market_symbol: Optional[str] = Field(alias="marketSymbol", default=None)
    state: str
    last_timestamp: datetime = Field(alias="lastTimestamp")
    stock_symbol: Optional[str] = Field(alias="stockSymbol", default=None)

    model_config = {"populate_by_name": True}


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    record_count: int = Field(alias="recordCount")
    items: List[T]

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

    Briefs = "briefs"
    Bloomberg = "bloomberg"
    Fda = "fda"
    Reuters = "Reuters"

class NewsOrderBy(str, Enum):
    """News Order by options."""

    Timestamp = "timestamp"


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
    name: str
    mean_type: int = Field(alias="meanType")

    model_config = {"populate_by_name": True}

class NewsSector(BaseModel):
    name: str
    news_count: int = Field(alias="newsCount")
    category_type: Optional[str] = Field(alias="categoryType", default=None)
    mean_type: Optional[int] = Field(alias="meanType", default=None)

    model_config = {"populate_by_name": True}

class NewsCategory(BaseModel):
    name: str
    news_count: int = Field(alias="newsCount")
    category_type: Optional[str] = Field(alias="categoryType", default=None)
    mean_type: Optional[int] = Field(alias="meanType", default=None)

    model_config = {"populate_by_name": True}

class NewsContent(BaseModel):
    title: str
    description: str
    content: List[str]
    summary: List[str]
    investor_insight: str = Field(alias="investorInsight")

    model_config = {"populate_by_name": True}

class News(BaseModel):
    created_at: datetime = Field(alias="createdAt")
    url: str
    image_url: str = Field(alias="imageUrl")
    timestamp: datetime
    publisher_url: str = Field(alias="publisherUrl")

    publisher: NewsPublisher
    related_tickers: List[NewsTicker] = Field(alias="relatedTickers")

    tickers: Optional[List[NewsTicker]] = None
    categories: Optional[NewsCategory] = None
    sectors: Optional[NewsSector] = None
    content: Optional[NewsContent] = None
    industries: Optional[NewsIndustry] = None

    quality_score: int = Field(alias="qualityScore")

    model_config = {"populate_by_name": True}
class NewsHighlight(BaseModel):
    consumer: List[str]
    energy_and_utilities: List[str] = Field(alias="energyAndUtilities")
    finance: List[str]
    healthcare: List[str]
    industrials_and_materials: List[str] = Field(alias="industrialsAndMaterials")
    tech: List[str]
    other: List[str]

    model_config = {"populate_by_name": True}

class WebsocketMonthlyUsageDataResponse(BaseModel):
    external_user_id: str = Field(alias="externalUserID")
    first_connection_time: datetime = Field(alias="firstConnectionTime")
    unique_device_count: int = Field(alias="uniqueDeviceCount")

    model_config = {"populate_by_name": True}
