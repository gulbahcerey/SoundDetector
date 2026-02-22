import threading
import queue

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import realtime_detect

app = FastAPI()

# allow your browser to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ok for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

q_obj = queue.Queue()
stop_obj = threading.Event()
worker_thread = None

latest = {"category": "Other", "label": "Unknown", "conf": 0.0, "rms": 0.0}


def worker():
    realtime_detect.run_realtime(output_queue=q_obj, stop_event=stop_obj)


def drain_queue():
    global latest
    while True:
        try:
            msg = q_obj.get_nowait()
            latest = {
                "category": msg.get("category", "Other"),
                "label": msg.get("label", "Unknown"),
                "conf": float(msg.get("conf", 0.0)),
                "rms": float(msg.get("rms", 0.0)),
            }
        except queue.Empty:
            break


@app.get("/latest")
def get_latest():
    drain_queue()
    return latest


@app.post("/start")
def start():
    global worker_thread
    stop_obj.clear()

    if worker_thread is None or (not worker_thread.is_alive()):
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()

    return {"ok": True}


@app.post("/stop")
def stop():
    stop_obj.set()
    return {"ok": True}