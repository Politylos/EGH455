#!/bin/bash

# Delete egh455 database
# Check if bash script was run as sudo (required root permissions)
user_check() {
	if [ $(id -u) -ne 0 ]; then
		printf "Script must be run as root. Try 'sudo $0'\n"
		exit 1
	fi
}

# Delete database
delete_database() {
    if ! command -v mariadb &> /dev/null
    then
        echo "MariaDB not installed"
        exit
    fi
    sudo mariadb -u root -e "DROP DATABASE egh455;"
}

user_check
delete_database