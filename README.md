# 🎤 Говорун – Telegram STT+Summarization Bot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.4-green)](https://github.com/aiogram/aiogram)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Bot Status](https://img.shields.io/badge/Bot-Online-brightgreen?style=flat&logo=telegram)](https://t.me/voice_combine_bot)

> Telegram-бот, який дозволяє надсилати голосові повідомлення, текст або PDF/текстові файли та отримувати згенеровані підсумки з використанням Whisper і LLM.

---

## 🔧 Функціональність

- 🎙️ Транскрипція голосових повідомлень (Whisper)
- 📄 Обробка тексту, PDF
- 🧠 Генерація стислого підсумку (LLM)
- 📂 Тимчасове зберігання файлів з автоматичним очищенням
- ⚙️ Користувацькі налаштування стилю підсумку

---

## 🚀 Запуск

### 1. Клонування репозиторію

```bash
git clone https://github.com/SARAFANUA/govorun.git
cd govorun
```

### 2. Налаштування `.env`

```bash
cp .env.example .env
# Встав свій TELEGRAM_BOT_TOKEN
```

### 3. Віртуальне середовище

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 4. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 5. Запуск бота

```bash
python main_bot.py
```

---

## 📁 Структура проєкту

```
govorun/
├── handlers/               # Хендлери для повідомлень
├── keyboards/              # Кнопки меню
├── services/               # Транскрипція, обробка PDF, генерація
├── states/                 # FSM стани
├── main_bot.py             # Точка входу
├── .env.example            # Шаблон .env
├── requirements.txt        # Залежності
└── README.md
```

---

## 🔐 Безпека

- Файли зберігаються у тимчасовій директорії та одразу видаляються після обробки.
- Дані користувача не логуються.

🙌 Подяки
- @magerkopython
- OpenAI Whisper
- HuggingFace Transformers
- Aiogram 3