#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
from urlparse import urlparse
import psql_interface
from psql_interface import query_t
import request_calls

SERVER_PORT = 5434
APP_NAME = 'distributed_computing/0.1'

'''
1. create server response:
	send error codes back to client via http
	if no error, send response code
	send data if any back to client
'''

class RequestHandler(BaseHTTPRequestHandler):
	def verify(self):
		if 'user-agent' in self.headers:
			if self.headers['user-agent'] == APP_NAME:
				query = urlparse(self.path).query
				self.query_components = dict(qc.split("=") for qc in query.split("&"))
				'''
					TODO: error checking for client's input parameters for the query/req
					ex. return error code, check which error code, if client did not put a value for a key in a POST req
					if get: has key, if post: has key/value, if delete, has key, etc.
					'''
				return True
		self.error()
		return False

	def do_GET(self):
		if not self.verify():
			return
		cur, conn = psql_interface.open_db()
		query = query_t()
		query.key = self.query_components["key"]
		retval, res = psql_interface.GET(cur, query)

		if retval:
			print vars(res)
			print "GET " + query.key + " SUCCESS"
			# return OK 200 in response
		elif retval == 0: 
			print "key not found - return 404"
		elif retval == -1:
			print "exception - return 400?"
		psql_interface.close_db(conn)

	def do_POST(self):
		if not self.verify():
			return
		cur, conn = psql_interface.open_db()
		query = query_t()

		query.key = self.query_components["key"]
		query.value = self.query_components["value"]
		query.modified_by = self.query_components["host"]

		retval = psql_interface.INSERT(cur, query)
		if retval:
			print "INSERT " + query.key + " SUCCESS"
		else:
			print "INSERT " + query.key + " ERROR"
		
		psql_interface.close_db(conn)

	def do_DELETE(self):
		if not self.verify():
			return
		cur, conn = psql_interface.open_db()
		query = query_t()
		query.key = self.query_components["key"]
		retval = psql_interface.DELETE(cur, query)
		if retval:
			print "DELETE " + query.key + " SUCCESS"
		else:
			print "DELETE " + query.key + " ERROR"
		psql_interface.close_db(conn)


SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.TCPServer(("", SERVER_PORT), RequestHandler)

'''

memtable only keeps track of recently performed queries (key, value) pairs
if key is not in memtable, do query directly from psql

create a class that runs this. create an instance variable on the class of a memtable. make a thread that flushes the memtable
bloom filter


'''

httpd.serve_forever()


