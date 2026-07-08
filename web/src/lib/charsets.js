export const CHARSET_PRESETS = {
  standard: " .:-=+*#%@",
  simple: " .#",
  blocks: " ░▒▓█",
  dense: " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
};

export function resolveCharsetPreset(name, fallback = "standard") {
  return CHARSET_PRESETS[name] ?? CHARSET_PRESETS[fallback];
}
