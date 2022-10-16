#!/usr/bin/env python3

# Reads contents of database and prints to screen

#import datetime
import mariadb
import sys

def read_database():
    try:
        conn = mariadb.connect(
            user='group12',
            password='1234',
            host='127.0.0.1',
            port=3306,
            database='egh455')
    except mariadb.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    else:
        print("Database connection established!")
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sensors")
        results = cur.fetchall()
    except mariadb.Error as e:
        print(f"Error reading database: {e}")
    else:
        if len(results) == 0:
            print("Database empty!")
        else:
            for row in results:
                index_read = row[0]
                time_read = row[1]
                sensor1 = row[2]
                sensor2 = row[3]
                sensor3 = row[4]
                sensor4 = row[5]
                sensor5 = row[6]
                sensor6 = row[7]
                sensor7 = row[8]
                sensor8 = row[9]
                print(f"Idx: {index_read} dt: {time_read} s1: {sensor1} s2: {sensor2} s3: {sensor3} s4: {sensor4} s5: {sensor5} s6: {sensor6} s7: {sensor7} s8: {sensor8}\n")
    conn.close()

def main():
    read_database()

if __name__ == "__main__":
    main()