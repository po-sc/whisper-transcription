# whisper-transcription

CLI-инструмент для транскрипции видео и аудио в текст с помощью [OpenAI Whisper](https://github.com/openai/whisper).

Поддерживает `.mov`, `.mp4`, `.mp3`, `.wav`, `.m4a` и другие форматы. По умолчанию использует модель `large` и русский язык.

## Установка

**Зависимости:**
```bash
# ffmpeg (нужен для видео)
brew install ffmpeg

# Python-пакеты
pip install openai-whisper
```

Или через requirements.txt:
```bash
pip install -r requirements.txt
```

## Использование

```bash
# Базовый запуск (модель large, язык ru)
python transcribe.py video.mov

# Другой язык
python transcribe.py interview.mp4 --language en

# Быстрая модель (менее точная)
python transcribe.py audio.mp3 --model medium

# Указать выходной файл
python transcribe.py video.mov --output result.txt

# Вывести транскрипт в терминал
python transcribe.py video.mov --print
```

## Параметры

| Параметр | По умолчанию | Описание |
|---|---|---|
| `input` | — | Входной файл |
| `-m, --model` | `large` | Модель Whisper: `tiny`, `base`, `small`, `medium`, `large` |
| `-l, --language` | `ru` | Код языка: `ru`, `en`, `de`, ... |
| `-o, --output` | `<input>.txt` | Путь к выходному файлу |
| `--print` | false | Вывести текст в stdout |

## Модели

| Модель | Размер | Скорость | Точность |
|---|---|---|---|
| `tiny` | 75 MB | очень быстро | низкая |
| `base` | 145 MB | быстро | средняя |
| `small` | 465 MB | быстро | хорошая |
| `medium` | 1.5 GB | средне | очень хорошая |
| `large` | 3 GB | медленно | максимальная |

Модели кэшируются в `~/.cache/whisper/` после первой загрузки.

## Заметки

- На CPU модель `large` транскрибирует ~17 мин аудио за 15–30 мин
- Whisper хорошо распознаёт русский начиная с модели `medium`
- Видео можно передавать напрямую — ffmpeg извлечёт аудио автоматически
