#!/usr/bin/env python3

import json
import logging
import random
import sys
import time
from datetime import datetime
from typing import Iterator
import os
from threading import Thread, Event

from flask import Flask, Response, render_template, request, stream_with_context, send_from_directory, send_file
import mariadb

#from camera import VideoCamera

from enviroplus import gas
from bme280 import BME280
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont

from subprocess import PIPE, Popen
import socket

import cv2

# Aruco
import argparse
import imutils
import numpy as np

# Servo
from gpiozero import Servo

bme280 = BME280()

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

application = Flask(__name__)
random.seed()  # Initialize the random number generator

lcd_screen = "SHOW_IP"

aruco_feed_runonce = False

# Get device IP address
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_frame():
    global cam_feed
    global image
    success, image = cam_feed.read()
    event_wait_camera_frame.set()
    if success == True:
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
    else:
        return 0

# Connect to database
def connect_database():
    try:
        db_conn = mariadb.connect(
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
        return db_conn

# # Insert sensor data to database
# def insert_database(conn, current_time, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8):
#     try:
#         cur = conn.cursor()
#         cur.execute("INSERT INTO sensors (time, cpu_temp, bme_temp, bme_pres, bme_humi, env_ligh, gas_oxid, gas_redu, gas_nh3) VALUES (?,?,?,?,?,?,?,?,?)",
#         (current_time, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8))
#     except mariadb.Error as e:
#         print(f"Error inserting data to database: {e}")
#     else:
#         conn.commit()
#         #print("Data inserted into database")

# Read data from database
def get_database_data():
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
        # Read from database
        try:
            cur = conn.cursor()
            cur.execute("select * from sensors where id > ((select count(*) from sensors) - 600)")
            results = cur.fetchall()
        except mariadb.Error as e:
            print(f"Error reading database: {e}")
        else:
            if len(results) == 0:
                logger.info("Database empty!")
                print("Database empty!")
            else:
                logger.info("Reading database!")
                labels = [row[1].strftime("%H:%M:%S") for row in results] # Datetime
                sensor1 = [row[2] for row in results] # CPU temp
                sensor2 = [row[3] for row in results] # BME temp
                sensor3 = [row[4] for row in results] # BME humd
                sensor4 = [row[5] for row in results] # BME pres
                sensor5 = [row[6] for row in results] # light
                sensor6 = [row[7] for row in results] # gas redu
                sensor7 = [row[8] for row in results] # gas oxid
                sensor8 = [row[9] for row in results] # gas nh3
            conn.close()
    return labels, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

# Get sensor readings
def get_sensor_data():
    global start_time, gas_oxi_calibration, gas_red_calibration, gas_nh3_calibration

    sensor1 = get_cpu_temperature()
    sensor2 = bme280.get_temperature()
    sensor3 = bme280.get_pressure()
    sensor4 = bme280.get_humidity()
    sensor5 = ltr559.get_lux()
    data = gas.read_all()
    sensor6 = data.oxidising
    sensor7 = data.reducing
    sensor8 = data.nh3

    # TODO Process and calibrate sensor data here
    # if (time.time() - start_time) > 120:
    #     if gas_oxi_calibration == 0:
    #         gas_oxi_calibration = sensor6
    #         gas_red_calibration = sensor7
    #         gas_nh3_calibration = sensor8
    #     else:
    #         try:
    #             sensor6 = sensor6 / gas_oxi_calibration
    #             sensor7 = sensor7 / gas_red_calibration
    #             sensor8 = sensor8 / gas_nh3_calibration
    #         except:
    #             pass

    try:
        sensor6 = sensor6 / 27000
        sensor7 = sensor7 / 16000
        sensor8 = sensor8 / 255000
    except:
        pass

    return [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8]

# Sensor reading thread
def sensor_reading_thread(thread_shutdown):
    print("Starting thread: sensor_reading_thread()")
    # Open database and get db object
    conn_sensors = connect_database()
    # Spin thread
    while True:
        time.sleep(1)
        current_time = datetime.now()
        [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8] = get_sensor_data()
        #insert_database(conn_sensors, current_time, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8)
        try:
            cur = conn_sensors.cursor()
            cur.execute("INSERT INTO sensors (time, cpu_temp, bme_temp, bme_pres, bme_humi, env_ligh, gas_oxid, gas_redu, gas_nh3) VALUES (?,?,?,?,?,?,?,?,?)",
            (current_time, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8))
        except mariadb.Error as e:
            print(f"Error inserting data to database: {e}")
        else:
            conn_sensors.commit()
        if thread_shutdown.is_set():
            print("Exit thread: sensor_reading_thread()")
            break
    conn_sensors.close()

variables = ["temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3",
             "CPU temperature"]

units = ["C",
         "hPa",
         "%",
         "Lux",
         "ppm",
         "ppm",
         "ppm",
         "C"]

limits = [[4, 18, 28, 35],
          [250, 650, 1013.25, 1015],
          [20, 30, 60, 70],
          [-1, -1, 30000, 100000],
          [-1, -1, 40, 50],
          [-1, -1, 450, 550],
          [-1, -1, 200, 300],
          [-1, -1, 50, 100],
          [-1, -1, 50, 100],
          [-1, -1, 50, 100]]

# RGB palette for values on the combined screen
palette = [(0, 0, 255),           # Dangerously Low
           (0, 255, 255),         # Low
           (0, 255, 0),           # Normal
           (255, 255, 0),         # High
           (255, 0, 0)]           # Dangerously High

values = {}
# Create LCD class instance.
disp = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)
# Initialize display.
disp.begin()

# Width and height to calculate text position.
WIDTH = disp.width
HEIGHT = disp.height
lcd_img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(lcd_img)
font_size_small = 10
font_size_large = 20
font = ImageFont.truetype(UserFont, font_size_large)
smallfont = ImageFont.truetype(UserFont, font_size_small)
x_offset = 2
y_offset = 2
message = ""

# Saves the data to be used in the graphs later and prints to the log
def save_data(idx, data):
    variable = variables[idx]
    # Maintain length of list
    values[variable] = values[variable][1:] + [data]
    unit = units[idx]
    message = "{}: {:.1f} {}".format(variable[:4], data, unit)
    # logging.info(message)

def display_everything():
    draw.rectangle((0, 0, WIDTH, HEIGHT), (0, 0, 0))
    column_count = 2
    row_count = (len(variables) / column_count)
    for i in range(len(variables)):
        variable = variables[i]
        data_value = values[variable][-1]
        unit = units[i]
        x = x_offset + ((WIDTH // column_count) * (i // row_count))
        y = y_offset + ((HEIGHT / row_count) * (i % row_count))
        message = "{}: {:.1f} {}".format(variable[:4], data_value, unit)
        lim = limits[i]
        rgb = palette[0]
        for j in range(len(lim)):
            if data_value > lim[j]:
                rgb = palette[j + 1]
        draw.text((x, y), message, font=smallfont, fill=rgb)
    disp.display(lcd_img)

# LCD Display control thread
def lcd_display_thread(thread_shutdown):
    print("Starting thread: lcd_display_thread()")
    global lcd_screen
    global lcd_screen_change
    # global cam_feed

    # Create LCD class instance.
    disp = ST7735.ST7735(
        port=0,
        cs=1,
        dc=9,
        backlight=12,
        rotation=270,
        spi_speed_hz=10000000
    )
    # Initialize display.
    disp.begin()

    # Width and height to calculate text position.
    WIDTH = disp.width
    HEIGHT = disp.height

    while True:
        if lcd_screen == "SHOW_IP":
            # New canvas to draw on.
            lcd_img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
            draw = ImageDraw.Draw(lcd_img)

            # Text settings.
            font_size = 20
            font = ImageFont.truetype(UserFont, font_size)
            text_colour = (255, 255, 255)
            back_colour = (0, 170, 170)
            font1_size = 18
            font1 = ImageFont.truetype(UserFont, font1_size)
            while True:
                #messageIP = subprocess.check_output(["hostname", "-I"]).split()[0].decode()
                messageIP = get_ip()
                messageDT = datetime.now().strftime("%H:%M")

                # Draw background rectangle and write text.
                draw.rectangle((0, 0, 160, 80), back_colour)
                #draw.text((1, 1), "IP Address", font=font, fill=text_colour)
                draw.text((1, 0), "user: group12", font=font1, fill=text_colour)
                draw.text((1,18), "password: 1234", font=font1, fill=text_colour)
                draw.text((1, 38), messageIP, font=font, fill=text_colour)
                draw.text((1, 58), "Time", font=font, fill=text_colour)
                draw.text((60, 58), messageDT, font=font, fill=text_colour)
                disp.display(lcd_img)
                # print("Current screen SHOW_IP")
                time.sleep(1)
                if lcd_screen_change.is_set():
                    lcd_screen_change.clear()
                    # print(lcd_screen)
                    break
                if thread_shutdown.is_set():
                    lcd_screen = "EXIT"
                    break

        if lcd_screen == "SHOW_SENSORS":
            # New canvas to draw on.
            lcd_img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
            draw = ImageDraw.Draw(lcd_img)

            font = ImageFont.truetype(UserFont, 10)
            factor = 2.25
            cpu_temps = [get_cpu_temperature()] * 5
            for v in variables:
                    values[v] = [1] * WIDTH
            while True:
                # Get sensor data
                [cpu_temp, raw_temp, raw_pres, raw_humd, raw_ligh, gas_oxid, gas_redu, gas_nh3] = get_sensor_data()
                # Smooth out with some averaging to decrease jitter
                cpu_temps = cpu_temps[1:] + [cpu_temp]
                avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
                raw_data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
                save_data(0, raw_data)
                save_data(7, avg_cpu_temp)
                display_everything()
                save_data(1, raw_pres)
                display_everything()
                save_data(2, raw_humd)
                save_data(3, raw_ligh)
                display_everything()
                save_data(4, gas_oxid)
                save_data(5, gas_redu)
                save_data(6, gas_nh3)
                display_everything()
                time.sleep(1)
                if lcd_screen_change.is_set():
                    lcd_screen_change.clear()
                    # print(lcd_screen)
                    break
                if thread_shutdown.is_set():
                    lcd_screen = "EXIT"
                    break

        if lcd_screen == "SHOW_LIVEFEED":
            while True:
                #ret, frame = cam_feed.read()
                # Our operations on the frame come here
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                #convert to PIL
                im_pil = Image.fromarray(gray)
                # Display the resulting frame
                # Resize the image
                im_pil = im_pil.resize((WIDTH, HEIGHT))
                #display image on lcd
                disp.display(im_pil)

                if lcd_screen_change.is_set():
                    lcd_screen_change.clear()
                    # print(lcd_screen)
                    break
                if thread_shutdown.is_set():
                    lcd_screen = "EXIT"
                    break
        
        if lcd_screen == "EXIT":
            print("Exit thread: lcd_display_thread()")
            break
        if thread_shutdown.is_set():
            lcd_screen = "EXIT"
            break

# Aruco marker pose estimation
def pose_esitmation(frame1, corners, ids, aruco_dict_type, arucoParams ,matrix_coefficients, distortion_coefficients):
    global aruco_detected_flag, aruco45_detected_flag
    '''
    tvec = [x,y,z]

    frame - Frame from the video stream
    matrix_coefficients - Intrinsic matrix of the calibrated camera
    distortion_coefficients - Distortion coefficients associated with your camera
    return:-
    frame - The frame with the axis drawn on it
    '''
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)
    # parameters = cv2.aruco.DetectorParameters_create()
    global aruco45_tvec
    global aruco45_ids

    aruco45_tvec = 0
    aruco45_ids = 0
    # corners, ids, rejected_img_points = cv2.aruco.detectMarkers(frame, aruco_dict_type , parameters=arucoParams,
    #     cameraMatrix=matrix_coefficients,
    #     distCoeff=distortion_coefficients)

        # If markers are detected
    for i in range(0, len(ids)):
        # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
        rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients,
        distortion_coefficients)

        
        # Draw Axis
        cv2.aruco.drawAxis(frame1, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)
        #cv2.drawFrameAxis(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)
        #cv2.putText(frame1, str(tvec), (bottomRight[0], bottomRight[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #print(tvec)
        aruco45_tvec = tvec
        aruco45_ids = ids[0]
        if (aruco45_ids == 45):
            aruco45_detected_flag = 1
            # Create new target image if non exists
            if not os.path.exists("static/images/target4.jpg"):
                cv2.imwrite('static/images/target4.jpg', frame1)
        else:
            aruco_detected_flag = 1
            # Create new target image if non exists
            if not os.path.exists("static/images/target3.jpg"):
                cv2.imwrite('static/images/target3.jpg', frame1)
    return frame1

# Aruco marker detection
def aruco_detector_thread(thread_shutdown):
    print("Starting thread: aruco_detector_thread()")
    global image
    global frame_ar
    

    arucoParams = cv2.aruco.DetectorParameters_create()
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
    # arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)
    # arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_250)
    # Position code

    # Camera calibration data 640x480
    # k = np.array([[678.194752, 0.00000000, 324.716040],
    #               [0.00000000, 907.069485, 236.057862],
    #               [0.00000000, 0.00000000, 1.00000000]])
    # d = np.array(([[0.215643, -0.374588, -0.000476, -0.000240, 0.000000]]))
    # Camera calibration data 2592x1944
    k = np.array([[1944.651788, 0.00000000, 1321.460626],
                  [0.00000000, 1944.904996, 996.893260],
                  [0.00000000, 0.00000000, 1.00000000]])
    d = np.array(([[0.136239, -0.180998, -0.002973, 0.002750, 0.000000]]))

    # initialize the video stream and allow the camera sensor to warm up
    
    event_wait_camera_frame.wait()
    frame_ar = image

    print("[INFO] starting video stream...")
    
    # loop over the frames from the video stream
    while True:
        
        # detect ArUco markers in the input frame
        (corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict, parameters=arucoParams)

        # verify *at least* one ArUco marker was detected
        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            
            # the corner value used in position
            corners_pose = corners
            
            # loop over the detected ArUCo corners
            for (markerCorner, markerID) in zip(corners, ids):
                # extract the marker corners (which are always returned
                # in top-left, top-right, bottom-right, and bottom-left
                # order)
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
    
                # convert each of the (x, y)-coordinate pairs to integers
                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))
    
                # draw the bounding box of the ArUCo detection
                cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
                cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
                cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
                cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
                # compute and draw the center (x, y)-coordinates of the
                # ArUco marker
                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
    
                # draw the ArUco marker ID on the frame
                cv2.putText(image, str(markerID),
                    (topLeft[0], topLeft[1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
                
                    # estimate pose
            frame_ar = pose_esitmation(image, corners_pose, ids, arucoDict, arucoParams , k, d)
        if thread_shutdown.isSet():
            break
    print("Exit thread: aruco_detector_thread()")

def target_detector_thread(thread_shutdown):
    while True:
        pass
        if thread_shutdown.isSet():
            break
    print("Exit thread: target_detector_thread()")

# Generate camera image
def gen():
    # global frame_ar
    while True:
        # Get camera frame
        frame = get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Unified JSON data
def get_json_data_complete() -> Iterator[str]:
    global target1_id, target2_id
    global target1_detected_flag, target2_detected_flag, aruco_detected_flag, aruco45_detected_flag
    global aruco45_tvec, aruco45_ids
    global image
    
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr or ""

    try:
        logger.info("Client %s connected", client_ip)
        while True:
            [cpu_temp, bme_temp, bme_pres, bme_humd, sen_lux, gas_oxi, gas_red, gas_nh3] = get_sensor_data()
            # Parse aruco vectors
            try:
                aruco_x = aruco45_tvec[0][0][0]
                aruco_y = aruco45_tvec[0][0][1]
                aruco_z = aruco45_tvec[0][0][2] * 2.8 # TODO Fix calibration
                aruco_id = str(aruco45_ids)
            except:
                aruco_x = 99.9
                aruco_y = 99.9
                aruco_z = 99.9
                aruco_id = "N/A"
            
            json_data = json.dumps(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "value1": cpu_temp,
                    "value2": bme_temp,
                    "value3": bme_pres,
                    "value4": bme_humd,
                    "value5": sen_lux,
                    "value6": gas_oxi,
                    "value7": gas_red,
                    "value8": gas_nh3,
                    "target1_id": target1_id,
                    "target1_detected": target1_detected_flag,
                    "target2_id": target2_id,
                    "target2_detected": target2_detected_flag,
                    "aruco_id": aruco_id,
                    "aruco_x": aruco_x,
                    "aruco_y": aruco_y,
                    "aruco_z": aruco_z,
                    "aruco_detected": aruco_detected_flag,
                    "aruco45_detected": aruco45_detected_flag,
                }
            )
            yield f"data:{json_data}\n\n"
            target1_detected_flag = 0
            target2_detected_flag = 0
            aruco_detected_flag = 0
            aruco45_detected_flag = 0
            time.sleep(1)
    except GeneratorExit:
        logger.info("Client %s disconnected", client_ip)

# Flask functions
@application.route("/")
def index() -> str:
    labels, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8 = get_database_data()
    
    return render_template("index.html", labels=labels,
                                         sensor1_values=sensor1,
                                         sensor2_values=sensor2,
                                         sensor3_values=sensor3,
                                         sensor4_values=sensor4,
                                         sensor5_values=sensor5,
                                         sensor6_values=sensor6,
                                         sensor7_values=sensor7,
                                         sensor8_values=sensor8)

@application.route("/JSON-data")
def json_data_sender() -> Response:
    response = Response(stream_with_context(get_json_data_complete()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response

# Render video feed
@application.route("/video_feed")
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Read webserver buttons
@application.route("/button/<lcd_cmd>")
def set_lcd_display(lcd_cmd = None):
    # print("Button press")
    global lcd_screen
    if lcd_cmd == "option1":
        print("LCD screen 1 selected")
        lcd_screen = "SHOW_IP"
        lcd_screen_change.set()
    elif lcd_cmd == "option2":
        print("LCD screen 2 selected")
        lcd_screen = "SHOW_SENSORS"
        lcd_screen_change.set()
    elif lcd_cmd == "option3":
        print("LCD screen 3 selected")
        lcd_screen = "SHOW_LIVEFEED"
        lcd_screen_change.set()
    elif lcd_cmd == "deploy_ss":
        print("Sample Tube Activated")
        deploy_sample_tube()
    return (''), 204

# Clear previous target images if existing
def startup_function():
    if os.path.exists("static/images/target1.jpg"):
        os.remove("static/images/target1.jpg")
    if os.path.exists("static/images/target2.jpg"):
        os.remove("static/images/target2.jpg")
    if os.path.exists("static/images/target3.jpg"):
        os.remove("static/images/target3.jpg")
    if os.path.exists("static/images/target4.jpg"):
        os.remove("static/images/target4.jpg")


# Deploy sample tube
def deploy_sample_tube():
    print("Deploy Sample tube")
    servo = Servo(4)
    servo.max()
    time.sleep(10)
    print("Retract Sample tube")
    servo.min()
    time.sleep(12)
    servo.mid()
    servo.detach()
    print("Sample complete")


# Main function
if __name__ == "__main__":
    # Clean up old targets
    startup_function()

    # Purge sensor
    for x in range(0,9):
        get_sensor_data()
    time.sleep(1)
    
    # Default variables
    target1_detected_flag = 0
    target2_detected_flag = 0
    aruco_detected_flag = 0
    aruco45_detected_flag = 0
    target1_id = 0
    target2_id = 0
    aruco45_id = 0
    start_time = time.time()
    gas_oxi_calibration = 0
    gas_red_calibration = 0
    gas_nh3_calibration = 0

    # Setup camera feed
    cam_feed = cv2.VideoCapture(0, cv2.CAP_V4L)
    cam_feed.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam_feed.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Setup event to stop sensor reading thread on exit
    thread_shutdown = Event()
    event_wait_camera_frame = Event()
    lcd_screen_change = Event()

    # Setup and run sensor reading thread
    sensor_thread = Thread(target=sensor_reading_thread, args=(thread_shutdown,))
    sensor_thread.start()

    # Setup LCD display thread
    display_thread = Thread(target=lcd_display_thread, args=(thread_shutdown,))
    display_thread.start()

    # Setup aruco marker thread
    aruco_detection_thread = Thread(target=aruco_detector_thread, args=(thread_shutdown,))
    aruco_detection_thread.start()

    # Setup target detector thread
    target_detection_thread = Thread(target=target_detector_thread, args=(thread_shutdown,))
    target_detection_thread.start()

    # Run webserver
    application.run(host="0.0.0.0", threaded=True)
    print()
    
    # Set event to stop sensor reading task
    thread_shutdown.set()

    # Wait for thread to end
    sensor_thread.join(timeout=5)
    display_thread.join(timeout=5)
    aruco_detection_thread.join(timeout=5)
    target_detection_thread.join(timeout=5)

    # Release opencv camera object
    cam_feed.release()

    print("Webserver Shutdown, Goodbye")
    