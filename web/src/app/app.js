import { TvaPlayer } from "../lib/player-api.js";
import { loadTvaFile } from "../lib/tva.js";

const dropZone = document.getElementById("drop-zone");
const controlsToggle = document.getElementById("controls-toggle");
const manifestToggle = document.getElementById("manifest-toggle");
const controlsOverlay = document.getElementById("controls-overlay");
const manifestOverlay = document.getElementById("manifest-overlay");
const fileInput = document.getElementById("file-input");
const statusEl = document.getElementById("status");
const frameOutput = document.getElementById("frame-output");
const playButton = document.getElementById("play-button");
const prevButton = document.getElementById("prev-button");
const nextButton = document.getElementById("next-button");
const seekInput = document.getElementById("seek-input");
const frameCounter = document.getElementById("frame-counter");
const fpsInput = document.getElementById("fps-input");
const loopInput = document.getElementById("loop-input");
const titleEl = document.getElementById("title");
const metadataEl = document.getElementById("metadata");
const markersEl = document.getElementById("markers");

const player = new TvaPlayer();

function setOverlayVisible(toggle, overlay, visible) {
  overlay.classList.toggle("is-hidden", !visible);
  toggle.setAttribute("aria-expanded", String(visible));
}

function toggleOverlay(toggle, overlay) {
  setOverlayVisible(toggle, overlay, overlay.classList.contains("is-hidden"));
}

player.on("framechange", ({ index, frame, frameCount }) => {
  frameOutput.textContent = frame;
  seekInput.value = String(index);
  frameCounter.textContent = `${index + 1} / ${frameCount}`;
});
player.on("play", () => {
  playButton.textContent = "Pause";
});
player.on("pause", () => {
  playButton.textContent = "Play";
});
player.on("stop", () => {
  playButton.textContent = "Play";
});
player.on("ended", () => {
  playButton.textContent = "Play";
});

controlsToggle.addEventListener("click", () => {
  toggleOverlay(controlsToggle, controlsOverlay);
});

manifestToggle.addEventListener("click", () => {
  toggleOverlay(manifestToggle, manifestOverlay);
});

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("is-error", isError);
}

function renderMetadata(manifest) {
  titleEl.textContent = manifest.title || "Untitled TVA";
  const rows = [
    ["Format", `${manifest.format} ${manifest.version}`],
    ["Size", `${manifest.width} x ${manifest.height} chars`],
    ["FPS", manifest.fps],
    ["Frames", manifest.frame_count],
    ["Duration", `${Number(manifest.duration).toFixed(2)} sec`],
    ["Author", manifest.author],
    ["License", manifest.license],
    ["Description", manifest.description]
  ].filter((row) => row[1] !== undefined && row[1] !== null && row[1] !== "");

  metadataEl.replaceChildren(
    ...rows.flatMap(([name, value]) => {
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = name;
      dd.textContent = String(value);
      return [dt, dd];
    })
  );
}

function renderMarkers(manifest) {
  markersEl.replaceChildren();
  const markers = Array.isArray(manifest.markers) ? manifest.markers : [];
  if (markers.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No markers";
    markersEl.append(empty);
    return;
  }

  for (const marker of markers) {
    const button = document.createElement("button");
    button.className = "marker-button";
    button.type = "button";
    button.textContent = `${String(marker.frame).padStart(6, "0")} ${marker.label}`;
    button.addEventListener("click", () => {
      player.pause();
      player.seekFrame(marker.frame);
    });
    markersEl.append(button);
  }
}

async function loadFile(file) {
  try {
    setStatus(`Loading ${file.name}...`);
    const tva = await loadTvaFile(file);
    player.load(tva);
    seekInput.max = String(tva.frames.length - 1);
    fpsInput.value = String(player.getFps());
    renderMetadata(tva.manifest);
    renderMarkers(tva.manifest);
    setStatus(`Loaded ${file.name}`);
  } catch (error) {
    player.stop();
    frameOutput.textContent = "";
    setStatus(error instanceof Error ? error.message : String(error), true);
  }
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (file) loadFile(file);
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("is-dragging");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("is-dragging");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("is-dragging");
  const file = event.dataTransfer?.files?.[0];
  if (file) loadFile(file);
});

playButton.addEventListener("click", () => {
  player.toggle();
});

prevButton.addEventListener("click", () => player.prevFrame());
nextButton.addEventListener("click", () => player.nextFrame());
seekInput.addEventListener("input", () => player.seekFrame(Number(seekInput.value)));
fpsInput.addEventListener("change", () => player.setFps(Number(fpsInput.value)));
loopInput.addEventListener("change", () => player.setLoop(loopInput.checked));
