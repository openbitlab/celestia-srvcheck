import requests
import srvcheck
from packaging import version
from . import Task, minutes, hours
from ..utils import Bash

def versionCompare(v1, v2):
	v1 = version.parse(v1.split('-')[0]) if isinstance(version.parse(v1), version.LegacyVersion) is True else version.parse(v1)
	v2 = version.parse(v2.split('-')[0]) if isinstance(version.parse(v2), version.LegacyVersion) is True else version.parse(v2)

	if v1 < v2:
		return -1
	elif v1 > v2:
		return 1
	else:
		return 0

class TaskAutoUpdater(Task):
	def __init__(self, services):
		super().__init__('TaskAutoUpdater', services, minutes(60), hours(2))

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		nTag = requests.get('https://api.github.com/repos/openbitlab/celestia-srvcheck/git/refs/tags').json()[-1]['ref'].split('/')[-1].split('v')[1]

		if versionCompare(nTag, srvcheck.__version__) > 0:
			self.notify(f'New monitor version detected: v{nTag}')
			self.s.notification.flush()
			Bash(f'pip install --force-reinstall git+https://github.com/openbitlab/celestia-srvcheck@v{nTag}')
			Bash('systemctl restart node-monitor.service')
