from instance import bot
from callBack import *
import logging
import os
from flask import Flask, render_template, Response, jsonify

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Создаем Flask-приложение
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "secret_key_for_development")

# Основной маршрут
@app.route('/')
def index():
    return jsonify({"status": "Telegram bot is running", "message": "Телеграм-бот запущен и работает"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Запуск бота в отдельном потоке при старте приложения
import threading
def start_bot():
    try:
        print("Бот запускается...")
        # Инициализируем необходимые базы данных
        init_quest_db()
        init_task_progress_db()
        init_users_db()
        init_favorites_db()
        
        # Принудительно синхронизируем домашние задания
        from fix_ritual_homework import force_sync_homework_tasks
        force_sync_homework_tasks()
        
        # Запускаем бота
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Произошла ошибка при запуске бота: {e}")
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        print("Бот остановлен.")

# Запускаем бота в отдельном потоке только когда файл запускается напрямую
if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask-приложение в режиме разработки
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    # Для запуска через gunicorn, запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    # Приложение app используется gunicorn'ом