# 🎤 Говорун – Telegram STT+Summarization Bot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.4-green)](https://github.com/aiogram/aiogram)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Bot Status](https://img.shields.io/badge/Bot-Online-brightgreen?style=flat&logo=telegram)](https://t.me/voice_combine_bot)

> Telegram-бот, що дозволяє надсилати голосові повідомлення, текст або PDF-файли та отримувати згенеровані підсумки з використанням Whisper та LLM.

---

## 🔧 Функціональність

- 🎙️ Транскрипція голосових повідомлень (Whisper)
- 📄 Обробка тексту та PDF
- 🧠 Генерація стислого змісту (LLM)
- 📥 Підтримка декількох форматів
- 📂 Обробка документів без збереження історії
- 🧪 Оптимізовано для тестування та кастомізації

---

## 🚀 Як запустити

### 🔐 1. Клонувати репозиторій

```bash
git clone https://github.com/SARAFANUA/govorun.git
cd govorun
🛠️ 2. Створити .env файл
bash
Копіювати
Редагувати
cp .env.example .env
Встав у .env свій токен бота:

env
Копіювати
Редагувати
TELEGRAM_BOT_TOKEN=your_token_here
🐍 3. Створити віртуальне середовище
bash
Копіювати
Редагувати
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
📦 4. Встановити залежності
bash
Копіювати
Редагувати
pip install -r requirements.txt
▶️ 5. Запустити бота
bash
Копіювати
Редагувати
python main_bot.py
🧠 Залежності
aiogram

openai-whisper

PyMuPDF

transformers (або інша бібліотека LLM)

python-dotenv

📁 Структура проєкту
bash
Копіювати
Редагувати
govorun/
├── handlers/               # Обробники повідомлень
├── keyboards/              # Меню і кнопки
├── services/               # Логіка транскрипції, PDF, LLM
├── states/                 # Стан машини FSM
├── main_bot.py             # Точка входу
├── .env.example            # Шаблон змінних середовища
├── requirements.txt        # Залежності
└── README.md
🧪 Приклад використання
Надішли голосове повідомлення — отримаєш текст.

Надішли текст або PDF — отримаєш стислий підсумок.

Усе працює у режимі «один запит — одна відповідь».

🔐 Безпека
Файли не зберігаються. Дані обробляються в оперативній памʼяті або тимчасових файлах, що автоматично видаляються.

🙌 Подяки
@magerkopython - за приклад коду

OpenAI Whisper — за точну транскрипцію

HuggingFace Transformers — за генерацію підсумків

Aiogram — за чудовий фреймворк для Telegram ботів
