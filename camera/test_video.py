#!/usr/bin/env python3

import cv2
def show_webcam():
    cam = cv2.VideoCapture(0)
    while True:
        ret, img = cam.read()
        cv2.imshow('camera', img)
        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()

def main():
    show_webcam()

if __name__ == '__main__':
    main()