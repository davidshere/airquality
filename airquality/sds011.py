import base64
import serial
import time
from enum import Enum
from typing import List, Tuple

PORT = serial.Serial("/dev/ttyUSB1", 9600, timeout=5)


WRITE_COMMAND_SIZE = 19
READ_COMMAND_SIZE = 10

# Packet head, tail, and command id
HEAD = b'\xaa'
TAIL = b'\xab'
SEND_COMMAND_BYTE = b'\xb4'

# Data constants (will be decoded by bytes later)
EMPTY_DATA_BYTE = b'00'
ALL_DEVICES = b'FF'

DATA_REPORTING_MODE = b'02'

class CommandBytes(Enum):
    pass

class PMICommandBytes(Enum):
    PMI = b'04'

class MetaCommandBytes(Enum):
    MODE = b'02'
    ID = b'05'
    DEVICE_STATUS = b'06'
    PERIOD = b'08'
    FIRMWARE = b'07'

class SensorCommand(Enum):
    PMI = b'C0'
    META = b'C5'

class Action(Enum):
    GET = b'00'
    SET = b'01'

class ReportingMode(Enum):
    ACTIVE = b'00'
    QUERY = b'01'

class DeviceStatus(Enum):
    SLEEP = b'00'
    WORK = b'01'

class WorkingPeriod(Enum):
    CONTINUOUS = b'00'
    ONE = b'01'
    TWO = b'02'
    THREE = b'03'
    FOUR = b'04'
    FIVE = b'05'
    TEN = b'10'
    FIFTEEN = b'15'
    TWENTY = b'20'
    TWENTY_FIVE = b'25'
    THIRTY = b'30'


def get_checksum(data_bytes):
    checksum = sum(b''.join(data_bytes)) % 256
    chk = checksum.to_bytes(1, 'little')
    return chk


def check_response_checksum(response):
    response_checksum = response[-2]
    if response_checksum != sum(response[2:8]) % 256:
        print("Checksum failed")
        return False
    else:
        return True


def _execute(cmd: bytes, port=PORT):
    # Clear everyting that's come into the port - otherwise the
    # command response may be at the back of a long queue
    port.flushInput()
    return port.write(cmd)


class CommandBuilder:
    def __init__(
        self,
        command_byte: CommandBytes=None,
        data_byte2: bytes=None,
        data_byte3: bytes=None,
        device_id: Tuple[bytes]=None,
        num_non_data_bytes: int=4,
        num_total_bytes: int=WRITE_COMMAND_SIZE
    ):
        self.device_id = list(device_id) if device_id else [ALL_DEVICES] * 2
        self.command_byte = command_byte

        non_null_non_id_data_bytes=[
            a.value for a in [
               self.command_byte,
                data_byte2,
                data_byte3
            ] if a is not None
        ]

        non_id_data_bytes = (
            non_null_non_id_data_bytes +
            [EMPTY_DATA_BYTE] *
            (
                num_total_bytes -
                num_non_data_bytes -
                len(non_null_non_id_data_bytes) -
                len(self.device_id)
            )
        )
        self.data_bytes = [
            *non_id_data_bytes,
            *self.device_id
        ]
        self.encoded_data_bytes = [base64.b16decode(a) for a in self.data_bytes]

    def build(self):
        byte_collection = [
            HEAD,
            SEND_COMMAND_BYTE,
            *self.encoded_data_bytes,
            get_checksum(self.encoded_data_bytes),
            TAIL
        ]
        print('bc', byte_collection)
        cmd = b''.join(byte_collection)
        if len(cmd) != WRITE_COMMAND_SIZE:
            raise Exception(f"Malformed command size: {len(cmd)} {cmd}")
        return cmd

#
# Methods to query the device
#
def data_reporting_mode(action=Action.GET, mode=ReportingMode.ACTIVE, device_id=None) -> bytes:
    if action not in Action:
        raise Exception("Misspecified action: Must be Action.GET or Action.SET")

    if mode not in ReportingMode:
        raise Exception("Misspecified mode: Must be ReportingMode.ACTIVE or ReportingModel.QUERY")

    builder = CommandBuilder(
        command_byte=MetaCommandBytes.MODE,
        data_byte2=action,
        data_byte3=mode,
        device_id=device_id
    )
    command = builder.build()
    _execute(command)
    return command

def sleep_and_work(action=Action.GET, status=DeviceStatus.SLEEP, device_id=None) -> bytes:
    if action not in Action:
        raise Exception("Misspecificed action: Must be Action.GET or Action.SET")

    if status not in DeviceStatus:
        raise Exception("Misspecified device status: Must be DeviceStatus.SLEEP or Device.Status.WORK")

    builder = CommandBuilder(
        command_byte=MetaCommandBytes.DEVICE_STATUS,
        data_byte2=action,
        data_byte3=status,
        device_id=device_id,
    )
    command = builder.build()
    _execute(command)
    return command

def working_period(action=Action.GET, period=WorkingPeriod.CONTINUOUS, device_id=None) -> bytes:
    if action not in Action:
        raise Exception("Misspecified Action: Must be Action.GET or Action.SET")

    if period not in WorkingPeriod:
        raise Exception("Misspecified Period: Must be one of CONTINUOUS, ONE, TWO, THREE, FOUR, FIVE, TEN, FIFTEEN, TWENTY, TWENTY_FIVE or THIRTY")

    builder = CommandBuilder(
        command_byte=MetaCommandBytes.PERIOD,
        data_byte2=action,
        data_byte3=period,
        device_id=device_id
    )
    command = builder.build()
    _execute(command)
    return command

def query_pmi():
    builder = CommandBuilder(PMICommandBytes.PMI)
    command = builder.build()
    _execute(command)
    return command

#
#  Methods to parse responses from the device
#
def parse_reporting_mode_response(result: List[bytes]) -> Tuple[Action, ReportingMode, Tuple[bytes, bytes]]:
    action = result[2]
    data_response = result[3]
    device_id = result[5], result[6]
    return Action(action), ReportingMode(data_response), device_id

def _get_pmi(low_byte: bytes, high_byte: bytes):
    if not (isinstance(low_byte, bytes) and isinstance(high_byte, bytes)):
        raise Exception("get_pmi_ inputs must be bytes")
    return int(high_byte + low_byte, 16) / 10

def parse_pmi_response(result: List[bytes]):
    two_point_five = result[1], result[2]
    ten = result[3], result[4]
    device_id = result[5], result[6]
    pmi_two_point_five = _get_pmi(*two_point_five)
    pmi_ten = _get_pmi(*ten)
    return pmi_two_point_five, pmi_ten, device_id

def parse_device_status_response(result: List[bytes]):
    action = result[2]
    data_response = result[3]
    device_id = result[5], result[6]
    return Action(action), DeviceStatus(data_response), device_id

def parse_working_period_response(result: List[bytes]):
    action = result[2]
    period = result[3]
    device_id = result[5], result[6]
    return Action(action), WorkingPeriod(period), device_id

#
# Methods to fetch and parse messages from the device
#
def get_response(port=PORT) -> bytes:
    resp = port.read(10)
    if not resp:
        print("Null response")
        return None

    if not check_response_checksum(resp):
        print("Invalid response: Checksum failed")
        return None

    encoded = base64.b16encode(resp)
    chunked = [
        encoded[i: i + 2]
        for i in range(0, len(encoded), 2)
    ]
    return chunked[1: -1]

def parse_response(response: List[bytes]):
    if response is None:
        print("response is None")
        return

    cmd_type = SensorCommand(response[0])
    if cmd_type == SensorCommand.PMI:
        return parse_pmi_response(response)

    cmd = MetaCommandBytes(response[1])
    if cmd == MetaCommandBytes.MODE:
        return parse_reporting_mode_response(response)
    elif cmd == MetaCommandBytes.DEVICE_STATUS:
        return parse_device_status_response(response)
    elif cmd == MetaCommandBytes.PERIOD:
        return parse_working_period_response(response)
    else:
        raise Exception(f"No response parser found for {cmd}")

print('reporting')
print(data_reporting_mode(Action.SET, ReportingMode.QUERY, device_id=(b'2A', b'84')))
print(parse_response(get_response()))

print("\npmi")
print(query_pmi())
print(parse_response(get_response()))

print('\nsleep and work')
print(sleep_and_work(Action.SET, DeviceStatus.WORK, device_id=(b'2A', b'84')))
print(parse_response(get_response()))

print('\nworking period')
print(working_period(Action.GET, WorkingPeriod.CONTINUOUS))
print(parse_response(get_response()))
