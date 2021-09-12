import struct
import time
from typing import List

import board
import digitalio
from more_itertools import chunked

from circuitpython_nrf24l01.rf24 import RF24

from sds011 import parse_response

csn = digitalio.DigitalInOut(board.D7)
ce = digitalio.DigitalInOut(board.D8)
spi = board.SPI()

nrf = RF24(spi, csn, ce)

nrf.pa_level = -12

# 00001=base, 00002=node
addresses = [b"00001", b"00002"]

nrf.open_rx_pipe(0, addresses[0])


nrf.listen = True

nrf.allow_ask_no_ack = False
nrf.dynamic_payloads = False
nrf.payload_length = 32

import base64

def get_reading() -> bytearray:
  if nrf.available():
      payload_size, pipe_number = nrf.any(), nrf.pipe
      return nrf.read()

def parse_response(resp: bytearray) -> List[bytes]:
  """ Turns from a bytearray to a list of encoded bytes """
  result = b''
  for i in range(0, 10, 2):
    result += base64.b16encode(bytes(resp)[i: i+2])
  return [b''.join([chr(x).encode() for x in a]) for a in chunked(result, 2)]

if __name__ == "__main__":
  while True:
    reading = get_reading()
    if reading is not None:
      print(parse_response(reading))
      break
    else:
      time.sleep(1)
