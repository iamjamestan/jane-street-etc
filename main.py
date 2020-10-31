import json
import time

from socket import *
from socket import error as socket_error
from typing import Any, BinaryIO
from enum import Enum

###########################
## CONSTANT DECLARATIONS ##
###########################

TEAM_NAME = "COLLEGEAVEEAST"
TEST_ENV = "test"
PROD_ENV = "production"
ENV = TEST_ENV
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
  VALBZ = "VALBZ"
  VALE = "VALE"
  WFC = "WFC"
  XLF = "XLF"

class Direction(PrintEnum):
  BUY = "BUY"
  SELL = "SELL"

####################
## MISC FUNCTIONS ##
####################

def initialize() -> None:
  print("Initialising...")
  print("Environmnet: {}".format(ENV))
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

def write_to_exchange(exchange: BinaryIO, obj: Any) -> None:
  json.dump(obj, exchange)
  exchange.write("\n")

def read_from_exchange(exchange: BinaryIO) -> Any:
  return json.loads(exchange.readline())

#################################
## MAIN DATA / DATA STRUCTURES ##
#################################

SERVER_STATUS = 1

####################
## MAIN FUNCTIONS ##
####################

def main() -> None:
  exchange: BinaryIO = create_exchange()
  print("Exchange successfully initialised")

  write_to_exchange(exchange, HELLO)
  response = read_from_exchange(exchange)
  print("Reply from exchange: {}".format(response))
  while True:
    break

if __name__ == '__main__':
  initialize()
  while True:
    try:
      main()
    except socket_error:
      print("\nERROR: Retrying the connection...\n")
      time.sleep(0.1)
