from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Order:
    symbol: str
    side: str          # "buy" or "sell"
    quantity: int
    order_type: str    # "limit", "market"
    limit_price: float | None = None
    meta: Dict[str, Any] | None = None

class Broker:
    """
    Abstract broker interface.

    Right now this is a simple PAPER broker that simulates fills.
    Later you can replace methods with real API calls (IBKR, Tasty, Alpaca, etc.).
    """

    def __init__(self, mode: str = "paper"):
        self.mode = mode
        self.cash = 25000.0  # starting paper cash
        # positions: { option_symbol: {"quantity": int, "avg_price": float} }
        self.positions: Dict[str, Dict[str, Any]] = {}

    def get_cash(self) -> float:
        """
        Return current cash balance.
        In live mode, replace with broker API call.
        """
        return self.cash

    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """
        Return current positions.
        In live mode, replace with broker API call.
        """
        return self.positions

    def place_order(self, order: Order) -> Dict[str, Any]:
        """
        Execute an order.

        PAPER MODE:
        - Assume immediate fill at limit_price.
        - Update cash and positions.
        """
        if self.mode == "paper":
            if order.limit_price is None:
                raise ValueError("Paper mode requires limit_price for now.")

            fill_price = order.limit_price
            contract_size = 100  # standard US equity options
            notional = fill_price * order.quantity * contract_size

            if order.side == "buy":
                self.cash -= notional
            elif order.side == "sell":
                self.cash += notional
            else:
                raise ValueError(f"Invalid side: {order.side}")

            pos = self.positions.get(order.symbol, {"quantity": 0, "avg_price": 0.0})
            old_qty = pos["quantity"]
            old_avg = pos["avg_price"]

            if order.side == "buy":
                new_qty = old_qty + order.quantity
            else:  # sell
                new_qty = old_qty - order.quantity

            # Simple average price update (not perfect but fine for paper)
            if new_qty != 0:
                pos["avg_price"] = fill_price
            else:
                pos["avg_price"] = 0.0

            pos["quantity"] = new_qty
            self.positions[order.symbol] = pos

            return {
                "status": "filled",
                "symbol": order.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "fill_price": fill_price,
                "mode": self.mode,
            }

        # LIVE MODE: you will implement this later
        raise NotImplementedError("Live broker mode not implemented yet.")
