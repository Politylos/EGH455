from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
# import cv2 as cv
# from PIL import Image
import sys

# Raspberry Pi library
import cv2 as cv
from PIL import Image
import ST7735 as ST7735
from time import sleep
import numpy as np

cap = cv.VideoCapture(0)
cap.set(3, 2592)  # Set horizontal resolution
cap.set(4, 1944)  # Set vertical resolution
if not cap.isOpened():
    print("Cannot open camera")
    exit()
    
# Create ST7735 LCD display class.
disp = ST7735.ST7735(
    port=0,
    cs=ST7735.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    rotation=90,
    spi_speed_hz=4000000
)

def pose_esitmation(frame, corners, ids, aruco_dict_type, arucoParams ,matrix_coefficients, distortion_coefficients):

    '''
    frame - Frame from the video stream
    matrix_coefficients - Intrinsic matrix of the calibrated camera
    distortion_coefficients - Distortion coefficients associated with your camera
    return:-
    frame - The frame with the axis drawn on it
    '''

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)
    # parameters = cv2.aruco.DetectorParameters_create()


    # corners, ids, rejected_img_points = cv2.aruco.detectMarkers(frame, aruco_dict_type , parameters=arucoParams,
    #     cameraMatrix=matrix_coefficients,
    #     distCoeff=distortion_coefficients)

        # If markers are detected
    for i in range(0, len(ids)):
        # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
        rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients,
        distortion_coefficients)

        # Draw Axis
        cv2.drawFrameAxes(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)
        cv2.putText(frame, str(tvec), (bottomRight[0], bottomRight[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame




# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--type", type=str, default="DICT_ARUCO_ORIGINAL", help="type of ArUCo tag to detect")
# ap.add_argument("-k", "--K_Matrix", required=True, help="Path to calibration matrix (numpy file)")
# ap.add_argument("-d", "--D_Coeff", required=True, help="Path to distortion coefficients (numpy file)")
args = vars(ap.parse_args())

ARUCO_DICT = {
    # "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_5X5_50,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_5X5_100,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_5X5_250,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_5X5_1000,
	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

# verify that the supplied ArUCo tag exists and is supported by
# OpenCV
if ARUCO_DICT.get(args["type"], None) is None:
	print("[INFO] ArUCo tag of '{}' is not supported".format(
		args["type"]))
	sys.exit(0)
# load the ArUCo dictionary and grab the ArUCo parameters
print("[INFO] detecting '{}' tags...".format(args["type"]))
arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[args["type"]])
arucoParams = cv2.aruco.DetectorParameters_create()

# Position code
k = np.array([[1944.651788, 0.00000000 ,1321.460626],
[  0.,         1944.904996 ,996.893260],
[  0.,           0.,           1.        ]])

d = np.array(([[0.136239 , -0.180998, 0.002973 , 0.002750 ,0.000000]]))

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
# vs = VideoStream(src=0).start()
time.sleep(2.0)

WIDTH = disp.width
HEIGHT = disp.height

# loop over the frames from the video stream
while True:
    # print("kahdh")
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 1000 pixels
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    frame = imutils.resize(frame, width=1000)
    
	# detect ArUco markers in the input frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
		arucoDict, parameters=arucoParams)
 
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
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
			# compute and draw the center (x, y)-coordinates of the
			# ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
   
			# draw the ArUco marker ID on the frame
            cv2.putText(frame, str(markerID),
				(topLeft[0], topLeft[1] - 15),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.5, (0, 255, 0), 2)
            
                # estimate pose
        frame = pose_esitmation(frame, corners_pose, ids, arucoDict, arucoParams , k, d)
        


	# show the output frame
    # cv2.imshow("Frame", frame)
    
    #convert to PIL
    im_pil = Image.fromarray(frame)
    
     # Display the resulting frame
    # Resize the image
    im_pil = im_pil.resize((WIDTH, HEIGHT))

    # show on the LCD screen
    disp.display(im_pil)
    key = cv2.waitKey(1) & 0xFF
	# if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
# do a bit of cleanup
cv2.destroyAllWindows()
cap.stop()
