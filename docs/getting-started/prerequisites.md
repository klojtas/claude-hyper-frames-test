# Prerequisites

## System dependencies

| Dependency | Minimum version | Purpose |
|---|---|---|
| Python | 3.10+ | Running `build.py` |
| Node.js | 18+ | `npx hyperframes` render CLI |
| ffprobe | any recent | Audio duration probing (ships with ffmpeg) |
| ffmpeg | any with libx264 + AAC | Used internally by the HyperFrames renderer |

### Installing ffmpeg

=== "Ubuntu / Debian"
    ```bash
    sudo apt install ffmpeg
    ```

=== "macOS (Homebrew)"
    ```bash
    brew install ffmpeg
    ```

=== "Windows (winget)"
    ```bash
    winget install Gyan.FFmpeg
    ```

### Installing Node.js

Download from [nodejs.org](https://nodejs.org) or use a version manager like `nvm`:

```bash
nvm install --lts
```

## ElevenLabs API key

`build.py` calls ElevenLabs to generate narration. You need a free or paid account.

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Go to **Profile → API Keys** and copy your key
3. Create a `.env` file at the repo root:

```bash
cp .env.example .env
# then edit .env and set ELEVENLABS_API_KEY=your_key_here
```

### Optional ElevenLabs overrides

```bash
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM   # default: Rachel
ELEVENLABS_MODEL_ID=eleven_multilingual_v2   # default
```

Browse available voices at [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library).

## HyperFrames CLI

The renderer is installed on-demand via `npx` — no global install required. The first run downloads it; subsequent runs use the npm cache.

To pin a specific version:

```bash
npx hyperframes@0.4.42 render video/hf
```

!!! note "Chromium download"
    The HyperFrames renderer ships with Puppeteer, which downloads a compatible Chromium binary on first use (~170 MB). This happens automatically and only once.
