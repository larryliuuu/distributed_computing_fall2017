#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
from urlparse import urlparse
import psql_interface
from psql_interface import query_t
import request_calls
import threading
import time

import socket
import netifaces as ni
import os
import json

SERVER_PORT = 5434
APP_NAME = 'distributed_computing/0.1'
LOCALHOST = '127.0.0.1'
config_file = "config"

CAUSAL_CONSISTENCY = True
SEQUENTIAL_CONSISTENCY = False

causal_timestamps = dict()
causal_timestamps_lock = threading.Lock()

epoch_times = dict()

buf = []

# psql database neededd when we thread requests out of server handler, (when we keep db connection open)


# have a for loop with 1) delay 2) check_timestamps for some amount of time
# if time passes and checktimestamps always fails, discard msg, print error msg etc.
# this way, we simply buffer within the thread (= by the server class instance) instead of passing buffering bw threads
# this doesnt work ^^^ :(

def init(timestamps, config_file):
	f = open(config_file)
	for ip in f.readlines():
		timestamps[ip.strip()] = 0
		epoch_times[ip.strip()] = time.time() 

def check_timestamps(rcv_ip, rcv_timestamps):
	if rcv_ip == LOCALHOST:
		rcv_ip = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
	if rcv_timestamps[rcv_ip] == 1 + causal_timestamps[rcv_ip]:
		for ip, seq_num in rcv_timestamps:
			if ip != rcv_ip:
				if seq_num > causal_timestamps[ip]:
					return False
		return True
	else:
		return False

def buffer_msg(timestamps, rcv_ip, op, key, value):
	buf.append((timestamps, rcv_ip, op, key, value))

def check_buffer():
	for (timestamps, rcv_ip, op, key, value) in buf:
		if check_timestamps(rcv_ip, timestamps):
			if op == 'GET':
				exec_GET(key)
			elif op == 'POST':
				exec_POST(key, value)
			elif op == 'DELETE':
				exec_DELETE(key)
			else:
				print "error: no operation"
				exit()

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
				if 'vt' in self.headers:
					self.rcv_vt = json.loads(self.headers['vt'])
					self.rcv_ip = self.client_address[0]
				else:
					self.send_response(401) # vector timestamp not included
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
		if not check_timestamps(self.rcv_ip, self.rcv_vt):
			while True:
				time.sleep(5)
				if check_timestamps(self.rcv_ip, self.rcv_vt):
					break

		#if not check_timestamps:
		#	buffer_msg(self.headers['vt'], self.client_address[0], 'GET', self.query_components['key'], '')

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
		if not check_timestamps(self.rcv_ip, self.rcv_vt):
			while True:
				print self.rcv_vt
				time.sleep(5)
				if check_timestamps(self.rcv_ip, self.rcv_vt):
					break

		cur, conn = psql_interface.open_db()
		query = query_t()

		query.key = self.query_components["key"]
		query.value = self.query_components["value"]
		query.modified_by = self.query_components["host"]

		retval = psql_interface.INSERT(cur, query)
		if retval:
			print "INSERT " + query.key + " SUCCESS"
			self.send_response(200)
		else:
			print "INSERT " + query.key + " ERROR"
			self.send_response(503) # database error
		
		psql_interface.close_db(conn)

	def do_DELETE(self):
		if not self.verify():
			return
		if not check_timestamps(self.rcv_ip, self.rcv_vt):
			while True:
				time.sleep(5)
				if check_timestamps(self.rcv_ip, self.rcv_vt):
					break

		cur, conn = psql_interface.open_db()
		query = query_t()
		query.key = self.query_components["key"]

		retval = psql_interface.DELETE(cur, query)
		if retval:
			print "DELETE " + query.key + " SUCCESS"
			self.send_response(200)
		else:
			print "DELETE " + query.key + " ERROR"
			self.send_response(503) # database error

		psql_interface.close_db(conn)

def server(data):
	SocketServer.TCPServer.allow_reuse_address = True
	httpd = SocketServer.TCPServer(("", SERVER_PORT), RequestHandler)
	httpd.daemon = True
	httpd.serve_forever()

def process_request(req):
		cmd_idx = req.find(' ')
		cmd = req[0:cmd_idx]

		ip = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
		if (cmd == 'READ'):
			key = req[cmd_idx+1:]
			with causal_timestamps_lock:
				causal_timestamps[ip] += 1
			request_calls.READ(key, json.dumps(causal_timestamps))
		elif (cmd == 'WRITE'):
			key_idx = req.find(' ', cmd_idx+1)
			key = req[cmd_idx+1:key_idx]
			value = req[key_idx+1:]
			with causal_timestamps_lock:
				causal_timestamps[ip] += 1
			request_calls.WRITE(key, value, ip, json.dumps(causal_timestamps))
		elif (cmd == 'DELETE'):
			key = req[cmd_idx+1:]
			with causal_timestamps_lock:
				causal_timestamps[ip] += 1
			request_calls.DELETE(key, json.dumps(causal_timestamps))
		elif (req == 'vt'):
			print causal_timestamps
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

'''-------------------------------------------------- MAIN --------------------------------------------------'''

if CAUSAL_CONSISTENCY:
	init(causal_timestamps, config_file)
elif SEQUENTIAL_CONSISTENCY:
	print "do sequential"
	#init(sequntial_timestamps, config_file)

t_server = threading.Thread(target=server, kwargs={"data": "server data input param"})
t_server.daemon = True
t_server.start()

t_client = threading.Thread(target=client, kwargs={"data": "client data input param"})
t_client.start()


'''

memtable only keeps track of recently performed queries (key, value) pairs
if key is not in memtable, do query directly from psql

create a class that runs this. create an instance variable on the class of a memtable. make a thread that flushes the memtable
bloom filter
'''



