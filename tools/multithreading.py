<<<<<<< HEAD
import queue
import threading

class ThreadPool():
    def __init__(self, num):
        self.num = num
        self.taskQ = queue.Queue()
        self.threads = []

    def addTask(self, func, args = ()):
        self.taskQ.put((func, *args))

    def runTask(self):
        while True:
            if not self.taskQ.empty():
                task = self.taskQ.get(block = True, timeout = 1)
                task[0](*task[1:])
                self.taskQ.task_done()
            else:
                break

    def run(self):
        for n in range(self.num):
            th = threading.Thread(target=self.runTask)
            th.setDaemon(True)
            self.threads.append(th)
            th.start()

    def join(self):
        #for th in self.threads:
        #    th.join()
        self.taskQ.join()
=======
import queue
import threading

class ThreadPool():
    def __init__(self, num):
        self.num = num
        self.taskQ = queue.Queue()
        self.threads = []

    def addTask(self, func, args = ()):
        self.taskQ.put((func, *args))

    def runTask(self):
        while True:
            if not self.taskQ.empty():
                task = self.taskQ.get(block = True, timeout = 1)
                task[0](*task[1:])
                self.taskQ.task_done()
            else:
                break

    def run(self):
        for n in range(self.num):
            th = threading.Thread(target=self.runTask)
            th.setDaemon(True)
            self.threads.append(th)
            th.start()

    def join(self):
        #for th in self.threads:
        #    th.join()
        self.taskQ.join()
>>>>>>> history
