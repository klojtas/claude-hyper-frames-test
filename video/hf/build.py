"""Generate ElevenLabs narration and a HyperFrames composition.

Emits a small host (index.html) that includes one HyperFrames block per scene
under scenes/. Calls ElevenLabs per scene using credentials in ../../.env.
Style follows Orsted.com — clean white/off-white, deep navy headings, corporate
blue #007ACC accents, sharp image cards, Orsted easing.
"""
import json
import os
import subprocess
import sys
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
AUDIO_DIR = ROOT / "audio"
SCENES_DIR = ROOT / "scenes"

env_path = REPO_ROOT / ".env"
env: dict[str, str] = {}
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

API_KEY = env.get("ELEVENLABS_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = env.get("ELEVENLABS_VOICE_ID") or os.environ.get(
    "ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"
)
MODEL_ID = env.get("ELEVENLABS_MODEL_ID") or os.environ.get(
    "ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"
)
if not API_KEY:
    sys.exit("ELEVENLABS_API_KEY missing — set it in .env or env")

SCENES = [
    {
        "id": "intro",
        "kicker": "AI INFRASTRUCTURE",
        "title": "The Five Layers\nof Agentic AI",
        "bullets": [
            "LLM Gateway",
            "AI Gateway",
            "MCP Gateway",
            "MCP Registry",
            "Skill Registry",
        ],
        "narration": (
            "AI systems are evolving from single models into orchestrated platforms. "
            "Five components are emerging as the connective tissue of modern AI infrastructure. "
            "Let's walk through each one and what they actually do."
        ),
    },
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
    {
        "id": "ai",
        "kicker": "2  /  AI GATEWAY",
        "title": "Governance\nfor Every Model",
        "bullets": [
            "Multi-modal traffic: text, vision, speech, embeddings",
            "Policy enforcement for safety and compliance",
            "Sensitive data redaction at the edge",
            "Fine-grained access control",
            "Full audit logging for every call",
        ],
        "narration": (
            "The A I Gateway extends those ideas beyond text. "
            "It governs every kind of A I traffic, including language models, embeddings, image generation, and speech. "
            "Its capabilities include multi-modal routing, policy enforcement for safety and compliance, "
            "sensitive data redaction, fine-grained access control, and full audit logging. "
            "Where the L L M Gateway focuses on performance, the A I Gateway focuses on governance."
        ),
    },
    {
        "id": "mcpgw",
        "kicker": "3  /  MCP GATEWAY",
        "title": "Aggregating\nthe Tool Surface",
        "bullets": [
            "Single endpoint for many MCP servers",
            "Unified authentication and identity",
            "Permission scoping per tool and per user",
            "Per-tool rate limits and quotas",
            "Audit trail of every tool invocation",
        ],
        "narration": (
            "The M C P Gateway aggregates many Model Context Protocol servers behind a single endpoint. "
            "Instead of agents connecting to dozens of tool servers, they connect once. "
            "Its capabilities are unified authentication, permission scoping per tool and per user, "
            "request shaping, rate limits, and audit trails. "
            "It transforms a sprawl of independent integrations into a managed surface."
        ),
    },
    {
        "id": "mcpreg",
        "kicker": "4  /  MCP REGISTRY",
        "title": "Discovery\nand Trust",
        "bullets": [
            "Searchable catalog of MCP servers",
            "Semantic versioning of capabilities",
            "Cryptographic signing and verification",
            "Dependency and compatibility metadata",
            "Capability descriptors agents can reason over",
        ],
        "narration": (
            "The M C P Registry is the catalog where servers are published and discovered. "
            "Think of it as a package index for tools an agent can use. "
            "Its capabilities are searchable metadata, versioning, cryptographic signing for trust, "
            "dependency information, and capability descriptors so agents know what each server actually does. "
            "The registry answers a simple question. Which servers exist, and which can I trust?"
        ),
    },
    {
        "id": "skill",
        "kicker": "5  /  SKILL REGISTRY",
        "title": "Capabilities,\non Demand",
        "bullets": [
            "Skills as packaged units of capability",
            "Dynamic loading at runtime",
            "Semantic versioning across releases",
            "Dependency resolution between skills",
            "Composition into complex behaviors",
        ],
        "narration": (
            "A Skill Registry catalogs skills, the packaged units of capability an agent can load on demand. "
            "Each skill bundles instructions, scripts, and resources for a specific task. "
            "Capabilities include dynamic loading at runtime, semantic version management, "
            "dependency resolution between skills, and composition. "
            "It is how agents stay small at the core but grow vast in what they can do."
        ),
    },
    {
        "id": "outro",
        "kicker": "PUTTING IT TOGETHER",
        "title": "Gateways +\nRegistries",
        "bullets": [
            "Gateways manage traffic and policy",
            "Registries manage discovery and trust",
            "Together: a platform, not just a model",
        ],
        "narration": (
            "Together, these five components form the backbone of agentic A I infrastructure. "
            "Gateways manage traffic and policy. Registries manage discovery and trust. "
            "Master both, and you have a platform, not just a model."
        ),
    },
]

PAD_LEAD = 0.6
PAD_TRAIL = 0.9
OVERLAP = 0.4

ACCENTS = {
    "intro":  "#007ACC",
    "llm":    "#007ACC",
    "ai":     "#009775",
    "mcpgw":  "#005C99",
    "mcpreg": "#007ACC",
    "skill":  "#009775",
    "outro":  "#001142",
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

# Decorative numbering displayed behind the title (skip intro/outro).
SCENE_NUMS = {"llm": "01", "ai": "02", "mcpgw": "03", "mcpreg": "04", "skill": "05"}

ORSTED_EASE = "cubic-bezier(0.165, 0.84, 0.26, 0.98)"

SCENE_CSS = """\
    body { margin: 0; }
    #scene {
      position: relative;
      width: 1920px;
      height: 1080px;
      background: var(--scene-bg, #F5F7FA);
      color: #001142;
      font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
      overflow: hidden;
      box-sizing: border-box;
    }

    .scene-fill {
      position: absolute;
      inset: 0;
      background: var(--scene-bg, #F5F7FA);
      z-index: 0;
    }
    .scene-fill::after {
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(ellipse 70% 55% at 15% 50%,  rgba(0,122,204,0.05) 0%, transparent 65%),
        radial-gradient(ellipse 50% 40% at 85% 15%, rgba(0,151,117,0.04) 0%, transparent 60%);
    }

    .accent-bar {
      position: absolute;
      top: 0; left: 0;
      width: 100%;
      height: 6px;
      background: var(--accent);
      transform-origin: left center;
      z-index: 2;
    }

    .scene-bg-num {
      position: absolute;
      right: -20px;
      bottom: -60px;
      font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
      font-size: 480px;
      font-weight: 900;
      letter-spacing: -0.05em;
      color: var(--accent);
      opacity: 0.04;
      line-height: 1;
      pointer-events: none;
      user-select: none;
      z-index: 1;
    }

    .scene-content {
      position: relative;
      width: 100%;
      height: 100%;
      padding: 96px 80px 96px 120px;
      display: flex;
      flex-direction: row;
      align-items: center;
      box-sizing: border-box;
      gap: 0;
      z-index: 2;
    }
    .scene-left {
      flex: 0 0 820px;
      display: flex;
      flex-direction: column;
    }
    .kicker {
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.13em;
      text-transform: uppercase;
      color: var(--accent);
      margin: 0 0 28px;
    }
    .title {
      font-size: 88px;
      font-weight: 900;
      line-height: 1.0;
      letter-spacing: -0.03em;
      color: #001142;
      margin: 0 0 44px;
      max-width: 780px;
    }
    .bullets {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .bullets li {
      display: flex;
      align-items: center;
      gap: 20px;
      font-size: 38px;
      font-weight: 400;
      line-height: 1.3;
      color: #2D3748;
    }
    .bullets .marker {
      flex: 0 0 auto;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent);
    }

    .scene-divider {
      flex: 0 0 1px;
      height: 540px;
      margin: 0 64px;
      background: linear-gradient(to bottom,
        transparent 0%,
        var(--accent) 20%,
        var(--accent) 80%,
        transparent 100%
      );
      opacity: 0.18;
      align-self: center;
      transform-origin: center top;
    }

    .scene-right {
      flex: 1;
      height: 840px;
      position: relative;
      align-self: center;
    }
    .img-tilt-wrap {
      width: 100%;
      height: 100%;
      border-radius: 8px;
      overflow: hidden;
      position: relative;
      box-shadow:
        0 4px 12px rgba(0,17,66,0.10),
        0 12px 40px rgba(0,17,66,0.14);
    }
    .img-kb-wrap {
      width: 100%;
      height: 100%;
      overflow: hidden;
      border-radius: 8px;
    }
    .img-el {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .img-inset-border {
      position: absolute;
      inset: 0;
      border-radius: 8px;
      box-shadow: inset 0 0 0 1px rgba(0,122,204,0.14);
      pointer-events: none;
    }

    .footer {
      position: absolute;
      left: 120px;
      right: 80px;
      bottom: 44px;
      display: flex;
      align-items: center;
      gap: 20px;
      color: #64748B;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.10em;
      text-transform: uppercase;
      z-index: 2;
    }
    .footer .footer-line {
      display: inline-block;
      width: 36px;
      height: 2px;
      background: var(--accent);
      flex-shrink: 0;
    }"""

HOST_CSS = """\
    body { margin: 0; background: #F5F7FA; }
    #root {
      position: relative;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
    }
    #fade-out {
      position: absolute;
      inset: 0;
      background: #001142;
      opacity: 0;
      pointer-events: none;
      z-index: 100;
    }"""


def fetch_tts(text: str, out: Path) -> None:
    body = json.dumps({
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
        data=body,
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        out.write_bytes(r.read())


def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ])
    return float(out.strip())


def render_scene_block(idx: int, scene: dict, audio_dur: float) -> str:
    """One self-contained HyperFrames block: visuals + audio + per-block GSAP timeline."""
    sid = scene["id"]
    accent = ACCENTS[sid]
    bg = BG_TINTS[sid]
    duration = PAD_LEAD + audio_dur + PAD_TRAIL
    kb_dur = max(duration - 0.6, 1.0)
    title_html = "<br>".join(escape(line) for line in scene["title"].split("\n"))
    bullets_html = "\n            ".join(
        f'<li><span class="marker"></span><span class="text">{escape(b)}</span></li>'
        for b in scene["bullets"]
    )
    scene_num = SCENE_NUMS.get(sid, "")
    bg_num_html = (
        f'<span class="scene-bg-num" aria-hidden="true">{scene_num}</span>'
        if scene_num else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Scene · {escape(sid)}</title>
  <style>
{SCENE_CSS}
  </style>
</head>
<body>
  <div id="scene" data-composition-id="scene-{sid}" data-width="1920" data-height="1080" data-start="0" data-duration="{duration:.3f}" style="--accent: {accent}; --scene-bg: {bg};">
    <div class="scene-fill"></div>
    <div class="accent-bar"></div>
    {bg_num_html}
    <div class="scene-content">
      <div class="scene-left">
        <p class="kicker">{escape(scene['kicker'])}</p>
        <h1 class="title">{title_html}</h1>
        <ul class="bullets">
            {bullets_html}
        </ul>
      </div>
      <div class="scene-divider"></div>
      <div class="scene-right">
        <div id="img-tilt" class="img-tilt-wrap">
          <div id="img-kb" class="img-kb-wrap">
            <img class="img-el" src="../img/{idx:02d}_{sid}.png" alt="" crossorigin="anonymous">
          </div>
          <div class="img-inset-border"></div>
        </div>
      </div>
    </div>
    <div class="footer">
      <span class="footer-line"></span>
      <span class="footer-text">AI INFRASTRUCTURE · GATEWAYS &amp; REGISTRIES</span>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#scene",            {{ opacity: 0 }},                                            {{ opacity: 1, duration: 0.35, ease: "power1.out" }}, 0.00);
      tl.fromTo("#scene .accent-bar",   {{ scaleX: 0 }},                                          {{ scaleX: 1, duration: 0.45, ease: "{ORSTED_EASE}" }}, 0.08);
      tl.fromTo("#scene .scene-bg-num", {{ x: 60, opacity: 0 }},                                  {{ x: 0, opacity: 1, duration: 0.80, ease: "power2.out" }}, 0.10);
      tl.fromTo("#scene .kicker",       {{ y: 18, opacity: 0 }},                                  {{ y: 0, opacity: 1, duration: 0.35, ease: "{ORSTED_EASE}" }}, 0.20);
      tl.fromTo("#scene .scene-divider",{{ scaleY: 0, opacity: 0 }},                              {{ scaleY: 1, opacity: 1, duration: 0.55, ease: "{ORSTED_EASE}" }}, 0.25);
      tl.fromTo("#scene .title",        {{ y: 44, opacity: 0 }},                                  {{ y: 0, opacity: 1, duration: 0.50, ease: "{ORSTED_EASE}" }}, 0.32);
      tl.fromTo("#img-tilt",            {{ x: 70, opacity: 0, rotationY: -10, transformPerspective: 1400 }}, {{ x: 0, opacity: 1, rotationY: -3, transformPerspective: 1400, duration: 0.60, ease: "{ORSTED_EASE}" }}, 0.42);
      tl.fromTo("#scene .bullets li",   {{ x: -28, opacity: 0 }},                                 {{ x: 0, opacity: 1, duration: 0.38, ease: "{ORSTED_EASE}", stagger: 0.07 }}, 0.68);
      tl.fromTo("#scene .footer",       {{ opacity: 0 }},                                         {{ opacity: 1, duration: 0.40, ease: "power1.out" }}, 1.20);
      tl.fromTo("#img-kb",              {{ scale: 1.0 }},                                         {{ scale: 1.04, duration: {kb_dur:.3f}, ease: "none" }}, 0.00);
      window.__timelines["scene-{sid}"] = tl;
    </script>
  </div>
</body>
</html>
"""


def render_host(scene_starts: list[float], scene_durations: list[float], audio_durations: list[float], total: float) -> str:
    """Host composition: scene blocks via data-composition-src + all audio at absolute times."""
    block_includes = "\n".join(
        f'    <div data-composition-id="scene-{scene["id"]}" '
        f'data-composition-src="scenes/{i:02d}_{scene["id"]}.html" '
        f'data-start="{scene_starts[i]:.3f}" data-duration="{scene_durations[i]:.3f}" '
        f'data-track-index="{1 + (i % 2)}" data-width="1920" data-height="1080"></div>'
        for i, scene in enumerate(SCENES)
    )
    audio_includes = "\n".join(
        f'    <audio id="aud-{i}" class="clip" '
        f'data-start="{scene_starts[i] + PAD_LEAD:.3f}" data-duration="{audio_durations[i]:.3f}" '
        f'data-track-index="3" data-volume="1" '
        f'src="audio/{i:02d}_{scene["id"]}.mp3" crossorigin="anonymous"></audio>'
        for i, scene in enumerate(SCENES)
    )

    final_fade_at = total - 0.6
    fade_start = final_fade_at - 0.05
    fade_dur = total - fade_start + 0.1

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Five Layers of Agentic AI</title>
  <style>
{HOST_CSS}
  </style>
</head>
<body>
  <div id="root" data-composition-id="root" data-width="1920" data-height="1080" data-start="0" data-duration="{total:.3f}">
{block_includes}
{audio_includes}
    <div id="fade-out" class="clip" data-start="{fade_start:.3f}" data-duration="{fade_dur:.3f}" data-track-index="100"></div>

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#fade-out", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "power2.in" }}, {final_fade_at:.3f});
      window.__timelines["root"] = tl;
    </script>
  </div>
</body>
</html>
"""


def main() -> None:
    AUDIO_DIR.mkdir(exist_ok=True)
    SCENES_DIR.mkdir(exist_ok=True)

    audio_durations: list[float] = []
    for i, scene in enumerate(SCENES):
        out = AUDIO_DIR / f"{i:02d}_{scene['id']}.mp3"
        if not out.exists() or out.stat().st_size == 0:
            print(f"[{i:02d} {scene['id']}] tts (elevenlabs)…", flush=True)
            fetch_tts(scene["narration"], out)
        dur = probe_duration(out)
        audio_durations.append(dur)
        print(f"  {out.name}  {dur:.2f}s")

    scene_durations = [PAD_LEAD + d + PAD_TRAIL for d in audio_durations]
    scene_starts: list[float] = []
    t = 0.0
    for i, sd in enumerate(scene_durations):
        scene_starts.append(t)
        t += sd - (OVERLAP if i < len(scene_durations) - 1 else 0.0)
    total_duration = t

    for i, scene in enumerate(SCENES):
        block_path = SCENES_DIR / f"{i:02d}_{scene['id']}.html"
        block_path.write_text(render_scene_block(i, scene, audio_durations[i]))
        print(f"  wrote {block_path.relative_to(ROOT)}")

    (ROOT / "index.html").write_text(render_host(scene_starts, scene_durations, audio_durations, total_duration))
    print(f"\nwrote {ROOT / 'index.html'}")
    print(f"total duration: {total_duration:.2f}s ({len(SCENES)} scenes)")


if __name__ == "__main__":
    main()
