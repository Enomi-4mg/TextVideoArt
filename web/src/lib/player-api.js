export class TvaPlayer extends EventTarget {
  constructor({ fps = 10, loop = false } = {}) {
    super();
    this.manifest = null;
    this.frames = [];
    this.currentFrame = 0;
    this.fps = fps;
    this.loop = loop;
    this.playing = false;
    this.animationFrameId = null;
    this.playbackStartTime = 0;
    this.playbackStartFrame = 0;
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
    this.playbackStartFrame = this.currentFrame;
    this.playbackStartTime = this.now();
    this.dispatch("play", {});
    this.scheduleTick();
  }

  pause() {
    if (!this.playing && this.animationFrameId === null) return;
    this.playing = false;
    this.cancelTick();
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
    if (this.playing) {
      this.playbackStartFrame = this.currentFrame;
      this.playbackStartTime = this.now();
    }
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

  now() {
    return globalThis.performance?.now ? globalThis.performance.now() : Date.now();
  }

  requestFrame(callback) {
    if (globalThis.requestAnimationFrame) {
      return globalThis.requestAnimationFrame(callback);
    }
    return globalThis.setTimeout(() => callback(this.now()), 16);
  }

  cancelFrame(id) {
    if (globalThis.cancelAnimationFrame) {
      globalThis.cancelAnimationFrame(id);
    } else {
      globalThis.clearTimeout(id);
    }
  }

  scheduleTick() {
    this.cancelTick();
    this.animationFrameId = this.requestFrame((timestamp) => this.tick(timestamp));
  }

  cancelTick() {
    if (this.animationFrameId !== null) {
      this.cancelFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  tick(timestamp) {
    if (!this.playing || this.frames.length === 0) return;

    const elapsedSeconds = Math.max(0, (timestamp - this.playbackStartTime) / 1000);
    const frameOffset = Math.floor(elapsedSeconds * this.fps);
    let nextIndex = this.playbackStartFrame + frameOffset;

    if (nextIndex >= this.frames.length) {
      if (this.loop) {
        nextIndex %= this.frames.length;
        this.playbackStartFrame = nextIndex;
        this.playbackStartTime = timestamp;
      } else {
        this.currentFrame = this.frames.length - 1;
        this.emitFrameChange();
        this.pause();
        this.dispatch("ended", {});
        return;
      }
    }

    if (nextIndex !== this.currentFrame) {
      this.currentFrame = nextIndex;
      this.emitFrameChange();
    }

    this.scheduleTick();
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
