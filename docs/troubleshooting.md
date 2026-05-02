# Troubleshooting

## `ELEVENLABS_API_KEY missing`

`build.py` exits with this message if the key is not set.

**Fix:** create `.env` at the repo root:

```bash
cp .env.example .env
# edit .env and add: ELEVENLABS_API_KEY=your_key_here
```

Or export it in your shell:

```bash
export ELEVENLABS_API_KEY=your_key_here
python3 video/hf/build.py
```

---

## Final video has no audio

**Symptom:** `ffprobe` shows only a `video` stream, no `audio`.

**Cause:** Audio `<audio>` elements were inside sub-composition blocks (`scenes/*.html`) instead of the host `index.html`. HyperFrames only assembles audio from the root composition.

**Fix:** ensure `build.py`'s `render_host()` emits `<audio>` elements with absolute `data-start` timestamps in `index.html`. Re-run `build.py` and re-render.

---

## `Not a directory: video/hf/index.html`

**Cause:** The `hyperframes render` command expects a **directory**, not a file path.

**Fix:**

```bash
# Wrong
npx hyperframes render video/hf/index.html

# Correct
npx hyperframes render video/hf -o video/hf/final.mp4
```

---

## `ffprobe: command not found`

`build.py` uses `ffprobe` to measure audio duration.

**Fix:** install ffmpeg (which includes ffprobe):

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

---

## Audio is mis-timed (voice starts too early or too late)

**Cause:** `PAD_LEAD` or `PAD_TRAIL` constants are off, or audio duration changed but timing was not recomputed.

**Fix:** re-run `python3 video/hf/build.py` — timing is always recomputed from the actual audio durations reported by `ffprobe`. Then re-render.

---

## Scene image not showing

**Cause:** The image file does not match the expected naming convention.

Each scene block references `../img/NN_<id>.png` where `NN` is the zero-based scene index.

**Fix:** check `video/hf/img/` and ensure the file exists with the correct name:

```bash
ls video/hf/img/
```

Expected: `00_intro.png`, `01_llm.png`, ..., `06_outro.png`.

---

## GSAP warnings during render

```
[Browser:WARN] GSAP target  not found. https://gsap.com
```

**Cause:** The host GSAP timeline runs against the full DOM, but scene blocks are loaded as sub-compositions and their elements are in isolated contexts. These warnings appear when the host timeline tries to target elements that don't exist in the host DOM.

**Status:** Harmless. The warnings come from the `#fade-out` tween targeting elements that are inside blocks. All per-scene animations are handled by the block-level timelines which run in their own context.

---

## Render is very slow

By default, HyperFrames auto-detects the number of CPU cores and uses up to 4 workers. Each worker launches a separate Chrome process (~256 MB RAM).

- On a machine with limited RAM, reduce workers: `--workers 2`
- For a draft check, use: `-q draft`

```bash
npx hyperframes render video/hf -o video/hf/draft.mp4 -q draft --workers 2
```

---

## Changes to `SCENES` not reflected in the video

You must re-run **both** stages after changing content:

```bash
python3 video/hf/build.py           # regenerates HTML + audio
npx hyperframes render video/hf -o video/hf/final.mp4  # re-renders
```

If only the visuals changed (no narration), audio is cached and `build.py` is fast. If narration changed, delete the relevant MP3 first so ElevenLabs is called again:

```bash
rm video/hf/audio/01_llm.mp3
python3 video/hf/build.py
```
