#!/usr/bin/python

import psycopg2
import datetime

class key_t:
	key_num = -1;
	value = "";
	modified_by = "";
	time_modified = "";
	temp1 = "";
	temp2 = "";
	temp3 = "";

def GET(cur, key):
	res = []
	get_query = "SELECT * FROM keys WHERE key_num = " + str(key.key_num)
	try:
		cur.execute(get_query)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		rows = cur.fetchall()
		for row in rows:
			out_key = key_t()
			out_key.key_num = row[0]
			out_key.value = row[1]
			out_key.modified_by = row[2]
			out_key.time_modified = row[3]
			out_key.temp1 = row[4]
			out_key.temp2 = row[5]
			out_key.temp3 = row[6]
			res.append(out_key)
		return res

def INSERT(cur, key):
	insert_res = "INSERT INTO keys(key_num, value, modified_by, time_modified, temp1, temp2, temp3)" + "VALUES(" + "'"+str(key.key_num)+"'," + "'"+key.value+"'," + "'"+key.modified_by+"'," + "'"+str(key.time_modified)+"'," + "'"+key.temp1+"'," + "'"+key.temp2+"'," + "'"+key.temp3+"')"
	try:
		cur.execute(insert_res)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		return 1

def POST(cur, key):
	update_query = "UPDATE keys SET value = " + "'"+key.value+"' WHERE key_num = " + str(key.key_num) 
	try:
		cur.execute(update_query)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		return 1

def DELETE(cur, key):
	delete_query = "DELETE FROM keys WHERE key_num = " + str(key.key_num)
	try:
		cur.execute(delete_query)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		return 1

# ------------------------------ MAIN ------------------------------ #

print "connecting to database: dc ..."

conn = psycopg2.connect(database="dc", user = "larry", 
						password = "larry", host = "localhost", port = "5432")

print "successfully connected to database dc!"

conn.autocommit = True # avoid executing conn.commit() for every query
cur = conn.cursor()

test_key = key_t()
test_key.key_num = 11
test_key.value = "updated_value_x"
test_key.time_modified = datetime.datetime.now()

'''
if (GET(cur, test_key)):
	insert_res = POST(cur, test_key)
else:
	update_res = INSERT(cur, test_key)
'''

delete_res = DELETE(cur, test_key)
print delete_res


get_res = GET(cur, test_key)
if get_res:
	print "get request for key: " + str(test_key.key_num)
	print "value: " + get_res[0].value
	print "modified_by: " + get_res[0].modified_by
	print "time_modified: " + get_res[0].time_modified
	print "temp1: " + get_res[0].temp1
	print "temp2: " + get_res[0].temp2
	print "temp3: " + get_res[0].temp3	
else:
	print "key " + str(test_key.key_num) + " does not exist"

conn.close()