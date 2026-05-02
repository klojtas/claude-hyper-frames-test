# build.py Reference

## Top-level constants

### `SCENES`

`list[dict]` — The complete scene definition list. See [Configuring Scenes](../guide/scenes.md) for the full schema.

### `ACCENTS`

`dict[str, str]` — Maps scene `id` to a hex accent colour. Used for the top bar, bullet markers, divider, footer line, and background numeral.

### `BG_TINTS`

`dict[str, str]` — Maps scene `id` to a hex background tint colour. Defines the off-white canvas colour per scene.

### `SCENE_NUMS`

`dict[str, str]` — Maps scene `id` to a decorative background number string (e.g. `"01"`). Scenes absent from this dict show no background number.

### `PAD_LEAD`, `PAD_TRAIL`, `OVERLAP`

Timing constants. See [Timing Constants](timing.md).

### `ORSTED_EASE`

`str` — The Orsted easing curve: `"cubic-bezier(0.165, 0.84, 0.26, 0.98)"`. Used for all entrance animations.

### `SCENE_CSS`, `HOST_CSS`

`str` — CSS string literals injected into scene blocks and the host respectively.

---

## Functions

### `fetch_tts(text, out)`

```python
def fetch_tts(text: str, out: Path) -> None
```

Calls the ElevenLabs TTS REST API and writes the response bytes to `out`.

Uses `API_KEY`, `VOICE_ID`, `MODEL_ID` from the module globals. Voice settings are hardcoded:

```python
{
    "stability": 0.45,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True,
}
```

Output format: `mp3_44100_128` (44.1 kHz, 128 kbps).

---

### `probe_duration(path)`

```python
def probe_duration(path: Path) -> float
```

Calls `ffprobe` to read the duration of an audio/video file. Returns duration in seconds as a float.

---

### `render_scene_block(idx, scene, audio_dur)`

```python
def render_scene_block(idx: int, scene: dict, audio_dur: float) -> str
```

Returns the full HTML string for a HyperFrames scene block.

**Parameters:**

- `idx` — zero-based scene index (used for image/audio file naming)
- `scene` — a single entry from `SCENES`
- `audio_dur` — duration of the scene's audio in seconds (from `probe_duration`)

**Returns:** complete `<!DOCTYPE html>` document with GSAP timeline and all visual elements. Does **not** include an `<audio>` element (audio is declared in the host).

---

### `render_host(scene_starts, scene_durations, audio_durations, total)`

```python
def render_host(
    scene_starts: list[float],
    scene_durations: list[float],
    audio_durations: list[float],
    total: float,
) -> str
```

Returns the full HTML string for the host `index.html`.

Generates:
- One `<div data-composition-src="scenes/NN_<id>.html">` per scene
- One `<audio>` element per scene with `data-start = scene_start[i] + PAD_LEAD`
- A `#fade-out` overlay starting at `total - 0.6 s`
- A GSAP timeline that drives only the final fade

---

### `main()`

```python
def main() -> None
```

Orchestrates the full build:

1. Creates `AUDIO_DIR` and `SCENES_DIR` if they don't exist
2. For each scene: fetch TTS (if not cached), probe duration
3. Compute `scene_durations`, `scene_starts`, `total_duration`
4. Write each scene block to `scenes/NN_<id>.html`
5. Write host to `index.html`
