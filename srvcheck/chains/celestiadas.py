import time
from .chain import Chain
from ..utils import Bash
from ..notification import Emoji
from ..tasks import Task,  hours, minutes
from ..tasks.taskchainstuck import elapsedToString

class TaskCelestiaDasHealthError(Task):
	def __init__(self, services, checkEvery = minutes(5), notifyEvery=hours(1)):
		super().__init__('TaskCelestiaDasHealthError', services, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		try:
			self.s.chain.getNetwork()
			return False
		except Exception as _:
			return self.notify(f'health error! {Emoji.Health}')

class TaskCelestiaDasCheckSamplesHeight(Task):
	def __init__(self, services, checkEvery = minutes(1), notifyEvery=minutes(5)):
		super().__init__('TaskCelestiaDasCheckSamplesHeight', services, checkEvery, notifyEvery)	
		self.since = None
		self.oc = 0

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		bh = self.s.chain.getHeight()
		bhSampled = self.s.chain.getSamplesHeight()

		if self.since is None:
			self.since = time.time()
			return False

		if bh > bhSampled:
			self.oc += 1
			elapsed = elapsedToString(self.since)
			return self.notify(f'is not sampling headers since block {bh} ({elapsed}) {Emoji.Stuck}')

		if self.oc > 1:
			elapsed = elapsedToString(self.since)
			self.notify (f'is back sampling headers ({elapsed} {Emoji.SyncOk}')

		self.since = time.time()
		self.oc = 0
		return False

class CelestiaDas(Chain):
	TYPE = "das"
	ROLE = "light"
	NAME = ""
	BLOCKTIME = 60
	AUTH_TOKEN = None
	EP = "http://localhost:26658/"
	CUSTOM_TASKS = [TaskCelestiaDasHealthError, TaskCelestiaDasCheckSamplesHeight]

	@staticmethod
	def detect(conf):
		try:
			CelestiaDas(conf).getNetwork()
			return True
		except:
			return False

	def rpcCall(self, method, headers=None, params=[]):
		if not self.AUTH_TOKEN:
			self.AUTH_TOKEN = Bash(f"celestia {self.ROLE} auth admin --p2p.network blockspacerace").value()
		headers = { 'Authorization': 'Bearer ' + self.AUTH_TOKEN }
		return super().rpcCall(method, headers, params)

	def getNetwork(self):
		return self.rpcCall('header.NetworkHead')["header"]["chain_id"]

	def getVersion(self):
		ver = Bash("celestia version | head -n 1").value().split(" ")
		return ver.split(" ")[-1]

	def getLocalVersion(self):
		try:
			return self.getVersion()
		except Exception as e:
			ver = self.conf.getOrDefault('chain.localVersion')
			if ver is None:
				raise Exception('No local version of the software specified!') from e
			return ver

	def getHeight(self):
		return self.rpcCall('header.NetworkHead')['header']['height']

	def getBlockHash(self):
		return self.rpcCall('header.NetworkHead')['header']['last_block_id']['hash']

	def getPeerCount(self):
		return len(self.rpcCall('p2p.Peers'))

	def isSynching(self):
		return not self.rpcCall('das.SamplingStats')['catch_up_done']

	def getSamplesHeight(self):
		return not self.rpcCall('das.SamplingStats')['head_of_sampled_chain']