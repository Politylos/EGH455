#!/usr/bin/env python3

import time
from enviroplus import gas
import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""gas.py - Print readings from the MICS6814 Gas sensor.
Press Ctrl+C to exit!
""")

try:
    while True:
        readings = gas.read_all()
        #logging.info(readings)
        print(readings.oxidising)
        time.sleep(1.0)
except KeyboardInterrupt:
    pass