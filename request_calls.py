#!/usr/bin/python

import requests

SERVER_IP = '192.168.0.125'
SERVER_PORT = '5434'
APP_NAME = 'distributed_computing/0.1'

def READ(key, vt):
	payload = {'key': key}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.get("http://" + SERVER_IP + ":" + SERVER_PORT, params=payload, headers=headers)
	print r.status_code

def WRITE(key, value, host, vt):
	payload = {'key': key, 'value': value, 'host': host}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.post("http://" + SERVER_IP + ":" + SERVER_PORT, params=payload, headers=headers)
	print r.status_code

def DELETE(key, vt):
	payload = {'key': key}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.delete("http://" + SERVER_IP + ":" + SERVER_PORT, params=payload, headers=headers)
	print r.status_code