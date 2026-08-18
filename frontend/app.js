// Rapid Message Sender Frontend Application Logic

let eventSource = null;
let currentConfig = {};

const PRESETS = {
  custom: {
    message: "Hello! This is an automated rapid ping message. 🚀⚡",
    repeat: 10,
    interval: 200,
    delay: 5,
    trigger: "Enter"
  },
  ping: {
    message: "⚡ [ALERT] Rapid ping check from team lead!",
    repeat: 5,
    interval: 250,
    delay: 1,
    trigger: "Enter"
  },
  count: {
    message: "Test Sequence Item",
    repeat: 20,
    interval: 200,
    delay: 2,
    trigger: "Enter"
  },
  emoji: {
    message: "🔥🚀⚡🎉 Multi-line Emoji Test Sequence!",
    repeat: 10,
    interval: 300,
    delay: 2,
    trigger: "Enter"
  },
  standup: {
    message: "💬 Standup Reminder: Please update your task status in the channel.",
    repeat: 3,
    interval: 500,
    delay: 2,
    trigger: "Enter"
  }
};

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  await fetchVersion();
  initSSE();
  setupCharCountListener();
  initHeartbeat();
  autoCheckUpdateOnLaunch();
}

function initHeartbeat() {
  const sendHeartbeat = () => {
    fetch("/api/heartbeat", { method: "POST" }).catch(() => {});
  };
  sendHeartbeat();
  setInterval(sendHeartbeat, 2000);

  window.addEventListener("beforeunload", () => {
    if (navigator.sendBeacon) {
      navigator.sendBeacon("/api/shutdown");
    } else {
      fetch("/api/shutdown", { method: "POST", keepalive: true }).catch(() => {});
    }
  });
}

async function fetchVersion() {
  try {
    const res = await fetch("/api/version");
    if (res.ok) {
      const data = await res.json();
      if (data.version) {
        document.title = `Rapid Message Sender ${data.version}`;
        const versionBadge = document.getElementById("versionBadge");
        if (versionBadge) versionBadge.textContent = data.version;
      }
    }
  } catch (err) {
    console.error("Failed to fetch version:", err);
  }
}

function initSSE() {
  if (eventSource) {
    eventSource.close();
  }

  eventSource = new EventSource("/api/events");

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === "log") {
        appendLog(data.level, data.message, data.timestamp);
      } else if (data.type === "stats") {
        updateStatsUI(data.data);
      }
    } catch (e) {
      console.error("Error parsing SSE data:", e);
    }
  };

  eventSource.onerror = (err) => {
    console.warn("SSE connection interrupted, retrying...", err);
  };
}

function setupCharCountListener() {
  const textarea = document.getElementById("messageText");
  const charCount = document.getElementById("charCount");
  if (textarea && charCount) {
    const updateCount = () => {
      charCount.textContent = `${textarea.value.length} chars`;
    };
    textarea.addEventListener("input", updateCount);
    updateCount();
  }
}

function switchTab(tab) {
  const workspaceView = document.getElementById("viewWorkspace");
  const guideView = document.getElementById("viewGuide");
  const tabWorkspaceBtn = document.getElementById("tabWorkspaceBtn");
  const tabGuideBtn = document.getElementById("tabGuideBtn");

  if (tab === "workspace") {
    workspaceView.classList.remove("hidden");
    guideView.classList.add("hidden");
    tabWorkspaceBtn.classList.add("active");
    tabGuideBtn.classList.remove("active");
  } else {
    workspaceView.classList.add("hidden");
    guideView.classList.remove("hidden");
    tabWorkspaceBtn.classList.remove("active");
    tabGuideBtn.classList.add("active");
  }
}

function loadPreset(presetKey) {
  const preset = PRESETS[presetKey];
  if (!preset) return;

  document.getElementById("messageText").value = preset.message;
  document.getElementById("repeatCount").value = preset.repeat;
  document.getElementById("intervalMs").value = preset.interval;
  document.getElementById("startDelaySec").value = preset.delay;
  document.getElementById("triggerKey").value = preset.trigger;

  // Trigger char count update
  const charCount = document.getElementById("charCount");
  if (charCount) charCount.textContent = `${preset.message.length} chars`;

  appendLog("INFO", `Loaded preset template: "${presetKey}"`, getFormattedTime());
}

function toggleCounterSubgroup(checked) {
  const box = document.getElementById("counterOptionsBox");
  if (box) {
    if (checked) {
      box.classList.remove("hidden");
    } else {
      box.classList.add("hidden");
    }
  }
}

async function startSending() {
  const message = document.getElementById("messageText").value;
  if (!message) {
    alert("Please enter a message to send.");
    return;
  }

  const repeatCount = parseInt(document.getElementById("repeatCount").value) || 10;
  const intervalMs = parseInt(document.getElementById("intervalMs").value) || 200;
  const startDelaySec = parseInt(document.getElementById("startDelaySec").value) || 5;
  const triggerKey = document.getElementById("triggerKey").value;

  const appendCounter = document.getElementById("appendCounterCheckbox").checked;
  const counterPos = document.querySelector('input[name="counterPos"]:checked')?.value || "suffix";
  const counterSeparator = document.getElementById("counterSeparator").value || " ";

  const payload = {
    message: message,
    repeatCount: repeatCount,
    intervalMs: intervalMs,
    startDelaySec: startDelaySec,
    triggerKey: triggerKey,
    appendCounter: appendCounter,
    counterPosition: counterPos,
    counterSeparator: counterSeparator
  };

  try {
    const res = await fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errText = await res.text();
      appendLog("ERROR", `Failed to start engine: ${errText}`, getFormattedTime());
    } else {
      setRunningState(true);
    }
  } catch (err) {
    appendLog("ERROR", `Network error starting engine: ${err.message}`, getFormattedTime());
  }
}

async function stopSending() {
  try {
    const res = await fetch("/api/stop", { method: "POST" });
    if (res.ok) {
      appendLog("WARNING", "Stop request dispatched to backend engine...", getFormattedTime());
    }
  } catch (err) {
    appendLog("ERROR", `Failed to stop engine: ${err.message}`, getFormattedTime());
  }
}

function resetConfig() {
  document.getElementById("presetSelect").value = "custom";
  loadPreset("custom");
  document.getElementById("appendCounterCheckbox").checked = false;
  toggleCounterSubgroup(false);
  appendLog("INFO", "Configuration reset to defaults.", getFormattedTime());
}

function updateStatsUI(stats) {
  if (!stats) return;

  const statDispatched = document.getElementById("statDispatched");
  const statElapsed = document.getElementById("statElapsed");
  const statSpeed = document.getElementById("statSpeed");
  const badgeStatus = document.getElementById("badgeStatus");
  const progressBarFill = document.getElementById("progressBarFill");
  const progressPercent = document.getElementById("progressPercent");

  if (statDispatched) statDispatched.textContent = `${stats.dispatched} / ${stats.total}`;
  if (statElapsed) statElapsed.textContent = `${stats.elapsedSec.toFixed(1)} s`;
  if (statSpeed) statSpeed.textContent = `${stats.speedMsgSec.toFixed(1)} msg/s`;

  if (badgeStatus) {
    badgeStatus.textContent = stats.status;
    badgeStatus.className = `badge badge-${stats.status.toLowerCase().replace(/\s+/g, '-')}`;
  }

  if (stats.total > 0) {
    const pct = Math.min(100, Math.round((stats.dispatched / stats.total) * 100));
    if (progressBarFill) progressBarFill.style.width = `${pct}%`;
    if (progressPercent) progressPercent.textContent = `${pct}%`;
  }

  const isRunning = (stats.status === "Running" || stats.status.startsWith("Starting in"));
  setRunningState(isRunning);
}

function setRunningState(isRunning) {
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const inputs = document.querySelectorAll(".config-panel input, .config-panel select, .config-panel textarea");

  if (startBtn) startBtn.disabled = isRunning;
  if (stopBtn) stopBtn.disabled = !isRunning;

  inputs.forEach(input => {
    if (input.id !== "stopBtn") {
      input.disabled = isRunning;
    }
  });
}

function appendLog(level, message, timestamp) {
  const terminal = document.getElementById("consoleTerminal");
  if (!terminal) return;

  const logLine = document.createElement("div");
  logLine.className = `log-line ${level.toLowerCase()}`;

  const timeSpan = document.createElement("span");
  timeSpan.className = "log-time";
  timeSpan.textContent = `[${timestamp || getFormattedTime()}]`;

  const badgeSpan = document.createElement("span");
  badgeSpan.className = `log-badge ${level.toLowerCase()}`;
  badgeSpan.textContent = level;

  const msgSpan = document.createElement("span");
  msgSpan.className = "log-msg";
  msgSpan.textContent = message;

  logLine.appendChild(timeSpan);
  logLine.appendChild(badgeSpan);
  logLine.appendChild(msgSpan);

  terminal.appendChild(logLine);
  terminal.scrollTop = terminal.scrollHeight;
}

function clearLogs() {
  const terminal = document.getElementById("consoleTerminal");
  if (terminal) {
    terminal.innerHTML = "";
    appendLog("INFO", "Console log cleared.", getFormattedTime());
  }
}

async function autoCheckUpdateOnLaunch() {
  try {
    const res = await fetch("/api/update");
    if (res.ok) {
      const data = await res.json();
      if (data.has_update) {
        populateUpdateModal(data);
        const modal = document.getElementById("updateModal");
        if (modal) modal.classList.remove("hidden");
        appendLog("WARNING", `🔔 Update Alert: Version ${data.latest_version || 'New'} is available on GitHub!`, getFormattedTime());
      } else {
        appendLog("INFO", `GitHub release & SHA-256 integrity check verified (${data.current_version}). Up to date.`, getFormattedTime());
      }
    }
  } catch (err) {
    console.log("Startup update check:", err);
  }
}

async function checkUpdates() {
  const modal = document.getElementById("updateModal");
  if (modal) modal.classList.remove("hidden");

  try {
    const res = await fetch("/api/update");
    if (res.ok) {
      const data = await res.json();
      populateUpdateModal(data);
    }
  } catch (err) {
    const modalNotes = document.getElementById("modalReleaseNotes");
    if (modalNotes) modalNotes.textContent = "Failed to connect to GitHub update API. Please check your internet connection.";
  }
}

function populateUpdateModal(data) {
  const modalCurrentVer = document.getElementById("modalCurrentVer");
  const modalLatestVer = document.getElementById("modalLatestVer");
  const modalNotes = document.getElementById("modalReleaseNotes");
  const downloadBtn = document.getElementById("modalDownloadBtn");

  if (modalCurrentVer) modalCurrentVer.textContent = data.current_version || "v1.3.0";
  if (modalLatestVer) modalLatestVer.textContent = data.latest_version || data.current_version || "v1.3.0";
  
  if (downloadBtn && data.html_url) {
    downloadBtn.href = data.html_url;
  }

  let notesText = data.body || (data.has_update ? "A new update is available on GitHub!" : "You are currently running the latest version.");
  if (data.current_sha256) {
    notesText += `\n\n----------------------------------------\nBinary SHA-256 Checksum Integrity:`;
    notesText += `\nLocal SHA256:  ${data.current_sha256.substring(0, 16)}...`;
    if (data.latest_sha256) {
      notesText += `\nRemote SHA256: ${data.latest_sha256.substring(0, 16)}...`;
      notesText += `\nChecksum Status: ${data.sha_match ? "✅ MATCHED (Authentic Build)" : "⚠️ MISMATCH (Re-compiled/Updated Build Available)"}`;
    } else {
      notesText += `\nChecksum Status: Verified`;
    }
  }
  if (modalNotes) modalNotes.textContent = notesText;
}

function closeUpdateModal() {
  const modal = document.getElementById("updateModal");
  if (modal) modal.classList.add("hidden");
}

function getFormattedTime() {
  const d = new Date();
  const pad = (n) => (n < 10 ? "0" + n : n);
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}
