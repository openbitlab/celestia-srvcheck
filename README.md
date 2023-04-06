# CELESTIA-SRVCHECK

celestia-srvcheck helps you to monitor Celestia nodes.

It supports all types of Celesia nodes:
- **Light node**
- **Full node**
- **Bridge node**
- **Validator node**

It supports these notification outputs:
- **stdout**
- **telegram chats**

And offer tasks for checking:
- **TaskAutoUpdater** (auto updates celestia-srvcheck when is found a new release)
- **TaskChainStuck** (checks if the chain is stuck)
- **TaskChainLowPeer** (checks if the number of peers connected is low)
- **TaskChainSynching** (checks if the node is synching new data availability samples for light and full node or is synching blocks for the others)
- **TaskChainUnreachable** (checks if the node is unreachbale, if so it probably means that the node is down)
- **TaskSystemCpuAlert** (checks if the cpu usage is too high)
- **TaskSystemUsage** (sends daily stats about disk usage, uptime, etc.)
- **TaskNewRelease** (checks if there is a new release of the installed node)
- **TaskSystemDiskAlert** (check if the disk usage is too high, > 90%)
- **TaskSystemRamAlert** (checks if the ram usage is too high)

Celestia Light and Full node specific tasks:
- **TaskNodeIsSynching** (checks if the node is synching blocks)
- **TaskCelestiaDasCheckSamplesHeight** (check if the node is sampling new headers)

Celestia Validator node specific tasks:
- **TaskCelestiaBlockMissed** (checks if the validator is missing blocks)
- **TaskCelestiaNewProposal** (checks if there are new governance proposal)
- **TaskCelestiaPositionChanged** (checks if the validator position has changed)

We suggest adding the binary of the node to the PATH in order to benefit from all the monitor features' 

## Setup Telegram Bot & Chat

In order to receive alerts on Telegram, you need to create a telegram bot and setup a new telegram group where the bot will send the alerts.<br>
For the creation of the new bot first you need to start the **`@BotFather`** bot on telegram, then type `/newbot` to create a new bot specifying the name and also the username.<br>
Once you have created successfully the bot, you should now have the **token** which you will need later to install the monitor.<br>
Now, create a new telegram group adding the bot you have just created to the group, then you need to get the **id** of the chat.<br>
In order to get the id you have a few options, the easiest one is to add **`@MissRose_bot`** to your group and then type `/id` in the chat group.<br>
You will use the **id** and **token** during the installation, these will be called rispectively **<tg_chat_id>** and **<tg_token>**


## Install & Update

```bash 
curl -s https://raw.githubusercontent.com/openbitlab/celestia-srvcheck/main/install.sh | bash -s -- -t <tg_chat_id> <tg_token> -s <service_name> <optional_flags>
```

The install script can be customized with these flags (most of them are optional):

```
install --help
     --active-set <active_set_number> number of the validators in the active set [default is the number of active validators]
     --admin <@username> the admin telegram username that is interested to new governance proposals
 -b  --block-time <time> expected block time [default is 60 seconds]
     --branch <name> name of the branch to use for the installation [default is main]
     --endpoint <url:port> node local rpc address
     --git <git_api> git api to query the latest realease version installed
     --gov enable checks on new governance proposals
     --mount <mount_point> mount point where the node saves data
 -n  --name <name> monitor name [default is the server hostname]
     --rel <version> release version installed (required if git_api is specified)
     --signed-blocks <max_misses> <blocks_window> max number of blocks not signed in a specified blocks window [default is 5 blocks missed out of the latest 100 blocks]
 -s  --service <name> service name of the node to monitor [required]
 -t  --telegram <chat_id> <token> telegram chat options (id and token) where the alerts will be sent [required]
 -v  --verbose enable verbose installation
```

## Results

#### For example this is the output that is sent in the chat when the monitor is installed and detects a Celestia node

<img width=50% src="https://user-images.githubusercontent.com/49374667/230424648-11471db6-25fc-4cde-83c8-60778681b915.jpg" />

#### This is the output that is sent in the chat when the monitor is installed and every day

<img width=50% src="https://user-images.githubusercontent.com/49374667/230424699-42fdb043-e2d8-4a20-8e08-399d03893b9d.jpg" />

#### These are the charts that give a better overview of the system usage during the last month (or since the node has been is installed)

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
```

## Credits

Made with love by the [Openbitlab](https://openbitlab.com) team

## License

Read the LICENSE file.
