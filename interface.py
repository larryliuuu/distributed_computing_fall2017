#!/usr/bin/python

import psycopg2

print "connecting to database: dc ..."

conn = psycopg2.connect(database="dc", user = "larry", 
						password = "larry", host = "localhost", port = "5432")

print "successfully connected to database dc!"

cur = conn.cursor()

cur.execute("SELECT id, name, address, salary  from COMPANY")
rows = cur.fetchall()
for row in rows:
   print "ID = ", row[0]
   print "NAME = ", row[1]
   print "ADDRESS = ", row[2]
   print "SALARY = ", row[3], "\n"

print "Operation done successfully";
conn.close()