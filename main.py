import json
import time
import pandas as pd

from helper import *
from pprint import pprint
from socket import *
from socket import error as socket_error
from typing import Any, BinaryIO, Dict
from enum import Enum
from bond import bond_strategy
from adr import adr_strategy
from xlf import xlf_strategy, xlf_ema_strategy

###########################
## CONSTANT DECLARATIONS ##
###########################

TEAM_NAME = "COLLEGEAVEEAST"
TEST_ENV = "test"
PROD_ENV = "production"
ENV = PROD_ENV
TEST_EXCHANGE_INDEX = 0
PORT = 25000 + (TEST_EXCHANGE_INDEX if ENV == TEST_ENV else 0)
ZEROETH_HOSTNAME = "0-prod-like"
FIRST_HOSTNAME = "1-slower"
SECOND_HOSTNAME = "2-empty"
EXCHANGE_HOSTNAME = "test-exch-" + TEAM_NAME.lower() if ENV == TEST_ENV else PROD_ENV

HELLO = { "type": "hello", "team": TEAM_NAME.upper() }

## Enums for exchange sending
class PrintEnum(Enum):
  def __str__(self):
    return self.value

class Action(PrintEnum):
  ADD = "add"
  CONVERT = "convert"

class Symbol(PrintEnum):
  BOND = "BOND"
  GS = "GS"
  MS = "MS"
  USD = "USD"
  VALBZ = "VALBZ"
  VALE = "VALE"
  WFC = "WFC"
  XLF = "XLF"

class Direction(PrintEnum):
  BUY = "BUY"
  SELL = "SELL"

class InfoType(PrintEnum):
  HELLO = "hello"
  OPEN = "open"
  CLOSE = "close"
  ERROR = "error"
  BOOK = "book"
  TRADE = "trade"
  ACK = "ack"
  REJECT = "reject"
  FILL = "fill"
  OUT = "out"

#################################
## MAIN DATA / DATA STRUCTURES ##
#################################

SERVER_STATUS = 1
ORDER_ID = 0

## Book handler for each symbol
symbol_book_handlers = {
  "BOND": bond_strategy,
  "XLF": xlf_strategy
}

## Trade Prices
symbol_trade = {
  "BOND": [],
  "GS": [],
  "MS": [],
  "USD": [],
  "VALBZ": [],
  "VALE": [],
  "WFC": [],
  "XLF": []
}

## Book Prices
symbol_book = {
  "BOND": {},
  "GS": {},
  "MS": {},
  "USD": {},
  "VALBZ": {},
  "VALE": {},
  "WFC": {},
  "XLF": {}
}

## Open/Close Status of Symbols
symbol_open = {
  "BOND": False,
  "GS": False,
  "MS": False,
  "USD": False,
  "VALBZ": False,
  "VALE": False,
  "WFC": False,
  "XLF": False
}

## Positions of Symbols
symbol_positions = {
  "BOND": 0,
  "GS": 0,
  "MS": 0,
  "USD": 0,
  "VALBZ": 0,
  "VALE": 0,
  "WFC": 0,
  "XLF": 0
}

## Limits of Symbols
symbol_limits = {
  "BOND": 100,
  "GS": 100,
  "MS": 100,
  "VALBZ": 10,
  "VALE": 10,
  "WFC": 100,
  "XLF": 100
}

orders: Dict[int, Any] = {}

conversions: Dict[int, Any] = {}

####################
## MISC FUNCTIONS ##
####################

def initialize() -> None:
  print("Initialising...")
  print("Environment: {}".format(ENV))
  print("Port: {}".format(PORT))
  print("Hostname: {}".format(EXCHANGE_HOSTNAME))
  print()

########################
## EXCHANGE FUNCTIONS ##
########################

def create_exchange() -> BinaryIO:
  global SERVER_STATUS
  sock = socket(AF_INET, SOCK_STREAM)
  print("Connecting to the server now...")
  sock.connect((EXCHANGE_HOSTNAME, PORT))
  print("Connected.")
  SERVER_STATUS = 1
  print()
  return sock.makefile("rw", 1)

def recreate_exchange() -> BinaryIO:
  global SERVER_STATUS
  global ORDER_ID
  print("Reconnecting to server now...")
  attempts = 0
  while SERVER_STATUS == 0 and attempts < 20:
    try:
      attempts += 1
      exchange = create_exchange()
      SERVER_STATUS = 1
      write_to_exchange(exchange, HELLO)
      response = read_from_exchange(exchange)
      print(response)
      if response["type"] == str(InfoType.HELLO):
        SERVER_STATUS = 1
        print("POSITIONS: {}".format(response["symbols"]))
        symbols = response["symbols"]
        for symbol in symbols:
          symbol_positions[symbol["symbol"]] = symbol["position"]
        print("Reconnected!")
        ORDER_ID = 0
        return exchange
      elif response["type"] == str(InfoType.OPEN):
        print("OPENING: {}".format(response["symbols"]))
        for symbol in response["symbols"]:
          symbol_open[symbol] = True
        return exchange
      else:
        time.sleep(0.1)
        SERVER_STATUS = 0
    except socket_error:
      print("Failed to reconnect, trying again...")
      time.sleep(0.1)

def write_to_exchange(exchange: BinaryIO, obj: Any) -> None:
  json.dump(obj, exchange)
  exchange.write("\n")

def read_from_exchange(exchange: BinaryIO) -> Any:
  return json.loads(exchange.readline())

####################
## MAIN FUNCTIONS ##
####################

def server_info(exchange: BinaryIO) -> None:
  global SERVER_STATUS
  global ORDER_ID
  global symbol_trade
  global symbol_book

  iterations = 0

  while iterations < 250:
    info = read_from_exchange(exchange)
    iterations += 1
    if not info:
      break
    info_type = info["type"]

    if info_type == str(InfoType.HELLO):
      print("POSITIONS: {}".format(info["symbols"]))
      symbols = info["symbols"]
      ORDER_ID = 0
      for symbol in symbols:
        symbol_positions[symbol["symbol"]] = symbol["position"]
    elif info_type == str(InfoType.OPEN):
      print("OPENING: {}".format(info["symbols"]))
      for symbol in info["symbols"]:
        symbol_open[symbol] = True
    elif info_type == str(InfoType.CLOSE):
      print("CLOSING: {}".format(info["symbols"]))
      for symbol in info["symbols"]:
        symbol_open[symbol] = False
      has_open = False
      for symbol, status in symbol_open.items():
        if status == True:
          has_open = True
      if not has_open:
        SERVER_STATUS = 0
        symbol_trade = {
          "BOND": [],
          "GS": [],
          "MS": [],
          "USD": [],
          "VALBZ": [],
          "VALE": [],
          "WFC": [],
          "XLF": []
        }
        symbol_book = {
          "BOND": {},
          "GS": {},
          "MS": {},
          "USD": {},
          "VALBZ": {},
          "VALE": {},
          "WFC": {},
          "XLF": {}
        }
        return
    elif info_type == str(InfoType.ERROR):
      print("ERROR: {}".format(info["error"]))
    elif info_type == str(InfoType.TRADE):
      symbol_trade[info["symbol"]].append((info["price"], info["size"]))
      # pprint(symbol_trade)
    elif info_type == str(InfoType.ACK):
      _order_id = info["order_id"]
      if _order_id in orders:
        order = orders[_order_id]
        print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {} has been placed on the books"
                .format(_order_id, order[0], order[1], order[2], order[3], order[4]))
      else:
        conversion = conversions[_order_id]
        print("Order {}: Dir - {}, Symbol - {}, Size - {} has been converted"
                .format(_order_id, conversion[0], conversion[1], conversion[2]))
        if conversion[1] == str(Symbol.VALE):
          symbol_positions[str(Symbol.VALE)] -= conversion[2]
          symbol_positions[str(Symbol.VALBZ)] += conversion[2]
          symbol_positions[str(Symbol.USD)] -= 10
        elif conversion[1] == str(Symbol.XLF):
          symbol_positions[str(Symbol.USD)] -= 100
          if conversion[0] == str(Direction.BUY):
            symbol_positions[str(Symbol.BOND)] -= 3
            symbol_positions[str(Symbol.GS)] -= 2
            symbol_positions[str(Symbol.MS)] -= 3
            symbol_positions[str(Symbol.WFC)] -= 2
            symbol_positions[str(Symbol.XLF)] += 10
          elif conversion[0] == str(Direction.SELL):
            symbol_positions[str(Symbol.BOND)] += 3
            symbol_positions[str(Symbol.GS)] += 2
            symbol_positions[str(Symbol.MS)] += 3
            symbol_positions[str(Symbol.WFC)] += 2
            symbol_positions[str(Symbol.XLF)] -= 10

        print("CURRENT POSITION: {}".format(symbol_positions))

    elif info_type == str(InfoType.FILL):
      _order_id = info["order_id"]
      order = orders[_order_id]
      price = order[2]
      size = info["size"]

      orders[_order_id] = (order[0], order[1], order[2], order[3], order[4] - size)
      order = orders[_order_id]

      print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {}, Current - {} has been filled"
              .format(_order_id, order[0], order[1], order[2], order[3], order[4]))

      if order[0] == str(Direction.SELL):
        symbol_positions[str(Symbol.USD)] += (price * size)
        symbol_positions[str(order[1])] -= size
      else:
        symbol_positions[str(order[1])] += size
      print("CURRENT POSITION: {}".format(symbol_positions))

    elif info_type == str(InfoType.OUT):
      _order_id = info["order_id"]
      order = orders[_order_id]
      print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {}, Current - {} is off the books"
              .format(_order_id, order[0], order[1], order[2], order[3], order[4]))

    elif info_type == str(InfoType.BOOK):
      symbol = info["symbol"]
      buy = info["buy"]
      sell = info["sell"]
      symbol_book[symbol] = { "BUY": buy, "SELL": sell }
      if symbol in symbol_book_handlers:
        fn = symbol_book_handlers[symbol]
        if symbol == str(Symbol.BOND):
          responses = fn(buy, sell)
          if responses:
            for response in responses:
              price = response["price"]
              size = response["size"]
              direction = response["dir"]
              write_to_exchange(exchange, { "type": str(Action.ADD), "order_id": ORDER_ID, "symbol": symbol, \
                                            "dir": direction, "price": price, "size": size })
              orders[ORDER_ID] = (direction, symbol, price, size, size)
              ORDER_ID += 1
              if direction == str(Direction.BUY):
                symbol_positions[str(Symbol.USD)] = symbol_positions[str(Symbol.USD)] - (price * size)
        elif symbol == str(Symbol.XLF): 
          responses = fn(symbol_book[str(Symbol.BOND)], symbol_book[str(Symbol.GS)], \
                        symbol_book[str(Symbol.MS)], symbol_book[str(Symbol.WFC)], \
                        symbol_book[str(Symbol.XLF)])
          if responses:
            for response in responses:
              response["order_id"] = ORDER_ID
              write_to_exchange(exchange, response)
              if response["type"] != str(Action.CONVERT):
                orders[ORDER_ID] = (response["dir"], response["symbol"], response["price"], response["size"], response["size"])
                if response["dir"] == str(Direction.BUY):
                  symbol_positions[str(Symbol.USD)] = symbol_positions[str(Symbol.USD)] - (response["price"] * response["size"])
              else:
                conversions[ORDER_ID] = (response["dir"], response["symbol"], response["size"])
              ORDER_ID += 1

def do_action(exchange: BinaryIO):
  global ORDER_ID
  adr_actions = adr_strategy(symbol_trade[str(Symbol.VALE)], symbol_trade[str(Symbol.VALBZ)])
  if adr_actions:
    for action in adr_actions:
      action["order_id"] = ORDER_ID
      write_to_exchange(exchange, action)
      if action["type"] != str(Action.CONVERT):
        orders[ORDER_ID] = (action["dir"], action["symbol"], action["price"], action["size"], action["size"])
      else:
        conversions[ORDER_ID] = (action["dir"], action["symbol"], action["size"])
      ORDER_ID += 1
      if action["dir"] == str(Direction.BUY):
        symbol_positions[str(Symbol.USD)] = symbol_positions[str(Symbol.USD)] - (action["price"] * action["size"])
  # bond_df = pd.DataFrame(symbol_trade[str(Symbol.BOND)], columns=["price", "qty"])
  # gs_df = pd.DataFrame(symbol_trade[str(Symbol.GS)], columns=["price", "qty"])
  # ms_df = pd.DataFrame(symbol_trade[str(Symbol.MS)], columns=["price", "qty"])
  # wfc_df = pd.DataFrame(symbol_trade[str(Symbol.WFC)], columns=["price", "qty"])
  # xlf_df = pd.DataFrame(symbol_trade[str(Symbol.XLF)], columns=["price", "qty"])
  # xlf_actions = xlf_ema_strategy(symbol_book[str(Symbol.BOND)], symbol_book[str(Symbol.GS)], \
  #                         symbol_book[str(Symbol.MS)], symbol_book[str(Symbol.WFC)], \
  #                         symbol_book[str(Symbol.XLF)], bond_df, gs_df, ms_df, \
  #                         wfc_df, xlf_df)
  # if xlf_actions:
  #   for action in xlf_actions:
  #     action["order_id"] = ORDER_ID
  #     write_to_exchange(exchange, action)
  #     if action["type"] != str(Action.CONVERT):
  #       orders[ORDER_ID] = (action["dir"], action["symbol"], action["price"], action["size"], action["size"])
  #       if action["dir"] == str(Direction.BUY):
  #         symbol_positions[str(Symbol.USD)] = symbol_positions[str(Symbol.USD)] - (action["price"] * action["size"])
  #     else:
  #       conversions[ORDER_ID] = (action["dir"], action["symbol"], action["size"])
  #     ORDER_ID += 1


def main() -> None:
  global SERVER_STATUS
  exchange: BinaryIO = create_exchange()
  print("Exchange successfully initialised")
  write_to_exchange(exchange, HELLO)
  while True:
    server_info(exchange)
    if SERVER_STATUS == 1:
      do_action(exchange)
    elif SERVER_STATUS == 0:
      exchange = recreate_exchange()
      if SERVER_STATUS == 0:
        break

if __name__ == '__main__':
  initialize()
  while True:
    try:
      main()
    except socket_error:
      print("\nERROR: Retrying the connection...\n")
      time.sleep(0.1)
