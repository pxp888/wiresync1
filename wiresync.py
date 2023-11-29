import requests
import os 
import time
import subprocess as sp
import configparser


try:
    config = configparser.ConfigParser()
    config.read('wiresync.ini')
    gin = dict(config['wiresync'])
except Exception as e:
    print(e)
    print('No config file found, using defaults')
    gin = {
        'server': '52.56.34.125:5001',
        'interface': 'wg0',
        'lan_name': 'home'
    }


def show(item):
    out = {}
    com = f'sudo wg show wg0 {item}'
    res = sp.getoutput(com).split('\n')
    for i in res:
        n = i.split('\t')
        if n[1] != '(none)':
            out[n[0]] = n[1]
    return out


lan_name = gin['lan_name']
publickey = sp.getoutput('sudo wg show wg0 public-key')
endpoints = show('endpoints')
ips = show('allowed-ips')
lastinfo = 0 


def update():
    data = {'t':'update',
            'lan_name': lan_name,
            'publickey': publickey,
            'endpoints': endpoints,
            'ips': ips}
    try:
        response = requests.post(f'http://{gin["server"]}/test', json={'data': data})
        return response.json()
    except Exception as e:
        print(e)
        return None


update()


def check():
    data = {'t':'check',
            'publickey': publickey}
    try:
        response = requests.post(f'http://{gin["server"]}/test', json={'data': data})
        return response.json()
    except Exception as e:
        print(e)
        return None


while True:
    pending = check()
    if pending is not None:
        print(pending)
    

    time.sleep(3)



