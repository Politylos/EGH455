from flask import Flask, render_template, Response
import mariadb
from datetime import datetime
from camera import VideoCamera

# Renders a html page showing a basic chart.js using data from mariadb
# Requirements: mariadb database named 'egh455' with a table named 'sensors'
# See read_database.py in wvi/test folder for info

# Usage: python app.py


# Support functions
def get_data():
    # Connect to database
    try:
        conn = mariadb.connect(
            user='group12',
            password='1234',
            host='127.0.0.1',
            port=3306,
            database='egh455')
    except mariadb.Error as e:
        print(f"Error connecting to database: {e}")
        # sys.exit(1)
    else:
        print("Database connection established!")
    # Read from database
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
            #labels = [{row[1].strftime("%d/%m/%Y, %H:%M:%S")} for row in results]
            labels = [row[1].strftime("%d/%m/%Y, %H:%M:%S") for row in results]
            #[label.strftime("%d/%m/%Y, %H:%M:%S") for label in labels]
            values = [row[2] for row in results]
            # for row in results:
            #     index_red = row[0]
            #     time_read = row[1]
            #     sensor1 = row[2]
            #     sensor2 = row[3]
            #     sensor3 = row[4]
            #     sensor4 = row[5]
            #     sensor5 = row[6]
            #     sensor6 = row[7]
            #     sensor7 = row[8]
            #     sensor8 = row[9]
            #     print(f"Idx: {index_red} dt: {time_read} s1: {sensor1} s2: {sensor2} s3: {sensor3} s4: {sensor4} s5: {sensor5} s6: {sensor6} s7: {sensor7} s8: {sensor8}\n")
    conn.close()
    return labels, values

# Generate camera image
def gen(camera):
    while True:
        # Get camera frame
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Flask functions
app = Flask(__name__)

# render template
@app.route("/")
def index():
    labels, values = get_data()
    return render_template("index.html", labels=labels, values=values)

# Render video feed
@app.route("/video_feed")
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

# # Get labels from database
# @app.route("/labels")
# def labels():
#     return Response(get_data()[0])

# # Get values from database
# @app.route("/values")
# def values():
#     return Response(get_data()[1])

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000',debug=True)