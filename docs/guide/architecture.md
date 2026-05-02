# Architecture

## Overview

The pipeline has two stages, joined by the filesystem:

```
build.py ──► scenes/NN_<id>.html  ──┐
         ──► audio/NN_<id>.mp3    ──┤
         ──► index.html           ──┘
                                     └──► hyperframes render ──► final.mp4
```

### Stage 1 — `build.py` (content + composition)

`build.py` owns everything before rendering:

- **Source of truth**: the `SCENES` list at the top of the file defines all content — kicker, title, bullets, narration text, and implicit references to image and audio assets.
- **TTS**: for each scene, calls ElevenLabs via the REST API and writes `audio/NN_<id>.mp3`. Files are cached — they are not re-fetched if they already exist.
- **Timing**: probes each audio file with `ffprobe`, then computes per-scene durations and start offsets with configurable lead/trail padding and crossfade overlap.
- **Scene blocks**: emits `scenes/NN_<id>.html` — one self-contained HyperFrames sub-composition per scene. Each block has its own `<style>`, composition root, GSAP timeline, and Ken Burns image.
- **Host**: emits `index.html` — a 44-line host that references the blocks via `data-composition-src` and contains all `<audio>` elements with absolute timestamps.

### Stage 2 — `hyperframes render` (frame capture + encoding)

The HyperFrames CLI renders the composition deterministically:

1. **Compile**: parses `index.html`, resolves sub-compositions and media, builds a scene graph. Reports `audioCount`, `videoCount`, total duration.
2. **Extract video frames**: any `<video>` elements (none in this project) are decoded.
3. **Process audio**: all `<audio>` elements in the host are mixed into a single track.
4. **Frame capture**: Chrome/Puppeteer seeks the GSAP timeline to each frame time, screenshots the canvas. 4 workers in parallel by default.
5. **Encode video**: H.264 yuv420p @ 30fps via libx264.
6. **Assemble**: mux video + audio into the final MP4.

## File tree

```
video/hf/
├── build.py              # Stage 1 entrypoint (tracked in git)
├── index.html            # Generated host composition
├── final.mp4             # Rendered output
│
├── scenes/               # Generated HyperFrames blocks (one per scene)
│   ├── 00_intro.html
│   ├── 01_llm.html
│   ├── 02_ai.html
│   ├── 03_mcpgw.html
│   ├── 04_mcpreg.html
│   ├── 05_skill.html
│   └── 06_outro.html
│
├── audio/                # ElevenLabs MP3s (generated, cached)
│   ├── 00_intro.mp3
│   └── ...
│
└── img/                  # PNG image assets (tracked in git)
    ├── 00_intro.png
    ├── 01_llm.png
    ├── 02_ai.png
    ├── 03_mcpgw.png
    ├── 04_mcpreg.png
    ├── 05_skill.png
    └── 06_outro.png
```

### Naming convention

All assets share the same `NN_<id>` prefix, where `NN` is the zero-based scene index and `<id>` is the scene's `id` field from `SCENES`. This keeps audio, images, and scene blocks in sync without any mapping tables.

## HyperFrames composition structure

### Host (`index.html`)

The host is intentionally minimal. It contains:

- One `<div data-composition-src="...">` per scene block (the visual sub-compositions)
- Seven `<audio>` elements with **absolute** `data-start` times (scene start + lead pad)
- A `#fade-out` overlay clip for the closing fade
- A single GSAP timeline that only drives the final fade

```html
<div id="root" data-composition-id="root" data-width="1920" data-height="1080"
     data-start="0" data-duration="182.572">

  <!-- Scene blocks -->
  <div data-composition-id="scene-intro"
       data-composition-src="scenes/00_intro.html"
       data-start="0.000" data-duration="15.946"
       data-track-index="1" data-width="1920" data-height="1080"></div>
  <!-- ... more scenes ... -->

  <!-- Audio — must live in the host, not inside sub-compositions -->
  <audio id="aud-0" class="clip"
         data-start="0.600" data-duration="14.446"
         data-track-index="3" data-volume="1"
         src="audio/00_intro.mp3"></audio>
  <!-- ... -->
</div>
```

!!! warning "Audio must be in the host"
    HyperFrames only assembles audio declared directly in the root `index.html`. Audio elements inside sub-composition blocks (`data-composition-src` files) are rendered visually but their audio tracks are **not** extracted into the final MP4. Always declare `<audio>` in the host with absolute start times.

### Scene blocks (`scenes/NN_<id>.html`)

Each scene block is a full standalone HTML file containing:

- A `<div data-composition-id="scene-<id>">` root scoped to `data-start="0"` (time is relative within the block)
- All visual structure: accent bar, background fill, split-panel content, footer
- A dedicated GSAP timeline registered as `window.__timelines["scene-<id>"]`
- The Ken Burns effect on the image (`#img-kb`)

The HyperFrames runtime loads each block into an isolated context, finds its `window.__timelines` entry, and seeks it in sync with the host timeline, offset by `data-start`.

## Timing model

```
scene_duration  = PAD_LEAD + audio_duration + PAD_TRAIL
                = 0.6s     + X seconds      + 0.9s

scene_start[0] = 0
scene_start[i] = scene_start[i-1] + scene_duration[i-1] - OVERLAP
                                                          - 0.4s crossfade

total_duration  = scene_start[-1] + scene_duration[-1]
```

Within each scene block, audio starts at `data-start="0.6"` (= `PAD_LEAD`). In the host, the audio `data-start` is `scene_start[i] + PAD_LEAD` — the same moment expressed as an absolute timeline position.
