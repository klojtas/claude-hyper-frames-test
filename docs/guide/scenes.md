# Configuring Scenes

All video content is defined in the `SCENES` list at the top of `video/hf/build.py`. It is the single source of truth — changing it is all you need to do to update the video.

## Scene schema

```python
{
    "id": str,          # unique snake_case identifier
    "kicker": str,      # small label above the title (all-caps recommended)
    "title": str,       # large headline, use \n for line breaks
    "bullets": list[str],  # 3–5 bullet points
    "narration": str,   # text sent to ElevenLabs TTS
}
```

### Full example

```python
{
    "id": "llm",
    "kicker": "1  /  LLM GATEWAY",
    "title": "One API,\nMany Models",
    "bullets": [
        "Intelligent multi-provider routing",
        "Automatic fallback on failure",
        "Response caching for cost and latency",
        "Rate limiting and quota management",
        "Centralized observability and metrics",
    ],
    "narration": (
        "The L L M Gateway sits between your application and language model providers. "
        "It gives you one consistent A P I across many models. "
        "Its core capabilities are intelligent routing, automatic fallback when a provider fails, "
        "response caching to cut latency and cost, rate limiting to stay within quotas, "
        "and centralized observability. "
        "It is the load balancer of the language model world."
    ),
},
```

## Scene `id` rules

- Must be unique across all scenes
- Used in file names: `scenes/NN_<id>.html`, `audio/NN_<id>.mp3`, `img/NN_<id>.png`
- Must match a key in the `ACCENTS`, `BG_TINTS` dicts in `build.py`

When you add a new scene, add its `id` to both dicts:

```python
ACCENTS = {
    ...,
    "my_scene": "#007ACC",
}
BG_TINTS = {
    ...,
    "my_scene": "#F5F7FA",
}
```

And add a corresponding image at `video/hf/img/NN_<id>.png` (see [Images & Assets](assets.md)).

## Narration tips

### Acronym pronunciation

TTS reads text literally. Spell out acronyms with spaces so letters are pronounced individually:

| Write in code | TTS says |
|---|---|
| `"L L M"` | "el el em" |
| `"A P I"` | "ay pee eye" |
| `"M C P"` | "em see pee" |
| `"A I"` | "ay eye" |

!!! warning "Don't clean these up"
    The spaced acronyms look odd in the source but they are intentional. Removing the spaces will cause the TTS to mispronounce them as words ("llm" → "loom").

### Pacing

- ~2.5 words per second is natural speaking pace
- 15 s ≈ 37 words, 30 s ≈ 75 words
- Leave room for pauses between sentences

### Audio caching

`build.py` skips re-fetching audio if the file already exists and is non-empty. To force regeneration of a single scene:

```bash
rm video/hf/audio/01_llm.mp3
python3 video/hf/build.py
```

To regenerate all audio:

```bash
rm video/hf/audio/*.mp3
python3 video/hf/build.py
```

## Scene colours

Each scene has an accent colour and a background tint, set in `build.py`:

```python
ACCENTS = {
    "intro":  "#007ACC",   # corporate blue
    "llm":    "#007ACC",
    "ai":     "#009775",   # teal
    "mcpgw":  "#005C99",   # deep blue
    "mcpreg": "#007ACC",
    "skill":  "#009775",
    "outro":  "#001142",   # deep navy
}

BG_TINTS = {
    "intro":  "#F5F7FA",
    "llm":    "#F0F4F9",
    "ai":     "#F4F9F7",
    "mcpgw":  "#F0F4F9",
    "mcpreg": "#F5F7FA",
    "skill":  "#F4F9F7",
    "outro":  "#EEF2F8",
}
```

The accent drives the top bar, bullet markers, divider line, footer dash, and decorative background number.

## Background scene numbers

Scenes with a position number (01–05) display a large muted numeral as a background decoration. Controlled by `SCENE_NUMS`:

```python
SCENE_NUMS = {
    "llm": "01", "ai": "02", "mcpgw": "03",
    "mcpreg": "04", "skill": "05",
}
```

Scenes not in this dict (intro, outro) have no background number.

## Adding or removing scenes

1. Add/remove the entry from `SCENES`
2. Update `ACCENTS` and `BG_TINTS`
3. Update `SCENE_NUMS` if the scene should show a number
4. Add/remove the corresponding `img/NN_<id>.png`
5. Re-run `python3 video/hf/build.py`
6. Re-run `npx hyperframes render video/hf -o video/hf/final.mp4`
