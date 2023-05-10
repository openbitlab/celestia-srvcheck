# CELESTIA-SRVCHECK

celestia-srvcheck helps you monitor Celestia nodes and be promptly informed about unexpected scenarios.

It supports all types of Celestia nodes:
- **Light node**
- **Full node**
- **Bridge node**
- **Validator node**

It supports these notification outputs:
- **stdout**
- **telegram chats**

And it offers many features thanks to the following tasks:
- **TaskAutoUpdater**: automatic updates for celestia-srvcheck when a new release is found
- **TaskChainStuck**: check if the chain is stuck
- **TaskChainLowPeer**: check if the number of connected peers is low
- **TaskChainSynching**: check if the node is synching new data availability samples (available for Light and Full nodes), or is synching blocks (valid for Bridge and Validator nodes)
- **TaskChainUnreachable**: check if the node is unreachable, and consequently down
- **TaskSystemCpuAlert**: check if the cpu usage is too high
- **TaskSystemUsage**: send daily stats about disk usage, uptime, and other metrics
- **TaskNewRelease**: check if there is a new release of the installed node
- **TaskSystemDiskAlert**: check if the disk usage is too high (>90%)
- **TaskSystemRamAlert**: check if the ram usage is too high

Celestia Light and Full node specific tasks:
- **TaskNodeIsSynching**: check if the node is synching blocks
- **TaskCelestiaDasCheckSamplesHeight**: check if the node is sampling new headers
- **TaskExporter**: export node metrics on prometheus

Celestia Validator node specific tasks:
- **TaskCelestiaBlockMissed**: check if the validator is missing blocks
- **TaskCelestiaNewProposal**: check if there are new governance proposals
- **TaskCelestiaPositionChanged**: check if the validator position has changed

We suggest adding the binary of the node to the PATH in order to benefit from all the monitoring features. 

## Telegram Bot Setup

In order to receive alerts on Telegram, you need to create a telegram bot and setup a new telegram group. The bot will send alerts there.<br>
Start the **`@BotFather`** bot on Telegram, then type `/newbot` to create a new bot and specify name and username.<br>
You should now have the **token**, which is required on a later step to install the monitor.<br>
Then, open a new Telegram group, **add the created bot** to it.<br>
You will need the chat id, and the easiest way to get it is to add `@MissRose_bot` to your group and then type `/id` in the chat group.<br>
During the installation, you will use the **id** and **token**. These parameters will be flagged respectively **<tg_chat_id>** and **<tg_token>**.


## Install & Update

```bash 
curl -s https://raw.githubusercontent.com/openbitlab/celestia-srvcheck/main/install.sh | bash -s -- -t <tg_chat_id> <tg_token> -s <service_name> <optional_flags>
```

The install script can be customized with these flags (most of them are optional):

```
install --help
     --active-set <active_set_number> number of the validators in the active set [number of active validators provided by default]
     --admin <@username> the Telegram username that is tagged once new governance proposals are live
 -b  --block-time <time> expected block time [default is 60 seconds]
     --branch <name> name of the branch to use for the installation [default is main]
     --endpoint <url:port> node local rpc address
     --git <git_repo> git repo to query the latest realease version that is installed
     --gov enable checks on new governance proposals
     --mount <mount_point> mount point where the node saves data
 -n  --name <name> monitor name [default is the server hostname]
     --rel <version> release version installed (required if git_repo is specified)
     --signed-blocks <max_misses> <blocks_window> max number of blocks not signed in a specified blocks window [default is 5 blocks missed out of the latest 100 blocks]
 -s  --service <name> service name of the node to monitor [required]
 -t  --telegram <chat_id> <token> telegram chat options (id and token) where the alerts will be sent [required]
 -v  --verbose enable verbose installation
 -e  --exporter <port> enable prometheus exporter on <port> (port optional, default 9001)"
```

#### A few examples of the installation with optional flags:

Install with `--git` flag to get alerts on new node releases (in this case [celestia-node](https://github.com/celestiaorg/celestia-node))

```bash 
curl -s https://raw.githubusercontent.com/openbitlab/celestia-srvcheck/main/install.sh | bash -s -- -t <tg_chat_id> <tg_token> -s <service_name> --git celestiaorg/celestia-node
```

Install with `--admin` and `--gov` flags to be tagged once new proposals are out

```bash 
curl -s https://raw.githubusercontent.com/openbitlab/celestia-srvcheck/main/install.sh | bash -s -- -t <tg_chat_id> <tg_token> -s <service_name> --admin @MyTelegramUsername --gov
```

## Outcomes

The following screenshots represent the chat outputs when the monitor is triggered by predetermined events.

#### Celestia node detection and task activation

<img width=50% src="https://user-images.githubusercontent.com/49374667/230424648-11471db6-25fc-4cde-83c8-60778681b915.jpg" />

#### Daily stats

<img width=50% src="https://user-images.githubusercontent.com/49374667/230424699-42fdb043-e2d8-4a20-8e08-399d03893b9d.jpg" />

#### System usage charts (in the last month or since node setup)

<img width=75% src="https://user-images.githubusercontent.com/49374667/230424743-45776691-0442-46b2-a1db-ac9260b1f68d.jpg" />

## Customize Configuration
Edit /etc/srvcheck.conf:

```
; telegram notifications 
[notification.telegram]
enabled = true
apiToken = 
chatIds = 

; a dummy notification wich prints to stdout
[notification.dummy]
enabled = true

; chain settings
[chain]
; name to be displayed on notifications
name = 
; chain type (e.g. "tendermint" | "substrate")
type = 
; systemd service name
service = 
; endpoint uri, if different from default
endpoint = 
; block time
blockTime =
activeSet = 
thresholdNotsigned = 
blockWindow = 
; Github repository (org/repo)
ghRepository = 
; software version
localVersion = 
; mount point
mountPoint = 

; task specific settings
[tasks]
; comma separated list of disabled tasks
disabled = TaskTendermintNewProposal
; enable auto recovery
autoRecover = true 
; Governance administrator (proposal voting, with @), optional
govAdmin =
; Prometheus exporter port
exporterPort =
```

## Prometheus custom exporter: metrics
A custom exporter has been developed to export metrics related to Celestia node with a fixed scraping frequency of 15s, specifically the following metrics are exported:

| Name | Description | Type |
|--|--|--|
| peers_count | Number of peers connected to the node | Guage |
| node_height | Node height | Guage |
| network_height | Network height | Guage |
| out_of_sync_counter | Incremental value to indicate how many times the node result in syncing state | Counter |
| first_header | Height of the first processed header in the latest block range  | Guage |
| latest_header | Height of the latest processed header in the latest block range | Guage |
| finished_s | Processing time of the latest block range | Guage |
| errors | Number of errors encountered during the processing of the latest block range | Guage |

## Credits

Made with love by the [Openbitlab](https://openbitlab.com) team

## License

Read the LICENSE file.
