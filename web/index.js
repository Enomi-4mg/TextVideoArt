import { TvaPlayer } from "./src/lib/player-api.js";
import { PreFrameRenderer } from "./src/lib/renderer-pre.js";
import { loadTvaUrl } from "./src/lib/tva.js";

const demoOutput = document.getElementById("landing-demo");
const player = new TvaPlayer({ loop: true });
const renderer = new PreFrameRenderer(demoOutput);
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

player.on("framechange", ({ frame }) => {
  renderer.render(frame || "");
});

async function startLandingDemo() {
  try {
    const source = await loadTvaUrl("./samples/landing-demo.tva");
    player.load(source);
    player.setLoop(true);

    if (reduceMotion.matches) {
      player.seekFrame(Math.min(2, player.getFrameCount() - 1));
      return;
    }

    player.play();
  } catch (error) {
    demoOutput.textContent = error instanceof Error ? error.message : String(error);
  }
}

reduceMotion.addEventListener("change", () => {
  if (reduceMotion.matches) {
    player.pause();
  } else if (player.getFrameCount() > 0) {
    player.play();
  }
});

startLandingDemo();
