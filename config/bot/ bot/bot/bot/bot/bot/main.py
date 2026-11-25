import time
import yaml
from pathlib import Path

from bot.utils import setup_logger
from bot.broker import Broker, Order
from bot.data_provider import DataProvider
from bot.risk_manager import RiskManager, RiskConfig
from bot.strategy import BullPutSpreadStrategy, TradeIdea

CONFIG_PATH = Path("config/config.yaml")

def load_config() -> dict:
    """
    Load YAML config from CONFIG_PATH.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config file not found at {CONFIG_PATH}. "
            f"Copy config.example.yaml to config.yaml and edit your settings."
        )
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def place_trade_idea(
    broker: Broker,
    risk_manager: RiskManager,
    idea: TradeIdea,
    logger,
    contracts: int = 1
):
    """
    Take a TradeIdea and send orders for each leg.
    """
    trade_risk = idea.max_loss

    if not risk_manager.can_open_new_trade(trade_risk):
        logger.warning(
            f"Risk limits prevent new trade on {idea.underlying}. "
            f"Requested risk: {trade_risk:.2f}"
        )
        return

    for leg in idea.legs:
        order = Order(
            symbol=leg.symbol,
            side=leg.side,
            quantity=contracts,
            order_type="limit",
            limit_price=leg.price,
            meta={
                "underlying": idea.underlying,
                "strategy": idea.strategy_type,
            },
        )
        result = broker.place_order(order)
        logger.info(f"Placed order: {result}")

    risk_manager.register_new_trade(trade_risk)
    logger.info(
        f"Opened {idea.strategy_type} on {idea.underlying}: "
        f"max_loss={idea.max_loss:.2f}, max_gain={idea.max_gain:.2f}, "
        f"credit={idea.credit:.2f}"
    )
    logger.info(f"Notes: {idea.notes}")

def main():
    config = load_config()
    logger = setup_logger("bot", "data/trading_bot.log")

    account_balance = config["account"]["starting_balance"]
    risk_cfg = RiskConfig(
        account_balance=account_balance,
        max_risk_per_trade_pct=config["account"]["max_risk_per_trade_pct"],
        max_daily_loss_pct=config["account"]["max_daily_loss_pct"],
        max_open_risk_pct=config["account"]["max_open_risk_pct"],
    )
    risk_manager = RiskManager(risk_cfg)

    broker = Broker(mode=config["broker"]["mode"])
    data_provider = DataProvider()

    # For now we only wire BullPutSpreadStrategy
    strategy = BullPutSpreadStrategy(
        min_dte=config["trading"]["min_dte"],
        max_dte=config["trading"]["max_dte"],
        width=5.0,
    )

    tickers = config["trading"]["tickers"]
    poll_interval = config["trading"]["poll_interval_seconds"]

    logger.info("Starting options trading bot (paper mode unless configured otherwise)...")

    while True:
        try:
            for ticker in tickers:
                logger.info(f"Checking for trade ideas on {ticker}...")

                # 1) Get data
                underlying_price = data_provider.get_underlying_price(ticker)
                option_chain = data_provider.get_option_chain(
                    ticker,
                    min_dte=config["trading"]["min_dte"],
                    max_dte=config["trading"]["max_dte"],
                )

                # 2) Generate trade idea
                idea = strategy.generate_trade(ticker, underlying_price, option_chain)
                if idea is None:
                    logger.info(f"No trade idea for {ticker} this cycle.")
                    continue

                # 3) Place trade (1 contract by default)
                place_trade_idea(
                    broker=broker,
                    risk_manager=risk_manager,
                    idea=idea,
                    logger=logger,
                    contracts=1,
                )

        except NotImplementedError as nie:
            logger.error(
                f"NotImplementedError: {nie}. "
                "You need to implement DataProvider or Broker live mode."
            )
            # Break so you see the error instead of looping forever
            break
        except Exception as e:
            logger.exception(f"Error in main loop: {e}")

        logger.info(f"Sleeping for {poll_interval} seconds...")
        time.sleep(poll_interval)

if __name__ == "__main__":
    main()
