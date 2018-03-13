import netifaces as ni
import request_calls


class config_t():
	neighbors = []
	network = []
	iterations = 0
	staleness = 0
	blocking = True
	variables = []
	delay = 0 
	code = []
	ip_self = ip.str(ni.ifaddresses('en0')[ni.AF_INET][0]['addr'])
	blank_vt = json.dumps({})

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

	def run():

