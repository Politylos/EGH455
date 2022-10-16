#!/bin/bash

# Script file for loading startup programs. This is called from systemd.

#/usr/bin/python '/home/group12/EGH455/wvi/webserver/app.py 2>&1 >> /home/group12/EGH455/wvi/logs..log' &

/bin/bash -c 'cd /home/group12/EGH455/wvi/webserver/ && python app.py 2>&1 >> /home/group12/EGH455/wvi/logs.log'

while :
do
sleep 120;
done
