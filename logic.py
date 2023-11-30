import threading
import queue
from flask import jsonify
import sqlite3


class Logic:
    def __init__(self):
        print('creating logic')
        self.input_queue = queue.Queue()
        self.pendingLock = threading.Lock()
        self.pending = {}
        self.workthread = threading.Thread(target=self.run)
        self.workthread.start()
        
        '''create dbase'''
        self.conn = sqlite3.connect('dbase.db')
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS clients
                     (publickey text, lan_name text, lanip text, wanip text)''')
        self.conn.commit()
        


    def update(self, data):
        self.input_queue.put(data)
        response_data = { "t": "update" }
        return jsonify(response_data)


    def check(self, data):
        pk = data['publickey']
        self.pendingLock.acquire()
        if pk in self.pending:
            response_data = { "t": "check", 
                             "pending": True, 
                             "data": self.pending[pk] }
        else:
            response_data = { "t": "check", 
                             "pending": False }
        self.pendingLock.release()
        return response_data


    def run(self):
        print('logic running')
        while True:
            data = self.input_queue.get()
            if data==0: break
            self.input_queue.task_done()

            
            



    def stop(self):
        self.input_queue.put(0)
        self.workthread.join()

