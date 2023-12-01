import requests
import os 
import time
import subprocess
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
    res = subprocess.getoutput(com).split('\n')
    for i in res:
        n = i.split('\t')
        if n[1] != '(none)':
            out[n[0]] = n[1]
    return out


def getLanIP(prefix='192.168.1'):
	command = f'ifconfig | grep {prefix}'
	m = subprocess.check_output(command, shell=True).decode('utf-8').strip().split(' ')[1]
	return m


def getWanIP():
	command = 'curl -s ifconfig.me'
	try:
		m = subprocess.check_output(command, shell=True).decode('utf-8').strip()
		return m
	except:
		return 'WAN IP failed'


lan_name = gin['lan_name']
publickey = subprocess.getoutput('sudo wg show wg0 public-key')
endpoints = show('endpoints')
ips = show('allowed-ips')


def sendmsg(data):
    try:
        response = requests.post(f'http://{gin["server"]}/test', json={'data': data})
        return response.json()
    except Exception as e:
        print(e)
        return None


def update():
    data = {'t':'update',
            'publickey': publickey,
            'wgip': getLanIP('10.0.0'),
            'lan_name': lan_name,
            'lanip': getLanIP(),
            'wanip': getWanIP()}
    return sendmsg(data)


def check():
    data = {'t':'check', 'publickey': publickey}
    return sendmsg(data)


def getPeer(pk):
    data = {'t':'getPeer', 'publickey': pk}
    return sendmsg(data)


if __name__ == '__main__':
    update()
    count=0
    while True:
        time.sleep(1)
        count = (count+1)%1024
        if count%3==0:
            pending = check()
            if pending is None: continue
            for i in pending['items']:
                 print(i)


    
    

