#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
from urlparse import urlparse
import psql_interface
from psql_interface import query_t
import request_calls
import threading

import socket
import netifaces as ni
import os

SERVER_PORT = 5434
APP_NAME = 'distributed_computing/0.1'

CAUSAL_CONSISTENCY = True
SEQUENTIAL_CONSISTENCY = False

causal_timestamps = dict()
causal_timestamps_lock = threading.Lock()

class RequestHandler(BaseHTTPRequestHandler):
	server_version = APP_NAME
	def verify(self):
		if 'user-agent' in self.headers:
			if self.headers['user-agent'] == APP_NAME:
				query = urlparse(self.path).query
				if 'key' not in query:
					self.send_response(400) # key not found
					return False

				self.query_components = dict(qc.split("=") for qc in query.split("&"))

				'''
				if CAUSAL_CONSISTENCY:
					check if client ip is in membership list (check timestamps dict)
					if it is not: add to timestamp, init with timestamp 0
					if it is: 
						- spawn separate thread to take care of request: 
						do logic around checking timestamp number, may need to queue request
						- may need to modify this class, to put functions outside of class
				'''
				if self.command == 'GET':
					if 'key' not in self.query_components:
						self.send_response(400) # key not found
						return False
				if self.command == 'POST':
					if 'key' not in self.query_components:
						self.send_response(400) # key not found
						return False
					if 'value' not in self.query_components:
						self.send_response(400) # val not found
						return False
				if self.command == 'DELETE':
					if 'key' not in self.query_components:
						self.send_response(400) # key not found
						return False
				return True
			else:
				self.send_response(400) # user agent incorrect
				return False
		self.send_response(400) # user-agent not found
		return False

	def do_GET(self):
		if not self.verify():
			return

		cur, conn = psql_interface.open_db()
		query = query_t()
		query.key = self.query_components["key"]
		retval, res = psql_interface.GET(cur, query)

		if retval:
			self.send_response(200, query.key + "=" + str(res))
		elif retval == 0: 
			self.send_response(404) # key not found
		elif retval == -1:
			self.send_response(503) # database error

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
			self.send_response(200)
			#200
		else:
			print "INSERT " + query.key + " ERROR"
			self.send_response(503) #database error
		
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
			self.send_response(200) #deleted
		else:
			print "DELETE " + query.key + " ERROR"
			self.send_response(503) #database error

		psql_interface.close_db(conn)

def server(data):
	SocketServer.TCPServer.allow_reuse_address = True
	httpd = SocketServer.TCPServer(("", SERVER_PORT), RequestHandler)
	httpd.serve_forever()

def process_request(req):
		cmd_idx = req.find(' ')
		cmd = req[0:cmd_idx]

		ip = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
		if (cmd == 'READ'):
			key = req[cmd_idx+1:]
			request_calls.READ(key)
		elif (cmd == 'WRITE'):
			key_idx = req.find(' ', cmd_idx+1)
			key = req[cmd_idx+1:key_idx]
			value = req[key_idx+1]
			request_calls.WRITE(key, value, ip)
		elif (cmd == 'DELETE'):
			key = req[cmd_idx+1:]
			request_calls.DELETE(key)
		elif (req == 'quit'):
			os._exit(1)
		elif (req == 'help'):
			print "--------------------------------------------------"
			print "Distributed Key Value Storage System Usage: "
			print "    READ [key]"
			print "    WRITE [key] [value]"
			print "    DELETE [key]"
			print "--------------------------------------------------"
		else:
			print "Invalid Command. Type 'help' for more information or 'quit' to exit program."

def client(data):
	global quit_flag
	while True:
		user_cmd = raw_input("")
		process_request(user_cmd)

t_server = threading.Thread(target=server, kwargs={"data": "server data input param"})
t_server.start()

t_client = threading.Thread(target=client, kwargs={"data": "client data input param"})
t_client.start()


'''

memtable only keeps track of recently performed queries (key, value) pairs
if key is not in memtable, do query directly from psql

create a class that runs this. create an instance variable on the class of a memtable. make a thread that flushes the memtable
bloom filter
'''



