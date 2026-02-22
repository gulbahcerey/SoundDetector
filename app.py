# import time
# import threading
# import queue
# import streamlit as st
#
# import realtime_detect
# import main
#
# st.set_page_config(page_title="Sound Detector", layout="centered")
# st.title("🔊 Deaf Assist Sound Detector")
#
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Anton&display=swap');
#
# :root {
#   --background: #ffffff;
#   --primary: #030213;
#   --radius: 0.625rem;
#
#   /* optional nice defaults */
#   --card-bg: #ffffff;
#   --card-border: rgba(0,0,0,0.08);
#   --text: #0f172a;
#   --muted: rgba(15,23,42,0.7);
# }
#
# .stApp {
#   background: var(--background);
#   font-family: 'Inter', sans-serif;
# }
#
# /* Card container */
# .card {
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--radius);
#   padding: 18px;
#   margin-top: 10px;
# }
#
# /* Big category box */
# .bigbox {
#   border-radius: calc(var(--radius) + 6px);
#   padding: 26px;
#   text-align: center;
#   font-size: 54px;
#   font-weight: 900;
#   color: white;
#   font-family: 'Anton', sans-serif; /* optional */
# }
#
# /* Label + confidence line */
# .meta {
#   margin-top: 10px;
#   text-align: center;
#   color: var(--text);
#   font-size: 16px;
# }
#
# /* “Recent detections” title */
# .smallh {
#   margin-top: 14px;
#   margin-bottom: 6px;
#   color: var(--text);
#   font-size: 16px;
#   font-weight: 800;
# }
# </style>
# """, unsafe_allow_html=True)
#
# if "running" not in st.session_state:
#     st.session_state.running = False
# if "category" not in st.session_state:
#     st.session_state.category = "Other"
# if "label" not in st.session_state:
#     st.session_state.label = "Unknown"
# if "conf" not in st.session_state:
#     st.session_state.conf = 0.0
# if "history" not in st.session_state:
#     st.session_state.history = []
# if "q_obj" not in st.session_state:
#     st.session_state.q_obj = queue.Queue()
# if "stop_obj" not in st.session_state:
#     st.session_state.stop_obj = threading.Event()
# if "worker_thread" not in st.session_state:
#     st.session_state.worker_thread = None
#
#
# def worker(q_obj, stop_obj):
#     realtime_detect.run_realtime( output_queue=q_obj, stop_event=stop_obj)
#
#
# c1, c2, c3 = st.columns(3)
#
# with c1:
#     if st.button("🎙️ Record 3s WAV", use_container_width=True):
#         main.record_aud()
#
# with c2:
#     if st.button("Start", use_container_width=True):
#         if not st.session_state.running:
#             st.session_state.running = True
#             st.session_state.stop_obj.clear()
#
#             t = st.session_state.worker_thread
#             if t is None or not t.is_alive():
#                 st.session_state.worker_thread = threading.Thread(
#                     target=worker,
#                     args=(st.session_state.q_obj, st.session_state.stop_obj),
#                     daemon=True
#                 )
#                 st.session_state.worker_thread.start()
#
# with c3:
#     if st.button("Stop", use_container_width=True):
#         st.session_state.running = False
#         st.session_state.stop_obj.set()
#
#
# for _ in range(50):
#     try:
#         msg = st.session_state.q_obj.get_nowait()
#     except queue.Empty:
#         break
#
#     st.session_state.category = msg["category"]
#     st.session_state.label = msg["label"]
#     st.session_state.conf = msg["conf"]
#
#     st.session_state.history.insert(
#         0, f'{msg["category"]} | {msg["label"]} | {msg["conf"]:.2f}'
#     )
#     st.session_state.history = st.session_state.history[:10]
#
#
# cat = st.session_state.category
# lab = st.session_state.label
# conf = float(st.session_state.conf)
#
# colors = {
#     "Person": "#2ecc71",
#     "Animal": "#3498db",
#     "Alarm":  "#e74c3c",
#     "Other":  "#95a5a6",
# }
#
# st.markdown('<div class="card">', unsafe_allow_html=True)
# st.markdown(
#     f'<div class="bigbox" style="background:{colors.get(cat, "#95a5a6")};">{cat}</div>'
#     f'<div class="meta"><b>Label:</b> {lab} &nbsp;&nbsp; <b>Confidence:</b> {conf:.2f}</div>',
#     unsafe_allow_html=True
# )
# st.progress(min(1.0, max(0.0, conf)))
# st.markdown("</div>", unsafe_allow_html=True)
#
# st.markdown('<div class="smallh">Recent detections</div>', unsafe_allow_html=True)
# st.write(st.session_state.history)
#
#
# if st.session_state.running:
#     time.sleep(0.2)
#     st.rerun()