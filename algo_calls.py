import netifaces as ni
import requests
import time

SERVER_PORT = '5434'
APP_NAME = 'distributed_computing/0.1'

class config_t():
	neighbors = []
	network = []
	network_size = 0
	neighbor_size = 0
	iterations = 0
	staleness = 0
	blocking = True
	delay = 0 
	variables = []
	ip_self = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])

host = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
config = config_t()

def INIT(config_file):
	time.sleep(3)
	INIT_ALGO(config_file)
	INIT_KEYS(config.variables)
	return config

def INIT_KEYS(variables):
	for key, value in variables:
		DELETE(host, key)
		WRITE(host, key, str(value), 0)

def CLEAN_KEYS(keys):
	for key in keys:
		DELETE(host, key)

def READ(dst, key, version):
	global config
	payload = {'key': key, 'version': version}
	headers = {'user-agent': APP_NAME}
	r = requests.get("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	if r.status_code == 200:
		pass
	elif r.status_code == 404 and not config.blocking:
		for i in range(1, staleness):
			payload = {'key': key, 'version': (version - i)}
			r = requests.get("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
			if r.status_code == 200:
				continue
		return 0.
	else:
		while(r.status_code != 200):
			time.sleep(config.delay)
			r = requests.get("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	return float((r.text).split(":")[1])

def WRITE(dst = host, key, value, version):
	payload = {'key': key, 'value': value, 'host': host, 'version': version}
	headers = {'user-agent': APP_NAME}
	r = requests.post("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	return r.status_code, r.text

def DELETE(dst, key):
	payload = {'key': key}
	headers = {'user-agent': APP_NAME}
	r = requests.delete("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	return r.status_code, r.text

def INIT_ALGO(config_file):
	global config
	f = open(config_file)
	state = None

	for line in f.readlines():
		if line.startswith("Neighbors"):
			state = "neighbor"
			continue
		if line.startswith("Network"):
			state = "network"
			continue
		if line.startswith("Iterations"):
			state = "iteration"
			continue
		if line.startswith("Blocking"):
			state = "blocking"
			continue
		if line.startswith("Staleness"):
			state = "staleness"
			continue
		if line.startswith("Variables"):
			state = "variables"
			continue
		if line.startswith("Delay"):
			state = "delay"
			continue
		if line.startswith("Algorithm"):
			state = "code"
			continue


		if not line.strip():
			continue


		if state == "neighbor":
			config.neighbors.append(line.strip())
			config.network.append(line.strip())
			continue
		if state == "network":
			config.network.append(line.strip())
			continue
		if state == "iteration":
			config.iterations = int(line.strip())
			state = None
			continue
		if state == "blocking":
			config.blocking = bool(line.strip())
			state = None
			continue
		if state == "staleness":
			config.staleness = int(line.strip())
			state = None
			continue
		if state == "variables":
			line = line.split("=")
			config.variables.append((line[0].strip(), float(line[1].strip())))
			continue
		if state == "delay":
			config.delay = float(line.strip())
			state = None
			continue
		if state == "code":
			config.code.append(line)

	config.network_size = len(config.network)
	config.neighbor_size = len(config.neighbors)
	'''
		print config.neighbors
		print config.network
		print config.iterations
		print config.staleness
		print config.blocking
		print config.variables
		print config.delay
	'''






'''
# OLD

class algo_params:
	config = config_t()

	def neighbor_size():
		return len(config.neighbors)

	def network_size():
		return len(config.network) + 1

	def local(iteration, var, val, R_W):
		if (R_W == "R"):
			status, text = request_calls.READ(config.ip_self, var, config.blank_vt, iteration)
			if status == "404" and not blocking:
				return False
			elif status == "404" and blocking: 
				while(status == "404"):
					time.delay(config.delay)
					status, text = request_calls.READ(config.ip_self, var, config.blank_vt, iteration)
				return True
		elif (R_W == "W"):
			status, text = request_calls.WRITE(config.ip_self, var, val, config.ip_self, config.blank_vt, iteration)
			if
		else:
			return False

	def neighbors(var, iter, R_W_D):

	def greatest_neighbor(var, iter):

	def smallest_neighbor(var, iter):

	def parse_algo():

	def run():
'''
