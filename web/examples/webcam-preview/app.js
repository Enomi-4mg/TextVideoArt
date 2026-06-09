const frameOutput = document.getElementById("frame-output");
const video = document.getElementById("camera-video");
const canvas = document.getElementById("sample-canvas");
const controlsOverlay = document.getElementById("controls-overlay");
const startButton = document.getElementById("start-button");
const stopButton = document.getElementById("stop-button");
const widthInput = document.getElementById("width-input");
const fpsInput = document.getElementById("fps-input");
const charsetInput = document.getElementById("charset-input");
const invertInput = document.getElementById("invert-input");
const aspectInput = document.getElementById("aspect-input");
const statusOutput = document.getElementById("status");

const context = canvas.getContext("2d", { willReadFrequently: true });

let stream = null;
let timerId = null;

function setStatus(message, isError = false) {
  statusOutput.textContent = message;
  statusOutput.classList.toggle("is-error", isError);
}

function readSettings() {
  const width = Number.parseInt(widthInput.value, 10);
  const fps = Number.parseFloat(fpsInput.value);
  const charset = charsetInput.value;
  const aspectCorrection = Number.parseFloat(aspectInput.value);

  if (!Number.isFinite(width) || width <= 0) {
    throw new Error("Width must be a positive number.");
  }
  if (!Number.isFinite(fps) || fps <= 0) {
    throw new Error("FPS must be a positive number.");
  }
  if (!Number.isFinite(aspectCorrection) || aspectCorrection <= 0) {
    throw new Error("Aspect correction must be a positive number.");
  }
  if (charset.length < 2) {
    throw new Error("Charset must contain at least 2 characters.");
  }

  return {
    width,
    fps,
    charset,
    invert: invertInput.checked,
    aspectCorrection,
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

  const height = Math.max(
    1,
    Math.floor((video.videoHeight / video.videoWidth) * settings.width * settings.aspectCorrection),
  );

  canvas.width = settings.width;
  canvas.height = height;
  context.drawImage(video, 0, 0, settings.width, height);

  const imageData = context.getImageData(0, 0, settings.width, height);
  frameOutput.textContent = imageDataToTextFrame(
    imageData,
    settings.width,
    height,
    settings.charset,
    settings.invert,
  );
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

function toggleOverlay() {
  controlsOverlay.classList.toggle("is-hidden");
}

document.addEventListener("keydown", (event) => {
  if (isFormControl(event.target)) {
    return;
  }

  if (event.key === "h" || event.key === "H") {
    toggleOverlay();
  } else if (event.key === "Escape") {
    controlsOverlay.classList.add("is-hidden");
  }
});

startButton.addEventListener("click", startCamera);
stopButton.addEventListener("click", stopCamera);

fpsInput.addEventListener("change", restartTimerIfRunning);
widthInput.addEventListener("change", renderFrame);
charsetInput.addEventListener("change", renderFrame);
invertInput.addEventListener("change", renderFrame);
aspectInput.addEventListener("change", renderFrame);

window.addEventListener("beforeunload", stopCamera);

setStatus("Waiting for camera.");
