#!/bin/bash

USER_HOME=/home/$SUDO_USER
STARTUP_SCRIPT_PATH=$USER_HOME/EGH455
STARTUP_SCRIPT_FILE=$STARTUP_SCRIPT_PATH/startup.sh
STARTUP_SYSTEMD_FILE=/lib/systemd/system/startup.service
NTP_CONF_FILE=/etc/systemd/timesyncd.conf

user_check() {
	if [ $(id -u) -ne 0 ]; then
		printf "Script must be run as root. Try 'sudo $0'\n"
		exit 1
	fi
}

make_startup() {
    {
        echo '[Unit]'
        echo 'Description=Startup Script for EGH455'
        echo 'After=multi-user.target'
        echo ''
        echo '[Service]'
        echo 'Type=idle'
        echo 'ExecStart=/usr/bin/sh' $STARTUP_SCRIPT_FILE
        echo ''
        echo '[Install]'
        echo 'WantedBy=multi-user.target'
    } > $STARTUP_SYSTEMD_FILE
    sudo chmod +x $STARTUP_SCRIPT_FILE
    sudo chmod 644 /lib/systemd/system/startup.service
    sudo systemctl daemon-reload
    sudo systemctl enable startup.service
}

fix_user() {
    sudo usermod -a -G dialout group12
    sudo usermod -a -G video group12
}

fix_qut_time() {
    {
        echo '[Time]'
        echo 'NTP=time.qut.edu.au ntp.ubuntu.com'
        echo 'FallbackNTP=0.oceania.pool.ntp.org 1.oceania.pool.ntp.org 2.oceania.pool.ntp.org 3.oceania.pool.ntp.org'
        echo ''
    } > $NTP_CONF_FILE
    sudo systemctl enable systemd-timesyncd.service
    sudo systemctl restart systemd-timesyncd.service
}

install_requirements() {
    sudo apt update -y
    sudo apt upgrade -y
    sudo apt install openssh-server -y
    sudo apt install libopencv-dev -y
    sudo apt install python3-opencv -y
    sudo apt install python-is-python3 -y
}

user_check
install_requirements
make_startup
fix_user
fix_qut_time

echo
echo
echo "Please reboot system!"