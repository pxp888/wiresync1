import time
import threading
import queue
from flask import jsonify
from collections import defaultdict
import sqlite3


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
		response_data = { "t": "updateack" }
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
		response_data = { "t": "getPeerack" }
		return jsonify(response_data)


	def _createDatabase(self):
		self.conn = sqlite3.connect('dbase.db')
		self.cur = self.conn.cursor()
		self.cur.execute('''CREATE TABLE IF NOT EXISTS clients(publickey text UNIQUE, wgip text, lan_name text, lanip text, wanip text, time text)''')
		self.conn.commit()


	def _getPeer(self, data):
		self.cur.execute(f'SELECT * FROM clients WHERE publickey="{data["publickey"]}"')
		row = self.cur.fetchone()
		if row is None:
			response_data = { "t": "noPeer", "publickey": data["publickey"] }
		else:
			response_data = { "t": "peer", "publickey": data["publickey"], 'wgip': row[1], 'lan_name': row[2], 'lanip': row[3], 'wanip': row[4] }
		self.pendingLock.acquire()
		self.pending[data['publickey']].append(response_data)
		self.pendingLock.release()


	def _updateDB(self, data):
		self.cur.execute(f'''REPLACE INTO clients VALUES ('{data['publickey']}', '{data['wgip']}', '{data['lan_name']}', '{data['lanip']}', '{data['wanip']}', '{time.time()}' )''')
		self.conn.commit()
		print('dbase updated', data)


	def _peersBylan_name(self, lan_name):
		peers = []
		self.cur.execute(f'SELECT * FROM clients WHERE lan_name="{lan_name}"')
		for row in self.cur.fetchall():
			peers.append({'publickey': row[0], 'wgip': row[1], 'lan_name': row[2], 'lanip': row[3], 'wanip': row[4]})
		return peers


	def run(self):
		print('logic running')
		self._createDatabase()

		while True:
			data = self.input_queue.get()
			if data==0: break
			if data['t'] == 'update':
				self._updateDB(data)
				peers = self._peersBylan_name(data['lan_name'])
				response_data = { "t": "lanpeers", "peers": peers }
				self.pendingLock.acquire()
				self.pending[data['publickey']].append(response_data)
				self.pendingLock.release()

			elif data['t'] == 'getPeer':
				self._getPeer(data)


			self.input_queue.task_done()

		self.conn.close()


	def stop(self):
		self.input_queue.put(0)
		self.workthread.join()
		print('logic stopped')

