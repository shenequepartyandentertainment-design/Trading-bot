from typing import Dict, Any, List

class DataProvider:
    """
    Wraps market data + option chain.

    Right now this is just an interface with NotImplementedError.
    You will plug in a real data source (Polygon, Tradier, IBKR, etc.).
    """

    def get_underlying_price(self, ticker: str) -> float:
        """
        Return the latest price of the underlying stock/ETF.

        Example return: 475.32
        """
        # TODO: replace with real-time price API
        raise NotImplementedError("Price API not implemented. Plug in your data source here.")

    def get_option_chain(
        self,
        ticker: str,
        min_dte: int = 14,
        max_dte: int = 45
    ) -> List[Dict[str, Any]]:
        """
        Return a list of option contracts.

        Expected structure for each contract:
        {
          'symbol': 'SPY',              # underlying
          'option_symbol': 'SPY_20261218_450P',  # your provider's option ticker
          'expiry': '2026-12-18',
          'strike': 450.0,
          'type': 'put',                # 'call' or 'put'
          'bid': 1.25,
          'ask': 1.35,
          'iv': 0.28,
          'dte': 30                     # days to expiry
        }

        Filter contracts to only those with dte between min_dte and max_dte.
        """
        # TODO: implement using your data provider
        raise NotImplementedError("Option chain API not implemented. Plug in your data source here.")
