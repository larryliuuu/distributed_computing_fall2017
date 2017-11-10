import socket
import request_calls
import netifaces as ni

ip = str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])

request_calls.READ("0")

'''
for i in range (0,10):
	key = str(i)
	value = "new_val" + str(i)
	try:
		request_calls.WRITE(key, value, ip)
	except:
		continue
	finally:
		p = 1
'''
