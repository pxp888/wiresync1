import threading
import queue

input_queue = queue.Queue()
lock = threading.Lock()
pending = {}





def run():
    while True:
        data = input_queue.get()
        if data==0: break
        print(data)
        input_queue.task_done()


def start():
    t = threading.Thread(target=run)
    t.start()
    return t


def stop():
    input_queue.put(0)
    input_queue.join()
    print('stopped')

