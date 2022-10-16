#!/bin/bash

# Create database for EGH455 sensors

# Check if bash script was run as sudo (required root permissions)
user_check() {
	if [ $(id -u) -ne 0 ]; then
		printf "Script must be run as root. Try 'sudo $0'\n"
		exit 1
	fi
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
create_database