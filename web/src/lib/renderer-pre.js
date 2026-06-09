export class PreFrameRenderer {
  constructor(target) {
    if (!(target instanceof HTMLElement)) {
      throw new TypeError("PreFrameRenderer target must be an HTMLElement");
    }
    this.target = target;
  }

  render(frame) {
    this.target.textContent = String(frame);
  }

  clear() {
    this.target.textContent = "";
  }
}
