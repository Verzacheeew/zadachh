import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Создаем базу данных SQLite
def init_db():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT
        )
    """)
    conn.commit()
    conn.close()

# Добавить заметку
async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    note_text = " ".join(context.args)

    if not note_text:
        await update.message.reply_text("Укажите текст заметки! Например: /add_note Покупки на завтра.")
        return

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (user_id, text) VALUES (?, ?)", (user_id, note_text))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"Заметка добавлена: {note_text}")

# Показать все заметки
async def show_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, text FROM notes WHERE user_id = ?", (user_id,))
    notes = cursor.fetchall()
    conn.close()

    if not notes:
        await update.message.reply_text("У вас нет заметок.")
        return

    notes_list = "\n".join([f"{note[0]}. {note[1]}" for note in notes])
    await update.message.reply_text(f"📋 Ваши заметки:\n{notes_list}")

# Удалить заметку
async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        note_id = int(context.args[0])

        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        conn.commit()
        conn.close()

        if cursor.rowcount > 0:
            await update.message.reply_text(f"Заметка с ID {note_id} удалена.")
        else:
            await update.message.reply_text("Заметка не найдена.")
    except Exception as e:
        await update.message.reply_text("Ошибка! Используйте формат: /delete_note <номер>")

# Очистить все заметки
async def clear_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    await update.message.reply_text("Все ваши заметки удалены.")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу вам управлять заметками. "
        "Используйте следующие команды:\n"
        "/add_note <текст> — добавить заметку\n"
        "/show_notes — показать все заметки\n"
        "/delete_note <номер> — удалить заметку\n"
        "/clear_notes — очистить все заметки"
    )

# Основная функция
def main():
    # Инициализируем базу данных
    init_db()

    # Получаем токен из переменных окружения
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_note", add_note))
    application.add_handler(CommandHandler("show_notes", show_notes))
    application.add_handler(CommandHandler("delete_note", delete_note))
    application.add_handler(CommandHandler("clear_notes", clear_notes))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
