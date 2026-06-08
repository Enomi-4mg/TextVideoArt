import { TvaPlayer } from "../../src/lib/player-api.js";
import { loadTvaFile } from "../../src/lib/tva.js";

// Create the player directly. External apps can keep this instance in their own state layer.
const player = new TvaPlayer();

const elements = {
  fileInput: document.getElementById("file-input"),
  status: document.getElementById("status"),
  dropZone: document.getElementById("drop-zone"),
  playToggle: document.getElementById("play-toggle"),
  stopButton: document.getElementById("stop-button"),
  prevButton: document.getElementById("prev-button"),
  nextButton: document.getElementById("next-button"),
  seekInput: document.getElementById("seek-input"),
  frameReadout: document.getElementById("frame-readout"),
  fpsInput: document.getElementById("fps-input"),
  loopInput: document.getElementById("loop-input"),
  frameOutput: document.getElementById("frame-output"),
  manifestOutput: document.getElementById("manifest-output"),
  markersOutput: document.getElementById("markers-output"),
  eventLog: document.getElementById("event-log")
};

setControlsEnabled(false);

elements.fileInput.addEventListener("change", () => {
  const [file] = elements.fileInput.files;
  if (file) loadFile(file);
});

elements.dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  elements.dropZone.classList.add("is-dragging");
});

elements.dropZone.addEventListener("dragleave", () => {
  elements.dropZone.classList.remove("is-dragging");
});

elements.dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  elements.dropZone.classList.remove("is-dragging");
  const [file] = event.dataTransfer.files;
  if (file) loadFile(file);
});

elements.playToggle.addEventListener("click", () => {
  if (player.isPlaying()) {
    player.pause();
  } else {
    player.play();
  }
});
elements.stopButton.addEventListener("click", () => player.stop());
elements.prevButton.addEventListener("click", () => player.prevFrame());
elements.nextButton.addEventListener("click", () => player.nextFrame());

elements.seekInput.addEventListener("input", () => {
  player.pause();
  player.seekFrame(Number(elements.seekInput.value));
});

elements.fpsInput.addEventListener("change", () => {
  player.setFps(Number(elements.fpsInput.value));
});

elements.loopInput.addEventListener("change", () => {
  player.setLoop(elements.loopInput.checked);
});

async function loadFile(file) {
  setStatus(`Loading ${file.name}...`);
  try {
    // Parse the archive with the TVA helper, then load it into TvaPlayer.
    const tva = await loadTvaFile(file);
    player.load(tva);
    setControlsEnabled(true);
    setStatus(`Loaded ${file.name}`);
  } catch (error) {
    player.stop();
    setControlsEnabled(false);
    setStatus(error instanceof Error ? error.message : String(error), true);
  }
}

// Subscribe to player events. Apps can use these callbacks to sync their own UI.
player.on("load", ({ manifest, frameCount }) => {
  elements.seekInput.max = Math.max(0, frameCount - 1);
  elements.seekInput.value = "0";
  elements.fpsInput.value = String(player.getFps());
  renderManifest(player.getManifest() || manifest);
  renderMarkers(player.getMarkers());
  logEvent("load", `${frameCount} frames`);
});

player.on("framechange", ({ index, frameCount, frame }) => {
  elements.frameOutput.textContent = frame || "";
  elements.seekInput.value = String(index);
  elements.frameReadout.textContent = `${index + 1} / ${frameCount}`;
  logEvent("framechange", `${index + 1} / ${frameCount}`);
});

player.on("play", () => {
  elements.playToggle.textContent = "Pause";
  logEvent("play", "");
});

player.on("pause", () => {
  elements.playToggle.textContent = "Play";
  logEvent("pause", "");
});

player.on("stop", () => {
  elements.playToggle.textContent = "Play";
  logEvent("stop", "");
});

player.on("ended", () => {
  elements.playToggle.textContent = "Play";
  logEvent("ended", "");
});

player.on("fpschange", ({ fps }) => {
  elements.fpsInput.value = String(fps);
  logEvent("fpschange", `${fps} fps`);
});

player.on("loopchange", ({ loop }) => {
  elements.loopInput.checked = loop;
  logEvent("loopchange", loop ? "on" : "off");
});

function renderManifest(manifest) {
  // Read manifest data through the player API to demonstrate metadata access.
  const currentManifest = player.getManifest() || manifest;
  const rows = [
    ["Title", currentManifest.title || "(untitled)"],
    ["Format", `${currentManifest.format} ${currentManifest.version}`],
    ["Size", `${currentManifest.width} x ${currentManifest.height}`],
    ["FPS", currentManifest.fps],
    ["Frames", currentManifest.frame_count],
    ["Duration", `${currentManifest.duration}s`]
  ];

  if (currentManifest.author) rows.push(["Author", currentManifest.author]);
  if (currentManifest.license) rows.push(["License", currentManifest.license]);
  if (currentManifest.description) rows.push(["Description", currentManifest.description]);
  if (currentManifest.source) rows.push(["Source", summarizeObject(currentManifest.source)]);
  if (currentManifest.conversion) rows.push(["Conversion", summarizeObject(currentManifest.conversion)]);

  elements.manifestOutput.innerHTML = "";
  for (const [label, value] of rows) {
    const term = document.createElement("dt");
    const detail = document.createElement("dd");
    term.textContent = label;
    detail.textContent = String(value);
    elements.manifestOutput.append(term, detail);
  }
}

function renderMarkers(markers) {
  // Marker data is available through player.getMarkers().
  elements.markersOutput.innerHTML = "";
  if (markers.length === 0) {
    elements.markersOutput.textContent = "No markers.";
    return;
  }

  for (const marker of markers) {
    const row = document.createElement("div");
    row.className = "marker-row";

    const frame = document.createElement("span");
    frame.textContent = String(marker.frame);

    const label = document.createElement("span");
    label.textContent = marker.label;

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Jump";
    button.addEventListener("click", () => {
      player.pause();
      player.seekFrame(marker.frame);
    });

    row.append(frame, label, button);
    elements.markersOutput.append(row);
  }
}

function logEvent(name, detail) {
  const item = document.createElement("li");
  item.textContent = detail ? `${name}: ${detail}` : name;
  elements.eventLog.prepend(item);
  while (elements.eventLog.children.length > 80) {
    elements.eventLog.lastElementChild.remove();
  }
}

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.classList.toggle("is-error", isError);
}

function setControlsEnabled(enabled) {
  for (const control of [
    elements.playToggle,
    elements.stopButton,
    elements.prevButton,
    elements.nextButton,
    elements.seekInput,
    elements.fpsInput,
    elements.loopInput
  ]) {
    control.disabled = !enabled;
  }
}

function summarizeObject(value) {
  return Object.entries(value)
    .map(([key, item]) => `${key}: ${item}`)
    .join(", ");
}
