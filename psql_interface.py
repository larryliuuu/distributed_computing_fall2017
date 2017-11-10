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
	get_query = "SELECT * FROM keys WHERE key = " + "'"+str(query.key)+"' ORDER BY time_modified DESC"
	print get_query
	try:
		cur.execute(get_query)
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
	insert_query = ("INSERT INTO keys(key, value, modified_by, time_modified," 
		+ " temp1, temp2, temp3)" + " VALUES(" + "'"+str(query.key)+"'," + "'"
		+ query.value+"'," + "'"+query.modified_by+"'," + "'"+str(datetime.datetime.now())+"'," 
		+ "'"+query.temp1+"'," + "'"+query.temp2+"'," + "'"+query.temp3+"')")
	print insert_query
	try:
		cur.execute(insert_query)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		return 1

def DELETE(cur, query):
	delete_query = "DELETE FROM keys WHERE key = " + "'"+str(query.key)+"'"
	print delete_query
	try:
		cur.execute(delete_query)
	except DatabaseError, exception:
		print exception
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

