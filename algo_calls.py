import netifaces as ni
import requests
import time
from pathlib import Path

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
	code = {"init" : [], "pre" : [], "round" : [], "post" : []}

host = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
config = config_t()

def INIT(config_file):
	time.sleep(2)
	INIT_ALGO(config_file)
	INIT_KEYS(config.variables)
	return config

def INIT_KEYS(variables):
	for key, value in variables:
		DELETE(host, key)
		WRITE(key, str(value), 0, host)

def CLEANUP():
	time.sleep(5)
	for key in config.variables[0]:
		DELETE(host, key)

def READ(key, version, dst):
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

def WRITE(key, value, version, dst = host):
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
	neighbor_location = Path("neighbors")
	if neighbor_location.exists():
		neighbor_file = open("neighbors")
		for line in neighbor_file:
			config.neighbors.append(line.strip())

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

		if line.startswith("Initialize"):
			state = "init"
			continue

		if line.startswith("Pre-Round"):
			state = "pre"
			continue

		if line.startswith("Round"):
			state = "round"
			continue

		if line.startswith("Post-Round"):
			state = "post"
			continue

		if not line.strip():
			continue


		if state == "neighbor":
			if not neighbor_location.exists():
				config.neighbors.append(line.strip())
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
		
			
		
		if state == "init":
			config.code["init"].append(line)
		if state == "pre":
			config.code["pre"].append(line)
		if state == "round":
			config.code["round"].append(line)
		if state == "post":
			config.code["post"].append(line)


	config.network_size = len(config.network)
	config.neighbor_size = len(config.neighbors)

