import { PreFrameRenderer } from "../../src/lib/renderer-pre.js";

const params = new URLSearchParams(window.location.search);
const output = document.querySelector("#output");
const stage = document.querySelector("#stage");
const overlay = document.querySelector("#overlay");
const fileInput = document.querySelector("#file");
const playButton = document.querySelector("#play");
const prevButton = document.querySelector("#prev");
const nextButton = document.querySelector("#next");
const loopInput = document.querySelector("#loop");
const renderer = new PreFrameRenderer(output);

let frames = ["Drop a .tva file or choose one below."];
let frameIndex = 0;
let playing = false;
let timer = null;

function option(name, fallback) {
  return params.get(name) ?? fallback;
}

function applyOptions() {
  document.documentElement.style.setProperty("--font-size", `${option("fontSize", "16")}px`);
  document.documentElement.style.setProperty("--line-height", option("lineHeight", "1"));
  document.documentElement.style.setProperty("--foreground", option("foreground", "#f2f2f2"));
  document.documentElement.style.setProperty("--background", option("background", "#050505"));
  document.documentElement.style.setProperty("--scale", option("scale", "1"));
  stage.classList.toggle("center", params.has("center"));
  stage.classList.toggle("contain", option("fitMode", "scroll") === "contain");
  loopInput.checked = params.has("loop");
}

function renderCurrent() {
  renderer.render(frames[frameIndex] ?? "");
}

function step(delta) {
  frameIndex += delta;
  if (frameIndex >= frames.length) {
    if (loopInput.checked) {
      frameIndex = 0;
    } else {
      frameIndex = frames.length - 1;
      pause();
    }
  }
  if (frameIndex < 0) {
    frameIndex = frames.length - 1;
  }
  renderCurrent();
}

function play() {
  if (playing) {
    return;
  }
  playing = true;
  const fps = Number(option("fps", "10"));
  timer = window.setInterval(() => step(1), 1000 / Math.max(1, fps));
}

function pause() {
  playing = false;
  window.clearInterval(timer);
  timer = null;
}

function togglePlay() {
  if (playing) {
    pause();
  } else {
    play();
  }
}

async function loadTva(file) {
  const zip = await import("https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm");
  const archive = await zip.default.loadAsync(await file.arrayBuffer());
  const manifest = JSON.parse(await archive.file("manifest.json").async("string"));
  frames = [];
  for (let index = 0; index < manifest.frame_count; index += 1) {
    frames.push(await archive.file(`frames/${String(index).padStart(6, "0")}.txt`).async("string"));
  }
  frameIndex = 0;
  renderCurrent();
  if (params.has("autoplay")) {
    play();
  }
}

fileInput.addEventListener("change", () => {
  const [file] = fileInput.files;
  if (file) {
    loadTva(file);
  }
});

stage.addEventListener("dragover", (event) => event.preventDefault());
stage.addEventListener("drop", (event) => {
  event.preventDefault();
  const [file] = event.dataTransfer.files;
  if (file) {
    loadTva(file);
  }
});

playButton.addEventListener("click", togglePlay);
prevButton.addEventListener("click", () => step(-1));
nextButton.addEventListener("click", () => step(1));

window.addEventListener("keydown", (event) => {
  if (event.key === " ") {
    event.preventDefault();
    togglePlay();
  } else if (event.key === "ArrowLeft") {
    step(-1);
  } else if (event.key === "ArrowRight") {
    step(1);
  } else if (event.key.toLowerCase() === "h") {
    overlay.classList.toggle("hidden");
  } else if (event.key === "Escape") {
    pause();
  }
});

applyOptions();
renderCurrent();
if (params.has("autoplay")) {
  play();
}
