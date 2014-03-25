NetLatency
==========

A small tool to detect network latency between hosts in micro-seconds


## Overwiew

Using this tool, you can detect the network latency between hosts in micro-second. The network information is described in file network.cfg and the report looks like this:
```
| source      | target      | Ethernet |          IP | Latency (micro-second) |
|-------------+-------------+----------+-------------+------------------------|
| sample1.com | sample2.com | en1      | 192.168.0.2 |                     23 |
| sample1.com | sample3.com | en6      | 192.168.0.3 |                     27 |
```

## Latency test method

`ping` command and `tcpdump` command are used in the latency test. The destation servser will run `tcpdump` command to tracking the package timestamp and `ping` command is run on source server against the destion server. So the destation server can get the timestamp of each ICMP package between the source and destation server. The latency is caulated from the delta time between each timestamp.

## Usage

The network configuration is described in file network.cfg. The configuration file is consist of sections start with [session name], each section refesants of a network connection need to be tested. Each section consists of following vatiables:
* SRC_HOST: The hostname (or IP address) of source server. The machine running this tool will use this IP address to connect source server.
* DST_HOST: The hostname (or IP address) of destation server. The machine running this tool will use this IP address to connect destation server.
* DST\_HOST\_INTERNAL: The hostname (or IP address) of destation server that is used to connect to source server. If this value is not set, will use DST_HOST as default.

For example, gived following network configuration, the network.cfg will looks like this:
```
[s1]
SRC_HOST = sample1.com
DST_HOST = sample2.com
DST_HOST_INTERNAL = sample2.internal.com

[s2]
SRC_HOST = sample1.com
DST_HOST = sample3.com
DST_HOST_INTERNAL = sample32.internal.com
```
