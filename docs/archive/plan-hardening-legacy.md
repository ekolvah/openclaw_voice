# План Hardening для `openclaw_voice` (минимум багов и поддержки)

## Кратко
Берем совет архитектора как основу, но адаптируем под фактическое состояние проекта и текущие риски:
1. Целевой STT на этом этапе: локальный `RealtimeSTT` (`model="tiny`) для стабильности.
2. Внедряем quality-слой фазами: `pyproject` + логирование + тесты ядра -> pre-commit -> CI.
3. Сохраняем `mypy strict`, но с typed-адаптером для `RealtimeSTT`, чтобы не разносить `type: ignore` по коду.

---

## Анализ совета архитектора (что принимаем/что корректируем)
1. **Принимаем полностью**:
- единый `pyproject.toml` для `ruff`/`mypy`/`pytest`;
- мокирование внешних API в тестах;
- `.env` только локально, `.env.example` в git;
- pre-commit и CI как обязательные quality-gates;
- переход с `print` на `logging`.

2. **Корректируем**:
- CI Python версия: не `3.11`, а `3.12` (локально уже `3.12.8`, меньше расхождений).
- Тестовый фокус: добавить тесты state-loop и recorder boundary (через адаптер), а не только `ask_openclaw`.
- Для текущей версии `RealtimeSTT` фиксируем контракт через адаптер, потому что сигнатуры/поведение уже вызывали runtime-ошибки.

---

## Фаза 1 (сразу): Базовый quality-фундамент

### 1. Структура проекта
Добавить:
- `tests/`
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml` (пока создаем, включаем в фазе 3)

Уточнить существующие:
- `.gitignore` расширить: `.env`, `*.mp3`, `voice_bridge.log`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `requirements.txt` дополнить dev-зависимостями через extra (см. интерфейсы ниже)

### 2. Модульная декомпозиция (без изменения поведения)
Разделить `voice_bridge.py` на устойчивые слои:
- `config` (чтение/валидация env)
- `clients/openclaw_client` (HTTP-запросы + trim history)
- `services/tts_service` (edge-tts + playback)
- `adapters/realtimestt_adapter` (все вызовы `AudioToTextRecorder`, единая граница нестабильного API)
- `app/bridge_runner` (главный цикл и state transitions)

Важно: публичный CLI-энтрипоинт оставить прежним (`python voice_bridge.py` через `run.bat`).

### 3. Логирование вместо print
Ввести `logging`:
- `INFO`: state transitions, wake detected, request started/finished, tts started/finished
- `ERROR`: сеть, сериализация ответа, TTS/STT сбои
- handlers:
  - `StreamHandler` (консоль)
  - `FileHandler("voice_bridge.log")`
- единый формат: timestamp + level + event + context

### 4. Явная state machine (контракт)
Зафиксировать состояния:
- `IDLE` -> `LISTENING` -> `PROCESSING` -> `SPEAKING` -> `IDLE`
Правила:
- во время `SPEAKING` микрофон приостанавливается;
- любой сбой в `PROCESSING` не должен убивать процесс, только лог + возврат в `IDLE`;
- history trimming строго ограничен (`history_limit`).

---

## Фаза 2 (до следующего коммита): Lint/Type/Test

### 1. `pyproject.toml`
Настроить:
- `ruff`:
  - `line-length = 100`
  - rules: `E`, `F`, `I`, плюс `UP` (безопасные py-улучшения)
- `mypy`:
  - `strict = true`
  - `python_version = "3.12"`
  - `warn_unused_ignores = true`
- `pytest`:
  - `testpaths = ["tests"]`

### 2. Typed-адаптер для RealtimeSTT
Создать локальный протокол/обертку:
- `RecorderPort` с методами `text() -> str`, `start/pause/resume/stop` (если доступны)
- `RealtimeSTTRecorderAdapter` инкапсулирует нестрого типизированную библиотеку
- В остальном коде работать только через `RecorderPort`

Цель: `mypy strict` проходит без каскада игноров.

### 3. Тесты (приоритет MVP)
Добавить минимум:
- `tests/test_openclaw_client.py`
  - успешный ответ
  - HTTP ошибка/timeout
  - некорректный JSON-ответ
  - trim history
- `tests/test_bridge_state.py`
  - пустой текст не вызывает OpenClaw/TTS
  - ошибка OpenClaw не роняет цикл
  - speaking вызывает pause/resume recorder
- `tests/test_config.py`
  - отсутствующий обязательный env
  - невалидные float-параметры
- `tests/test_tts_service.py`
  - создание temp файла/cleanup через моки
  - обработка исключения edge-tts

Все внешнее мокируется: `requests`, `edge_tts`, `pygame`, recorder adapter.

---

## Фаза 3 (после MVP): pre-commit + CI

### 1. pre-commit
`.pre-commit-config.yaml`:
- `ruff` (`check` + `format` по выбранной стратегии)
- `mypy`
- `pytest -q` (опционально, если время на commit приемлемо)

### 2. GitHub Actions
`ci.yml`:
- trigger: `push`, `pull_request`
- matrix: `windows-latest` (обязательно), опционально `ubuntu-latest` для unit-only
- steps:
  - setup Python 3.12
  - install deps (`.[dev]` или dev requirements)
  - `ruff check .`
  - `mypy .`
  - `pytest -v`

---

## Изменения интерфейсов/контрактов

### Публичные интерфейсы проекта
1. `run.bat` и `install.bat` остаются входной точкой пользователя.
2. `voice_bridge.py` остается executable entrypoint, но превращается в thin launcher.
3. `.env.example` — единственный публичный шаблон конфигурации.

### Внутренние интерфейсы (новые)
1. `VoiceConfig.from_env() -> VoiceConfig` с fail-fast validation.
2. `OpenClawClient.ask(text: str) -> str` (без сайд-эффектов вне клиента).
3. `RecorderPort` + `RealtimeSTTRecorderAdapter`.
4. `BridgeRunner.run_forever()` с явной state-machine.

---

## Тестовые сценарии и acceptance criteria

### Базовые acceptance criteria
1. `pytest` проходит полностью без реальных API.
2. `ruff check .` и `mypy .` проходят без ошибок.
3. При сетевой ошибке OpenClaw процесс не завершается.
4. История диалога ограничивается `history_limit`.
5. Во время TTS recorder pause/resume вызывается детерминированно.
6. Секреты (`.env`) не попадают в git.

### Smoke-run (ручной)
1. `.\install.bat` на чистой машине с Python 3.12.
2. `.\run.bat` запускает цикл без traceback.
3. Wake -> speech -> reply -> speech output.
4. Повторные циклы не деградируют по памяти/логам.

---

## Явные допущения и выбранные defaults
1. Default STT в этом плане: локальный `tiny` (стабильность > latency).
2. `GROQ_API_KEY` пока не обязательный в конфиге runtime (можно вернуть в Phase 4 как optional provider).
3. Основная ОС для эксплуатации: Windows (из-за аудио/микрофона), Python 3.12 фиксирован.
4. CI первично на Windows runner, чтобы совпадал с рабочим окружением.

---

## Риски и контроль
1. Риск: нестабильный внешний API `RealtimeSTT`.
- Контроль: adapter boundary + unit tests на контракт.
2. Риск: regressions при рефакторинге single-file в модули.
- Контроль: пошаговая декомпозиция с неизменным entrypoint и smoke после каждой фазы.
3. Риск: leak секретов.
- Контроль: `.gitignore` + pre-commit secret checks (добавить в Phase 3.5, если нужно).
