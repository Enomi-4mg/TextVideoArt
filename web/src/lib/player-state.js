import { TvaPlayer } from "./player-api.js";

export class PlayerState extends TvaPlayer {
  constructor(onFrameChange) {
    super();
    if (onFrameChange) {
      this.on("framechange", ({ index, frame }) => onFrameChange(index, frame));
    }
  }

  seek(index) {
    this.seekFrame(index);
  }

  next() {
    this.nextFrame();
  }

  prev() {
    this.prevFrame();
  }
}
