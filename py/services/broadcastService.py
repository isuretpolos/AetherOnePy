# Broadcast service for sending messages to all connected clients, using a queue.
# The Queue repeats the task until the condition is met
import os
import queue
import sys
import threading
import time, hashlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from domains.aetherOneDomains import Analysis, BroadCastData
from services.hotbitsService import HotbitsService
from services.analyzeService import checkGeneralVitality
from services.broadcaster import DigitalBroadcaster


class BroadcastTask:
    def __init__(self, broadcastData: BroadCastData, analysis: Analysis):
        self.broadcastData = broadcastData
        self.analysis = analysis

    # Check if the task is valid
    def is_valid(self, hotbits_service: HotbitsService) -> bool:
        gv = checkGeneralVitality(hotbits_service)
        if self.broadcastData.entering_with_general_vitality is None:
            self.broadcastData.entering_with_general_vitality = gv
        self.broadcastData.leaving_with_general_vitality = gv
        print(f"Signature: ${self.broadcastData.signature} Target GV: ${self.analysis.target_gv}, Current GV: ${gv}")
        if gv < self.analysis.target_gv:
            return False
        return True


class BroadcastService:
    def __init__(self, hotbits_service: HotbitsService, main):
        self.PROJECT_ROOT = main.PROJECT_ROOT
        self.hotbits_service = hotbits_service
        self.main = main
        self.task_queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.start()

    def add_task(self, task: BroadcastTask):
        if self.running:
            self.task_queue.put(task)
            self.main.emitMessage("broadcast_info", f"broadcasting for {task.broadcastData.signature} started")

    def _process_queue(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                task.broadcastData.repeat += 1
                broadcaster = DigitalBroadcaster(task.broadcastData.signature, self.PROJECT_ROOT, duration=10)
                broadcaster.start_broadcasting()
                if self._condition_met(task):
                    self.task_queue.task_done()
                    self.main.emitMessage("broadcast_info",task.broadcastData.signature)
                else:
                    time.sleep(1)
                    self.task_queue.put(task)
                self.main.aetherOneDB.insert_broadcast(task.broadcastData)
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