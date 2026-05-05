# whisper-transcription

CLI для транскрипции видео и аудио в текст с помощью [OpenAI Whisper](https://github.com/openai/whisper).

Поддерживает `.mov`, `.mp4`, `.mp3`, `.wav`, `.m4a` и другие форматы. По умолчанию использует модель `turbo` — почти такая же точная как `large-v3`, но в ~8 раз быстрее.

## Установка

```bash
# ffmpeg — нужен для видео
brew install ffmpeg

# Whisper
pip install openai-whisper
```

## Использование

```bash
# Базовый запуск (модель turbo, язык ru)
python transcribe.py video.mov

# Несколько файлов сразу
python transcribe.py *.mp3

# Другой язык
python transcribe.py interview.mp4 --language en

# Субтитры (.srt для видеоплееров)
python transcribe.py video.mov --format srt

# Текст с таймстемпами
python transcribe.py audio.mp3 --timestamps

# Максимальное качество
python transcribe.py audio.mp3 --model large-v3

# Вывести список моделей
python transcribe.py --list-models
```

## Параметры

| Параметр | По умолчанию | Описание |
|---|---|---|
| `inputs` | — | Один или несколько файлов |
| `-m, --model` | `turbo` | Модель Whisper (см. таблицу ниже) |
| `-l, --language` | `ru` | Код языка: `ru`, `en`, `de`, `fr`, ... |
| `-f, --format` | `txt` | Формат: `txt`, `srt`, `vtt`, `json` |
| `-o, --output` | `<input>.<ext>` | Выходной файл (только для одного файла) |
| `-t, --timestamps` | false | Добавить таймстемпы в txt |
| `--print` | false | Вывести текст в stdout |
| `--list-models` | — | Показать таблицу моделей |

## Модели

| Модель | Размер | Описание |
|---|---|---|
| `tiny` | 75 MB | Максимально быстро, низкая точность |
| `base` | 145 MB | Быстро, базовая точность |
| `small` | 465 MB | Хороший баланс для коротких записей |
| `medium` | 1.5 GB | Хорошая точность |
| **`turbo`** | **809 MB** | **large-v3-turbo — рекомендуется: в ~8x быстрее large-v3, почти та же точность** |
| `large-v2` | 3 GB | Предыдущая топовая модель |
| `large-v3` | 3 GB | Максимальная точность, самая медленная |

Модели скачиваются автоматически при первом запуске и кэшируются в `~/.cache/whisper/`.

## Форматы вывода

- **`txt`** — чистый текст (с `--timestamps` добавляет `[HH:MM:SS]` перед каждым сегментом)
- **`srt`** — субтитры для видеоплееров (VLC, IINA, Premiere)
- **`vtt`** — субтитры WebVTT для браузера
- **`json`** — полный результат Whisper со всеми метаданными сегментов

## Заметки

- На CPU `turbo` транскрибирует ~17 мин аудио примерно за 5–10 мин, `large-v3` — 30–40 мин
- Русский язык хорошо распознаётся начиная с модели `small`, отлично — с `turbo`
- Видео передаётся напрямую — ffmpeg извлечёт аудио автоматически
