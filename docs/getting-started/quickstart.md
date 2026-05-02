# Quick Start

## 1. Clone and configure

```bash
git clone https://github.com/klojtas/claude-hyper-frames-test.git
cd claude-hyper-frames-test
cp .env.example .env
```

Edit `.env` and set your ElevenLabs API key:

```bash
ELEVENLABS_API_KEY=your_key_here
```

## 2. Run the build

```bash
python3 video/hf/build.py
```

This will:

1. Read the `SCENES` list defined in `build.py`
2. Call ElevenLabs for each scene → `video/hf/audio/NN_<id>.mp3`  
   *(skips any file that already exists and is non-empty — cached)*
3. Probe each audio file for duration with `ffprobe`
4. Compute per-scene timing (lead pad + audio + trail pad, with crossfade overlap)
5. Emit `video/hf/scenes/NN_<id>.html` — one self-contained HyperFrames block per scene
6. Emit `video/hf/index.html` — slim host with `<audio>` elements and block includes

Expected output:

```
  00_intro.mp3  14.45s
  01_llm.mp3    28.87s
  ...
  06_outro.mp3  15.05s
  wrote scenes/00_intro.html
  ...
  wrote scenes/06_outro.html

wrote /path/to/video/hf/index.html
total duration: 182.57s (7 scenes)
```

## 3. Render to video

```bash
npx hyperframes render video/hf -o video/hf/final.mp4
```

The first run installs `hyperframes` via npm and downloads a Chromium binary (~170 MB, one time). Then it renders all 5478 frames across 4 parallel workers.

Expected duration: **3–5 minutes** on a modern machine.

```
  █████████████████████████  100%  Render complete
◇  video/hf/final.mp4
   55 MB · 3m 1.7s · completed
```

## 4. Play the video

```bash
# macOS
open video/hf/final.mp4

# Linux
xdg-open video/hf/final.mp4
```

## Making changes

To change content, edit `SCENES` in `video/hf/build.py`, then re-run steps 2 and 3.

To regenerate audio for a specific scene only, delete its MP3 first:

```bash
rm video/hf/audio/01_llm.mp3
python3 video/hf/build.py
```

See [Configuring Scenes](../guide/scenes.md) for the full scene schema.
