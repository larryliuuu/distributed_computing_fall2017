from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
from urlparse import urlparse
import psql_interface
from psql_interface import query_t
import request_calls

REQUEST_PORT = 5434
APP_NAME = 'distributed_computing/0.1'

'''

send error codes back to client via http
send response back ^ put error code in response
have better print statements for results of query

user UPSERT for POST queries
'''

class RequestHandler(BaseHTTPRequestHandler):
	def verify(self):
		if 'user-agent' in self.headers:
			if self.headers['user-agent'] == APP_NAME:
				query = urlparse(self.path).query
				self.query_components = dict(qc.split("=") for qc in query.split("&"))
				'''
					TODO: error checking for client's input parameters for the query/req
					ex. return error code, check which error code, if client did not put a value for a key in a POST req
					if get: has key, if post: has key/value, if delete, has key, etc.
					'''
				return True
		self.error()
		return False


	def do_GET(self):
		if not self.verify():
			return
		print "in get"
		cur, conn = psql_interface.open_db()
		query = query_t()

		query.key = self.query_components["key"]
		retval, res = psql_interface.GET(cur, query)

		if retval:
			print res.key
			print res.value
		elif retval == 0: 
			print "key not found"
		elif retval == -1:
			print "exception"
		psql_interface.close_db(conn)

	def do_POST(self):
		if not self.verify():
			return
		print "post request identified"
		cur, conn = psql_interface.open_db()
		query = query_t()

		query.key = self.query_components["key"]
		query.value = self.query_components["value"]
		query.modified_by = self.query_components["host"]

		retval = psql_interface.POST(cur, query)
		if retval:
			print "updated key successfully"
		else:
			print "update unsuccessful"
		
		psql_interface.close_db(conn)

	def do_DELETE(self):
		if not self.verify():
			return
		print "in delete"
		key = self.query_components["key"]
		print key

httpd = SocketServer.TCPServer(("", REQUEST_PORT), RequestHandler)
httpd.serve_forever()

