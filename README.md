# AI Trading Prototype
[![Python version](https://img.shields.io/badge/python-3.8_%7C_3.9_%7C_3.10_%7C_3.11-blue)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code_style-black-black)](https://black.readthedocs.io/en/stable/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project uses OpenAI to determine the sentiment of cryptocurrency news headlines and subsequently executes orders on the Binance Spot Market.

It is composed of two main components: [Sentiment Generator](#sentiment-generator-sg) and [Trading Bot](#trading-bot-tb).

![Data Flow Diagram](../assets/dfd.drawio.png)


## Disclaimer
This project is for demonstration purposes only and has never been executed on a production site. We do not know whether this project can generate profits and don’t hold any responsibility for any losses that may be incurred. You should NOT use this project in your own trading application.

## Features
- Decoupled Architecture: The two main components can function autonomously on different machines or on the same machine.
- Sentiment Persistence: The generated sentiments can be either persisted locally or broadcasted over Redis.
- Redis Publish/Subscribe Messaging Paradigm: The generated sentiments events can be real-time accessed by the Trading Bot or any other subscriber to the same Redis channel.
- Option to define your variables for the default trading strategy.
- Trading Bot Dry-run: Configure the Trading Bot with [Spot Testnet](https://testnet.binance.vision/) URL to test without costs.
- Trading Bot Backtesting: Run a simulation of the trading strategy for historical headlines by using [ai-trading-prototype-backtester](https://github.com/binance/ai-trading-prototype-backtester/).
- News Headlines Retrieval: News headlines to feed *Sentiment Generator* can be retrieved by using [ai-trading-prototype-headlines](https://github.com/binance/ai-trading-prototype-headlines).

## Requirements
Signature Generator:
- [OpenAI API key](https://platform.openai.com/account/api-keys) with enough credit to cover the `gpt-3.5-turbo` max 4K context usage. The [costs](https://openai.com/pricing) depends on the amount of provided headlines and the length of the same.
- (Optional) If you decide to use Redis, you need to have a running instance of [Redis](https://redis.io/) Server.

Trading Bot:
- [Binance Exchange Spot API Key](https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072) or [Binance Spot Testnet API key](https://testnet.binance.vision/).
- A running instance of [Redis](https://redis.io/) Server

## Installation
Clone from GitHub:
```
git clone git@github.com:binance/ai-trading-prototype.git
```

Install the required libraries:
```
cd <path_to_cloned_repository>
pip install -r requirements.txt
```

## Usage

### Commands
```
usage: aitradingprototype [-h] (-sg | -tb) config_file

Free open source AI trading bot prototype

positional arguments:
  config_file           .YAML config file for sentiment_generator or trading_bot process

optional arguments:
  -h, --help            show this help message and exit
  -sg, --sentiment_generator
                        starts the sentiment generator process
  -tb, --trading_bot     starts the trading bot process
```

### Sentiment Generator and Trading Bot
The complete AI Trading is achieved by running two processes simultaneously: One to use the [Sentiment Generator](#sentiment-generator-sg) and the other to use the [Trading Bot](#trading-bot-tb).

### Sentiment Generator (SG)
Analyzes user-provided news headlines to generate sentiments (`bullish`, `bearish` or `unknown`) for a predefined cryptocurrency.

![SG Process Flow Diagram](../assets/sg_pfd.drawio.png)

1. Create and fill `sg_config.yaml` by following the instructions provided in the `sg_config_example.yaml` file.
2. Run:

```
python -m aitradingprototype <sg_config.yaml.example> -sg
```

The `headlines_file` in the config file is utilized to locate the headlines file. Remarks on this file:
- The required line format is `"headline collected source","headline collected timestamp (ms)","headline published timestamp (ms)","headline"`.
- Each field is wrapped with `"` and can't contain `,"`.
- This file can't have comment lines. If there's empty lines, they'll be ignored.
- If SG is already running and there's addition of new lines, those will still be processed.

The `output_option` in the config file, defines where to push results:
 - `redis` - (Default) Publishes sentiment events to Redis channel (`redis_channel` in the config file). This is to allow real-time access to sentiment signals by the Trading Bot or any other subscriber to the same Redis channel.
 - `file` - The generated sentiments are saved into `/output/sentiments_<asset>.csv` (line format: `"headline collected source","headline collected timestamp (ms)","headline published timestamp (ms)","headline","sentiment"`) so that user can have the option to self-inspect the accuracy of the headlines sentiments.

### Trading Bot (TB)
Executes trading orders on Binance based on received sentiments.

![TB Process Flow Diagram](../assets/tb_pfd.drawio.png)

1. Create and fill `tb_config.yaml` by following the instructions provided in the `tb_config_example.yaml` file.
2. Run:

```
python -m aitradingprototype <tb_config.yaml.example> -tb
```

The `input_option` in the config file decides which source to obtain the sentiment, which can be:
  - `redis` - (Default) Subscribes and listens to a Redis server channel for sentiments events.
  - `file` - Read sentiments from config file's `sentiments_file` (line format:`"headline collected source","headline collected timestamp (ms)","headline published timestamp (ms)","headline","sentiment"`).

#### Trading Strategy
There's only one default trading strategy, which places MARKET orders to the Binance Spot Market.

Under `trading_strategy` field in the config file, you can define these trading variables:
  - `symbol` - The trading pair Trading Bot places orders.
  - `base_asset` - The symbol's base asset, buyings and sellings underlying asset.
  - `order_quantity` - The fixed quantity for every order.
  - `total_quantity_limit` - The upper limit on the total quantity of 'base_asset' that can be held via the accumulation of BUY orders at any given point.

The order placement logic is:
- BUY order, when sentiment is `bullish` and `total_quantity_limit` won't be exceeded.
- SELL order, when sentiment is `bearish` and we have [holding quantity](#holding-quantity) to sell.
- Skip order, when the above conditions are not met or when the sentiment is `unknown`/invalid.

#### "Holding Quantity"
This is term we use to indicate the total base asset quantiy that is incremented or decremented by trades net quantity:
  - net quantity = order's `executedQty` - order's `commission`.
  - `commission` is the sum of each `fill` commission from order's response.

Please consult [`FULL` order response](https://binance-docs.github.io/apidocs/spot/en/#new-order-trade) for fields reference.

#### Commission

At the moment, this project is only doing `commission` calculation for when the `commissionAsset` is the base asset!

If this is not your case, you can reconfigure your Binance account's chosen option for commission asset, otherwise the "holding quantity" will be incorrect.

#### Mimimum Notional

Since the minimum notional changes with market price fluctuations, it's ideal to have an order quantity that'll unlikey to encounter `Filter failure: NOTIONAL` error, which happens when `minNotional` value (notional = price * quantity) is not reached.

If a `Filter failure: NOTIONAL` is received during BUY or SELL order, the trading bot will stop with an indication of a valid minimum quantity.

#### Interruption
If Trading Bot is interrupted (maybe due to technical issues or maintenance), the current "holding quantity" is saved in Redis, so that the bot can continue where it left off when it's restarted.
This Redis key format for the "holding quantity" is `aitp_<strategyname>_holding_qty_<asset>` (ex: `aitp_successivestrategy_holding_qty_btc`).

#### Rate Limits
The IP and Order rate limits are according to [Binance Spot Market Limits](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#limits).

If you encounter an error, you should do proper adjustments. For example, reduce reduce the number of headline sentiments that you feed to the *trading bot* or reconfigure the `trading_strategy` in the config file.


## Logging
The logging level is adjustable in either the sentiment generator's YAML config or the trading bot's YAML config.