# Rendering to Video

## Basic render

```bash
npx hyperframes render video/hf -o video/hf/final.mp4
```

The `DIR` argument is the **project directory** (containing `index.html`), not the HTML file itself. The `-o` flag sets the output path.

## Render options

| Flag | Default | Description |
|---|---|---|
| `-o / --output` | `renders/<name>.mp4` | Output file path |
| `-f / --fps` | `30` | Frame rate: 24, 30, or 60 |
| `-q / --quality` | `standard` | `draft`, `standard`, or `high` |
| `--format` | `mp4` | `mp4`, `webm`, or `mov` |
| `-w / --workers` | auto | Parallel Chrome workers (each ~256 MB RAM) |

### Quality presets

| Preset | Use case |
|---|---|
| `draft` | Fast iteration — lower bitrate, fewer workers |
| `standard` | Default — good balance of speed and quality |
| `high` | Final deliverable — higher bitrate |

### Examples

```bash
# Draft pass for quick review
npx hyperframes render video/hf -o video/hf/draft.mp4 -q draft

# High quality final render at 60fps
npx hyperframes render video/hf -o video/hf/final.mp4 -q high -f 60

# Limit workers to reduce RAM usage
npx hyperframes render video/hf -o video/hf/final.mp4 --workers 2
```

## What the renderer does

1. **Compile** — parses `index.html`, resolves sub-compositions (`scenes/*.html`) and all media references. Validates structure and reports `audioCount`, `videoCount`, total duration.
2. **Extract video frames** — no `<video>` elements in this project, so this step is instant.
3. **Process audio** — mixes all `<audio>` elements declared in the host into a single AAC track. Audio must be in the host (not in sub-composition files).
4. **Frame capture** — Chrome/Puppeteer seeks the GSAP timeline to each frame timestamp and screenshots the 1920×1080 canvas. Workers run in parallel.
5. **Encode** — H.264 yuv420p via libx264.
6. **Assemble** — muxes video and audio into the final MP4.

## Expected output

For this 7-scene, ~183 s composition at 30 fps:

- **Total frames**: 5478
- **Render time**: ~3 minutes on a 12-core machine with 4 auto workers
- **Output size**: ~50–55 MB at standard quality

## Verifying the output

```bash
ffprobe -v error -show_streams -of json video/hf/final.mp4 | \
  python3 -c "import json,sys; [print(s['codec_type'],s['codec_name']) for s in json.load(sys.stdin)['streams']]"
```

Expected:
```
video h264
audio aac
```

A missing `audio aac` line means audio elements were not in the host `index.html` — see [Architecture — Audio must be in the host](architecture.md#host-indexhtml).

## GSAP warnings during render

You may see:

```
[Browser:WARN] GSAP target  not found. https://gsap.com
```

These appear at frames where the host GSAP timeline references elements that have not yet been mounted (they are inside sub-compositions). They are harmless — the sub-composition timelines handle those elements independently.
