# Environment Variables

All variables are read from `.env` at the repo root (if it exists) and then from the shell environment. Shell variables take precedence over `.env`.

## `.env.example`

```bash
ELEVENLABS_API_KEY=your_key_here
# ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
# ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```

## Variables

### `ELEVENLABS_API_KEY`

**Required.** Your ElevenLabs API key. Get one at [elevenlabs.io](https://elevenlabs.io/app/settings/api-keys).

`build.py` exits immediately with an error if this is not set.

---

### `ELEVENLABS_VOICE_ID`

**Optional.** Default: `21m00Tcm4TlvDq8ikWAM` (Rachel).

The ID of the ElevenLabs voice to use for all scenes. Browse voices and find their IDs in the [ElevenLabs voice library](https://elevenlabs.io/voice-library).

---

### `ELEVENLABS_MODEL_ID`

**Optional.** Default: `eleven_multilingual_v2`.

The ElevenLabs model to use for TTS. Available models:

| Model ID | Notes |
|---|---|
| `eleven_multilingual_v2` | Default — good quality, supports 29 languages |
| `eleven_turbo_v2` | Faster, lower latency, English-optimised |
| `eleven_monolingual_v1` | Legacy English-only model |

## `.env` loading behaviour

`build.py` parses `.env` itself (no shell sourcing). It handles:

- `KEY=VALUE` lines
- Lines starting with `#` (comments) — ignored
- Blank lines — ignored
- No shell variable expansion (`$VAR` references in values are kept literal)

The `.env` file is gitignored. Never commit it.
