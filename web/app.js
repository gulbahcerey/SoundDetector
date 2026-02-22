// app.js (frontend)
const startBtn = document.getElementById("startBtn");
const btnTitle = document.getElementById("btnTitle");
const btnSub = document.getElementById("btnSub");

const audioState = document.getElementById("audioState");
const statusRow = document.getElementById("statusRow");
const detCount = document.getElementById("detCount");
const sttBox = document.getElementById("sttBox");
const logBox = document.getElementById("logBox");
const listenState = document.getElementById("listenState");

let listening = false;
let pollTimer = null;
let detections = 0;

function setListeningUI(isOn) {
  listenState.innerHTML = isOn
    ? `<span class="badge"><span class="dot green"></span>Listening</span>`
    : `<span class="badge"><span class="dot"></span>Not listening</span>`;
}

async function startBackend() {
  await fetch("http://127.0.0.1:8000/start", { method: "POST" }); // FIXED: call backend
}

async function stopBackend() {
  await fetch("http://127.0.0.1:8000/stop", { method: "POST" }); // FIXED
}

async function fetchLatest() {
  const res = await fetch("http://127.0.0.1:8000/latest");
  return await res.json();
}

function startPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(async () => {
    try {
      const data = await fetchLatest();

      statusRow.textContent = "Status: Running…";
      audioState.textContent = `${data.category} • ${data.label} (${(data.conf * 100).toFixed(0)}%)`;

      if (data.label && data.label !== "Unknown" && data.conf >= 0.03) {
        detections += 1;
        detCount.textContent = String(detections);
      }
    } catch (e) {
      statusRow.textContent = "Status: Backend not reachable";
    }
  }, 250); // 4 times per second (smooth enough)
}

function stopPolling() {
  if (!pollTimer) return;
  clearInterval(pollTimer);
  pollTimer = null;
}

setListeningUI(false);

startBtn.addEventListener("click", async () => {
  listening = !listening;

  startBtn.classList.toggle("listening", listening);
  btnTitle.textContent = listening ? "Stop Listening" : "Start Listening";
  btnSub.textContent = listening ? "TAP TO STOP" : "TAP TO BEGIN";

  setListeningUI(listening);

  if (listening) {
    logBox.textContent += "\nStarted listening...";
    await startBackend();
    startPolling();
  } else {
    logBox.textContent += "\nStopped listening...";
    await stopBackend();
    stopPolling();
    statusRow.textContent = "Status: Idle";
    audioState.textContent = "No audio detected";
  }

  logBox.scrollTop = logBox.scrollHeight;
});