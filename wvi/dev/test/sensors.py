#!/usr/bin/env python3

# This program reads fake sensors to populate the SQL database
# Current reading rate is 1 Hz
# This code should be run on device startup

import time
import datetime
import signal
import sys
import mariadb
import random

# Pimoroni
from bme280 import BME280
from enviroplus import gas
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559
from subprocess import PIPE, Popen

bme280 = BME280()

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])


# Some globals
# sensor1 = 30.1
# sensor2 = 27.2
# sensor3 = 1013.6
# sensor4 = 66.6
# sensor5 = 856
# sensor6 = 5.5
# sensor7 = 701.4
# sensor8 = 76.9

# Connect to database
def connect_database():
    try:
        conn = mariadb.connect(
            user='group12',
            password='1234',
            host='127.0.0.1',
            port=3306,
            database='egh455')
    except mariadb.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    else:
        print("Database connection established!")
        return conn

# Insert sensor data to database
def insert_database(conn, current_time, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8):
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO sensors (time, cpu_temp, bme_temp, bme_pres, bme_humi, env_ligh, gas_oxid, gas_redu, gas_nh3) VALUES (?,?,?,?,?,?,?,?,?)",
        (current_time, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8))
    except mariadb.Error as e:
        print(f"Error inserting data to database: {e}")
    else:
        conn.commit()
        print("Data inserted into database")

# Print contents of database
def print_database(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sensors")
        results = cur.fetchall()
    except mariadb.Error as e:
        print(f"Error reading database: {e}")
    else:
        if len(results) == 0:
            print("Database empty!")
        else:
            for row in results:
                index_red = row[0]
                time_read = row[1]
                sensor1 = row[2]
                sensor2 = row[3]
                sensor3 = row[4]
                sensor4 = row[5]
                sensor5 = row[6]
                sensor6 = row[7]
                sensor7 = row[8]
                sensor8 = row[9]
                print(f"Idx: {index_red} dt: {time_read} s1: {sensor1} s2: {sensor2} s3: {sensor3} s4: {sensor4} s5: {sensor5} s6: {sensor6} s7: {sensor7} s8: {sensor8}")

# Generate dummy sensor data for 8 sensors
"""
sensor1 - cpu_temp  - CPU temperature (10-40)
sensor2 - bme_temp  - BME280 Temperature (10-40)
sensor3 - bme_pres  - BME280 Pressure (800-1200)
sensor4 - bme_humd  - BME280 Humidity (10-90)
sensor5 - env_ligh  - Light Sensor (lux) (100-2500)
sensor6 - gas_oxid  - Gas Sensor (Oxidising) (1-10)
sensor7 - gas_redu  - Gas Sensor (Reducing) (100-1000)
sensor8 - gas_nh3   - Gas Sensor (NH3) (10-120)
"""
def get_sensor1(): # CPU temperature
    value = random.randint(100, 400)
    return value/10
def get_sensor2(): # BME280 temperature
    value = random.randint(100, 400)
    return value/10
def get_sensor3():
    value = random.randint(8000, 12000)
    return value/10
def get_sensor4():
    value = random.randint(100, 900)
    return value/10
def get_sensor5():
    value = random.randint(1000, 25000)
    return value/10
def get_sensor6():
    value = random.randint(10, 100)
    return value/10
def get_sensor7():
    value = random.randint(1000, 10000)
    return value/10
def get_sensor8():
    value = random.randint(100, 1200)
    return value/10

def get_sensor_data():
    #sensor1 = get_sensor1()
    sensor1 = get_cpu_temperature()
    #sensor2 = get_sensor2()
    sensor2 = bme280.get_temperature()
    #sensor3 = get_sensor3()
    sensor3 = bme280.get_pressure()
    #sensor4 = get_sensor4()
    sensor4 = bme280.get_humidity()
    #sensor5 = get_sensor5()
    sensor5 = ltr559.get_lux()
    #sensor6 = get_sensor6()
    #sensor7 = get_sensor7()
    #sensor8 = get_sensor8()
    data = gas.read_all()
    sensor6 = data.oxidising
    sensor7 = data.reducing
    sensor8 = data.nh3
    return [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8]

# Print sensor data
def print_sensor_data():
    [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8] = get_sensor_data()
    current_time = datetime.datetime.now()
    print(f"Time: {current_time}\nSensor1: {sensor1}\nSensor2: {sensor2}\nSensor3: {sensor3}\nSensor4: {sensor4}\nSensor5: {sensor5}\nSensor6: {sensor6}\nSensor7: {sensor7}\nSensor8: {sensor8}")

# Add sensor data to database
def save_to_database(conn):
    [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8] = get_sensor_data()
    current_time = datetime.datetime.now()
    insert_database(conn, current_time, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8)

# Main function
def main():
    # Connect to database
    conn = connect_database()

    # Handle ctrl+c exit of program
    def signal_handler(sig, frame):
        print_database(conn)
        try:
            conn.close()
        except mariadb.Error as e:
            print(f"Error closing database: {e}")
        else:
            print("Database connection closed")
        print('You pressed Ctrl+C!')
        sys.exit(0)

    # Setup Ctrl+C clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    # Welcome message
    print("Simulating sensor reading and storage to database")
    print('Press Ctrl+C to exit')
    
    # Run once
    #print_sensor_data()
    #save_to_database(conn)
    #print_database(conn)
    # Main loop
    while True:
        time.sleep(1)
        save_to_database(conn)

if __name__ == "__main__":
    main()