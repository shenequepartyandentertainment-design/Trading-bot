from dataclasses import dataclass

@dataclass
class RiskConfig:
    account_balance: float
    max_risk_per_trade_pct: float
    max_daily_loss_pct: float
    max_open_risk_pct: float

class RiskManager:
    """
    Handles risk limits:
    - Max risk per trade
    - Max daily loss
    - Max open risk
    """

    def __init__(self, config: RiskConfig):
        self.config = config
        self.daily_pnl = 0.0
        self.open_risk = 0.0

    def can_open_new_trade(self, trade_risk: float) -> bool:
        """
        trade_risk: max loss of the new trade (in dollars).
        """
        # 1) Per-trade risk limit
        if trade_risk > self.config.account_balance * self.config.max_risk_per_trade_pct:
            return False

        # 2) Daily loss circuit breaker
        if self.daily_pnl < -self.config.account_balance * self.config.max_daily_loss_pct:
            return False

        # 3) Total open risk limit
        if self.open_risk + trade_risk > self.config.account_balance * self.config.max_open_risk_pct:
            return False

        return True

    def register_new_trade(self, trade_risk: float):
        """
        Call this when a new trade is opened.
        """
        self.open_risk += trade_risk

    def register_closed_trade(self, pnl: float, trade_risk: float):
        """
        Call this when a trade is closed.
        pnl: realized profit/loss in dollars
        trade_risk: original max loss of that trade
        """
        self.daily_pnl += pnl
        self.open_risk -= trade_risk
        if self.open_risk < 0:
            self.open_risk = 0.0
