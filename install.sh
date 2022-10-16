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
        echo 'KillSignal=SIGINT'
        echo 'Type=idle'
        echo 'ExecStart=/bin/bash -c '\''cd /home/group12/EGH455/wvi/webserver/ && python app.py 2>&1 >> /home/group12/EGH455/wvi/logs.log'\'
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
    sudo apt install python3 -y
    sudo apt install openssh-server -y
    sudo apt install libopencv-dev -y
    sudo apt install python3-opencv -y
    sudo apt install python-is-python3 -y
    sudo apt install mariadb-server -y
    sudo apt install libmariadb3 -y
    sudo apt install libmariadb-dev -y
    sudo apt install python3-pip -y
    pip3 install Flask
    pip3 install mariadb
    pip3 install opencv-contrib-python
    pip3 install imutils
}

# Create database
create_database() {
    # Check if mariadb is installed
    if ! command -v mariadb &> /dev/null
    then
        echo "MariaDB not installed"
        exit
    fi
    # Create database
    sudo mariadb -u root -e "CREATE USER IF NOT EXISTS 'group12'@'localhost' IDENTIFIED BY '1234';
        GRANT ALL PRIVILEGES ON *.* TO 'group12'@'localhost';
        CREATE DATABASE IF NOT EXISTS egh455;
        USE egh455;
        CREATE TABLE IF NOT EXISTS sensors (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
			    time  DATETIME,
                cpu_temp DOUBLE,
                bme_temp DOUBLE,
                bme_pres DOUBLE,
                bme_humi DOUBLE,
                env_ligh DOUBLE,
                gas_oxid DOUBLE,
                gas_redu DOUBLE,
                gas_nh3 DOUBLE);"
}

user_check
install_requirements
make_startup
fix_user
fix_qut_time
create_database

echo
echo
echo "Please reboot system!"