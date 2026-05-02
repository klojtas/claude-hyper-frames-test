# Building the Composition

## Running the build

```bash
python3 video/hf/build.py
```

The script requires no arguments. It reads configuration from `SCENES`, the timing constants, and the `.env` file at the repo root.

## What gets generated

### `audio/NN_<id>.mp3`

One MP3 per scene, fetched from ElevenLabs. Files are cached — `build.py` skips any file that already exists and has non-zero size.

### `scenes/NN_<id>.html`

One self-contained HyperFrames block per scene. Each file is a complete `<!DOCTYPE html>` document containing:

- Scene-specific CSS variables (`--accent`, `--scene-bg`)
- Full visual structure: accent bar, background fill, split-panel (text + image), footer
- A GSAP timeline registered as `window.__timelines["scene-<id>"]`
- Ken Burns zoom effect on the image

Timings inside each block are **relative** — they start from `t=0` within the block's own duration.

### `index.html`

The host composition. Generated fresh on every `build.py` run. Contains:

- One `<div data-composition-src="scenes/NN_<id>.html">` per scene
- Seven `<audio>` elements with **absolute** `data-start` timestamps
- A `#fade-out` overlay for the closing fade
- A GSAP timeline that only drives the final fade to navy

## Regenerating selectively

To update a single scene's narration without re-fetching the others:

```bash
rm video/hf/audio/03_mcpgw.mp3
python3 video/hf/build.py
```

To update visuals only (no audio changes), just re-run `build.py` — audio files are left untouched.

## Timing computation

`build.py` computes scene timing as follows:

```python
scene_duration[i]  = PAD_LEAD + audio_duration[i] + PAD_TRAIL

scene_start[0]     = 0
scene_start[i]     = scene_start[i-1] + scene_duration[i-1] - OVERLAP

total_duration     = scene_start[-1] + scene_duration[-1]
```

See [Timing Constants](../reference/timing.md) for the default values.

## GSAP animation structure

Each scene block's timeline is written at t=0 (relative to the block start). Entrance animations are:

| Element | Animation | Delay |
|---|---|---|
| Scene root (`#scene`) | Fade in | +0.00 s |
| Accent bar | Scale X from 0 | +0.08 s |
| Background number | Slide in from right | +0.10 s |
| Kicker | Slide up + fade | +0.20 s |
| Scene divider | Scale Y from 0 | +0.25 s |
| Title | Slide up + fade | +0.32 s |
| Image panel | Slide in from right + 3D tilt | +0.42 s |
| Bullet list items | Stagger slide from left | +0.68 s (stagger 0.07 s) |
| Footer | Fade in | +1.20 s |
| Ken Burns (image zoom) | Scale 1.0 → 1.04 over scene duration | +0.00 s |

All animations use Orsted easing: `cubic-bezier(0.165, 0.84, 0.26, 0.98)` except the final fade which uses `power2.in`.
