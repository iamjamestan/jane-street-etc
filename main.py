import json
import time

from socket import *
from socket import error as socket_error
from typing import Any, BinaryIO, Dict
from enum import Enum
from bond import bond_strategy

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

## Book handler for each symbol
symbol_book_handlers = {
  "BOND": bond_strategy
}

orders: Dict[int, Any] = {}

####################
## MISC FUNCTIONS ##
####################

def initialize() -> None:
  print("Initialising...")
  print("Environment: {}".format(ENV))
  print("Port: {}".format(PORT))
  print("Hostname: {}".format(EXCHANGE_HOSTNAME))
  print()

def mean(l) -> int:
  return sum(l) // len(l)

########################
## EXCHANGE FUNCTIONS ##
########################

def create_exchange() -> BinaryIO:
  sock = socket(AF_INET, SOCK_STREAM)
  print("Connecting to the server now...")
  sock.connect((EXCHANGE_HOSTNAME, PORT))
  print("Connected.")
  print()
  return sock.makefile("rw", 1)

def recreate_exchange() -> BinaryIO:
  global SERVER_STATUS
  print("Reconnecting to server now...")
  while SERVER_STATUS == 0:
    try:
      exchange = create_exchange()
      write_to_exchange(exchange, HELLO)
      response = read_from_exchange(exchange)
      if response["type"] == str(InfoType.HELLO):
        SERVER_STATUS = 1
        print("POSITIONS: {}".format(response["symbols"]))
        symbols = response["symbols"]
        for symbol in symbols:
          symbol_positions[symbol["symbol"]] = symbol["position"]
        print("Reconnected!")
        return exchange
      else:
        SERVER_STATUS = 0
        continue
    except socket_error:
      print("Failed to reconnect, trying again...")
      time.sleep(0.1)
      continue

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

  iterations = 0

  while iterations < 1000:
    info = read_from_exchange(exchange)
    iterations += 1
    if not info:
      break
    info_type = info["type"]

    if info_type == str(InfoType.HELLO):
      print("POSITIONS: {}".format(info["symbols"]))
      symbols = info["symbols"]
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
        return
    elif info_type == str(InfoType.ERROR):
      print("ERROR: {}".format(info["error"]))
    elif info_type == str(InfoType.TRADE):
      symbol_trade[info["symbol"]].append((info["price"], info["size"]))
    elif info_type == str(InfoType.ACK):
      _order_id = info["order_id"]
      order = orders[_order_id]
      print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {} has been placed on the books"
              .format(_order_id, order[0], order[1], order[2], order[3], order[4]))

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
      if symbol in symbol_book_handlers:
        fn = symbol_book_handlers[symbol]
        response = fn(buy, sell)
        if response:
          price = response["price"]
          size = response["size"]
          direction = response["dir"]
          write_to_exchange(exchange, { "type": str(Action.ADD), "order_id": ORDER_ID, "symbol": symbol, \
                                        "dir": direction, "price": price, "size": size })
          orders[ORDER_ID] = (direction, symbol, price, size, size)
          ORDER_ID += 1
          if direction == str(Direction.BUY):
            symbol_positions[str(Symbol.USD)] = symbol_positions[str(Symbol.USD)] - (price * size)

def do_action():
  pass

def main() -> None:
  global SERVER_STATUS
  exchange: BinaryIO = create_exchange()
  print("Exchange successfully initialised")
  write_to_exchange(exchange, HELLO)
  while True:
    server_info(exchange)
    if SERVER_STATUS == 1:
      do_action()
    elif SERVER_STATUS == 0:
      exchange = recreate_exchange()

if __name__ == '__main__':
  initialize()
  while True:
    try:
      main()
    except socket_error:
      print("\nERROR: Retrying the connection...\n")
      time.sleep(0.1)
