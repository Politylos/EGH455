#!/bin/bash

# Script file for loading startup programs. This is called from systemd.

/usr/bin/python /home/group12/EGH455/display/display.py &

while :
do
sleep 120;
done