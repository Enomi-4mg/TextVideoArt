import { CHARSET_PRESETS } from "../../src/lib/charsets.js";

const frameOutput = document.getElementById("frame-output");
const frameCanvas = document.getElementById("frame-canvas");
const previewStage = document.getElementById("preview-stage");
const video = document.getElementById("camera-video");
const canvas = document.getElementById("sample-canvas");
const previewSurface = document.getElementById("preview-surface");
const controlsOverlay = document.getElementById("controls-overlay");
const controlsToggle = document.getElementById("controls-toggle");
const startButton = document.getElementById("start-button");
const stopButton = document.getElementById("stop-button");
const fpsInput = document.getElementById("fps-input");
const resolutionInput = document.getElementById("resolution-input");
const charsetInput = document.getElementById("charset-input");
const invertInput = document.getElementById("invert-input");
const aspectInput = document.getElementById("aspect-input");
const statusOutput = document.getElementById("status");

const context = canvas.getContext("2d", { willReadFrequently: true });
const frameContext = frameCanvas.getContext("2d");
const MIN_RESOLUTION = 1;
const MAX_RESOLUTION = 64;
const DEFAULT_RESOLUTION = 24;
let stream = null;
let timerId = null;

function setStatus(message, isError = false) {
  statusOutput.textContent = message;
  statusOutput.classList.toggle("is-error", isError);
}

function outputFont() {
  return getComputedStyle(frameOutput).font;
}

function availablePreviewSize() {
  const style = getComputedStyle(previewStage);
  const width =
    previewStage.clientWidth -
    Number.parseFloat(style.paddingLeft) -
    Number.parseFloat(style.paddingRight);
  const height =
    previewStage.clientHeight -
    Number.parseFloat(style.paddingTop) -
    Number.parseFloat(style.paddingBottom);

  return {
    width: Math.max(1, width),
    height: Math.max(1, height),
  };
}

function cameraDisplaySize(columns, rows) {
  if (video.videoWidth > 0 && video.videoHeight > 0) {
    return {
      width: video.videoWidth,
      height: video.videoHeight,
    };
  }

  return {
    width: Math.max(1, columns),
    height: Math.max(1, rows),
  };
}

function previewCanvasSize(columns, rows) {
  const available = availablePreviewSize();
  const nativeSize = cameraDisplaySize(columns, rows);
  const scale = Math.min(
    available.width / nativeSize.width,
    available.height / nativeSize.height,
  );

  return {
    width: Math.max(1, nativeSize.width * scale),
    height: Math.max(1, nativeSize.height * scale),
  };
}

function readResolution() {
  const value = Number.parseInt(resolutionInput.value, 10);
  if (!Number.isFinite(value)) return DEFAULT_RESOLUTION;
  return Math.max(MIN_RESOLUTION, Math.min(MAX_RESOLUTION, value));
}

function resolutionToFrameSize(resolution, aspectCorrection) {
  const targetColumns = Math.max(4, Math.round(16 + resolution * 3.5));
  const sourceRatio = video.videoHeight / video.videoWidth;
  const targetRows = Math.max(2, Math.round(targetColumns * sourceRatio * aspectCorrection));
  return { width: targetColumns, height: targetRows };
}

function readSettings() {
  const fps = Number.parseFloat(fpsInput.value);
  const charset = CHARSET_PRESETS[charsetInput.value];
  const aspectCorrection = Number.parseFloat(aspectInput.value);
  const resolution = readResolution();

  if (!Number.isFinite(fps) || fps <= 0) {
    throw new Error("FPS must be a positive number.");
  }
  if (!Number.isFinite(aspectCorrection) || aspectCorrection <= 0) {
    throw new Error("Aspect correction must be a positive number.");
  }
  if (charset.length < 2) {
    throw new Error("Select a charset preset.");
  }

  return {
    fps,
    charset,
    invert: invertInput.checked,
    aspectCorrection,
    resolution,
  };
}

function brightnessToChar(brightness, charset, invert) {
  const maxIndex = charset.length - 1;
  const index = Math.floor((brightness / 255) * maxIndex);
  return charset[invert ? maxIndex - index : index];
}

function imageDataToTextFrame(imageData, width, height, charset, invert) {
  const rows = [];
  const data = imageData.data;

  for (let y = 0; y < height; y += 1) {
    let row = "";
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      const r = data[offset];
      const g = data[offset + 1];
      const b = data[offset + 2];
      const brightness = 0.299 * r + 0.587 * g + 0.114 * b;
      row += brightnessToChar(brightness, charset, invert);
    }
    rows.push(row);
  }

  return rows.join("\n");
}

function resizeOutputCanvas(columns, rows) {
  const size = previewCanvasSize(columns, rows);
  const scale = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.floor(size.width * scale));
  const height = Math.max(1, Math.floor(size.height * scale));

  if (frameCanvas.width !== width || frameCanvas.height !== height) {
    frameCanvas.width = width;
    frameCanvas.height = height;
  }
  frameCanvas.style.width = `${size.width}px`;
  frameCanvas.style.height = `${size.height}px`;
  frameContext.setTransform(scale, 0, 0, scale, 0, 0);
  return size;
}

function drawTextFrame(textFrame) {
  const rows = textFrame.split("\n");
  const columns = Math.max(1, Math.max(...rows.map((row) => row.length)));
  const size = resizeOutputCanvas(columns, rows.length);
  const cellWidth = size.width / columns;
  const cellHeight = size.height / Math.max(1, rows.length);
  const fontSize = Math.max(1, Math.min(cellHeight * 0.88, cellWidth * 1.85));
  const xOffset = cellWidth / 2;
  const yOffset = cellHeight / 2;

  frameContext.clearRect(0, 0, size.width, size.height);
  frameContext.fillStyle = "#050505";
  frameContext.fillRect(0, 0, size.width, size.height);
  frameContext.font = outputFont().replace(/\d+(\.\d+)?px/, `${fontSize}px`);
  frameContext.fillStyle = "#ffffff";
  frameContext.textAlign = "center";
  frameContext.textBaseline = "middle";

  rows.forEach((row, index) => {
    for (let column = 0; column < row.length; column += 1) {
      frameContext.fillText(row[column], column * cellWidth + xOffset, index * cellHeight + yOffset);
    }
  });
}

function renderFrame() {
  if (!stream || video.videoWidth <= 0 || video.videoHeight <= 0) {
    return;
  }

  let settings;
  try {
    settings = readSettings();
  } catch (error) {
    setStatus(error.message, true);
    return;
  }

  const { width, height } = resolutionToFrameSize(settings.resolution, settings.aspectCorrection);

  canvas.width = width;
  canvas.height = height;
  context.drawImage(video, 0, 0, width, height);

  const imageData = context.getImageData(0, 0, width, height);
  const textFrame = imageDataToTextFrame(
    imageData,
    width,
    height,
    settings.charset,
    settings.invert,
  );
  frameOutput.textContent = textFrame;
  drawTextFrame(textFrame);
  setStatus("Running.");
}

function clearPreviewTimer() {
  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
}

function startPreviewTimer() {
  clearPreviewTimer();

  let settings;
  try {
    settings = readSettings();
  } catch (error) {
    setStatus(error.message, true);
    return;
  }

  renderFrame();
  timerId = window.setInterval(renderFrame, 1000 / settings.fps);
}

function stopCamera() {
  clearPreviewTimer();

  if (stream) {
    for (const track of stream.getTracks()) {
      track.stop();
    }
  }

  stream = null;
  video.srcObject = null;
  startButton.disabled = false;
  stopButton.disabled = true;
  setStatus("Stopped.");
}

async function startCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    setStatus("Unsupported browser: mediaDevices.getUserMedia is unavailable.", true);
    return;
  }

  stopCamera();
  setStatus("Requesting camera permission.");

  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    await video.play();
    startButton.disabled = true;
    stopButton.disabled = false;
    setStatus("Running.");
    startPreviewTimer();
  } catch (error) {
    stream = null;
    video.srcObject = null;
    setStatus(`Camera error: ${error.message}`, true);
  }
}

function restartTimerIfRunning() {
  if (stream) {
    startPreviewTimer();
  }
}

function isFormControl(element) {
  return ["INPUT", "TEXTAREA", "SELECT", "BUTTON"].includes(element.tagName);
}

function setOverlayVisible(isVisible) {
  controlsOverlay.classList.toggle("is-hidden", !isVisible);
  previewSurface.classList.toggle("controls-hidden", !isVisible);
  controlsToggle.setAttribute("aria-expanded", String(isVisible));
  controlsToggle.textContent = isVisible ? "Hide Controls" : "Show Controls";
}

function toggleOverlay() {
  setOverlayVisible(controlsOverlay.classList.contains("is-hidden"));
}

document.addEventListener("keydown", (event) => {
  if (isFormControl(event.target)) {
    return;
  }

  if (event.key === "h" || event.key === "H") {
    toggleOverlay();
  } else if (event.key === "Escape") {
    setOverlayVisible(false);
  }
});

controlsToggle.addEventListener("click", toggleOverlay);
startButton.addEventListener("click", startCamera);
stopButton.addEventListener("click", stopCamera);

fpsInput.addEventListener("change", restartTimerIfRunning);
resolutionInput.addEventListener("change", renderFrame);
charsetInput.addEventListener("change", renderFrame);
invertInput.addEventListener("change", renderFrame);
aspectInput.addEventListener("change", renderFrame);
window.addEventListener("resize", renderFrame);

window.addEventListener("beforeunload", stopCamera);

setStatus("Waiting for camera.");
