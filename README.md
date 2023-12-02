# wireSync

This is a synchronization service that keeps wireguard client ip address in sync IP address changes.  This is useful in situations where clients may not have fixed IP addresses, or are travelling.  


This relies on a publicly reachable server which is running app.py.  The clients run wiresync.py, preferrably as a service.  


## Todo list

* Finalize API communication flow
* Need to generate commands when receiving peer data
* Website interface for monitoring
* websockets interface, at the moment clients poll the server for changes.

## deployment
Dockerfile and docker-compose are set up to containerize a webserver with flask and nginx.  

still need to package client, maybe pyinstaller?  

# Structure



## Class structure


```mermaid
graph TD
fl(flask - app.py)
lg(ogic class)
wt(workthread)
cl(client - wiresync.py)
env([env.py])
wini([wiresync.ini])
q(Queue)
pd(pending)



fl --- env
fl --- lg

subgraph logic.py
    lg --- wt & q & pd
    wt --- db(DBase class)
end

cl --- wini

```


## information flow
```mermaid
graph TD
fl(flask - app.py)
lg(logic)
wt(workthread)
cl(client - wiresync.py)
q(Queue)
pd(pending)

cl <-.-> fl
fl <--> lg --> q --> wt --> pd -.-> lg
wt <--> db
```


### Standard Peer Information

|Peer info|Description|
|-|-|
|publickey|public key
|wgip|Wireguard Address
|listen_port| Wireguard listening port
|lanip|LAN Ip Address
|wanip|WAN Ip Address
|lan_name|MAC Address of gateway


## client messages

|type|description|response|description
|-|-|-|-|
|update|self peer info| update_ack| ack
|check|check for responses| pending | list of messages
|getPeer| peer publickey | getPeer_ack| ack


## server messages
|type|description
|-|-|
|peer| details of one peer
|peers|list of peers on the same LAN


