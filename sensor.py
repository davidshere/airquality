from sds011 import SDS011

PORT = "/dev/ttyUSB0"

sensor = SDS011(serial_port=PORT, use_query_mode=True)

def get_pmi_result():
    return sensor.query()

if __name__ == "__main__":
  print(get_pmi_result())
