import time
import threading
import queue
from flask import jsonify
from collections import defaultdict
import sqlite3


class Dbase:
	def __init__(self) -> None:
		self.conn = sqlite3.connect('dbase.db')
		self.cur = self.conn.cursor()
		self.cur.execute('''CREATE TABLE IF NOT EXISTS clients(publickey text UNIQUE, wgip text, listen_port text, lan_name text, lanip text, wanip text, time text)''')
		self.conn.commit()


	def updateDB(self, data):
		self.cur.execute(f'''REPLACE INTO clients VALUES ('{data['publickey']}', '{data['wgip']}', '{data['listen_port']}', '{data['lan_name']}', '{data['lanip']}', '{data['wanip']}', '{time.time()}' )''')
		self.conn.commit()


	def peersBylan_name(self, lan_name):
		peers = []
		self.cur.execute(f'SELECT * FROM clients WHERE lan_name="{lan_name}"')
		for row in self.cur.fetchall():
			peers.append({'t':'peer', 'publickey': row[0], 'wgip': row[1], 'listen_port':row[2], 'lan_name': row[3], 'lanip': row[4], 'wanip': row[5]})
		return peers


	def getPeer(self, publickey):
		self.cur.execute(f'SELECT * FROM clients WHERE publickey="{publickey}"')
		row = self.cur.fetchone()
		if row is None:
			return None
		else:
			return {'t':'peer', 'publickey': row[0], 'wgip': row[1], 'listen_port':row[2], 'lan_name': row[3], 'lanip': row[4], 'wanip': row[5]}


	def close(self):
		self.conn.close()


class Logic:
	def __init__(self):
		print('creating logic')
		self.input_queue = queue.Queue()
		self.pendingLock = threading.Lock()
		self.pending = defaultdict(list)
		self.workthread = threading.Thread(target=self.run)
		self.workthread.start()


	def update(self, data):
		self.input_queue.put(data)
		response_data = { "t": "update_ack" }
		return jsonify(response_data)


	def check(self, data):
		pk = data['publickey']
		self.pendingLock.acquire()
		response_data = { "t": "pending", "items": self.pending[pk] }
		self.pending[pk] = []
		self.pendingLock.release()
		return response_data


	def getPeer(self, data):
		self.input_queue.put(data)
		response_data = { "t": "getPeer_ack" }
		return jsonify(response_data)


	def _getPeer(self, data):
		row = self.db.getPeer(data["publickey"])
		if row is None:
			response_data = { "t": "noPeer", "publickey": data["publickey"] }
		else:
			response_data = row
		self.pendingLock.acquire()
		self.pending[data['publickey']].append(response_data)
		self.pendingLock.release()


	def _update(self, data):
		self.db.updateDB(data)
		peers = self.db.peersBylan_name(data['lan_name'])
		response_data = { "t": "peers", "peers": peers }
		self.pendingLock.acquire()
		self.pending[data['publickey']].append(response_data)
		self.pendingLock.release()


	def run(self):
		print('logic running')
		self.db = Dbase()

		while True:
			data = self.input_queue.get()
			if data==0: break
			if data['t'] == 'update':
				self._update(data)
			elif data['t'] == 'getPeer':
				self._getPeer(data)

			self.input_queue.task_done()

		self.db.close()


	def stop(self):
		self.input_queue.put(0)
		self.workthread.join()
		print('logic stopped')

