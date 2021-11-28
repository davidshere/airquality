import base64
import json
import logging
import struct
import time
from typing import List

import board
import digitalio
from more_itertools import chunked

from circuitpython_nrf24l01.rf24 import RF24

from sds011 import parse_response

logger = logging.getLogger(__name__)

csn = digitalio.DigitalInOut(board.D7)
ce = digitalio.DigitalInOut(board.D22)
spi = board.SPI()
nrf = RF24(spi, csn, ce)

nrf.pa_level = -18

# 00001=base, 00002=node
addresses = [b"00001", b"00002"]

nrf.open_rx_pipe(0, addresses[0])

nrf.listen = True

nrf.allow_ask_no_ack = False
nrf.dynamic_payloads = False
nrf.payload_length = 32

def get_reading() -> bytearray:
  if nrf.available():
    payload_size, pipe_number = nrf.any(), nrf.pipe
    return nrf.read()

def process_raw_response(resp: bytearray) -> List[bytes]:
  """ Turns from a bytearray to a list of encoded bytes """
  result = b''
  for i in range(0, 10, 2):
    result += base64.b16encode(bytes(resp)[i: i+2])
  return [b''.join([chr(x).encode() for x in a]) for a in chunked(result, 2)]

def get_results():
  reading = get_reading()
  if not reading:
    return None

  response = parse_response(process_raw_response(reading)[1:-1])
  return response

if __name__ == "__main__":
  nrf.listen = True
  nrf.flush_rx()
  while True:
    result = get_results()
    print(result)
    nrf.flush_rx()
    time.sleep(5)



