from ..notification import Emoji
from . import Task, minutes


class TaskChainSynching(Task):
	def __init__(self, services):
		super().__init__('TaskChainSynching', services, minutes(1), minutes(30))
		self.prev = None

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		if self.s.chain.isSynching() and self.s.chain.TYPE == 'Validator node':
			return self.notify(f'chain is synching {Emoji.Slow}')
		elif self.s.chain.isSynching():
			return self.notify(f'is synching data availability samples {Emoji.Slow}')

		return False
