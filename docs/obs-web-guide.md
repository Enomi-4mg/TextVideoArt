# Web / OBS: standalone HTML

Use the existing HTML exporter:

```sh
tvart export html work.tva -o work.html
```

Open work.html in a browser and use its Play and loop controls. For a web page hosted alongside it:

```html
<iframe src="work.html" title="Text video artwork" width="1280" height="720"></iframe>
```

For OBS, add a Browser Source, enable Local file, choose work.html and set width/height (for example 1280×720). Use Interact to operate playback. This example uses the existing controls; it does not add autoplay or hide-controls flags to the exporter. OBS has not been tested in this session.

For local MP4, use the new renderer with an installed FFmpeg containing libx264:

```sh
tvart render png work.tva -o frames --size 1280x720 --fit contain
tvart render mp4 work.tva -o card.mp4 --size 1280x720 --fit contain
ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,nb_read_frames:format=duration -of json card.mp4
```

The PNG directory must be new. MP4 requires an .mp4 extension; existing output is refused unless --overwrite is explicit. --ffmpeg accepts an executable path. MP4 dimensions are rounded up to even pixels. Local glyph rendering supports ASCII and ░▒▓█; use browser PNG for other Unicode. No audio is included. Browser recordings identify their actual container; a WebM download is not an MP4.

Official references checked on 2026-10-06: [OBS Browser Source](https://obsproject.com/kb/browser-source), [FFmpeg image2 and formats](https://ffmpeg.org/ffmpeg-formats.html), [W3C MediaStream Recording](https://www.w3.org/TR/mediastream-recording/).
