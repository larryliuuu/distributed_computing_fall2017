#!/usr/bin/python

import requests

SERVER_PORT = '5434'
APP_NAME = 'distributed_computing/0.1'

def READ(dst, key, vt):
	payload = {'key': key}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.get("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	print str(r.status_code) + ":" + r.text

def WRITE(dst, key, value, host, vt):
	payload = {'key': key, 'value': value, 'host': host}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.post("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	print str(r.status_code) + ":" + key + ":" + value

def DELETE(dst, key, vt):
	payload = {'key': key}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.delete("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	print str(r.status_code) + ":" + key