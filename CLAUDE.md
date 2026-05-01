# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A pipeline that produces a 1080p narrated explainer video about AI infrastructure (LLM Gateway, AI Gateway, MCP Gateway, MCP Registry, Skill Registry) using HyperFrames. The composition is rendered via the `hyperframes` CLI.

## Commands

```bash
# Generate ElevenLabs audio and emit video/hf/index.html (the HyperFrames composition).
python3 video/hf/build.py

# Preview the composition in the HyperFrames studio.
hyperframes preview video/hf/index.html

# Render the final video.
hyperframes render video/hf/index.html --output video/hf/final.mp4
```

`build.py` requires `ELEVENLABS_API_KEY` either exported in the shell or set in `.env` at the repo root (see `.env.example`). Optional overrides: `ELEVENLABS_VOICE_ID`, `ELEVENLABS_MODEL_ID`.

System dependencies: `python3`, `ffprobe` (for audio duration probing), `hyperframes` CLI.

## Architecture

`video/hf/build.py` is the single entry point. It:
1. Reads `SCENES` (defined inline) — the source of truth for kicker/title/bullets/narration per scene.
2. Calls ElevenLabs per scene → `video/hf/audio/NN_<id>.mp3`
3. Probes each audio file for duration and computes scene timing with 600ms lead + 900ms trail padding and 400ms crossfade between scenes.
4. Emits one HyperFrames block per scene → `video/hf/scenes/NN_<id>.html`. Each block is a self-contained sub-composition with its own GSAP timeline, audio clip, and Ken Burns image effect.
5. Emits `video/hf/index.html` — a slim host composition that pulls each scene block in via `data-composition-src` and adds a final fade-to-navy.

Each scene uses a split-panel layout (text left, image right) with an Orsted-inspired palette (deep navy `#001142`, corporate blue `#007ACC`, teal `#009775`). Audio (`audio/NN_<id>.mp3`) and images (`img/NN_<id>.png`) share the same numeric prefix, keyed by the scene's index in `SCENES`.

## Gotchas worth knowing

- **Narration acronym hack.** Inside `SCENES[*]["narration"]`, acronyms are spelled out with spaces (`"L L M"`, `"A I"`, `"M C P"`, `"A P I"`) so TTS pronounces letters individually. Don't "clean these up" — they're intentional.
- **Audio caching.** `build.py` skips re-fetching an audio file if it already exists and is non-empty. Delete `video/hf/audio/` (or a specific file) to force regeneration.
- **Generated artifacts are gitignored.** `video/hf/audio/`, `video/hf/index.html`, and `video/hf/scenes/` are gitignored — only `build.py`, the `img/` assets, `.env.example`, `.gitignore`, and this file are tracked.
