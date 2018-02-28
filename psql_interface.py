#!/usr/bin/python

import psycopg2
import datetime

PSQL_DB = "dc"
PSQL_USER = "db_user"
PSQL_PW = "db_pw"
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
	get_key = "SELECT * FROM keys WHERE key = %(key)s AND version = %(version)s ORDER BY time_modified DESC"
	get_param = {'key': query.key, 'version': query.version}
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
	insert_key = "INSERT INTO keys(key, value, modified_by, time_modified, version, temp2, temp3) VALUES (%(key)s, %(value)s, %(modified_by)s, %(time_modified)s, %(version)s, %(temp2)s, %(temp3)s)"
	insert_param = {'key': query.key, 'value': query.value, 'modified_by': query.modified_by, 'time_modified': datetime.datetime.now(), 'version': query.version, 'temp2': "", 'temp3': ""}
	try:
		cur.execute(insert_key, insert_param)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		return 1

def UPDATE(cur, query):
	insert_key = "UPDATE keys SET value = %(value)s, modified_by = %(modified_by)s,  time_modified = %(time_modified)s, temp1 =  %(temp1)s, temp2 = %(temp2)s, temp3 = %(temp3)s WHERE key = %(key)s"
	insert_param = {'key': query.key, 'value': query.value, 'modified_by': query.modified_by, 'time_modified': datetime.datetime.now(), 'temp1': "", 'temp2': "", 'temp3': ""}
	try:
		cur.execute(insert_key, insert_param)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		return 1

def DELETE(cur, query):
	delete_key = "DELETE FROM keys WHERE key = %(key)s"
	delete_param = {'key': query.key}
	try:
		cur.execute(delete_key, delete_param)
	except DatabaseError, exception:
		print exception
		return -1
	finally:
		return 1

def open_db():
	#print "connecting to database: dc ..."
	try: 
		conn = psycopg2.connect(database = PSQL_DB, user = PSQL_USER, 
							password = PSQL_PW, host = PSQL_IP, port = PSQL_PORT)
	except:
		print "unable to connect"
	#print "successfully connected to database dc!"
	conn.autocommit = True # avoid executing conn.commit() for every query
	cur = conn.cursor()
	#print "--------------- OPEN DB ---------------"
	return cur, conn

def close_db(conn):
	conn.close()
	#print "--------------- CLOSE DB ---------------"

# ------------------------------ MAIN ------------------------------ #

