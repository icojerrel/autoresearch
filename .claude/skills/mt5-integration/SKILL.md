---
name: mt5-integration
description: MetaTrader 5 (MT5) Python API integration for forex trading. Use for connecting to MT5 terminal, fetching historical data, real-time data streaming, account info, order execution, and trade management.
argument-hint: "[symbol] [timeframe] [bars_count]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
user-invocable: true
---

# MT5 Integration Skill

## Overview
Integrates with MetaTrader 5 terminal via Python API for forex trading operations.

## Environment Requirements
- MT5 Terminal installed and running
- Python package: `pip install MetaTrader5`
- MT5 terminal logged into account (demo or live)
- Enabled "Algo Trading" in MT5

## Arguments
Parse `$ARGUMENTS` as: symbol timeframe bars_count

- `$0` = Symbol (e.g., EURUSD, GBPUSD, USDJPY). Default: EURUSD
- `$1` = Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN1). Default: H1
- `$2` = Bars count (number of bars to fetch). Default: 1000

If no arguments, ask user for parameters.

## Core Functions

### 1. Initialize MT5 Connection

```python
import MetaTrader5 as mt5
from datetime import datetime, timedelta

# Initialize
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Check connection
if not mt5.terminal_info():
    print("Terminal not found")
    mt5.shutdown()
    quit()

print("MT5 connected successfully")
```

### 2. Fetch Account Information

```python
# Get account info
account_info = mt5.account_info()
if account_info:
    print(f"Account: {account_info.login}")
    print(f"Balance: {account_info.balance}")
    print(f"Equity: {account_info.equity}")
    print(f"Margin: {account_info.margin}")
    print(f"Free Margin: {account_info.margin_free}")
    print(f"Leverage: {account_info.leverage}")
```

### 3. Fetch Historical Data

```python
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1
bars_count = 1000

# Get current time
utc_from = datetime.now() - timedelta(days=bars_count // 24)

# Fetch rates
rates = mt5.copy_rates_from(symbol, timeframe, utc_from, bars_count)

if rates is None:
    print(f"No data for {symbol}, error code =", mt5.last_error())
else:
    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    print(f"Fetched {len(df)} bars for {symbol}")
    print(df.head())
```

### 4. Fetch Real-Time Data (Tick Data)

```python
# Get last N ticks
symbol = "EURUSD"
ticks = mt5.copy_ticks_from(symbol, datetime.now(), 100, mt5.COPY_TICKS_ALL)

if ticks is not None:
    ticks_df = pd.DataFrame(ticks)
    ticks_df['time'] = pd.to_datetime(ticks_df['time'], unit='s')
    print(ticks_df.tail())
```

### 5. Get Symbol Information

```python
symbol_info = mt5.symbol_info("EURUSD")
if symbol_info:
    print(f"Description: {symbol_info.description}")
    print(f"Tick Size: {symbol_info.trade_tick_size}")
    print(f"Point Size: {symbol_info.point}")
    print(f"Digits: {symbol_info.digits}")
    print(f"Spread: {symbol_info.spread}")
    print(f"Contract Size: {symbol_info.trade_contract_size}")
```

### 6. Place Market Order

```python
symbol = "EURUSD"
lot_size = 0.1
order_type = mt5.ORDER_TYPE_BUY
price = mt5.symbol_info_tick(symbol).ask

# Request structure
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot_size,
    "type": order_type,
    "price": price,
    "deviation": 20,
    "magic": 234000,
    "comment": "Auto trade",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

# Send order
result = mt5.order_send(request)

if result.retcode != mt5.TRADE_RETCODE_DONE:
    print("Order failed, return code =", result.retcode)
else:
    print(f"Order placed successfully, ticket {result.order}")
```

### 7. Close Position

```python
# Get open positions
positions = mt5.positions_get(symbol="EURUSD")

if positions:
    position = positions[0]
    ticket = position.ticket

    # Close request
    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
        "position": ticket,
        "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
        "deviation": 20,
        "magic": 234000,
        "comment": "Auto close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(close_request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"Position {ticket} closed successfully")
```

### 8. Get Open Positions

```python
positions = mt5.positions_get()
if positions:
    for position in positions:
        print(f"Ticket: {position.ticket}")
        print(f"Symbol: {position.symbol}")
        print(f"Type: {'BUY' if position.type == mt5.POSITION_TYPE_BUY else 'SELL'}")
        print(f"Volume: {position.volume}")
        print(f"Price Open: {position.price_open}")
        print(f"Price Current: {position.price_current}")
        print(f"Profit: {position.profit}")
        print("---")
```

### 9. Convert MT5 Data to pandas for vectorbt

```python
def mt5_to_dataframe(symbol, timeframe, bars_count):
    """Fetch MT5 data and convert to pandas DataFrame for vectorbt."""
    # Timeframe mapping
    tf_map = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
        'W1': mt5.TIMEFRAME_W1,
    }

    if timeframe not in tf_map:
        raise ValueError(f"Invalid timeframe: {timeframe}")

    utc_from = datetime.now() - timedelta(days=bars_count // 24)
    rates = mt5.copy_rates_from(symbol, tf_map[timeframe], utc_from, bars_count)

    if rates is None:
        raise Exception(f"Failed to fetch data for {symbol}")

    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(rates)

    # Rename columns to match vectorbt expectations
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'spread': 'Spread',
        'time': 'datetime'
    })

    # Set datetime index
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('datetime', inplace=True)
    df.drop(columns=['time'], inplace=True)

    return df

# Usage
df = mt5_to_dataframe('EURUSD', 'H1', 1000)
print(df.head())
```

### 10. Shutdown MT5 Connection

```python
# Always shutdown when done
mt5.shutdown()
print("MT5 connection closed")
```

## Timeframe Reference

| Code | MT5 Constant | Description |
|------|-------------|-------------|
| M1 | mt5.TIMEFRAME_M1 | 1 Minute |
| M5 | mt5.TIMEFRAME_M5 | 5 Minutes |
| M15 | mt5.TIMEFRAME_M15 | 15 Minutes |
| M30 | mt5.TIMEFRAME_M30 | 30 Minutes |
| H1 | mt5.TIMEFRAME_H1 | 1 Hour |
| H4 | mt5.TIMEFRAME_H4 | 4 Hours |
| D1 | mt5.TIMEFRAME_D1 | Daily |
| W1 | mt5.TIMEFRAME_W1 | Weekly |

## Common FX Pairs

| Symbol | Description | Typical Spread (pips) |
|--------|-------------|----------------------|
| EURUSD | Euro / US Dollar | 0.1 - 0.2 |
| GBPUSD | British Pound / US Dollar | 0.2 - 0.5 |
| USDJPY | US Dollar / Japanese Yen | 0.1 - 0.3 |
| AUDUSD | Australian Dollar / US Dollar | 0.3 - 0.5 |
| USDCAD | US Dollar / Canadian Dollar | 0.2 - 0.4 |
| USDCHF | US Dollar / Swiss Franc | 0.2 - 0.4 |

## Error Handling

```python
def check_mt5_error():
    """Check for MT5 errors and provide helpful messages."""
    error_code = mt5.last_error()

    error_messages = {
        0: "Success",
        1: "Internal error",
        2: "Not enough memory",
        3: "No connection",
        4: "Timeout",
        5: "Invalid account",
        6: "Trading disabled",
        7: "Market closed",
        8: "Invalid price",
        9: "Invalid volume",
        10: "Position not found",
    }

    message = error_messages.get(error_code[0], f"Unknown error: {error_code[0]}")
    print(f"Error {error_code[0]}: {message}")

    return error_code[0]
```

## Example: Complete Workflow

```python
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import vectorbt as vbt

# 1. Connect
if not mt5.initialize():
    quit()

# 2. Fetch data
df = mt5_to_dataframe('EURUSD', 'H1', 1000)
close = df['Close']

# 3. Run backtest
ema_short = vbt.MA.run(close, 12, ewm=True)
ema_long = vbt.MA.run(close, 26, ewm=True)

entries = ema_short.ma_crossed_above(ema_long)
exits = ema_short.ma_crossed_below(ema_long)

pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000, fees=0.001)

# 4. Results
print(pf.stats())
print(f"Sharpe: {pf.sharpe_ratio():.2f}")
print(f"Max DD: {pf.max_drawdown()*100:.2f}%")

# 5. Disconnect
mt5.shutdown()
```

## Safety Notes

- Always test with DEMO account first
- Use proper position sizing (never risk > 2% per trade)
- Implement stop-loss in strategy, not just MT5
- Check margin before placing orders
- Handle connection errors gracefully
- Always shutdown MT5 connection when done

## Related Skills

- mt5-backtest: Backtesting with MT5 data and vectorbt
- autoresearch-trading: Autonomous strategy research
- paper-trading-manager: Manage paper trading experiments
