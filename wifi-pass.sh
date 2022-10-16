#!/bin/bash

echo "Enter your password "
read -s PASSWORD
echo "Your encrypted password is:"
echo -n ${PASSWORD} | iconv -t utf16le | openssl md4 | cut -d' ' -f2 | (echo -n "hash:" && cat)
echo "Use this in your wpa supplicant config file"
