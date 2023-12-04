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
		'server': '192.168.1.38:5000',
		'interface': 'wg0'
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
	except Exception as e:
		print(f"Error: {e}")
		return None


def get_wg_publickey(interface='wg0'):
	try:
		result = subprocess.getoutput(f'sudo wg show {interface} public-key')
		return result
	except Exception as e:
		print(f"Error: {e}")
		return None


def get_wg_port(interface='wg0'):
	try:
		result = subprocess.getoutput(f'sudo wg show {interface} listen-port')
		return result
	except Exception as e:
		print(f"Error: {e}")
		return None


def get_gateway_mac():
	try:
		result = subprocess.check_output("ip route | grep default", shell=True).decode('utf-8').strip()
		gateway_ip = result.split()[2]

		result = subprocess.check_output(f"arp -n {gateway_ip} | grep {gateway_ip}", shell=True).decode('utf-8').strip()
		gateway_mac = result.split()[2]

		return gateway_mac
	except Exception as e:
		print(f"Error: {e}")
		return None


def sendmsg(data):
	try:
		response = requests.post(f'http://{gin["server"]}/test', json={'data': data})
		# print(response.json())
		return response.json()
	except Exception as e:
		print(e)
		return None


class Client:
	def __init__(self) -> None:
		self.refresh()

		self.funcs = {'pending': self.pending,
					'peers': self.peers,
					'keys': self.keys,
					'peer': self.peer}
		
		self.endpoints = show('endpoints')


	def refresh(self):
		self.publickey = get_wg_publickey()
		self.wgip = getLanIP('10.0.0')
		self.listen_port = get_wg_port()
		self.lan_name = get_gateway_mac()


	def handle(self, data):
		if data is None:
			print('data is None')
			return 
		if not 't' in data: 
			print('no t in data')
			return
		self.funcs[data['t']](data)


	def update(self):
		self.lan_name = get_gateway_mac()
		data = {'t':'update',
				'publickey': self.publickey,
				'wgip': self.wgip,
				'listen_port': self.listen_port,
				'lan_name': self.lan_name,
				'lanip': getLanIP(),
				'wanip': getWanIP()}
		return sendmsg(data)


	def check(self):
		data = {'t':'check',
				'publickey': self.publickey}
		i = sendmsg(data)
		self.handle(i)


	def pending(self, data):
		for i in data['items']:
			self.handle(i)


	def peers(self, data):
		for i in data['peers']:
			self.handle(i)


	def keys(self, data):
		for i in data['keys']:
			data = {'t':'getPeer', 'publickey': self.publickey, 'targetkey': i}
			sendmsg(data)


	def peer(self, data):
		if data['publickey'] == self.publickey: 
			return

		if data['lan_name'] == self.lan_name:
			endpoint = data['lanip'] + ':' + data['listen_port']
		else:
			endpoint = data['wanip'] + ':' + data['listen_port']

		if data['publickey'] in self.endpoints:
			if self.endpoints[data['publickey']] == endpoint:
				return 

		self.endpoints[data['publickey']] = endpoint
		print(f'sudo wg set wg0 peer {data["publickey"]} allowed-ips {data["wgip"]}/32 endpoint {endpoint}')
		print(f'sudo ip route add {data["wgip"]}/32 via dev wg0')


if __name__ == '__main__':
	n = Client()

	n.update()
	while True:
		time.sleep(.25)
		n.check()
		time.sleep(1)
		# break


