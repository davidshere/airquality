import struct
import time

import board
import digitalio

from circuitpython_nrf24l01.rf24 import RF24

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

count=5
while count:
  if nrf.available():
      payload_size, pipe_number = nrf.any(), nrf.pipe
      buf = nrf.read()

      result = b""
      for i in range(0, 10, 2):

          b = base64.b16encode(bytes(buf)[i: i+2])
          b = b if not b.endswith(b'00') else b[:2] + b'0'
          result += b
      print(result)
  else:
    time.sleep(1)
    continue
  count-=1

  # AAC04D01912A8415AB
  # AAC04D01912A8415AB
