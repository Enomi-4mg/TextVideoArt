import JSZip from "https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm";

const MANIFEST_NAME = "manifest.json";
const FRAMES_PATH = "frames/";

export function framePath(index) {
  if (!Number.isInteger(index) || index < 0) {
    throw new Error("frame index must be a non-negative integer");
  }
  return `${FRAMES_PATH}${String(index).padStart(6, "0")}.txt`;
}

export function validateManifest(manifest) {
  const errors = [];
  const required = {
    format: "string",
    format_name: "string",
    version: "string",
    width: "number",
    height: "number",
    fps: "number",
    frame_count: "number",
    duration: "number",
    charset: "string",
    invert: "boolean",
    encoding: "string",
    color_mode: "string",
    frame_format: "string",
    frames_path: "string"
  };

  for (const [field, typeName] of Object.entries(required)) {
    if (!(field in manifest)) {
      errors.push(`missing manifest field: ${field}`);
    } else if (typeof manifest[field] !== typeName) {
      errors.push(`manifest field ${field} must be a ${typeName}`);
    }
  }
  if (errors.length > 0) return errors;

  if (manifest.format !== "TVA") errors.push('format must be "TVA"');
  if (manifest.format_name !== "Text Video Art") errors.push('format_name must be "Text Video Art"');
  if (manifest.width <= 0) errors.push("width must be positive");
  if (manifest.height <= 0) errors.push("height must be positive");
  if (manifest.fps <= 0) errors.push("fps must be positive");
  if (!Number.isInteger(manifest.frame_count) || manifest.frame_count <= 0) {
    errors.push("frame_count must be a positive integer");
  }
  if (manifest.duration <= 0) errors.push("duration must be positive");
  if (manifest.encoding !== "utf-8") errors.push('encoding must be "utf-8"');
  if (manifest.color_mode !== "none") errors.push('color_mode must be "none"');
  if (manifest.frame_format !== "plain_text") errors.push('frame_format must be "plain_text"');
  if (manifest.frames_path !== FRAMES_PATH) errors.push('frames_path must be "frames/"');

  if (Array.isArray(manifest.markers)) {
    for (const [index, marker] of manifest.markers.entries()) {
      if (typeof marker !== "object" || marker === null || Array.isArray(marker)) {
        errors.push(`markers[${index}] must be an object`);
        continue;
      }
      if (typeof marker.label !== "string" || marker.label.length === 0) {
        errors.push(`markers[${index}].label must be a non-empty string`);
      }
      if (!Number.isInteger(marker.frame)) {
        errors.push(`markers[${index}].frame must be an integer`);
      } else if (marker.frame < 0 || marker.frame >= manifest.frame_count) {
        errors.push(`markers[${index}].frame is out of range`);
      }
    }
  }

  return errors;
}

export async function loadTvaFile(file) {
  const zip = await JSZip.loadAsync(file);
  const manifestEntry = zip.file(MANIFEST_NAME);
  if (!manifestEntry) {
    throw new Error("manifest.json is missing");
  }

  const manifest = JSON.parse(await manifestEntry.async("string"));
  const errors = validateManifest(manifest);
  if (errors.length > 0) {
    throw new Error(errors.join("\n"));
  }

  const frames = [];
  for (let index = 0; index < manifest.frame_count; index += 1) {
    const name = framePath(index);
    const frameEntry = zip.file(name);
    if (!frameEntry) {
      throw new Error(`missing frame: ${name}`);
    }
    frames.push(await frameEntry.async("string"));
  }

  return { manifest, frames };
}
