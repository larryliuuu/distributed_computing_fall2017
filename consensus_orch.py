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
import importlib
from inspect import getmembers

from algo_calls import *

from subprocess import check_output

SERVER_IP = '192.168.0.114'
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

timestamps_flag = False

# psql database neededd when we thread requests out of server handler, (when we keep db connection open)

# have a for loop with 1) delay 2) check_timestamps for some amount of time
# if time passes and checktimestamps always fails, discard msg, print error msg etc.
# this way, we simply buffer within the thread (= by the server class instance) instead of passing buffering bw threads
# this doesnt work ^^^ :(
def init_averaging(config_file):
	f = open(config_file)
	neighbors = []
	for ip in f.readlines():
		neighbors.append(ip.strip())
	return neighbors 

def init(timestamps, config_file):
	f = open(config_file)
	for ip in f.readlines():
		timestamps[ip.strip()] = 0
		epoch_times[ip.strip()] = time.time() 
		#if ip.strip() == str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr']):
		#	timestamps[ip.strip()] = 6


def check_timestamps(rcv_ip, rcv_timestamps):
	return True

	global causal_timestamps

	if rcv_ip == LOCALHOST: # recieved messaged from self
		rcv_ip = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
		if rcv_timestamps[rcv_ip] == causal_timestamps[rcv_ip]:
			for ip, seq_num in rcv_timestamps.iteritems():
				if ip != rcv_ip:
					if seq_num > causal_timestamps[ip]:
						return False
			return True
		else:
			return False

	# received message from forgeign host
	if rcv_timestamps[rcv_ip] == 1 + causal_timestamps[rcv_ip]: 
		for ip, seq_num in rcv_timestamps.iteritems():
			if ip != rcv_ip:
				if seq_num > causal_timestamps[ip]:
					return False
		with causal_timestamps_lock:
			causal_timestamps[rcv_ip] += 1
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
	def log_message(self, format, *args):
		return
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
				#else:
				#	self.send_response(401) # vector timestamp not included
				#	return False
				return True
			else:
				self.send_response(400) # user agent incorrect
				return False

		self.send_response(400) # user-agent not found
		return False

	def do_GET(self):
		if not self.verify():
			return
		log_flag = True
		if timestamps_flag:
			while not check_timestamps(self.rcv_ip, self.rcv_vt):
				if log_flag:
					print "buffer msg from: " + self.rcv_ip + " ",
					print causal_timestamps
					log_flag = False
				time.sleep(.5)

		#if not check_timestamps:
		#	buffer_msg(self.headers['vt'], self.client_address[0], 'GET', self.query_components['key'], '')

		cur, conn = psql_interface.open_db()
		query = query_t()
		query.key = self.query_components["key"]
		query.version = self.query_components["version"]
		retval, res = psql_interface.GET(cur, query)

		if retval:
			#print "GET " + query.key + " SUCCESS"
			self.send_response(200)
			self.end_headers()
			self.wfile.write(query.key + ":" + str(res.value)) # return more informtion here
		elif retval == 0: 
			#print "GET " + query.key + " NOT FOUND"
			self.send_response(404) # key not found
		elif retval == -1:
			print "GET " + query.key + " ERROR"
			self.send_response(503) # database error

		psql_interface.close_db(conn)

	def do_POST(self):
		if not self.verify():
			return
		log_flag = True
		if timestamps_flag:
			while not check_timestamps(self.rcv_ip, self.rcv_vt) :
				if log_flag:
					print "buffer msg from: " + self.rcv_ip + " ",
					print causal_timestamps
					log_flag = False
				time.sleep(.5)

		cur, conn = psql_interface.open_db()

		query = query_t()
		query.key = self.query_components["key"]
		query.value = self.query_components["value"]
		query.modified_by = self.query_components["host"]
		query.version = self.query_components["version"]

		key_exists, res = psql_interface.GET(cur, query)
		if key_exists:
			retval = psql_interface.UPDATE(cur, query)
		else:
			retval = psql_interface.INSERT(cur, query)
		if retval:
			#print "WRITE " + query.key + " " + query.value + " SUCCESS"
			self.send_response(200)
		else:
			print "WRITE " + query.key + " " + query.value + " ERROR"
			self.send_response(503) # database error
		
		psql_interface.close_db(conn)

	def do_DELETE(self):
		if not self.verify():
			return
		log_flag = True
		if timestamps_flag:
			while not check_timestamps(self.rcv_ip, self.rcv_vt):
				if log_flag:
					print "buffer msg from: " + self.rcv_ip + " ",
					print causal_timestamps
					log_flag = False
				time.sleep(.5)

		cur, conn = psql_interface.open_db()
		query = query_t()
		query.key = self.query_components["key"]

		retval = psql_interface.DELETE(cur, query)
		if retval:
			#print "DELETE " + query.key + " SUCCESS"
			self.send_response(200)
		else:
			print "DELETE " + query.key + " ERROR"
			self.send_response(503) # database error

		psql_interface.close_db(conn)

def server(data):
	SocketServer.ThreadingTCPServer.allow_reuse_address = True
	httpd = SocketServer.ThreadingTCPServer(("", SERVER_PORT), RequestHandler)
	httpd.daemon = True
	httpd.serve_forever()

def process_request(req):
	global causal_timestamps
	cmd_idx = req.find(' ')
	cmd = req[0:cmd_idx].upper()

	ip = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
	if (cmd == 'READ'):
		key = req[cmd_idx+1:]
		with causal_timestamps_lock:
			causal_timestamps[ip] += 1
		request_calls.READ(SERVER_IP, key, json.dumps(causal_timestamps))
	elif (cmd == 'WRITE'):
		key_idx = req.find(' ', cmd_idx+1)
		key = req[cmd_idx+1:key_idx]
		value = req[key_idx+1:]
		with causal_timestamps_lock:
			causal_timestamps[ip] += 1
		request_calls.WRITE(SERVER_IP, key, value, ip, json.dumps(causal_timestamps))
	elif (cmd == 'DELETE'):
		key = req[cmd_idx+1:]
		with causal_timestamps_lock:
			causal_timestamps[ip] += 1
		request_calls.DELETE(SERVER_IP, key, json.dumps(causal_timestamps))
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


def averaging_algo():
	# begin program run
	config = INIT(config_file)

	# adjust weights & initialize value
	n_weight = 1. / config.network_size
	host_weight = 1. - config.neighbor_size * n_weight
	key = config.variables[0][0]
	val = config.variables[0][1] 

	for curr_iter in range(1, config.iterations):
		# pre-round computations
		val = val * host_weight

		# per-round computations
		for n in config.neighbors:
			res = READ(key, curr_iter-1, n)
			val += res * n_weight

		# post-round computations
		WRITE(key, str(val), curr_iter)

	# close program run
	print "Final average value: " + str(val)
	CLEANUP()

def run_algo():

	config = INIT(config_file)

	algorithm = open("algorithm.py", "w+")

	algorithm.write("from algo_calls import *\n")
	algorithm.write("def algo(config):\n")
	for line in config.code["init"]:
		algorithm.write("\t" + line)

	algorithm.write("\tfor curr_iter in range(1, config.iterations):\n")
	for line in config.code["pre"]:
		algorithm.write("\t\t" + line)

	algorithm.write("\t\tfor n in config.neighbors:\n")
	for line in config.code["round"]:
		algorithm.write("\t\t\t" + line)

	for line in config.code["post"]:
		algorithm.write("\t\t" + line)

	algorithm.write("\n")
	algorithm.close()

	code = __import__("algorithm")
	code.algo(config)


	CLEANUP()



def client(data):
	global quit_flag
	while True:
		user_cmd = raw_input("")
		process_request(user_cmd)

def add_neighbors():
	neighbors = {}
	address = "192.168.0.255"

	cmd = "ping " + address + " -t 3" + " -b"
	out = check_output(cmd, shell=True)
	for line in out.split("\n"):
		if line.split(' ')[0] == '64':
			IP = line.split(' ')[3][:-1]
			if IP not in neighbors:
				neighbors[IP] = 0

	n_file = open("neighbors", "w+")
	for neighbor in neighbors:
		n_file.write(neighbor + "\n")

def getopts(argv):
    opts = {}  
    while argv: 
        if argv[0][0] == '-': 
            opts[argv[0]] = 0 
        argv = argv[1:] 
    return opts

'''-------------------------------------------------- MAIN --------------------------------------------------'''
print "--------------------------------------------------"
print "Distributed Key Value Storage System Usage: "
print "    READ [key]"
print "    WRITE [key] [value]"
print "    DELETE [key]"
print "--------------------------------------------------"

if CAUSAL_CONSISTENCY:
	init(causal_timestamps, config_file)
elif SEQUENTIAL_CONSISTENCY:
	print "do sequential"
	#init(sequntial_timestamps, config_file)

t_server = threading.Thread(target=server, kwargs={"data": "server data input param"})
t_server.daemon = True
t_server.start()

try:
    os.remove("neighbors")
except OSError:
    pass

from sys import argv
myargs = getopts(argv)
if '-n' in myargs:  # Example usage.
	add_neighbors()

run_algo()

#t_client = threading.Thread(target=client, kwargs={"data": "client data input param"})
#t_client.start()




