# OpenClaw Voice Bridge v2.1 (Validated for OpenClaw 2026.2.26)

## Summary
Build a Windows background voice bridge (custom `voice_bridge.py`) with:
1. Wake word: Porcupine (`jarvis`)
2. STT: Groq Whisper (`whisper-large-v3`, RU)
3. LLM: OpenClaw Gateway HTTP API in WSL
4. TTS: `edge-tts` (`ru-RU-DmitryNeural`)

This keeps Telegram text flow unchanged and adds hands-free voice loop near the PC.

## Critical Corrections to v2
1. `POST /v1/chat/completions` is disabled by default in OpenClaw and must be explicitly enabled.
2. Your current config schema is `gateway.bind/gateway.port/gateway.auth`, not only `gateway.http.*` block.
3. In OpenAI-compatible API, `model` should target agent routing as `openclaw:<agentId>` or `agent:<agentId>`, or use header `x-openclaw-agent-id`.
4. For “same agent as Telegram”, use `main` unless you explicitly create `voice` agent.

## Target Configuration (OpenClaw)
1. Keep gateway auth token mode enabled.
2. Set bind for Windows access:
`gateway.bind = "0.0.0.0"` if `localhost` from Windows fails.
3. Enable endpoint:
`gateway.http.endpoints.chatCompletions.enabled = true`.
4. Agent routing:
Use `model: "openclaw:main"` in bridge requests (or header `x-openclaw-agent-id: main`).

## External Interface Contract
1. Groq STT:
`POST https://api.groq.com/openai/v1/audio/transcriptions`
2. OpenClaw:
`POST http://<gateway-host>:18789/v1/chat/completions`
3. Auth:
`Authorization: Bearer <gateway token>`
4. Chat payload:
`{"model":"openclaw:main","messages":[...],"stream":false,"user":"voice-bridge-local"}`

## Implementation Steps
1. Create project folder `openclaw_voice` on Windows.
2. Add files: `voice_bridge.py`, `.env`, `install.bat`, `run.bat`.
3. Install deps in `.venv` using your package list.
4. Configure `.env` with `PICOVOICE_ACCESS_KEY`, `GROQ_API_KEY`, gateway URL/token, RU voice.
5. Start bridge with `run.bat`.
6. Add shortcut to Startup folder for auto-launch.
7. Validate runtime logs and tune `WAKE_SENSITIVITY` and `SILENCE_SECONDS`.

## Required Code-Level Adjustments in Your Script Spec
1. OpenClaw call:
Replace `json={"model": AGENT_ID, ...}` with `json={"model": f"openclaw:{AGENT_ID}", ...}`.
2. Default `OPENCLAW_AGENT_ID` should be `main` (not `voice`) unless that agent exists.
3. Feedback-loop guard must be explicit in speaking stage:
pause/stop recorder before TTS playback, resume after playback.
4. Keep bounded history and set stable `user` field for session continuity.

## Test Cases
1. Health:
`curl http://localhost:18789/health` returns `ok=true`.
2. API probe:
`POST /v1/chat/completions` returns 200 (not 405).
3. Wake:
“Jarvis” triggers beep and recording state.
4. STT:
Russian phrase transcribes correctly.
5. LLM:
Assistant reply returns from `main` agent.
6. TTS:
Reply spoken in Russian voice.
7. Recovery:
After answer playback, system returns to idle listening.
8. Parallel channel:
Telegram still responds during/after voice sessions.
9. Latency:
End-of-speech to speech-start <= 4s target.

## Risks and Fallbacks
1. If Windows cannot reach WSL `localhost`, switch bridge URL to WSL IP and bind gateway to `0.0.0.0`.
2. If Groq quota is exhausted, fallback to local Whisper mode in RealtimeSTT.
3. If `edge-tts` fails, fallback to Windows local TTS backend.
4. If false wake triggers remain high, increase `WAKE_SENSITIVITY` and tighten silence window.

## Assumptions (Validated)
1. OpenClaw version is `2026.2.26`.
2. OpenAI-compatible endpoint exists and is configurable in current OpenClaw docs.
3. Agent selection through `model` (`openclaw:<id>` / `agent:<id>`) is supported.
4. `Purple-Horizons/openclaw-voice` exists, but this plan intentionally follows your custom bridge path.

## Sources
1. https://docs.openclaw.ai/gateway/openai-http-api
2. https://docs.openclaw.ai/gateway/configuration-reference
3. https://github.com/Purple-Horizons/openclaw-voice
