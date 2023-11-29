import threading
import queue
from flask import jsonify


class Logic:
    def __init__(self):
        self.input_queue = queue.Queue()
        self.lock = threading.Lock()
        self.pending = {}
        self.workthread = threading.Thread(target=self.run)
        self.workthread.start()


    def update(self, data):
        self.input_queue.put(data)
        response_data = { "t": "update" }
        return jsonify(response_data)


    def check(self, data):
        pk = data['publickey']
        self.lock.acquire()
        if pk in self.pending:
            response_data = { "t": "check", 
                             "pending": True, 
                             "data": self.pending[pk] }
        else:
            response_data = { "t": "check", 
                             "pending": False }
        self.lock.release()
        return response_data


    def run(self):
        while True:
            data = self.input_queue.get()
            if data==0: break
            print(data)
            self.input_queue.task_done()


    def stop(self):
        self.input_queue.put(0)
        self.workthread.join()

