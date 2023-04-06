from ..notification import Emoji
from . import Task, minutes

class TaskChainSynching(Task):
	def __init__(self, services):
		super().__init__('TaskChainSynching', services, minutes(5), minutes(5))
		self.prev = False

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		if self.s.chain.isSynching():
			self.prev = True
			if self.s.chain.TYPE == 'Validator node':
				return self.notify(f'chain is synching {Emoji.Slow}')
			else:
				return self.notify(f'is synching data availability samples {Emoji.Slow}')
		elif self.prev:
			self.prev = False
			if self.s.chain.TYPE == 'Validator node':
				return self.notify(f'chain synched {Emoji.SyncOk}')
			else:
				return self.notify(f'synched all data availability samples {Emoji.SyncOk}')

		return False
