import requests
import socket

IP = '127.0.0.1'
REQUEST_PORT = '5434'
APP_NAME = 'distributed_computing/0.1'

def READ(key):
	payload = {'key': key}
	headers = {'user-agent': APP_NAME}
	r = requests.get("http://" + IP + ":" + REQUEST_PORT, params=payload, headers=headers)
	print r.text

def WRITE(key, value):
	payload = {'key': key, 'value': value, 'host': socket.gethostbyname(socket.gethostname())}
	headers = {'user-agent': APP_NAME}
	r = requests.post("http://" + IP + ":" + REQUEST_PORT, params=payload, headers=headers)
	print r.text

def DELETE(key):
	payload = {'key': key}
	headers = {'user-agent': APP_NAME}
	r = requests.delete("http://" + IP + ":" + REQUEST_PORT, params=payload, headers=headers)
	print r.text