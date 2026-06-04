export class TvaPlayer extends EventTarget {
  constructor({ fps = 10, loop = false } = {}) {
    super();
    this.manifest = null;
    this.frames = [];
    this.currentFrame = 0;
    this.fps = fps;
    this.loop = loop;
    this.playing = false;
    this.timerId = null;
  }

  load({ manifest, frames }) {
    this.pause();
    this.manifest = manifest;
    this.frames = frames;
    this.currentFrame = 0;
    this.fps = Number(manifest.fps) || this.fps;
    this.dispatch("load", { manifest, frameCount: frames.length });
    this.emitFrameChange();
  }

  play() {
    if (this.playing || this.frames.length === 0) return;
    this.playing = true;
    this.dispatch("play", {});
    this.timerId = setInterval(() => this.nextFrame(), 1000 / this.fps);
  }

  pause() {
    if (!this.playing && this.timerId === null) return;
    this.playing = false;
    if (this.timerId !== null) {
      clearInterval(this.timerId);
      this.timerId = null;
    }
    this.dispatch("pause", {});
  }

  stop() {
    this.pause();
    this.seekFrame(0);
    this.dispatch("stop", {});
  }

  toggle() {
    if (this.playing) {
      this.pause();
    } else {
      this.play();
    }
  }

  seekFrame(index) {
    if (this.frames.length === 0) return;
    const nextIndex = Number(index);
    if (!Number.isFinite(nextIndex)) return;
    this.currentFrame = Math.max(0, Math.min(this.frames.length - 1, Math.floor(nextIndex)));
    this.emitFrameChange();
  }

  seekTime(time) {
    this.seekFrame(Math.floor(Number(time) * this.fps));
  }

  nextFrame() {
    if (this.frames.length === 0) return;
    if (this.currentFrame >= this.frames.length - 1) {
      if (this.loop) {
        this.seekFrame(0);
      } else {
        this.pause();
        this.dispatch("ended", {});
      }
      return;
    }
    this.seekFrame(this.currentFrame + 1);
  }

  prevFrame() {
    this.seekFrame(this.currentFrame - 1);
  }

  setFps(fps) {
    const nextFps = Number(fps);
    if (!Number.isFinite(nextFps) || nextFps <= 0) return;
    const wasPlaying = this.playing;
    this.pause();
    this.fps = nextFps;
    this.dispatch("fpschange", { fps: this.fps });
    if (wasPlaying) this.play();
  }

  setLoop(loop) {
    this.loop = Boolean(loop);
    this.dispatch("loopchange", { loop: this.loop });
  }

  getCurrentFrame() {
    return this.frames[this.currentFrame] || "";
  }

  getCurrentFrameIndex() {
    return this.currentFrame;
  }

  getFrameCount() {
    return this.frames.length;
  }

  getFps() {
    return this.fps;
  }

  getManifest() {
    return this.manifest;
  }

  getMarkers() {
    return Array.isArray(this.manifest?.markers) ? this.manifest.markers : [];
  }

  isPlaying() {
    return this.playing;
  }

  on(type, handler) {
    const listener = (event) => handler(event.detail);
    this.addEventListener(type, listener);
    return () => this.removeEventListener(type, listener);
  }

  dispatch(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }

  emitFrameChange() {
    this.dispatch("framechange", {
      index: this.currentFrame,
      frame: this.getCurrentFrame(),
      frameCount: this.frames.length,
      manifest: this.manifest
    });
  }
}
