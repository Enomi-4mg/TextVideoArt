import { TvaPlayer } from "../src/lib/player-api.js";
import { loadTvaFile } from "../src/lib/tva.js";
import { PreFrameRenderer } from "../src/lib/renderer-pre.js";

const params = new URLSearchParams(window.location.search);
const player = new TvaPlayer();

const elements = {
  dropZone: document.getElementById("drop-zone"),
  stage: document.getElementById("stage"),
  workspace: document.getElementById("workspace"),
  uiToggle: document.getElementById("ui-toggle"),
  fileInput: document.getElementById("file-input"),
  status: document.getElementById("status"),
  frameOutput: document.getElementById("frame-output"),
  tabs: Array.from(document.querySelectorAll("[data-tab]")),
  panels: Array.from(document.querySelectorAll("[data-panel]")),
  playButton: document.getElementById("play-button"),
  stopButton: document.getElementById("stop-button"),
  prevButton: document.getElementById("prev-button"),
  nextButton: document.getElementById("next-button"),
  seekInput: document.getElementById("seek-input"),
  frameCounter: document.getElementById("frame-counter"),
  fpsInput: document.getElementById("fps-input"),
  loopInput: document.getElementById("loop-input"),
  title: document.getElementById("title"),
  metadata: document.getElementById("metadata"),
  markers: document.getElementById("markers"),
  debugPlay: document.getElementById("debug-play"),
  debugPause: document.getElementById("debug-pause"),
  debugStop: document.getElementById("debug-stop"),
  debugPrev: document.getElementById("debug-prev"),
  debugNext: document.getElementById("debug-next"),
  debugFrameInput: document.getElementById("debug-frame-input"),
  debugSeekFrame: document.getElementById("debug-seek-frame"),
  debugTimeInput: document.getElementById("debug-time-input"),
  debugSeekTime: document.getElementById("debug-seek-time"),
  debugFpsInput: document.getElementById("debug-fps-input"),
  debugSetFps: document.getElementById("debug-set-fps"),
  debugLoopInput: document.getElementById("debug-loop-input"),
  debugState: document.getElementById("debug-state"),
  manifestJson: document.getElementById("manifest-json"),
  markersJson: document.getElementById("markers-json"),
  eventLog: document.getElementById("event-log"),
  vjFontSize: document.getElementById("vj-font-size"),
  vjLineHeight: document.getElementById("vj-line-height"),
  vjTheme: document.getElementById("vj-theme"),
  vjForeground: document.getElementById("vj-foreground"),
  vjBackground: document.getElementById("vj-background"),
  vjScale: document.getElementById("vj-scale"),
  vjFitMode: document.getElementById("vj-fit-mode"),
  vjCenter: document.getElementById("vj-center"),
  vjAutoplay: document.getElementById("vj-autoplay"),
  vjLoop: document.getElementById("vj-loop"),
  vjHideUi: document.getElementById("vj-hide-ui")
};

const renderer = new PreFrameRenderer(elements.frameOutput);
const THEME_PRESETS = {
  plain: {
    foreground: "#f2f2f2",
    background: "#050505",
    glow: "transparent"
  },
  "crt-green": {
    foreground: "#8cffb1",
    background: "#020403",
    glow: "rgb(0 255 102 / 70%)"
  },
  amber: {
    foreground: "#ffbf66",
    background: "#090502",
    glow: "rgb(255 160 55 / 66%)"
  }
};
const playerControls = [
  elements.playButton,
  elements.stopButton,
  elements.prevButton,
  elements.nextButton,
  elements.seekInput,
  elements.fpsInput,
  elements.loopInput
];
const debugControls = [
  elements.debugPlay,
  elements.debugPause,
  elements.debugStop,
  elements.debugPrev,
  elements.debugNext,
  elements.debugFrameInput,
  elements.debugSeekFrame,
  elements.debugTimeInput,
  elements.debugSeekTime,
  elements.debugFpsInput,
  elements.debugSetFps,
  elements.debugLoopInput
];

function paramValue(name, fallback) {
  return params.get(name) ?? fallback;
}

function paramFlag(name) {
  return params.has(name);
}

function initialTab() {
  const tab = params.get("tab");
  if (["player", "debug", "vj"].includes(tab)) return tab;
  if (params.get("mode") === "vj") return "vj";
  return "player";
}

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.classList.toggle("is-error", isError);
}

function setControlsEnabled(enabled) {
  for (const control of [...playerControls, ...debugControls]) {
    control.disabled = !enabled;
  }
}

function setActiveTab(name) {
  for (const tab of elements.tabs) {
    const active = tab.dataset.tab === name;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
  }
  for (const panel of elements.panels) {
    panel.classList.toggle("is-active", panel.dataset.panel === name);
  }
  elements.dropZone.classList.toggle("vj-mode", name === "vj");
}

function setUiVisible(visible) {
  elements.workspace.classList.toggle("is-hidden", !visible);
  elements.uiToggle.textContent = visible ? "Hide UI" : "Show UI";
  elements.uiToggle.setAttribute("aria-expanded", String(visible));
}

function renderDefinitionList(target, rows) {
  target.replaceChildren(
    ...rows.flatMap(([name, value]) => {
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = name;
      dd.textContent = String(value);
      return [dt, dd];
    })
  );
}

function manifestRows(manifest) {
  if (!manifest) return [];
  return [
    ["Title", manifest.title || "(untitled)"],
    ["Format", `${manifest.format} ${manifest.version}`],
    ["Size", `${manifest.width} x ${manifest.height} chars`],
    ["FPS", manifest.fps],
    ["Frames", manifest.frame_count],
    ["Duration", `${Number(manifest.duration).toFixed(2)} sec`],
    ["Author", manifest.author],
    ["License", manifest.license],
    ["Description", manifest.description]
  ].filter((row) => row[1] !== undefined && row[1] !== null && row[1] !== "");
}

function renderManifest() {
  const manifest = player.getManifest();
  elements.title.textContent = manifest?.title || "No TVA loaded";
  renderDefinitionList(elements.metadata, manifestRows(manifest));
  elements.manifestJson.textContent = JSON.stringify(manifest || {}, null, 2);
}

function renderMarkers() {
  const markers = player.getMarkers();
  elements.markersJson.textContent = JSON.stringify(markers, null, 2);
  elements.markers.replaceChildren();
  if (markers.length === 0) {
    elements.markers.textContent = "No markers loaded.";
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
    elements.markers.append(row);
  }
}

function updateDebugState() {
  const stateRows = [
    ["getCurrentFrameIndex()", player.getCurrentFrameIndex()],
    ["getFrameCount()", player.getFrameCount()],
    ["getFps()", player.getFps()],
    ["isPlaying()", player.isPlaying()],
    ["getManifest()", player.getManifest() ? "loaded" : "null"],
    ["getMarkers()", `${player.getMarkers().length} markers`]
  ];
  renderDefinitionList(elements.debugState, stateRows);
}

function logEvent(name, detail) {
  const item = document.createElement("li");
  const message = Object.keys(detail).length > 0 ? `${name}: ${summarizeEvent(detail)}` : name;
  item.textContent = message;
  elements.eventLog.prepend(item);
  while (elements.eventLog.children.length > 80) {
    elements.eventLog.lastElementChild.remove();
  }
}

function summarizeEvent(detail) {
  if ("index" in detail && "frameCount" in detail) {
    return `${detail.index + 1} / ${detail.frameCount}`;
  }
  if ("frameCount" in detail) return `${detail.frameCount} frames`;
  if ("fps" in detail) return `${detail.fps} fps`;
  if ("loop" in detail) return detail.loop ? "loop on" : "loop off";
  return "";
}

function syncControlValues() {
  const index = player.getCurrentFrameIndex();
  const count = player.getFrameCount();
  const maxFrame = Math.max(0, count - 1);
  const fps = player.getFps();
  const loop = player.loop;

  elements.seekInput.max = String(maxFrame);
  elements.seekInput.value = String(index);
  elements.frameCounter.textContent = count > 0 ? `${index + 1} / ${count}` : "0 / 0";
  elements.fpsInput.value = String(fps);
  elements.loopInput.checked = loop;
  elements.debugFrameInput.max = String(maxFrame);
  elements.debugFrameInput.value = String(index);
  elements.debugTimeInput.value = String(count > 0 ? (index / fps).toFixed(2) : 0);
  elements.debugFpsInput.value = String(fps);
  elements.debugLoopInput.checked = loop;
  elements.vjLoop.checked = loop;
  elements.playButton.textContent = player.isPlaying() ? "Pause" : "Play";
  updateDebugState();
}

function applyVjSettings() {
  const fontSize = Number(elements.vjFontSize.value) || 16;
  const lineHeight = Number(elements.vjLineHeight.value) || 1;
  const scale = Number(elements.vjScale.value) || 1;
  const theme = THEME_PRESETS[elements.vjTheme.value] ? elements.vjTheme.value : "plain";
  const themePreset = THEME_PRESETS[theme];

  document.documentElement.style.setProperty("--vj-font-size", `${fontSize}px`);
  document.documentElement.style.setProperty("--vj-line-height", String(lineHeight));
  document.documentElement.style.setProperty("--vj-foreground", elements.vjForeground.value);
  document.documentElement.style.setProperty("--vj-background", elements.vjBackground.value);
  document.documentElement.style.setProperty("--vj-scale", String(scale));
  document.documentElement.style.setProperty("--vj-glow", themePreset.glow);
  elements.stage.dataset.theme = theme;
  elements.stage.classList.toggle("is-centered", elements.vjCenter.checked);
  elements.stage.classList.toggle("is-contain", elements.vjFitMode.value === "contain");
  player.setLoop(elements.vjLoop.checked);
}

function applyThemePreset() {
  const theme = THEME_PRESETS[elements.vjTheme.value] ? elements.vjTheme.value : "plain";
  const preset = THEME_PRESETS[theme];
  elements.vjForeground.value = preset.foreground;
  elements.vjBackground.value = preset.background;
  applyVjSettings();
}

function applyInitialVjSettings() {
  const theme = paramValue("theme", "plain");
  elements.vjTheme.value = THEME_PRESETS[theme] ? theme : "plain";
  const themePreset = THEME_PRESETS[elements.vjTheme.value];
  elements.vjFontSize.value = paramValue("fontSize", "16");
  elements.vjLineHeight.value = paramValue("lineHeight", "1");
  elements.vjForeground.value = paramValue("foreground", themePreset.foreground);
  elements.vjBackground.value = paramValue("background", themePreset.background);
  elements.vjScale.value = paramValue("scale", "1");
  elements.vjFitMode.value = paramValue("fitMode", "scroll");
  elements.vjCenter.checked = paramFlag("center");
  elements.vjAutoplay.checked = paramFlag("autoplay");
  elements.vjLoop.checked = paramFlag("loop");
  applyVjSettings();

  const fps = Number(params.get("fps"));
  if (Number.isFinite(fps) && fps > 0) {
    player.setFps(fps);
    elements.fpsInput.value = String(fps);
    elements.debugFpsInput.value = String(fps);
  }
}

async function loadFile(file) {
  setStatus(`Loading ${file.name}...`);
  try {
    const tva = await loadTvaFile(file);
    player.load(tva);
    setControlsEnabled(true);
    renderManifest();
    renderMarkers();
    syncControlValues();
    setStatus(`Loaded ${file.name}`);
    if (elements.vjAutoplay.checked) player.play();
  } catch (error) {
    player.stop();
    setControlsEnabled(false);
    renderer.clear();
    setStatus(error instanceof Error ? error.message : String(error), true);
  }
}

elements.tabs.forEach((tab) => {
  tab.addEventListener("click", () => setActiveTab(tab.dataset.tab));
});

elements.uiToggle.addEventListener("click", () => {
  setUiVisible(elements.workspace.classList.contains("is-hidden"));
});

elements.vjHideUi.addEventListener("click", () => setUiVisible(false));

elements.fileInput.addEventListener("change", () => {
  const file = elements.fileInput.files?.[0];
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
  const file = event.dataTransfer?.files?.[0];
  if (file) loadFile(file);
});

elements.playButton.addEventListener("click", () => player.toggle());
elements.stopButton.addEventListener("click", () => player.stop());
elements.prevButton.addEventListener("click", () => player.prevFrame());
elements.nextButton.addEventListener("click", () => player.nextFrame());
elements.seekInput.addEventListener("input", () => {
  player.pause();
  player.seekFrame(Number(elements.seekInput.value));
});
elements.fpsInput.addEventListener("change", () => player.setFps(Number(elements.fpsInput.value)));
elements.loopInput.addEventListener("change", () => player.setLoop(elements.loopInput.checked));

elements.debugPlay.addEventListener("click", () => player.play());
elements.debugPause.addEventListener("click", () => player.pause());
elements.debugStop.addEventListener("click", () => player.stop());
elements.debugPrev.addEventListener("click", () => player.prevFrame());
elements.debugNext.addEventListener("click", () => player.nextFrame());
elements.debugSeekFrame.addEventListener("click", () => player.seekFrame(Number(elements.debugFrameInput.value)));
elements.debugSeekTime.addEventListener("click", () => player.seekTime(Number(elements.debugTimeInput.value)));
elements.debugSetFps.addEventListener("click", () => player.setFps(Number(elements.debugFpsInput.value)));
elements.debugLoopInput.addEventListener("change", () => player.setLoop(elements.debugLoopInput.checked));

for (const input of [
  elements.vjFontSize,
  elements.vjLineHeight,
  elements.vjForeground,
  elements.vjBackground,
  elements.vjScale,
  elements.vjFitMode,
  elements.vjCenter,
  elements.vjLoop
]) {
  input.addEventListener("input", applyVjSettings);
  input.addEventListener("change", applyVjSettings);
}

elements.vjTheme.addEventListener("change", applyThemePreset);

document.addEventListener("keydown", (event) => {
  if (["INPUT", "TEXTAREA", "SELECT", "BUTTON"].includes(event.target.tagName)) return;

  if (event.key === " ") {
    event.preventDefault();
    player.toggle();
  } else if (event.key === "ArrowLeft") {
    player.prevFrame();
  } else if (event.key === "ArrowRight") {
    player.nextFrame();
  } else if (event.key === "h" || event.key === "H") {
    setUiVisible(elements.workspace.classList.contains("is-hidden"));
  } else if (event.key === "Escape") {
    player.pause();
    setUiVisible(false);
  }
});

for (const eventName of ["load", "play", "pause", "stop", "ended", "fpschange", "loopchange"]) {
  player.on(eventName, (detail) => {
    logEvent(eventName, detail);
    syncControlValues();
  });
}

player.on("framechange", ({ index, frame, frameCount }) => {
  renderer.render(frame || "");
  elements.seekInput.value = String(index);
  elements.frameCounter.textContent = frameCount > 0 ? `${index + 1} / ${frameCount}` : "0 / 0";
  logEvent("framechange", { index, frameCount });
  syncControlValues();
});

setControlsEnabled(false);
applyInitialVjSettings();
setActiveTab(initialTab());
setStatus("Waiting for a TVA file.");
