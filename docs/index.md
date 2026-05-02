# AI Infrastructure Video Pipeline

A pipeline that produces a **1080p narrated explainer video** about AI infrastructure — LLM Gateway, AI Gateway, MCP Gateway, MCP Registry, and Skill Registry — using [HyperFrames](https://github.com/heygen-com/hyperframes) for composition and [ElevenLabs](https://elevenlabs.io) for text-to-speech narration.

## What it produces

A 3-minute, fully-animated 1920×1080 MP4 video (`video/hf/final.mp4`) with:

- 7 scenes, each as a self-contained HyperFrames block
- Per-scene ElevenLabs TTS narration with 600 ms lead / 900 ms trail padding
- 400 ms crossfade overlap between scenes
- Orsted-inspired split-panel layout (text left, image right)
- GSAP entrance animations and Ken Burns image effect per scene
- Final fade-to-navy closing card

## Quick overview

```
video/hf/
├── build.py          # Single source of truth — run this first
├── index.html        # Generated host composition (slim, 44 lines)
├── final.mp4         # Rendered output
├── scenes/           # One HyperFrames block per scene (generated)
├── audio/            # ElevenLabs MP3s per scene (generated, cached)
└── img/              # PNG image assets (tracked in git)
```

## Two-step workflow

```bash
# 1. Generate audio + emit index.html + scene blocks
python3 video/hf/build.py

# 2. Render to MP4
npx hyperframes render video/hf -o video/hf/final.mp4
```

See [Quick Start](getting-started/quickstart.md) for full setup, or jump to [Architecture](guide/architecture.md) to understand how the pieces fit together.
