# Timing Constants

Defined at the top of `video/hf/build.py`:

```python
PAD_LEAD  = 0.6   # silence before voice starts (seconds)
PAD_TRAIL = 0.9   # silence after voice ends (seconds)
OVERLAP   = 0.4   # crossfade between adjacent scenes (seconds)
```

## How they affect the timeline

```
Scene N:   |← PAD_LEAD →|←── audio ──→|← PAD_TRAIL →|
           0            0.6           0.6+dur        0.6+dur+0.9

Scene N+1 starts at:
  scene_start[N] + scene_duration[N] - OVERLAP
```

The OVERLAP creates a 0.4 s window where the previous scene is still visible while the next scene fades in. Because scene blocks simply have `opacity: 0` until their GSAP entrance fires, the overlap is handled naturally by the separate block timelines.

## Audio timing

Within a scene block, audio starts at `data-start="{PAD_LEAD}"` (0.600 s).  
In the host `index.html`, the absolute audio start is `scene_start[i] + PAD_LEAD`.

## Adjusting timing

To change the silence padding, edit the constants and re-run `build.py`. The changed values will propagate to all scene blocks and the host automatically.

To change timing for a single scene only, you would need to override that scene's computation in `main()` — there is currently no per-scene override mechanism.

## Scene duration summary

With the defaults above and the current narration durations:

| Scene | Audio dur | Scene dur | Start |
|---|---|---|---|
| 00 intro | 14.45 s | 15.95 s | 0.00 s |
| 01 llm | 28.87 s | 30.37 s | 15.55 s |
| 02 ai | 31.24 s | 32.74 s | 45.52 s |
| 03 mcpgw | 27.43 s | 28.93 s | 77.86 s |
| 04 mcpreg | 29.86 s | 31.36 s | 106.39 s |
| 05 skill | 27.59 s | 29.09 s | 137.35 s |
| 06 outro | 15.05 s | 16.55 s | 166.04 s |
| **Total** | | | **182.57 s** |
