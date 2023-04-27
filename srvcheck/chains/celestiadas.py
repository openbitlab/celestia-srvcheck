import time
import configparser
import re
from .chain import Chain
from ..utils import Bash, Exporter
from ..notification import Emoji
from ..tasks import Task, hours, minutes, seconds
from ..tasks.taskchainstuck import elapsedToString
from prometheus_client import Gauge, Counter
import json


class TaskCelestiaDasCheckSamplesHeight(Task):
    def __init__(self, services, checkEvery=minutes(5), notifyEvery=minutes(5)):
        super().__init__('TaskCelestiaDasCheckSamplesHeight', services, checkEvery, notifyEvery)
        self.since = None
        self.oc = 0

    @staticmethod
    def isPluggable(services):
        return services.chain.ROLE == 'light' or services.chain.ROLE == 'full'

    def run(self):
        if not self.s.chain.isSynching():
            bh = int(self.s.chain.getNetworkHeight())
            bhSampled = self.s.chain.getSamplesHeight()

            if self.since is None:
                self.since = time.time()
                return False

            if bh > bhSampled:
                self.oc += 1
                elapsed = elapsedToString(self.since)
                return self.notify(
                    f'is not sampling new headers, last block sampled is {bhSampled}, current block header is {bh} ({elapsed}) {Emoji.Stuck}')

            if self.oc > 0:
                elapsed = elapsedToString(self.since)
                self.notify(f'is back sampling new headers (after {elapsed}) {Emoji.SyncOk}')

            self.since = time.time()
            self.oc = 0
        return False


class TaskExporter(Task):
    exporter: Exporter

    def __init__(self, services, checkEvery=seconds(15), notifyEvery=seconds(15)):
        super().__init__('TaskExporter', services, checkEvery, notifyEvery)
        metrics = {Gauge('peers_count', "Number of connected peers"): self.s.chain.getPeerCount,
                   Gauge('node_height', "Node height"): self.s.chain.getHeight,
                   Gauge('network_height', "Network height"): self.s.chain.getNetworkHeight,
                   Counter('out_of_sync_counter', "How many times node has gone out of sync"): self.s.chain.isSynching,
                   Gauge('first_header', "First sampled header height"): self.s.chain.getFirstHeader,
                   Gauge('latest_header', "First sampled header height"): self.s.chain.getLatestHeader,
                   Gauge('finished_s', "Processing time of block range"): self.s.chain.getProcessingTime,
                   Gauge('errors', "Header sampling errors"): self.s.chain.getErrors}
        self.exporter = Exporter(metrics, self.s.chain.conf.getOrDefault('tasks.exporterPort'))

    @staticmethod
    def isPluggable(services):
        return services.chain.ROLE == 'light' or services.chain.ROLE == 'full'

    def run(self):
        # self.s.chain.peer_metric.set(self.s.chain.getPeerCount())
        self.s.chain.getLastSampledHeader()
        self.exporter.export()


class TaskNodeIsSynching(Task):
    def __init__(self, services):
        super().__init__('TaskNodeIsSynching', services, minutes(5), minutes(5))
        self.prev = None
        self.since = None
        self.oc = 0

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        bh = int(self.s.chain.getHeight())

        if self.prev is None:
            self.prev = bh
            self.since = time.time()
            return False

        nh = int(self.s.chain.getNetworkHeight())
        if bh > self.prev and abs(bh - nh) > 100:
            self.oc += 1
            return self.notify(
                f'chain is synching, last block stored is {bh}, current network height is {nh} {Emoji.Slow}')

        if self.oc > 0:
            elapsed = elapsedToString(self.since)
            self.notify(f'chain synched in {elapsed} {Emoji.SyncOk}')

        self.prev = bh
        self.since = time.time()
        self.oc = 0
        return False


class CelestiaDas(Chain):
    TYPE = ""
    ROLE = "light"
    NAME = ""
    BLOCKTIME = 60
    AUTH_TOKEN = None
    BIN = None
    EP = "http://localhost:26658/"
    CUSTOM_TASKS = [TaskCelestiaDasCheckSamplesHeight, TaskNodeIsSynching, TaskExporter]
    LATEST_SAMPLED_HEADERS = {}

    def __init__(self, conf):
        super().__init__(conf)
        serv = self.conf.getOrDefault('chain.service')
        if serv:
            c = configparser.ConfigParser()
            c.read(f"/etc/systemd/system/{serv}")
            cmd = re.split(' ', c["Service"]["ExecStart"])
            self.BIN = cmd[0]
            self.ROLE = cmd[1]
            self.TYPE = self.ROLE.capitalize() + " node"

    @staticmethod
    def detect(conf):
        try:
            CelestiaDas(conf).getNetwork()
            return True
        except:
            return False

    def rpcCall(self, method, headers=None, params=[]):
        if not self.AUTH_TOKEN:
            self.AUTH_TOKEN = Bash(f"{self.BIN} {self.ROLE} auth admin --p2p.network blockspacerace").value()
        headers = {'Authorization': 'Bearer ' + self.AUTH_TOKEN}
        return super().rpcCall(method, headers, params)

    def getNetwork(self):
        return self.rpcCall('header.NetworkHead')["header"]["chain_id"]

    def getVersion(self):
        ver = Bash(f"{self.BIN} version | head -n 1").value()
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
        return self.rpcCall('header.LocalHead')['header']['height']

    def getNetworkHeight(self):
        return self.rpcCall('header.NetworkHead')['header']['height']

    def getBlockHash(self):
        return self.rpcCall('header.NetworkHead')['header']['last_block_id']['hash']

    def getPeerCount(self):
        return len(self.rpcCall('p2p.Peers'))

    def isSynching(self):
        # RPC call return inconsistent data (different from logs)                
        serv = self.conf.getOrDefault('chain.service')
        if serv:
            synching = Bash(f'journalctl -u {serv} --no-pager --since "1 min ago"').value().split("\n")
            synchingBlocks =  [b for b in synching if "finished syncing headers" in b]
        return not self.rpcCall('das.SamplingStats')['catch_up_done'] or len(synchingBlocks) > 0

    def getSamplesHeight(self):
        # RPC call return inconsistent data (different from logs)
        serv = self.conf.getOrDefault('chain.service')
        lastSampledHeadRpc = self.rpcCall('das.SamplingStats')['head_of_sampled_chain']
        if serv:
            blocks = Bash(f'journalctl -u {serv} --no-pager --since "1 min ago"').value().split("\n")
            lastSampledHead = json.loads(re.findall("\{\"from.*}", [b for b in blocks if "finished sampling headers" in b][-1])[-1])["to"]
            if lastSampledHead > lastSampledHeadRpc:
                return lastSampledHead
        return lastSampledHeadRpc

    def getLastSampledHeader(self):
        serv = self.conf.getOrDefault('chain.service')
        if serv:
            blocks = Bash(f'journalctl -u {serv} --no-pager --since "1 min ago"').value().split("\n")
            self.LATEST_SAMPLED_HEADERS = json.loads(re.findall("\{\"from.*}", [b for b in blocks if "finished sampling headers" in b][-1])[-1])
        else:
            self.LATEST_SAMPLED_HEADERS = []

    def getFirstHeader(self):
        return self.LATEST_SAMPLED_HEADERS["from"]

    def getLatestHeader(self):
        return self.LATEST_SAMPLED_HEADERS["to"]

    def getProcessingTime(self):
        return self.LATEST_SAMPLED_HEADERS["finished (s)"]

    def getErrors(self):
        return self.LATEST_SAMPLED_HEADERS["errors"]