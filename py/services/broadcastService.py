# Broadcast service for sending messages to all connected clients, using a queue.
import os
import queue
import sys
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from domains.aetherOneDomains import Analysis, BroadCastData
from services.hotbitsService import HotbitsService
from services.analyzeService import checkGeneralVitality


class BroadcastTask:
    def __init__(self, task: BroadCastData, analysis: Analysis):
        self.task = task
        self.analysis = analysis

    # Check if the task is valid
    def is_valid(self, hotbits_service: HotbitsService) -> bool:
        gv = checkGeneralVitality(hotbits_service)
        print(gv)
        if gv < self.analysis.target_gv:
            return False
        return True


class BroadcastService:
    def __init__(self, hotbits_service: HotbitsService):
        self.hotbits_service = hotbits_service
        self.task_queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.start()

    def add_task(self, task: BroadcastTask):
        if self.running:
            self.task_queue.put(task)

    def _process_queue(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if self._condition_met(task):
                    self.task_queue.task_done()
                else:
                    self.task_queue.put(task)
            except queue.Empty:
                continue

    def _condition_met(self, task):
        return task.is_valid(self.hotbits_service)

    def stop(self):
        self.running = False
        self.worker_thread.join()

    def get_tasks(self):
        tasks = []
        while not self.task_queue.empty():
            tasks.append(self.task_queue.get())
        return tasks