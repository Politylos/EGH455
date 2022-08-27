#!/usr/bin/env python3

import cv2
import sys
import time

# Check command line arguments
if (len(sys.argv) == 1):
    filename = "output.mp4"
else:
    filename = str(sys.argv[1])

print("\n\nRecording video to " + filename + ".")
print("Press CTRL-C to exit.")

# Open camera object
cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)

# Check camera is open successfully
if (cap.isOpened() == False):
    print("Error opening camera.")
    exit()

# Open videowriter object
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
out = cv2.VideoWriter(filename, fourcc, 30, (640, 480), isColor=True)
start_time = time.time()

# Loop to record video frames
try:
    while(True):
        ret, frame = cap.read()
        frame = cv2.resize(frame, (640, 480))
        #cv2.imshow('frame', frame)
        out.write(frame)
except KeyboardInterrupt:
    # Close objects
    end_time = time.time()
    record_time = "{:.2f}".format(end_time - start_time)
    print("\nClosing video recording.")
    print("Recorded " + record_time + " seconds of video.")
    cap.release()
    out.release()
    cv2.destroyAllWindows()
