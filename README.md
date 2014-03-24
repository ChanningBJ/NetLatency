NetLatency
==========

A small tool to detect network latency between hosts


## Overwiew

Using this tool, you can detect the network latency between hosts. The network information is described in file network.cfg and the report looks like this:
```
| source      | target      | Ethernet |          IP | Latency |
|-------------+-------------+----------+-------------+---------|
| sample1.com | sample2.com | en1      | 192.168.0.2 |      23 |
| sample1.com | sample3.com | en6      | 192.168.0.3 |      27 |
```