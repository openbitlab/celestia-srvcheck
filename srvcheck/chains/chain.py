import requests
from ..utils import ConfItem, ConfSet

ConfSet.addItem(ConfItem('chain.endpoint', None, str, 'api endpoint'))
ConfSet.addItem(ConfItem('chain.blockTime', 10, int, 'block time in seconds'))
ConfSet.addItem(ConfItem('chain.name', None, str, 'chain name'))
ConfSet.addItem(ConfItem('chain.ghRepository', None, str, 'github repository'))
ConfSet.addItem(ConfItem('chain.service', None, str, 'systemd service name'))
ConfSet.addItem(ConfItem('chain.localVersion', None, str, 'local version'))

def rpcCall(url, method, headers=None, params=[]):
	d = requests.post(url, headers=headers, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}, timeout=60).json()
	return d['result']

def getCall(url, data):
	return requests.get(url, json=data, timeout=60).json()

class Chain:
	NAME = ""
	BLOCKTIME = 10
	EP = ""

	def __init__(self, conf):
		self.conf = conf
		if self.conf.getOrDefault('chain.endpoint') is not None:
			self.EP = self.conf.getOrDefault('chain.endpoint')
		self.NAME = self.conf.getOrDefault('chain.name')

	def rpcCall(self, method, headers=None, params=[]):
		""" Calls the RPC method with the given parameters """
		return rpcCall(self.EP, method, headers, params)

	def getCall(self, r, data=None):
		""" Calls the GET method with the given parameters """
		return getCall(self.EP + r, data)

	### Abstract methods
	@staticmethod
	def detect(conf):
		""" Checks if the current server is running this chain """
		raise Exception('Abstract detect()')

	def getVersion(self):
		""" Returns software version """
		raise Exception('Abstract getVersion()')

	def getLatestVersion(self):
		""" Returns software local version """
		gh_repo = self.conf.getOrDefault('chain.ghRepository')
		if gh_repo:
			c = requests.get(f"https://api.github.com/repos/{gh_repo}/releases/latest", timeout=60).json()
			return c['tag_name']
		raise Exception('No github repo specified!')

	def getLocalVersion(self):
		try:
			return self.getVersion()
		except Exception as e:
			ver = self.conf.getOrDefault('chain.localVersion')
			if ver is None:
				raise Exception('No local version of the software specified!') from e
			return ver

	def getHeight(self):
		""" Returns the block height """
		raise Exception('Abstract getHeight()')

	def getBlockHash(self):
		""" Returns the block height """
		raise Exception('Abstract getHeight()')

	def getPeerCount(self):
		""" Returns the number of peers """
		raise Exception('Abstract getPeerCount()')

	def getNetwork(self):
		""" Returns network used """
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		""" Returns true if the node is staking """
		raise Exception('Abstract isStaking()')

	def isSynching(self):
		""" Returns true if the node is synching """
		raise Exception('Abstract isSynching()')
