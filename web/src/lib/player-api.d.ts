export type TvaMarker = {
  frame: number;
  label: string;
  id?: string;
};

export type TvaManifest = {
  format: string;
  format_name: string;
  version: string;
  title?: string;
  author?: string;
  description?: string;
  license?: string;
  width: number;
  height: number;
  fps: number;
  frame_count: number;
  duration: number;
  charset: string;
  invert: boolean;
  encoding: string;
  color_mode: string;
  frame_format: string;
  frames_path: string;
  markers?: TvaMarker[];
  [key: string]: unknown;
};

export type TvaSource = {
  manifest: TvaManifest;
  frames: string[];
};

export type TvaPlayerEventMap = {
  load: { manifest: TvaManifest; frameCount: number };
  play: Record<string, never>;
  pause: Record<string, never>;
  stop: Record<string, never>;
  ended: Record<string, never>;
  framechange: { index: number; frame: string; frameCount: number; manifest: TvaManifest | null };
  fpschange: { fps: number };
  loopchange: { loop: boolean };
};

export class TvaPlayer extends EventTarget {
  constructor(options?: { fps?: number; loop?: boolean });
  load(source: TvaSource): void;
  play(): void;
  pause(): void;
  stop(): void;
  toggle(): void;
  seekFrame(index: number): void;
  seekTime(time: number): void;
  nextFrame(): void;
  prevFrame(): void;
  setFps(fps: number): void;
  setLoop(loop: boolean): void;
  getCurrentFrame(): string;
  getCurrentFrameIndex(): number;
  getFrameCount(): number;
  getFps(): number;
  getManifest(): TvaManifest | null;
  getMarkers(): TvaMarker[];
  isPlaying(): boolean;
  on<K extends keyof TvaPlayerEventMap>(type: K, handler: (detail: TvaPlayerEventMap[K]) => void): () => void;
}
