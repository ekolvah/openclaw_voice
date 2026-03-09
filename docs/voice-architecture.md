# Voice Architecture

`OpenClaw` remains the conversational brain for the voice bridge.

## Responsibilities
- `OpenClaw`: reasoning, memory, sessions, tools, and text response generation
- Voice bridge: wake-word flow, speech capture, spoken-response shaping, TTS provider selection, playback, and fallback behavior

## Spoken Output Layer
- Default provider: `Silero`
- Default fallback: disabled for the out-of-box local-first setup
- Future API-based providers can be added behind the same provider contract without changing `OpenClaw`
- Speech shaping happens in the bridge before TTS so Telegram and other text channels keep the original text behavior

## Runtime Flow
1. Wake-word detection and speech capture happen locally.
2. The bridge sends recognized text to `OpenClaw`.
3. `OpenClaw` returns a text response.
4. The bridge reshapes that text into speech-friendly chunks.
5. The bridge renders those chunks through the configured TTS provider.
6. Playback finishes and the bridge returns to listening.

## Runtime Setup
1. Copy `.env.example` to `.env`.
2. Set `OPENCLAW_GATEWAY_TOKEN`.
3. Keep `TTS_PROVIDER=silero` for the default local setup.
4. Leave `TTS_FALLBACK_PROVIDER=` empty unless you add another provider later.
5. Adjust `SILERO_*` values only if you intentionally want a different model or speaker.
6. Use `SPEECH_MAX_CHUNK_CHARS` to control how aggressively long replies are split before playback.

## Smoke Test
- Run `scripts/smoke_test_voice.ps1` for the local-first configuration checks.
- Then run `run.bat` and verify one complete voice cycle:
  - wake word is detected
  - speech is recognized
  - `OpenClaw` returns a reply
  - the reply is spoken through `Silero`
  - the bridge returns to idle/listening

## Design Constraints
- Do not move speech-specific shaping into `OpenClaw`.
- Keep provider contracts small and explicit.
- Prefer local-first behavior by default so the bridge works without mandatory cloud registration.
