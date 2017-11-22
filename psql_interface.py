#!/usr/bin/python

import psycopg2
import datetime

PSQL_DB = "dc"
PSQL_USER = "larry"
PSQL_PW = "larry"
PSQL_PORT = 5432
PSQL_IP = "127.0.0.1"

class query_t:
	key = "";
	value = "";
	modified_by = "";
	time_modified = "";
	temp1 = "";
	temp2 = "";
	temp3 = "";

def GET(cur, query):
	res = query_t()
	#get_q = "SELECT * FROM keys WHERE key = " + "'"+str(query.key)+"' ORDER BY time_modified DESC"
	get_key = "SELECT * FROM keys WHERE key = %(key)s ORDER BY time_modified DESC"
	get_param = {'key': query.key}
	print get_key
	try:
		cur.execute(get_key, get_param)
	except DatabaseError, exception:
		print exception
		return -1, res
	finally:
		rows = cur.fetchall()
		if not rows:
			return 0, res
		row = rows[0]
		res.key = row[0]
		res.value = row[1]
		res.modified_by = row[2]
		res.time_modified = row[3]
		res.temp1 = row[4]
		res.temp2 = row[5]
		res.temp3 = row[6]
		return 1, res

def INSERT(cur, query):
	#insert_query = ("INSERT INTO keys(key, value, modified_by, time_modified," 
	#	+ " temp1, temp2, temp3)" + " VALUES(" + "'"+str(query.key)+"'," + "'"
	#	+ query.value+"'," + "'"+query.modified_by+"'," + "'"+str(datetime.datetime.now())+"'," 
	#	+ "'"+query.temp1+"'," + "'"+query.temp2+"'," + "'"+query.temp3+"')")
	insert_key = "INSERT INTO keys(key, value, modified_by, time_modified, temp1, temp2, temp3) VALUES (%(key)s, %(value)s, %(modified_by)s, %(time_modified)s, %(temp1)s, %(temp2)s, %(temp3)s)"
	insert_param = {'key': query.key, 'value': query.value, 'modified_by': query.modified_by, 'time_modified': datetime.datetime.now(), 'temp1': "", 'temp2': "", 'temp3': ""}
	print insert_key
	try:
		cur.execute(insert_key, insert_param)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		return 1

def DELETE(cur, query):
	#delete_query = "DELETE FROM keys WHERE key = " + "'"+str(query.key)+"'"
	delete_key = "DELETE FROM keys WHERE key = %(key)s"
	delete_param = {'key': query.key}
	print delete_key
	try:
		cur.execute(delete_key, delete_param)
	except DatabaseError, exception:
		print exception
		#TODO:
		#if key not found give another exception
		


		return -1
	finally:
		return 1

def open_db():
	#print "connecting to database: dc ..."
	conn = psycopg2.connect(database = PSQL_DB, user = PSQL_USER, 
							password = PSQL_PW, host = PSQL_IP, port = PSQL_PORT)
	#print "successfully connected to database dc!"
	conn.autocommit = True # avoid executing conn.commit() for every query
	cur = conn.cursor()
	print "--------------- OPEN DB ---------------"
	return cur, conn

def close_db(conn):
	conn.close()
	print "--------------- CLOSE DB ---------------"

# ------------------------------ MAIN ------------------------------ #

