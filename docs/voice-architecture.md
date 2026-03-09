# Voice Architecture

`OpenClaw` remains the conversational brain for the voice bridge.

## Responsibilities
- `OpenClaw`: reasoning, memory, sessions, tools, and text response generation
- Voice bridge: STT, wake-word flow, spoken-response shaping, TTS provider selection, audio playback, and fallback behavior

## Spoken Output Layer
- Primary TTS provider: `SaluteSpeech`
- Fallback TTS provider: `Silero`
- Speech shaping happens in the bridge before TTS so Telegram and other text channels are not affected

## Runtime Flow
1. Wake-word and speech capture happen locally
2. OpenClaw returns a text response
3. The bridge reshapes text into spoken Russian-friendly chunks
4. The bridge renders speech through `SaluteSpeech`
5. If primary TTS fails, the bridge falls back to `Silero`

## Configuration
See `.env.example` for the active provider settings:
- `TTS_PROVIDER`
- `TTS_FALLBACK_PROVIDER`
- `SALUTE_*`
- `SILERO_*`
- `SPEECH_MAX_CHUNK_CHARS`
