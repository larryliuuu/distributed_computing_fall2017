from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
from urlparse import urlparse

REQUEST_PORT = 5434
APP_NAME = 'distributed_computing/0.1'


class RequestHandler(BaseHTTPRequestHandler):
	def verify(self):
		if 'user-agent' in self.headers:
			if self.headers['user-agent'] == APP_NAME:
				return True

		self.error()
		return False

	def do_GET(self):
		if not self.verify():
			return

		print "in get"
		query = urlparse(self.path).query
		query_components = dict(qc.split("=") for qc in query.split("&"))
		key = query_components["key"]
		print key

	def do_POST(self):
		if not self.verify():
			return

		print "in post"
		query = urlparse(self.path).query
		query_components = dict(qc.split("=") for qc in query.split("&"))
		key = query_components["key"]
		print key

	def do_DELETE(self):
		if not self.verify():
			return

		print "in delete"
		query = urlparse(self.path).query
		query_components = dict(qc.split("=") for qc in query.split("&"))
		key = query_components["key"]
		print key


httpd = SocketServer.TCPServer(("", REQUEST_PORT), RequestHandler)
httpd.serve_forever()

