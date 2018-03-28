#!/usr/bin/python

import requests
import netifaces as ni

SERVER_PORT = '5434'
APP_NAME = 'distributed_computing/0.1'

host = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])

# READ, WRITE, DELETE methods with vector timestamps
def READ(dst, key, vt, version):
	payload = {'key': key, 'version': version}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.get("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	#print str(r.status_code) + ":" + r.text
	return r.status_code, r.text

def WRITE(dst, key, value, vt, version):
	host = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
	payload = {'key': key, 'value': value, 'host': host, 'version': version}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.post("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	#print str(r.status_code) + ":" + key + ":" + value
	return r.status_code, r.text

def DELETE(dst, key, vt):
	payload = {'key': key}
	headers = {'user-agent': APP_NAME, 'vt': vt}
	r = requests.delete("http://" + dst + ":" + SERVER_PORT, params=payload, headers=headers)
	#print str(r.status_code) + ":" + key
	return r.status_code, r.text

