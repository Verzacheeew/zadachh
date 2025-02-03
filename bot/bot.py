import os
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Получаем токены из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Базовый URL для TMDb API
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Сопоставление жанров с ID
GENRE_MAP = {
    "комедия": 35,
    "фантастика": 878,
    "боевик": 28,
    "драма": 18,
    "ужасы": 27,
    "мелодрама": 10749,
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу тебе найти фильмы или сериалы. "
        "Используй /find_movie <жанр>, чтобы найти фильм по жанру, или /recommend для случайной рекомендации."
    )

# Команда /find_movie
async def find_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    genre_name = " ".join(context.args).lower()
    if not genre_name:
        await update.message.reply_text("Укажите жанр! Например: /find_movie комедия")
        return

    # Получаем ID жанра
    genre_id = GENRE_MAP.get(genre_name)
    if not genre_id:
        await update.message.reply_text("Неизвестный жанр. Попробуйте другой.")
        return

    # Запрос к TMDb API
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id,
        "language": "ru-RU",
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("results"):
        movie = random.choice(data["results"])
        title = movie.get("title", "Название неизвестно")
        year = movie.get("release_date", "Год неизвестен")[:4]
        await update.message.reply_text(f"🎬 Фильм: {title} ({year})")
    else:
        await update.message.reply_text("Фильмов такого жанра не найдено.")

# Команда /recommend
async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Запрос к TMDb API для популярных фильмов
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "ru-RU",
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("results"):
        movie = random.choice(data["results"])
        title = movie.get("title", "Название неизвестно")
        year = movie.get("release_date", "Год неизвестен")[:4]
        await update.message.reply_text(f"🌟 Рекомендация: {title} ({year})")
    else:
        await update.message.reply_text("Не удалось найти рекомендацию.")

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("find_movie", find_movie))
    application.add_handler(CommandHandler("recommend", recommend))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
