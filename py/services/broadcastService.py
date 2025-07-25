# Broadcast service for sending messages to all connected clients, using a queue.
# The Queue repeats the task until the condition is met
import os
import queue
import sys
import threading
import time


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from domains.aetherOneDomains import Analysis, BroadCastData
from services.hotbitsService import HotbitsService
from services.analyzeService import checkGeneralVitality
from services.broadcaster import DigitalBroadcaster


class BroadcastTask:
    def __init__(self, broadcastData: BroadCastData, analysis: Analysis | None = None):
        self.broadcastData = broadcastData
        self.analysis = analysis

    def to_dict(self):
        if (self.analysis is None):
            return {'broadcastData': self.broadcastData.to_dict()}
        return {
            'analysis': self.analysis.to_dict(),
            'broadcastData': self.broadcastData.to_dict()
        }

    # Check if the task is valid
    def is_valid(self, hotbits_service: HotbitsService) -> bool:
        gv = checkGeneralVitality(hotbits_service)
        if self.broadcastData.entering_with_general_vitality is None:
            self.broadcastData.entering_with_general_vitality = gv
        self.broadcastData.leaving_with_general_vitality = gv
        if self.analysis is not None:
            print(f"Signature: ${self.broadcastData.signature} Target GV: ${self.analysis.target_gv}, Current GV: ${gv}")
        else:
            print(f"Signature: ${self.broadcastData.signature} Current GV: ${gv}")
            return gv < checkGeneralVitality(hotbits_service)
        if gv < self.analysis.target_gv:
            return False
        return True


class BroadcastService:
    def __init__(self, hotbits_service: HotbitsService, main):
        self.PROJECT_ROOT = main.PROJECT_ROOT
        self.hotbits_service = hotbits_service
        self.main = main
        self.task_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.start()
        self.current_task = None
        self.stop_requested = False

    def add_task(self, task: BroadcastTask):
        self.task_queue.put(task)
        self.main.emitMessage("broadcast_info", f"broadcasting for {task.broadcastData.signature} started")

    def _process_queue(self):
        while True:

            self.stop_requested = False

            try:
                if self.task_queue.empty():
                    time.sleep(2)
                    continue
                task = self.task_queue.get(timeout=1)
                self.current_task = task
                task.broadcastData.repeat += 1
                if self.main.aetherOneDB.get_setting('useGPIOforBroadcasting'):
                    print(f"Using GPIO for broadcasting signature: {task.broadcastData.signature}")
                    from services.broadcasterGPIO import GPIOBroadcaster
                    broadcaster = GPIOBroadcaster(self.main.aetherOneDB)
                    broadcaster.broadcast(task.broadcastData.signature, 10, self.main.aetherOneDB.get_setting('gpioSleep'))

                else:
                    broadcaster = DigitalBroadcaster(task.broadcastData.signature, self.PROJECT_ROOT, duration=10)
                    broadcaster.start_broadcasting()
                    if self.stop_requested:
                        print("Broadcasting stopped by user.")
                        self.main.emitMessage("broadcast_info","broadcasting stopped by user")
                        return
                if task.is_valid(self.hotbits_service):
                    self.main.emitMessage("broadcast_info",task.broadcastData.signature)
                    self.task_queue.task_done()
                else:
                    time.sleep(1)
                    self.task_queue.put(task)
                self.main.aetherOneDB.insert_broadcast(task.broadcastData)
                self.current_task = None
            except queue.Empty:
                continue

    def stop(self):
        print("Stopping broadcasts")
        self.task_queue.queue.clear()
        self.current_task = None
        self.stop_requested = True

    def get_tasks(self):
        tasks = []
        for q in self.task_queue.queue:
            tasks.append(q.to_dict())
        return tasks

    def get_current_task(self):
        if self.current_task:
            return self.current_task.to_dict()
        return None