import socket
import request_calls
import netifaces as ni

ip = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])

request_calls.READ("aye")
'''
for i in range (0,10):
	key = str(i)
	value = "val" + str(i)
	request_calls.WRITE(key, value, ip)
'''
