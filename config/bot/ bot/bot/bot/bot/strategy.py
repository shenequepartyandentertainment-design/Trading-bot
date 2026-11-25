from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class SpreadLeg:
    symbol: str
    side: str      # "buy" or "sell"
    type: str      # "call" or "put"
    strike: float
    expiry: str
    price: float   # bid or ask used

@dataclass
class TradeIdea:
    underlying: str
    strategy_type: str
    legs: List[SpreadLeg]
    max_gain: float   # in dollars
    max_loss: float   # in dollars
    credit: float     # in dollars (for credit spreads)
    notes: str

class Strategy:
    """
    Base class for strategies.
    """

    def generate_trade(
        self,
        ticker: str,
        underlying_price: float,
        option_chain: List[Dict[str, Any]]
    ) -> Optional[TradeIdea]:
        raise NotImplementedError

class BullPutSpreadStrategy(Strategy):
    """
    Example strategy: Bull Put Spread (short premium, bullish/neutral).

    Logic:
    - Use puts between min_dte and max_dte.
    - Choose a short put slightly OTM (e.g., < 95% of underlying price).
    - Choose a long put further OTM (lower strike) with same expiry.
    - Use bid for short leg, ask for long leg (conservative).
    """

    def __init__(self, min_dte: int = 14, max_dte: int = 45, width: float = 5.0):
        self.min_dte = min_dte
        self.max_dte = max_dte
        self.width = width

    def generate_trade(
        self,
        ticker: str,
        underlying_price: float,
        option_chain: List[Dict[str, Any]]
    ) -> Optional[TradeIdea]:
        # Filter for puts within DTE window
        puts = [
            c for c in option_chain
            if c.get("type") == "put" and self.min_dte <= c.get("dte", 0) <= self.max_dte
        ]
        if not puts:
            return None

        # Sort by strike descending (closest OTM below price first)
        puts = sorted(puts, key=lambda x: x["strike"], reverse=True)

        # Pick short put slightly OTM (e.g., < 95% of price)
        short_put = None
        for c in puts:
            if c["strike"] < underlying_price * 0.95:
                short_put = c
                break

        if not short_put:
            return None

        # Find long put lower by ~width, same expiry
        target_strike = short_put["strike"] - self.width
        long_candidates = [
            c for c in puts
            if c["expiry"] == short_put["expiry"] and c["strike"] <= target_strike
        ]
        if not long_candidates:
            return None

        # Choose the closest strike below target
        long_put = sorted(long_candidates, key=lambda x: x["strike"])[0]

        # Conservative pricing: short at bid, long at ask
        short_bid = short_put.get("bid", 0.0)
        long_ask = long_put.get("ask", 0.0)
        credit_per_contract = short_bid - long_ask
        width = short_put["strike"] - long_put["strike"]

        if credit_per_contract <= 0 or width <= 0:
            return None

        contract_size = 100
        max_gain = credit_per_contract * contract_size
        max_loss = (width - credit_per_contract) * contract_size

        if max_loss <= 0:
            return None

        legs = [
            SpreadLeg(
                symbol=short_put["option_symbol"],
                side="sell",
                type="put",
                strike=short_put["strike"],
                expiry=short_put["expiry"],
                price=short_bid,
            ),
            SpreadLeg(
                symbol=long_put["option_symbol"],
                side="buy",
                type="put",
                strike=long_put["strike"],
                expiry=long_put["expiry"],
                price=long_ask,
            ),
        ]

        notes = (
            f"Bull put spread on {ticker}: short {short_put['strike']} put, "
            f"long {long_put['strike']} put, expiry {short_put['expiry']}, "
            f"credit ≈ {credit_per_contract:.2f} per contract, width {width:.2f}"
        )

        return TradeIdea(
            underlying=ticker,
            strategy_type="bull_put_spread",
            legs=legs,
            max_gain=max_gain,
            max_loss=max_loss,
            credit=credit_per_contract * contract_size,
            notes=notes,
        )

Later, if you want, I can add a LongCallMomentumStrategy class in this same file.
