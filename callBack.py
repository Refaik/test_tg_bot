from collections import defaultdict
from datetime import datetime, timedelta
import telebot
from telebot import types
from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton,Message,ReplyKeyboardMarkup, KeyboardButton
from telebot.apihelper import ApiTelegramException
import sqlite3
import logging
import time
import requests
import random
import os
import csv
import json
from logging.handlers import RotatingFileHandler
import sys
from threading import Thread
from instance import (bot, photo, photo_logarithms, photo_powers, photo_fsy, photo_modules, photo_parabola,
                      photo_quadratic_equations, photo_roots, photo_direct, photo_hyperbola,
                      photo_root_function, photo_exponential_function, photo_logarithmic_function,
                      photo_contact, photo_main, photo_definition, photo_reduction_formulas,
                      photo_trigonometric_formulas, photo_task_rhombus_trapezoid, photo_task_angles,
                      photo_trigonometric_circle, photo_task45, photo_task10, photo_task2, photo_task12, photo_task3,
                      photo_task81, photo_task82, photo_task_triangle_lines, photo_task_right_triangle,
                      photo_task_isosceles_equilateral_triangle, photo_task_triangle_similarity, photo_task_triangle,
                      photo_task_circle_2, photo_task_circle_1, photo_task_parallelogram, photo_task_regular_hexagon,
                      photo_trigonometry, photo_rationalization,photo_task14,photo_task16,photo_tasks,photo_cards,photo_timers,
                      photo_quize, photo_challenge, photo_quest_main, photo_quest_worlds, photo_quest_profile, photo_quest_trophies, photo_quest_shop, photo_quest_coming_soon,
                      photo_quest_book, photo_quest_quests, photo_quest_ritual
                      )
from screens import (tasks_screen, main_screen, contact_screen,
                     task_679_screen, task_10_screen, task_11_screen, task_12_screen,
                     task_45_screen, task_8_screen, task_1_screen, task_2_screen, task_3_screen,
                     back_to_task_679_screen, back_to_task_8_screen, back_to_task_gropCircle_screen,
                     back_to_task_11_screen, task_group_trigonometry_screen,
                     back_to_task_group_trigonometry_screen, back_to_task_1_screen, task_groupCircle_screen,
                     back_to_task_gropTriangles_screen, task_groupTriangles_screen, task_13_screen,
                     back_to_task_13_screen, task13group_trigonometry_screen, back_to_task13group_trigonometry_screen,
                     task_15_screen, back_to_task_15_screen, task_17_screen, back_to_task_17_screen,
                     task17groupTriangles_screen, back_to_task17gropTriangles_screen, back_to_task17gropCircle_screen,
                     task17groupCircle_screen, back_to_task17group_trigonometry_screen,task17group_trigonometry_screen, math_quest_screen, quest_worlds_screen, quest_profile_screen, quest_trophies_screen, quest_shop_screen, coming_soon_screen, loaded_world_screen)

# Настройка логирования с явной поддержкой UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Установка кодировки UTF-8 для вывода в консоль
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Тестовое сообщение
logging.info("✅ Логирование инициализировано с поддержкой UTF-8")

def ensure_user_data(user_id, default_data=None):
    if user_id not in user_data or not isinstance(user_data[user_id], dict):
        user_data[user_id] = default_data or {}
    return user_data[user_id]

# ================== Отслеживание активности ==================
users_db = 'users.db'
users_conn = sqlite3.connect(users_db, check_same_thread=False)
users_cursor = users_conn.cursor()

def init_users_db():
    try:
        with users_conn:
            users_cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    phone TEXT,
                    first_seen TEXT,
                    last_seen TEXT
                )''')
            users_cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS tutor_requests (
                    user_id INTEGER,
                    name TEXT,
                    school_class TEXT,
                    test_score TEXT,
                    expected_price TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (user_id, timestamp)
                )''')
            # Добавляем столбец phone, если его нет
            users_cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in users_cursor.fetchall()]
            if "phone" not in columns:
                users_cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
                logging.info("Столбец 'phone' добавлен в таблицу 'users'")
            users_conn.commit()
            logging.info("✅ Таблица 'users' и 'tutor_requests' обновлены!")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")

init_users_db()

def register_user(user_id, username=None, phone=None):
    current_time = datetime.now().isoformat()
    with users_conn:
        users_cursor.execute('SELECT username, phone FROM users WHERE user_id = ?', (user_id,))
        result = users_cursor.fetchone()
        if not result:
            users_cursor.execute('''
                INSERT INTO users (user_id, username, phone, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, phone, current_time, current_time))
        else:
            # Обновляем только те поля, которые предоставлены
            update_fields = []
            update_values = []
            if username:
                update_fields.append("username = ?")
                update_values.append(username)
            if phone:
                update_fields.append("phone = ?")
                update_values.append(phone)
            update_fields.append("last_seen = ?")
            update_values.append(current_time)
            update_values.append(user_id)
            if update_fields:
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
                users_cursor.execute(query, update_values)
        users_conn.commit()

def get_total_users():
    with users_conn:
        users_cursor.execute('SELECT COUNT(*) FROM users')
        total = users_cursor.fetchone()[0]
    return total

def get_active_users_today():
    today = datetime.now().strftime('%Y-%m-%d')
    with users_conn:
        users_cursor.execute('SELECT COUNT(*) FROM users WHERE last_seen LIKE ?', (f'{today}%',))
        active = users_cursor.fetchone()[0]
    return active

# Храним данные пользователей
user_sessions = {}
user_data = {}
user_chat_history = {}
user_messages = {}
user_task_data = {}
# Храним список пользователей
users = set()

# Определяем списки тем для алгебры и геометрии
ALGEBRA_THEMES = [
    ("Теория вероятностей", "probability"),
    ("ФСУ", "fsu"),
    ("Квадратные уравнения", "quadratic"),
    ("Степени", "powers"),
    ("Корни", "roots"),
    ("Производные", "derivative"),
    ("Текстовые задачи", "wordproblem"),
    ("Тригонометрические определения", "trigonometrydefinitions"),
    ("Тригонометрические формулы", "trigonometryformulas"),
    ("Логарифмы", "logarithms"),
    ("Модули", "modules"),
    ("Функция корня", "rootfunction"),
    ("Показательная функция", "exponentialfunction"),
    ("Логарифмическая функция", "logarithmicfunction")
]
GEOMETRY_THEMES = [
    ("Окружность", "circle"),
    ("Прямоугольный треугольник", "righttriangle"),
    ("Равносторонний треугольник", "equilateraltriangle"),
    ("Равенство/Подобие", "similarity"),
    ("Ромб и Трапеция", "rhombustrapezoid"),
    ("Шестиугольник", "hexagon"),
    ("Треугольник", "triangle"),
    ("Вектор", "vector"),
    ("Стереометрия", "stereometry"),
    ("Прямая", "direct"),
    ("Парабола", "parabola"),
    ("Гипербола", "hyperbola")
]

ALGEBRA_CODES = [theme[1] for theme in ALGEBRA_THEMES]
GEOMETRY_CODES = [theme[1] for theme in GEOMETRY_THEMES]

# ================== Задачи ==================
favorites_conn = sqlite3.connect('favorites.db', check_same_thread=False)
favorites_cursor = favorites_conn.cursor()

def init_favorites_db():
    favorites_cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            user_id TEXT,
            challenge_num TEXT,
            cat_code TEXT,
            task_idx INTEGER,
            PRIMARY KEY (user_id, challenge_num, cat_code, task_idx)
        )
    ''')
    favorites_conn.commit()
    logging.info("Таблица 'favorites' в favorites.db создана или уже существует!")
init_favorites_db()

def load_favorites(user_id=None):
    """Загружает избранные задания из базы данных
    
    Параметры:
        user_id (str, optional): ID пользователя, для которого нужно загрузить избранное.
            Если не указан, загружаются задания для всех пользователей.
    
    Возвращает:
        dict: Словарь с избранными заданиями, где ключ - ID пользователя, 
              значение - список словарей с информацией о задании
    """
    try:
        conn = sqlite3.connect('favorites.db')
        cursor = conn.cursor()
        
        if user_id:
            # Преобразуем user_id в строку для корректного сравнения в базе
            user_id_str = str(user_id)
            cursor.execute("SELECT user_id, challenge_num, cat_code, task_idx FROM favorites WHERE user_id = ?", (user_id_str,))
        else:
            cursor.execute("SELECT user_id, challenge_num, cat_code, task_idx FROM favorites")
            
        rows = cursor.fetchall()
        conn.close()

        favorites = {}
        for row in rows:
            u_id, challenge_num, cat_code, task_idx = row
            if u_id not in favorites:
                favorites[u_id] = []
            favorites[u_id].append({
                "challenge_num": challenge_num,
                "cat_code": cat_code,
                "task_idx": task_idx
            })
            
        user_str = user_id_str if user_id else 'всех'
        logging.info(f"Загружено избранных задач: {len(rows)} записей для user_id={user_str}")
        return favorites
    except Exception as e:
        logging.error(f"Ошибка при загрузке избранного: {e}")
        return {}

def get_user_favorites(user_id):
    """Получает список избранных заданий для конкретного пользователя"""
    favorites = load_favorites(user_id)
    # Всегда преобразуем user_id в строку перед обращением к словарю
    user_id_str = str(user_id)
    user_favorites = favorites.get(user_id_str, [])
    logging.info(f"Получено избранное для user_id={user_id_str}: {len(user_favorites)} задач")
    return user_favorites
# ================== Репетитор ==================
TUTOR_REVIEWS = [
    "https://imgur.com/zaaBUGU",
    "https://imgur.com/wdv4EAW",
    "https://imgur.com/Bj3rBZ2",
    "https://imgur.com/7ciKrv3",
    "https://imgur.com/Tu2XeFJ"
]

def get_user_display_name(user):
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    else:
        return f"User ID: {user.id}"

def get_display_name(user_id, chat_id):
    user_id = str(user_id)  # Убедимся, что user_id — строка

    # Проверяем данные в user_data
    if user_id in user_data and "username" in user_data[user_id] and user_data[user_id]["username"]:
        return f"@{user_data[user_id]['username']}"
    elif user_id in user_data and "phone" in user_data[user_id] and user_data[user_id]["phone"]:
        return f"📞 {user_data[user_id]['phone']}"

    # Проверяем базу данных
    try:
        with users_conn:
            users_cursor.execute('SELECT username, phone FROM users WHERE user_id = ?', (user_id,))
            result = users_cursor.fetchone()
            if result:
                username, phone = result
                if username:
                    return f"@{username}"
                elif phone:
                    return f"📞 {phone}"
    except sqlite3.Error as e:
        logging.error(f"Ошибка при запросе к базе users для user_id={user_id}: {e}")

    # Пробуем получить номер телефона через API Telegram
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.user.phone_number:
            phone = chat_member.user.phone_number
            # Сохраняем номер в базу данных
            with users_conn:
                users_cursor.execute('UPDATE users SET phone = ? WHERE user_id = ?', (phone, user_id))
                users_conn.commit()
            return f"📞 {phone}"
    except Exception as e:
        logging.error(f"Ошибка получения номера телефона через API для user_id={user_id}: {e}")

    # Если ничего не нашли, возвращаем ID
    return f"User ID: {user_id}"

def save_tutor_request(user_id, name, school_class, test_score, expected_price):
    try:
        with users_conn:
            timestamp = datetime.now().isoformat()
            users_cursor.execute('''
                INSERT INTO tutor_requests (user_id, name, school_class, test_score, expected_price, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, school_class, test_score, expected_price, timestamp))
            users_conn.commit()
            logging.info(f"Новая заявка для user_id {user_id} сохранена.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении заявки для user_id {user_id}: {e}")

def ask_tutor_question(chat_id, user_id, message_id):
    if user_id not in user_data or "tutor_step" not in user_data[user_id]:
        logging.error(f"Нет данных для user_id={user_id} или отсутствует tutor_step")
        return

    # Сохраняем username, если он есть
    if "username" not in user_data[user_id]:
        try:
            user = bot.get_chat_member(chat_id, user_id).user
            user_data[user_id]["username"] = user.username
        except Exception as e:
            logging.error(f"Ошибка получения username для user_id={user_id}: {e}")

    # Если нет username и телефона, запрашиваем номер
    if not user_data[user_id].get("username") and "phone" not in user_data[user_id]:
        # Используем ReplyKeyboardMarkup вместо InlineKeyboardMarkup
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        contact_button = KeyboardButton(text="📞 Поделиться номером телефона", request_contact=True)
        markup.add(contact_button)
        mark = InlineKeyboardMarkup()
        mark.add(InlineKeyboardButton("↩️ Назад", callback_data="tutor_call"))
        try:
            # Отправляем сообщение с обычной клавиатурой вместо редактирования
            bot.edit_message_media(
                media=types.InputMediaPhoto(
                    photo,
                    "Мы заметили, что у вас не указан Telegram-тег. Пожалуйста, поделитесь номером телефона через кнопку ниже."
                ),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=mark  # Убираем старую клавиатуру, если была
            )
            logging.info(f"Успешно запрошен номер телефона для user_id={user_id} через ReplyKeyboardMarkup")
            # Регистрируем обработчик для контакта
            bot.register_next_step_handler_by_chat_id(chat_id, handle_contact, user_id, message_id)
        except Exception as e:
            logging.error(f"Ошибка при запросе номера телефона для user_id={user_id}: {e}")
        return

    # Остальной код с вопросами
    step = user_data[user_id]["tutor_step"]
    display_name = get_display_name(user_id, chat_id)
    questions = [
        "Как вас зовут?",
        "В каком классе вы учитесь?",
        "Писали ли вы пробники? Если да, то на какой балл?",
        "Какую цену вы ожидаете за занятие?"
    ]

    if step < len(questions):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="tutor_call"))
        try:
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, questions[step]),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            bot.register_next_step_handler_by_chat_id(chat_id, process_tutor_answer, user_id, message_id)
            logging.info(f"Вопрос '{questions[step]}' отправлен для {display_name}")
        except Exception as e:
            logging.error(f"Ошибка при отправке вопроса для user_id={user_id}: {e}")
    else:
        answers = user_data[user_id]["tutor_answers"]
        try:
            save_tutor_request(
                user_id,
                answers["name"],
                answers["school_class"],
                answers["test_score"],
                answers["expected_price"]
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="main_back_call"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, "Заявка успешно отправлена!"),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            logging.info(f"Заявка успешно отправлена для {display_name}")
            del user_data[user_id]
        except Exception as e:
            logging.error(f"Ошибка при сохранении заявки для user_id={user_id}: {e}")
def handle_contact(message, user_id, message_id):
    chat_id = message.chat.id

    if message.contact is None:
        logging.error(f"Пользователь {user_id} не поделился контактом")
        bot.send_message(chat_id, "Пожалуйста, поделитесь номером телефона через кнопку.")
        return

    if user_id not in user_data:
        user_data[user_id] = {"tutor_step": 0, "tutor_answers": {}}

    # Сохраняем номер телефона
    phone = message.contact.phone_number
    user_data[user_id]["phone"] = phone
    register_user(user_id, message.from_user.username, phone)  # Передаём номер телефона в register_user
    logging.info(f"Получен номер телефона для user_id={user_id}: {phone}")

    # Удаляем сообщение с кнопкой
    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение с кнопкой для user_id={user_id}: {e}")

    # Переходим к первому вопросу
    ask_tutor_question(chat_id, user_id, message_id)

def process_tutor_answer(message, user_id, message_id):
    chat_id = message.chat.id
    if user_id not in user_data or "tutor_step" not in user_data[user_id]:
        return

    if "username" not in user_data[user_id]:
        user_data[user_id]["username"] = message.from_user.username

    step = user_data[user_id]["tutor_step"]
    display_name = get_display_name(user_id, chat_id)
    user_answer = message.text.strip()

    if user_answer.startswith('/'):
        bot.send_message(chat_id, "Пожалуйста, введите корректный ответ, а не команду!")
        bot.register_next_step_handler_by_chat_id(chat_id, process_tutor_answer, user_id, message_id)
        logging.warning(f"{display_name} ввёл команду '{user_answer}' вместо ответа")
        return

    if step == 0:
        user_data[user_id]["tutor_answers"]["name"] = user_answer
    elif step == 1:
        user_data[user_id]["tutor_answers"]["school_class"] = user_answer
    elif step == 2:
        user_data[user_id]["tutor_answers"]["test_score"] = user_answer
    elif step == 3:
        user_data[user_id]["tutor_answers"]["expected_price"] = user_answer

    logging.info(f"{display_name} ответил на шаг {step}: '{user_answer}'")
    user_data[user_id]["tutor_step"] += 1

    try:
        bot.delete_message(chat_id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        logging.warning(f"Не удалось удалить сообщение для {display_name}: {e}")

    ask_tutor_question(chat_id, user_id, message_id)

def finish_tutor_questions(chat_id, user_id, message_id):
    if user_id not in user_data or "tutor_answers" not in user_data[user_id]:
        bot.send_message(chat_id, "Ошибка: данные не найдены.")
        logging.error(f"Данные для User ID: {user_id} не найдены в user_data")
        return

    answers = user_data[user_id]["tutor_answers"]
    display_name = get_display_name(user_id, chat_id)
    timestamp = datetime.now().isoformat()

    try:
        with users_conn:
            users_cursor.execute('''
                INSERT OR REPLACE INTO tutor_requests (user_id, name, school_class, test_score, expected_price, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, answers.get("name", ""), answers.get("school_class", ""),
                  answers.get("test_score", ""), answers.get("expected_price", ""), timestamp))
            users_conn.commit()
        logging.info(f"Новая заявка для {display_name} сохранена в базе данных")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении заявки для {display_name}: {e}")
        bot.send_message(chat_id, "Ошибка при сохранении заявки. Попробуйте снова.")
        return

    text = "✅ Заявка сохранена!\n\nМы с вами свяжемся!"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Новая заявка", callback_data="tutor_call"))
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data="main_back_call"))
    bot.edit_message_media(
        media=types.InputMediaPhoto(photo, text),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )

    admin_chat_id = 1035828828
    notification_text = (
        f"📊 Новая заявка от {display_name}\n"
        f"Имя: {answers.get('name', 'Не указано')}\n"
        f"Класс: {answers.get('school_class', 'Не указано')}\n"
        f"Балл: {answers.get('test_score', 'Не указано')}\n"
        f"Цена: {answers.get('expected_price', 'Не указано')}\n"
        f"Время: {timestamp}"
    )

    try:
        bot.send_message(admin_chat_id, notification_text, timeout=30)
        logging.info(f"Уведомление успешно отправлено администратору для {display_name}")
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление администратору: {e}")

    # Очищаем только временные данные репетитора, сохраняя phone и username
    if user_id in user_data:
        user_data[user_id] = {
            "username": user_data[user_id].get("username"),
            "phone": user_data[user_id].get("phone")
        }

def show_review(chat_id, user_id, message_id):
    review_index = user_data[user_id]["review_index"]
    total_reviews = len(TUTOR_REVIEWS)
    photo_url = TUTOR_REVIEWS[review_index]

    # Текст для первой картинки
    if review_index == 0:
        caption = (
            "👋🏻 Привет, меня зовут Дмитрий.\n\n"
            "За последние 6 лет я выпустил более 100 учеников и 80% из них набрали более 76 баллов на ЕГЭ.\n\n"
            "P.S: Чтобы почитать отзывы — жми на кнопку «Далее»!"
        )
    else:
        caption = None  # Для остальных отзывов текст не нужен, только изображение

    markup = InlineKeyboardMarkup()

    # Первая строка: Навигационные кнопки
    nav_buttons = []
    if review_index > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data="review_prev"))
    if review_index < total_reviews - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data="review_next"))
    if nav_buttons:
        markup.row(*nav_buttons)

    # Вторая строка: Оставить заявку
    markup.row(InlineKeyboardButton("📩 Оставить заявку", callback_data="tutor_request"))

    # Третья строка: Назад (в "Занятие с репетитором")
    markup.row(InlineKeyboardButton("↩️ Назад", callback_data="tutor_call"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo_url, caption=caption if caption else ""),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка в show_review: {e}")
# ================== Метод карточек ==================
def init_cards_db():
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        # Проверяем, существует ли таблица cards, и создаём её, если нет
        cursor.execute("DROP TABLE IF EXISTS cards")
        cursor.execute("""
            CREATE TABLE cards (
                id INTEGER PRIMARY KEY,
                category TEXT,
                question_image TEXT,
                answer_image TEXT
            )
        """)
        print("✅ Таблица 'cards' создана или пересоздана.")

        # Проверяем, существует ли таблица user_groups, и создаём её, если нет
        cursor.execute("DROP TABLE IF EXISTS user_groups")
        cursor.execute("""
            CREATE TABLE user_groups (
                user_id INTEGER,
                group_name TEXT,
                themes TEXT,
                PRIMARY KEY (user_id, group_name)
            )
        """)
        print("✅ Таблица 'user_groups' создана или пересоздана.")
        conn.commit()
    except sqlite3.Error as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_card(id, category, question_image, answer_image):
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cards (id, category, question_image, answer_image)
            VALUES (?, ?, ?, ?)
        """, (id, category, question_image, answer_image))
        conn.commit()
        print(
            f"✅ Карточка с ID {id} добавлена: id={id}, category={category}, question={question_image}, answer={answer_image}")
    except sqlite3.IntegrityError:
        print(f"❌ Ошибка: ID {id} уже занят!")
    except sqlite3.Error as e:
        print(f"❌ Ошибка при добавлении карточки: {e}")
    finally:
        conn.close()


def delete_card(card_id):
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Карточка с ID {card_id} удалена!")
            return True
        else:
            print(f"❌ Карточка с ID {card_id} не найдена!")
            return False
    except sqlite3.Error as e:
        print(f"❌ Ошибка при удалении карточки: {e}")
        return False
    finally:
        conn.close()


def clear_cards_db():
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cards")
        cursor.execute("DELETE FROM user_groups")
        conn.commit()
        print("✅ Все карточки и группы удалены из базы данных!")
    except sqlite3.Error as e:
        print(f"❌ Ошибка при очистке базы данных: {e}")
    finally:
        conn.close()


def is_image_accessible(url):
    if not url or url == "None":
        return False
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.head(url, headers=headers, timeout=5)
        return response.status_code == 200 and 'image' in response.headers.get('Content-Type', '').lower()
    except Exception as e:
        print(f"Ошибка проверки ссылки {url}: {e}")
        return False


def view_all_data():
    conn = sqlite3.connect("cards.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards")
    cards_data = cursor.fetchall()
    if not cards_data:
        print("📭 Таблица 'cards' пустая!")
    else:
        print("📊 Данные из таблицы 'cards':")
        for row in cards_data:
            print(row)

    cursor.execute("SELECT * FROM user_groups")
    groups_data = cursor.fetchall()
    if not groups_data:
        print("📭 Таблица 'user_groups' пустая!")
    else:
        print("📊 Данные из таблицы 'user_groups':")
        for row in groups_data:
            print(row)
    conn.close()


def get_cards(category=None, shuffle=False):
    conn = sqlite3.connect('cards.db', check_same_thread=False)
    cursor = conn.cursor()

    if isinstance(category, list):
        placeholders = ','.join('?' for _ in category)
        query = f"SELECT * FROM cards WHERE category IN ({placeholders})"
        params = category
    else:
        query = "SELECT * FROM cards WHERE category = ?"
        params = [category]

    if shuffle:
        query += " ORDER BY RANDOM()"

    try:
        cursor.execute(query, params)
        cards = cursor.fetchall()
        print(f"Загружено карточек: {len(cards)} для категорий {category}")
        for card in cards:
            print(f"Карточка: ID={card[0]}, category={card[1]}, question={card[2]}, answer={card[3]}")
    except sqlite3.Error as e:
        print(f"Ошибка чтения базы данных: {e}")
        cards = []
    finally:
        conn.close()
    return cards


# Функции для работы с группами в базе данных
def load_card_groups():
    global user_data
    print("Попытка загрузки групп из базы данных")
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, group_name, themes FROM user_groups")
        groups = cursor.fetchall()
        user_data = {}
        for user_id, group_name, themes in groups:
            user_id = str(user_id)  # Преобразуем в строку для единообразия
            if user_id not in user_data:
                user_data[user_id] = {"selected_themes": [], "card_groups": {}}
            # Декодируем строку themes в список
            user_data[user_id]["card_groups"][group_name] = json.loads(themes)
        print(f"✅ Загружены группы: {user_data}")
    except sqlite3.Error as e:
        print(f"⚠️ Ошибка загрузки групп из базы данных: {e}")
        user_data = {}
    finally:
        conn.close()
    print(f"Текущий user_data после загрузки: {user_data}")


def save_card_groups(user_id=None):
    print("Попытка сохранить группы в базу данных")
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        # Удаляем старые записи для данного пользователя, если указан user_id
        if user_id is not None:
            cursor.execute("DELETE FROM user_groups WHERE user_id = ?", (user_id,))
        # Сохраняем новые данные
        for uid, data in user_data.items():
            if "card_groups" in data:
                for group_name, themes in data["card_groups"].items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO user_groups (user_id, group_name, themes)
                        VALUES (?, ?, ?)
                    """, (uid, group_name, json.dumps(themes)))
        conn.commit()
        print(f"✅ Группы сохранены для пользователей: {list(user_data.keys())}")
    except sqlite3.Error as e:
        print(f"⚠️ Ошибка сохранения групп в базу данных: {e}")
        conn.rollback()
    finally:
        conn.close()


# Загружаем группы при старте
load_card_groups()

# Инициализация базы данных и добавление карточек
init_cards_db()
# Алгебра
# Теория вероятностей
add_card(36, "probability", "https://i.imgur.com/H7eEwyK.jpeg", "https://i.imgur.com/b7FRGYL.jpeg")
add_card(37, "probability", "https://i.imgur.com/O4f0beM.jpeg", "https://i.imgur.com/QYMZigc.jpeg")
# ФСУ
add_card(38, "fsu", "https://i.imgur.com/HjiIqPu.jpeg", "https://i.imgur.com/Ata11FV.jpeg")
add_card(39, "fsu", "https://i.imgur.com/fJkHTm0.jpeg", "https://i.imgur.com/3fQrnZo.jpeg")
add_card(40, "fsu", "https://i.imgur.com/peVgQkO.jpeg", "https://i.imgur.com/HdCUo3s.jpeg")
add_card(41, "fsu", "https://i.imgur.com/8AHZw8n.jpeg", "https://i.imgur.com/D9ZcVLd.jpeg")
add_card(42, "fsu", "https://i.imgur.com/aa0Nuw8.jpeg", "https://i.imgur.com/NQnP8pU.jpeg")
# Квадратные уравнения
add_card(43, "quadratic", "https://i.imgur.com/OqY1Pjv.jpeg", "https://i.imgur.com/9hGF0CG.jpeg")
# Степени
add_card(47, "powers", "https://i.imgur.com/SyM1U2Z.jpeg", "https://i.imgur.com/1dXhPyb.jpeg")
add_card(48, "powers", "https://i.imgur.com/WBUhAD3.jpeg", "https://i.imgur.com/gsc25zE.jpeg")
add_card(49, "powers", "https://i.imgur.com/lFjVI60.jpeg", "https://i.imgur.com/OBlZLEd.jpeg")
add_card(50, "powers", "https://i.imgur.com/gpMLq0G.jpeg", "https://i.imgur.com/JbtwsAh.jpeg")
add_card(51, "powers", "https://i.imgur.com/vucgyxZ.jpeg", "https://i.imgur.com/YdOFXpO.jpeg")
add_card(52, "powers", "https://i.imgur.com/gofxbd5.jpeg", "https://i.imgur.com/5wgZtLS.jpeg")
add_card(53, "powers", "https://i.imgur.com/bCN1sGa.jpeg", "https://i.imgur.com/8ze2qT0.jpeg")
add_card(54, "powers", "https://i.imgur.com/Y7Vgs1S.jpeg", "https://i.imgur.com/eueiXJ1.jpeg")
# Корни
add_card(55, "roots", "https://i.imgur.com/k6gnZaw.jpeg", "https://i.imgur.com/eHs0fxg.jpeg")
add_card(56, "roots", "https://i.imgur.com/veIy6fr.jpeg", "https://i.imgur.com/WT4YTQq.jpeg")
add_card(57, "roots", "https://i.imgur.com/4gSEvla.jpeg", "https://i.imgur.com/00YYYYx.jpeg")
add_card(58, "roots", "https://i.imgur.com/biDoYma.jpeg", "https://i.imgur.com/ptpxXfk.jpeg")
add_card(59, "roots", "https://i.imgur.com/oOqDcbo.jpeg", "https://i.imgur.com/eYKlKee.jpeg")
add_card(60, "roots", "https://i.imgur.com/WIHaIDY.jpeg", "https://i.imgur.com/shijFSJ.jpeg")
# Тригонометрические определения
add_card(61, "trigonometrydefinitions", "https://i.imgur.com/OFpwGwD.jpeg", "https://i.imgur.com/7EpztRr.jpeg")
add_card(62, "trigonometrydefinitions", "https://i.imgur.com/p3U6Gyz.jpeg", "https://i.imgur.com/G2OaBV2.jpeg")
add_card(63, "trigonometrydefinitions", "https://i.imgur.com/Nky6XbH.jpeg", "https://i.imgur.com/gVMOZmH.jpeg")
add_card(64, "trigonometrydefinitions", "https://i.imgur.com/Bt0v1aE.jpeg", "https://i.imgur.com/8lW2duu.jpeg")
# Тригонометрические формулы
add_card(65, "trigonometryformulas", "https://i.imgur.com/vp3bPCp.jpeg", "https://i.imgur.com/sbcjT0L.jpeg")
add_card(66, "trigonometryformulas", "https://i.imgur.com/ssZT02P.png", "https://i.imgur.com/4wHR786.png")
add_card(67, "trigonometryformulas", "https://i.imgur.com/DHZSqmz.jpeg", "https://i.imgur.com/ylniISM.jpeg")
add_card(68, "trigonometryformulas", "https://i.imgur.com/GMClooA.png", "https://i.imgur.com/T1Sg075.png")
add_card(69, "trigonometryformulas", "https://i.imgur.com/LukvGDS.jpeg", "https://i.imgur.com/0QHpL5Z.png")
add_card(70, "trigonometryformulas", "https://i.imgur.com/RRkX3jC.jpeg", "https://i.imgur.com/5BAUlrP.png")
add_card(71, "trigonometryformulas", "https://i.imgur.com/hq2SQVk.jpeg", "https://i.imgur.com/koilgLa.jpeg")
add_card(72, "trigonometryformulas", "https://i.imgur.com/TzqU1UF.jpeg", "https://i.imgur.com/6pSFtF1.jpeg")
add_card(73, "trigonometryformulas", "https://i.imgur.com/g7ODfI7.jpeg", "https://i.imgur.com/EVYr47A.jpeg")
add_card(74, "trigonometryformulas", "https://i.imgur.com/e5bZRIi.jpeg", "https://i.imgur.com/xI4HZdR.jpeg")
add_card(75, "trigonometryformulas", "https://i.imgur.com/1lPYHhD.jpeg", "https://i.imgur.com/u7FFyC2.jpeg")
add_card(76, "trigonometryformulas", "https://i.imgur.com/OvyYJN3.jpeg", "https://i.imgur.com/vsCu8mw.jpeg")
# Логарифмы
add_card(77, "logarithms", "https://i.imgur.com/KdSLggi.jpeg", "https://i.imgur.com/e13xn5s.jpeg")
add_card(78, "logarithms", "https://i.imgur.com/tvNTnRw.jpeg", "https://i.imgur.com/dKSsia2.jpeg")
add_card(79, "logarithms", "https://i.imgur.com/vYOHJYx.jpeg", "https://i.imgur.com/SmarEaL.jpeg")
add_card(80, "logarithms", "https://i.imgur.com/Hpe9ceu.jpeg", "https://i.imgur.com/EEWMyGk.jpeg")
add_card(81, "logarithms", "https://i.imgur.com/dT5quyi.jpeg", "https://i.imgur.com/DBfUrja.jpeg")
add_card(82, "logarithms", "https://i.imgur.com/Egf8JQE.jpeg", "https://i.imgur.com/SflknHY.jpeg")
add_card(83, "logarithms", "https://i.imgur.com/LZRD2BS.jpeg", "https://i.imgur.com/mvjvRTf.jpeg")
add_card(84, "logarithms", "https://i.imgur.com/5NVY8sE.jpeg", "https://i.imgur.com/UxSWsp8.jpeg")
add_card(85, "logarithms", "https://i.imgur.com/KSFpIJJ.jpeg", "https://i.imgur.com/xeOWIUh.jpeg")
# Модули
add_card(86, "modules", "https://i.imgur.com/gFVIK86.jpeg", "https://i.imgur.com/Cer9t0c.jpeg")
add_card(87, "modules", "https://i.imgur.com/GkCpuoh.jpeg", "https://i.imgur.com/G4iST7X.jpeg")
add_card(88, "modules", "https://i.imgur.com/Uvw51TH.jpeg", "https://i.imgur.com/B8LQVOI.jpeg")
# Производные
add_card(89, "derivative", "https://i.imgur.com/9Jx0Zj1.jpeg", "https://i.imgur.com/ti38YhM.jpeg")
add_card(90, "derivative", "https://i.imgur.com/sEz4xTM.jpeg", "https://i.imgur.com/NdCSlJr.jpeg")
add_card(91, "derivative", "https://i.imgur.com/E3oQwfy.jpeg", "https://i.imgur.com/PcLyTBU.jpeg")
add_card(92, "derivative", "https://i.imgur.com/jMn3VBh.jpeg", "https://i.imgur.com/BlV5b8t.jpeg")
add_card(93, "derivative", "https://i.imgur.com/4fdzZws.jpeg", "https://i.imgur.com/0T0hleh.jpeg")
# Текстовые задачи
add_card(94, "wordproblem", "https://i.imgur.com/LrpPmiG.jpeg", "https://i.imgur.com/sgTp9NW.jpeg")
add_card(95, "wordproblem", "https://i.imgur.com/o5XKJJf.jpeg", "https://i.imgur.com/b6QuUNz.jpeg")
add_card(96, "wordproblem", "https://i.imgur.com/F7lHOiF.jpeg", "https://i.imgur.com/OjXPfON.jpeg")
add_card(97, "wordproblem", "https://i.imgur.com/S4JPG6e.jpeg", "https://i.imgur.com/PrvwNwf.jpeg")
add_card(98, "wordproblem", "https://i.imgur.com/39VHfc3.jpeg", "https://i.imgur.com/hHucJgd.jpeg")
add_card(99, "wordproblem", "https://i.imgur.com/FKd3CMf.jpeg", "https://i.imgur.com/UlyTZZb.jpeg")
# Функция корня
add_card(113, "rootfunction", "https://i.imgur.com/YhbsBdL.jpeg", "https://i.imgur.com/JInSNDw.jpeg")
# Показательная функция
add_card(114, "exponentialfunction", "https://i.imgur.com/UQHTQeA.jpeg", "https://i.imgur.com/7AyDiHc.jpeg")
add_card(115, "exponentialfunction", "https://i.imgur.com/gP9TPR9.jpeg", "https://i.imgur.com/H9LHpNs.jpeg")
add_card(116, "exponentialfunction", "https://i.imgur.com/CxbOGCV.jpeg", "https://i.imgur.com/IKKqiVN.jpeg")
add_card(117, "exponentialfunction", "https://i.imgur.com/Z01pCtC.jpeg", "https://i.imgur.com/wTjvTwo.jpeg")
add_card(118, "exponentialfunction", "https://i.imgur.com/1c3ZRTp.jpeg", "https://i.imgur.com/aAk9Ytf.jpeg")
# Логарифмическая функция
add_card(119, "logarithmicfunction", "https://i.imgur.com/sHrW0Lr.jpeg", "https://i.imgur.com/FDicEwE.jpeg")
add_card(120, "logarithmicfunction", "https://i.imgur.com/jGWCsfv.jpeg", "https://i.imgur.com/HRksM4N.jpeg")
add_card(121, "logarithmicfunction", "https://i.imgur.com/AGeMvm9.jpeg", "https://i.imgur.com/F4DDsrf.jpeg")
add_card(122, "logarithmicfunction", "https://i.imgur.com/pfqLBds.jpeg", "https://i.imgur.com/aQsGU1I.jpeg")
add_card(123, "logarithmicfunction", "https://i.imgur.com/U4XtgRX.jpeg", "https://i.imgur.com/z2LiDrG.jpeg")

# Геометрия
# Окружность
add_card(1, "circle", "https://i.imgur.com/7o21EEJ.jpeg", "https://i.imgur.com/W8DPEKb.jpeg")
add_card(2, "circle", "https://i.imgur.com/Y8NAFoa.jpeg", "https://i.imgur.com/nf7Qmd8.jpeg")
add_card(3, "circle", "https://i.imgur.com/Ov8bheW.jpeg", "https://i.imgur.com/VvzOf9o.jpeg")
add_card(4, "circle", "https://i.imgur.com/epdrfUO.jpeg", "https://i.imgur.com/VLbulJj.jpeg")
add_card(5, "circle", "https://i.imgur.com/FfkKQhm.jpeg", "https://i.imgur.com/AStLLBd.jpeg")
# Прямоугольный треугольник
add_card(9, "righttriangle", "https://i.imgur.com/jIDKP3d.jpeg", "https://i.imgur.com/SzWrTBR.jpeg")
add_card(10, "righttriangle", "https://i.imgur.com/CIzUwm5.jpeg", "https://i.imgur.com/gIjHIwp.jpeg")
add_card(11, "righttriangle", "https://i.imgur.com/d3NeDub.jpeg", "https://i.imgur.com/3j1jkwc.jpeg")
# Равносторонний треугольник
add_card(13, "equilateraltriangle", "https://i.imgur.com/GNfw2y2.jpeg", "https://i.imgur.com/GsrZKaF.jpeg")
add_card(14, "equilateraltriangle", "https://i.imgur.com/EAASCzD.jpeg", "https://i.imgur.com/ph8QUI5.jpeg")
add_card(15, "equilateraltriangle", "https://i.imgur.com/c69hlGc.jpeg", "https://i.imgur.com/B5OSyst.jpeg")
add_card(16, "equilateraltriangle", "https://i.imgur.com/i8a9jsn.jpeg", "https://i.imgur.com/Snv45Rz.jpeg")
# Равенство/Подобие
add_card(17, "similarity", "https://i.imgur.com/aTLFn8W.jpeg", "https://i.imgur.com/OF0dN15.jpeg")
add_card(18, "similarity", "https://i.imgur.com/7FfgCk6.jpeg", "https://i.imgur.com/1irQV4N.jpeg")
# Ромб и Трапеция
add_card(19, "rhombustrapezoid", "https://i.imgur.com/NWrWSD8.jpeg", "https://i.imgur.com/bHwFInE.jpeg")
add_card(20, "rhombustrapezoid", "https://i.imgur.com/w3ys1my.jpeg", "https://i.imgur.com/2s2D3xG.jpeg")
add_card(21, "rhombustrapezoid", "https://i.imgur.com/P2Xx8S2.jpeg", "https://i.imgur.com/AygQpCv.jpeg")
# Равносторонний шестиугольник
add_card(22, "hexagon", "https://i.imgur.com/hdiWXJO.jpeg", "https://i.imgur.com/ums0XaV.jpeg")
add_card(23, "hexagon", "https://i.imgur.com/GqiEjSc.jpeg", "https://i.imgur.com/ddZpzTf.jpeg")
add_card(24, "hexagon", "https://i.imgur.com/dniTMEc.jpeg", "https://i.imgur.com/jMZvTo2.jpeg")
add_card(25, "hexagon", "https://i.imgur.com/MNZXkLs.jpeg", "https://i.imgur.com/kTi7XYA.jpeg")
# Треугольник
add_card(26, "triangle", "https://i.imgur.com/3mzOeTW.jpeg", "https://i.imgur.com/lYrtISE.jpeg")
add_card(27, "triangle", "https://i.imgur.com/fwg4sTm.jpeg", "https://i.imgur.com/804kiIR.jpeg")
add_card(28, "triangle", "https://i.imgur.com/Ws9CdLG.jpeg", "https://i.imgur.com/mPOyrJx.jpeg")
add_card(29, "triangle", "https://i.imgur.com/ZhcjU8E.jpeg", "https://i.imgur.com/i6Rp4I7.jpeg")
add_card(30, "triangle", "https://i.imgur.com/rJ1kBoa.jpeg", "https://i.imgur.com/7UrsY2h.jpeg")
add_card(31, "triangle", "https://i.imgur.com/OhtEsap.jpeg", "https://i.imgur.com/Mnj31xP.jpeg")
add_card(32, "triangle", "https://i.imgur.com/GZA4J4T.jpeg", "https://i.imgur.com/13rIhlL.jpeg")
# Вектор
add_card(33, "vector", "https://i.imgur.com/CmZoeHy.jpeg", "https://i.imgur.com/jV8irGk.jpeg")
add_card(34, "vector", "https://i.imgur.com/6ao81ll.jpeg", "https://i.imgur.com/Ek9XFTi.jpeg")
add_card(35, "vector", "https://i.imgur.com/amkZPOX.jpeg", "https://i.imgur.com/NA5h4Zw.jpeg")
# Стереометрия
add_card(140, "stereometry", "https://i.imgur.com/nnjf5xb.jpeg", "https://i.imgur.com/yWw7DV5.jpeg")
add_card(141, "stereometry", "https://i.imgur.com/QmkkMuR.jpeg", "https://i.imgur.com/TIEz29u.jpeg")
add_card(142, "stereometry", "https://i.imgur.com/J0OIBvv.jpeg", "https://i.imgur.com/A4VHCMr.jpeg")
add_card(143, "stereometry", "https://i.imgur.com/47z7amI.jpeg", "https://i.imgur.com/US1mk6X.jpeg")
add_card(144, "stereometry", "https://i.imgur.com/L1Vs1qs.jpeg", "https://i.imgur.com/8AAVjUb.jpeg")
add_card(145, "stereometry", "https://i.imgur.com/wGfYadc.jpeg", "https://i.imgur.com/yCIvqcF.jpeg")
add_card(146, "stereometry", "https://i.imgur.com/hFqD8Rp.jpeg", "https://i.imgur.com/e5CjWdd.jpeg")
# Прямая
add_card(100, "direct", "https://i.imgur.com/PI1wfN3.jpeg", "https://i.imgur.com/AREIHxM.png")
add_card(101, "direct", "https://i.imgur.com/RfuQeQI.jpeg", "https://i.imgur.com/dwTKc3Y.jpeg")
# Парабола
add_card(102, "parabola", "https://i.imgur.com/y8uF2Hd.jpeg", "https://i.imgur.com/hP6NPCE.jpeg")
add_card(103, "parabola", "https://i.imgur.com/d7FejpK.jpeg", "https://i.imgur.com/0wfF32F.jpeg")
add_card(104, "parabola", "https://i.imgur.com/ijiIR7x.jpeg", "https://i.imgur.com/87lW0Nu.jpeg")
add_card(105, "parabola", "https://i.imgur.com/UZFRTMk.jpeg", "https://i.imgur.com/5itVKZd.jpeg")
add_card(106, "parabola", "https://i.imgur.com/DPcfVM9.jpeg", "https://i.imgur.com/dUv8RmI.jpeg")
add_card(107, "parabola", "https://i.imgur.com/QZAXdvA.jpeg", "https://i.imgur.com/nl4gWAd.jpeg")
# Гипербола
add_card(108, "hyperbola", "https://i.imgur.com/7fv1OFz.jpeg", "https://i.imgur.com/TUhkYne.jpeg")
add_card(109, "hyperbola", "https://i.imgur.com/TAKDnII.jpeg", "https://i.imgur.com/GCoPwfw.jpeg")
add_card(110, "hyperbola", "https://i.imgur.com/L4XrHuC.jpeg", "https://i.imgur.com/lfgKtwb.jpeg")
add_card(111, "hyperbola", "https://i.imgur.com/0hpkGYL.jpeg", "https://i.imgur.com/oLvrrU8.jpeg")
add_card(112, "hyperbola", "https://i.imgur.com/EXSjtks.jpeg", "https://i.imgur.com/m1RR74f.jpeg")


@bot.callback_query_handler(func=lambda call: call.data == "cards_method_call" or call.data == "cards_method_back")
def return_to_cards_menu(call):
    text = ("✨ Метод карточек ✨\n\n"
            "📘 Запоминайте знания с карточками — просто и эффективно.\n"
            "➡️ Выберите действие:")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать карточки", callback_data="select_cards"))
    user_id = str(call.from_user.id)  # Убедимся, что user_id — строка
    print(f"Проверка групп для пользователя {user_id}: {user_data.get(user_id, {}).get('card_groups', {})}")
    if user_id in user_data and "card_groups" in user_data[user_id]:
        print(f"Найдены группы для пользователя {user_id}: {user_data[user_id]['card_groups'].keys()}")
        for group_name in user_data[user_id]["card_groups"]:
            print(f"Добавляем кнопку для группы: {group_name}")
            markup.add(
                InlineKeyboardButton(group_name, callback_data=f"select_group_{group_name}"),
                InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_{group_name}")
            )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo_cards, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню карточек: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "select_cards")
def select_cards_menu(call):
    text = "Выберите раздел для выбора тем карточек:"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Алгебра", callback_data="select_algebra"),
        InlineKeyboardButton("Геометрия", callback_data="select_geometry")
    )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования начального меню выбора тем: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "select_algebra")
def select_algebra_menu(call):
    text = "Выберите темы для карточек из раздела Алгебра (можно выбрать несколько):"
    markup = InlineKeyboardMarkup(row_width=2)

    user_id = str(call.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {"selected_themes": [], "card_groups": {}}
    elif "selected_themes" not in user_data[user_id]:
        user_data[user_id]["selected_themes"] = []
    elif "card_groups" not in user_data[user_id]:
        user_data[user_id]["card_groups"] = {}

    selected_themes = user_data[user_id]["selected_themes"]

    for theme_name, theme_code in ALGEBRA_THEMES:
        prefix = "✅ " if theme_code in selected_themes else ""
        callback = f"toggle_theme_{theme_code}"
        print(f"Формируем кнопку: {theme_name}, callback_data={callback}")
        markup.add(InlineKeyboardButton(f"{prefix}{theme_name}", callback_data=callback))

    markup.add(InlineKeyboardButton("☑️ Готово", callback_data="finish_selection"))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="select_cards"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню алгебры: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "select_geometry")
def select_geometry_menu(call):
    text = "Выберите темы для карточек из раздела Геометрия (можно выбрать несколько):"
    markup = InlineKeyboardMarkup(row_width=2)

    user_id = str(call.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {"selected_themes": [], "card_groups": {}}
    elif "selected_themes" not in user_data[user_id]:
        user_data[user_id]["selected_themes"] = []
    elif "card_groups" not in user_data[user_id]:
        user_data[user_id]["card_groups"] = {}

    selected_themes = user_data[user_id]["selected_themes"]

    for theme_name, theme_code in GEOMETRY_THEMES:
        prefix = "✅ " if theme_code in selected_themes else ""
        callback = f"toggle_theme_{theme_code}"
        print(f"Формируем кнопку: {theme_name}, callback_data={callback}")
        markup.add(InlineKeyboardButton(f"{prefix}{theme_name}", callback_data=callback))

    markup.add(InlineKeyboardButton("☑️ Готово", callback_data="finish_selection"))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="select_cards"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню геометрии: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_theme_"))
def toggle_theme(call):
    theme_code = call.data.split("_")[2]
    user_id = str(call.from_user.id)

    print(f"Обработка toggle_theme: theme_code={theme_code}")

    if theme_code in user_data[user_id]["selected_themes"]:
        user_data[user_id]["selected_themes"].remove(theme_code)
        print(f"Тема {theme_code} снята с выбора")
    else:
        user_data[user_id]["selected_themes"].append(theme_code)
        print(f"Тема {theme_code} выбрана")

    if theme_code in ALGEBRA_CODES:
        print(f"Тема {theme_code} относится к алгебре")
        select_algebra_menu(call)
    elif theme_code in GEOMETRY_CODES:
        print(f"Тема {theme_code} относится к геометрии")
        select_geometry_menu(call)
    else:
        print(f"Ошибка: тема {theme_code} не найдена в списках ALGEBRA_CODES или GEOMETRY_CODES")
        text = "Ошибка: неизвестная тема. Выберите раздел заново:"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Алгебра", callback_data="select_algebra"),
            InlineKeyboardButton("Геометрия", callback_data="select_geometry")
        )
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при неизвестной теме: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "finish_selection")
def finish_selection(call):
    user_id = str(call.from_user.id)
    selected_themes = user_data.get(user_id, {}).get("selected_themes", [])

    if not selected_themes:
        bot.answer_callback_query(call.id, "Выберите хотя бы одну тему!", show_alert=True)
        return

    text = "📝 Введите название для вашей группы карточек:"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="select_cards"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования ввода названия группы: {e}")

    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_group_name, user_id,
                                              call.message.message_id)


def process_group_name(message, user_id, original_message_id):
    group_name = message.text.strip()
    if not group_name:
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, "Название не может быть пустым! Попробуйте снова."),
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="select_cards"))
            )
            bot.register_next_step_handler_by_chat_id(message.chat.id, process_group_name, user_id, original_message_id)
        except Exception as e:
            print(f"Ошибка редактирования при пустом названии: {e}")
        return

    if user_id not in user_data:
        user_data[user_id] = {"selected_themes": [], "card_groups": {}}
    elif "card_groups" not in user_data[user_id]:
        user_data[user_id]["card_groups"] = {}

    user_data[user_id]["card_groups"][group_name] = user_data[user_id]["selected_themes"].copy()
    user_data[user_id]["selected_themes"] = []

    save_card_groups(user_id)  # Сохраняем группы для конкретного пользователя

    text = ("📘 Метод карточек\n\n"
            "Это способ запоминания информации с помощью небольших карточек, на которых записаны вопросы с одной стороны и ответы с другой.\n"
            "Выберите действие:")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать карточки", callback_data="select_cards"))
    if "card_groups" in user_data[user_id]:
        for name in user_data[user_id]["card_groups"]:
            print(f"Добавляем кнопку для группы в меню: {name}")
            markup.add(
                InlineKeyboardButton(name, callback_data=f"select_group_{name}"),
                InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_{name}")
            )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))

    try:
        bot.delete_message(message.chat.id, message.message_id)
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=message.chat.id,
            message_id=original_message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню после ввода названия группы: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_"))
def confirm_delete_group(call):
    group_name = call.data.split("_", 2)[2]
    user_id = str(call.from_user.id)

    text = f"Вы точно хотите удалить группу '{group_name}'?"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Да", callback_data=f"delete_yes_{group_name}"),
        InlineKeyboardButton("Нет", callback_data=f"delete_no_{group_name}")
    )

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования подтверждения удаления группы: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_yes_"))
def delete_group_yes(call):
    group_name = call.data.split("_", 2)[2]
    user_id = str(call.from_user.id)

    if user_id in user_data and "card_groups" in user_data[user_id] and group_name in user_data[user_id]["card_groups"]:
        del user_data[user_id]["card_groups"][group_name]
        save_card_groups(user_id)  # Сохраняем обновлённые группы для конкретного пользователя
        bot.answer_callback_query(call.id, f"Группа '{group_name}' удалена!", show_alert=True)

    text = ("📘 Метод карточек\n\n"
            "Это способ запоминания информации с помощью небольших карточек, на которых записаны вопросы с одной стороны и ответы с другой.\n"
            "Выберите действие:")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать карточки", callback_data="select_cards"))
    if user_id in user_data and "card_groups" in user_data[user_id]:
        for name in user_data[user_id]["card_groups"]:
            print(f"Добавляем кнопку для группы в меню после удаления: {name}")
            markup.add(
                InlineKeyboardButton(name, callback_data=f"select_group_{name}"),
                InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_{name}")
            )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню после подтверждения удаления группы: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_no_"))
def delete_group_no(call):
    group_name = call.data.split("_", 2)[2]
    user_id = str(call.from_user.id)

    text = ("📘 Метод карточек\n\n"
            "Это способ запоминания информации с помощью небольших карточек, на которых записаны вопросы с одной стороны и ответы с другой.\n"
            "Выберите действие:")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать карточки", callback_data="select_cards"))
    if user_id in user_data and "card_groups" in user_data[user_id]:
        for name in user_data[user_id]["card_groups"]:
            print(f"Добавляем кнопку для группы в меню после отмены удаления: {name}")
            markup.add(
                InlineKeyboardButton(name, callback_data=f"select_group_{name}"),
                InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_{name}")
            )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню после отмены удаления группы: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("select_group_"))
def select_group(call):
    group_name = call.data.split("_", 2)[2]
    text = f"Вы выбрали группу '{group_name}'. Выберите порядок выполнения:"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔢 Подряд", callback_data=f"order_sequential_group_{group_name}"),
        InlineKeyboardButton("🔁 Вперемежку", callback_data=f"order_mixed_group_{group_name}")
    )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования выбора порядка: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_group_order(call):
    data = call.data.split("_")
    order_type = data[1]
    group_name = "_".join(data[3:])
    user_id = str(call.from_user.id)

    if user_id not in user_data or "card_groups" not in user_data[user_id] or group_name not in user_data[user_id][
        "card_groups"]:
        text = "Ошибка! Группа не найдена. Попробуйте создать новую группу."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при отсутствии группы: {e}")
        return

    shuffle = (order_type == "mixed")
    categories = user_data[user_id]["card_groups"][group_name]
    cards = get_cards(category=categories, shuffle=shuffle)

    if not cards:
        text = "Ошибка! Карточки не найдены для выбранных тем."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при отсутствии карточек: {e}")
        return

    user_data[user_id] = {
        "cards": cards,
        "current_index": 0,
        "wrong_cards": [],
        "last_message_id": call.message.message_id,
        "card_groups": user_data[user_id].get("card_groups", {})
    }
    send_card(call.message.chat.id)


def send_card(chat_id, message_id=None):
    session = user_data.get(str(chat_id))
    if not session:
        text = "Ошибка! Попробуйте начать заново."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=session["last_message_id"] if message_id is None and session else message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при отсутствии сессии: {e}")
        return

    cards = session["cards"]
    current_index = session["current_index"]

    if current_index >= len(cards):
        show_repeat_menu(chat_id)
        return

    card = cards[current_index]
    question_image = card[2]

    if not is_image_accessible(question_image):
        print(f"Изображение недоступно: {question_image} (ID {card[0]})")
        text = f"Изображение для карточки (ID {card[0]}) недоступно. Пропускаем."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=session["last_message_id"],
                reply_markup=markup
            )
            session["current_index"] += 1
            send_card(chat_id)
        except Exception as e:
            print(f"Ошибка редактирования при недоступном изображении: {e}")
        return

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("❕ Ответил", callback_data=f"answer:{card[0]}"),
        InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back")
    )
    text = f"Вспомни формулу (карточка {current_index + 1} из {len(cards)}):"

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(question_image, text),
            chat_id=chat_id,
            message_id=session["last_message_id"],
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования карточки (ID {card[0]}): {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("answer"))
def process_answer(call):
    chat_id = call.message.chat.id
    session = user_data.get(str(chat_id))
    if not session:
        return

    _, card_id = call.data.split(":")
    card = session["cards"][session["current_index"]]
    answer_image = card[3]

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Верно", callback_data=f"correct:{card[0]}"),
        InlineKeyboardButton("❌ Неверно", callback_data=f"wrong:{card[0]}")
    )
    markup.add(InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back"))
    text = "Верно ли ты вспомнил?"

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(answer_image, text),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования ответа: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("correct"))
def process_correct(call):
    chat_id = call.message.chat.id
    session = user_data.get(str(chat_id))
    if session:
        session["current_index"] += 1
        send_card(chat_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("wrong"))
def process_wrong(call):
    chat_id = call.message.chat.id
    session = user_data.get(str(chat_id))
    if session:
        session["wrong_cards"].append(session["cards"][session["current_index"]])
        session["current_index"] += 1
        send_card(chat_id)


def show_repeat_menu(chat_id):
    session = user_data.get(str(chat_id))
    if not session:
        return

    if session["wrong_cards"]:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Повторить неверные", callback_data="repeat_wrong"),
            InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back")
        )
        text = "Хочешь повторить неправильные карточки?"
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back"))
        text = "Ошибок не было или нет карточек для повторения."

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=chat_id,
            message_id=session["last_message_id"],
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню повторения: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "repeat_wrong")
def repeat_wrong(call):
    chat_id = call.message.chat.id
    session = user_data.get(str(chat_id))
    if session and session["wrong_cards"]:
        session["cards"] = session["wrong_cards"].copy()
        session["current_index"] = 0
        session["wrong_cards"] = []
        send_card(chat_id)
    else:
        text = "Ошибок не было или нет карточек для повторения."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при отсутствии неверных карточек: {e}")


# ================== ТАЙМЕРЫ ==================
logging.basicConfig(level=logging.INFO)
user_timer_data = {}
active_timers = {}
timer_conn = sqlite3.connect('timers.db', check_same_thread=False)
timer_cursor = timer_conn.cursor()


def init_timer_db():
    # Проверяем и создаём таблицу timers с учётом возможного отсутствия старых или новых полей
    timer_cursor.execute('''
        CREATE TABLE IF NOT EXISTS timers (
            timer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            is_running BOOLEAN,
            is_paused BOOLEAN,
            start_time INTEGER,
            pause_time INTEGER,
            accumulated_time INTEGER DEFAULT 0
        )''')

    # Проверяем, существуют ли необходимые столбцы (если нет — добавляем)
    timer_cursor.execute('PRAGMA table_info(timers)')
    columns = {col[1] for col in timer_cursor.fetchall()}
    if 'start_time' not in columns:
        timer_cursor.execute('ALTER TABLE timers ADD COLUMN start_time INTEGER')
        timer_conn.commit()
        logging.info("Столбец start_time добавлен в таблицу timers")
    if 'pause_time' not in columns:
        timer_cursor.execute('ALTER TABLE timers ADD COLUMN pause_time INTEGER')
        timer_conn.commit()
        logging.info("Столбец pause_time добавлен в таблицу timers")
    if 'accumulated_time' not in columns:
        timer_cursor.execute('ALTER TABLE timers ADD COLUMN accumulated_time INTEGER DEFAULT 0')
        timer_conn.commit()
        logging.info("Столбец accumulated_time добавлен в таблицу timers")

    timer_cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            timer_id INTEGER,
            date TEXT,
            total_time INTEGER,
            PRIMARY KEY (timer_id, date)
        )''')
    timer_conn.commit()
    print("✅ Таблицы таймеров созданы или уже существуют!")


init_timer_db()


def get_timer_name(timer_id):
    with timer_conn:
        timer_cursor.execute("SELECT name FROM timers WHERE timer_id = ?", (timer_id,))
        result = timer_cursor.fetchone()
        return result[0] if result else None


def get_current_time(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute(
                'SELECT start_time, pause_time, is_running, is_paused, accumulated_time FROM timers WHERE timer_id = ?',
                (timer_id,))
            timer_data = cursor.fetchone()

            if not timer_data:
                logging.debug(f"Таймер {timer_id} не найден")
                return 0  # Возвращаем 0 в секундах

            start_time = timer_data[0] or 0
            pause_time = timer_data[1] or 0
            is_running = timer_data[2]
            is_paused = timer_data[3]
            accumulated_time = timer_data[4] or 0
            current_time = int(time.time())

            logging.debug(
                f"Таймер {timer_id}: start_time={start_time}, pause_time={pause_time}, is_running={is_running}, is_paused={is_paused}, accumulated_time={accumulated_time}, current_time={current_time}")

            if not is_running and not is_paused:
                logging.debug(
                    f"Таймер {timer_id} остановлен, возвращаем accumulated_time: {accumulated_time} сек для статистики")
                return accumulated_time  # Возвращаем accumulated_time для статистики при остановке
            elif is_paused:
                logging.debug(f"Таймер {timer_id} на паузе, возвращаем accumulated_time: {accumulated_time} сек")
                return accumulated_time  # Время на момент паузы
            else:
                elapsed = current_time - start_time if start_time else 0
                total_time = accumulated_time + elapsed
                logging.debug(
                    f"Таймер {timer_id} запущен, общее время: {total_time} сек (accumulated={accumulated_time}, elapsed={elapsed})")
                return total_time  # Общее время (накопленное + текущая сессия)
    except Exception as e:
        logging.error(f"Ошибка при получении текущего времени таймера {timer_id}: {e}")
        return 0


def format_timedelta_stats(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"  # Формат "ЧЧ:ММ:СС" для кнопок и статистики


def get_stats_time(timer_id, period):
    now = datetime.now()
    date_query = ""
    params = ()

    if period == 'day':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        date_query = "date = ?"
        params = (start_date.strftime('%Y-%m-%d'),)
    elif period == 'week':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_query = "date >= ?"
        params = (start_date.strftime('%Y-%m-%d'),)
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        date_query = "date >= ?"
        params = (start_date.strftime('%Y-%m-%d'),)
    elif period == 'all':
        date_query = "1=1"

    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            query = f'SELECT SUM(total_time) FROM stats WHERE timer_id = ? AND {date_query}'
            cursor.execute(query, (timer_id, *params))
            stats_total_seconds = cursor.fetchone()[0] or 0
            logging.debug(f"Статистика для таймера {timer_id}, период {period}: {stats_total_seconds} сек")
            return stats_total_seconds  # Возвращаем секунды, а не timedelta
    except Exception as e:
        logging.error(f"Ошибка при получении статистики для таймера {timer_id}, период {period}: {e}")
        return 0


def show_timer_screen_1(call, timer_id, name):
    # Кнопка с временем уже убрана, оставлены только кнопки управления
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("▶️ Запустить", callback_data=f"launch_timer_{timer_id}"),
        InlineKeyboardButton("❌ Удалить", callback_data=f"delete_timer_{timer_id}")
    )
    markup.row(InlineKeyboardButton("📊 Статистика", callback_data=f"stats_menu_{timer_id}"))
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data="timer_main"))

    caption = f"⏳ Таймер: {name}\n\n⏹ Остановлен"
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=caption),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении экрана таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении экрана таймера {timer_id}: {e2}")


def show_timer_screen_2(call, timer_id, name):
    current_time = get_current_time(timer_id)
    time_text = format_timedelta_stats(current_time)
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("⏸ Пауза", callback_data=f"pause_timer_{timer_id}"),
        InlineKeyboardButton("⏹ Остановить", callback_data=f"stop_timer_{timer_id}")
    )
    markup.row(InlineKeyboardButton(time_text, callback_data="none"))  # Кнопка с временем осталась на экране 2

    caption = f"⏳ Таймер: {name}\n\n▶️ Запущен"
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=caption),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении экрана таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении экрана таймера {timer_id}: {e2}")


def show_timer_screen_3(call, timer_id, name):
    current_time = get_current_time(timer_id)
    time_text = format_timedelta_stats(current_time)
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("▶️ Возобновить", callback_data=f"resume_timer_{timer_id}"),
        InlineKeyboardButton("⏹ Остановить", callback_data=f"stop_timer_{timer_id}")
    )
    markup.row(InlineKeyboardButton(time_text, callback_data="none"))  # Кнопка с временем осталась на экране 3

    caption = f"⏳ Таймер: {name}\n\n⏸ На паузе"
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=caption),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении экрана таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении экрана таймера {timer_id}: {e2}")


def show_stats_menu(call, timer_id):
    day_time = get_stats_time(timer_id, 'day')
    week_time = get_stats_time(timer_id, 'week')
    month_time = get_stats_time(timer_id, 'month')
    all_time = get_stats_time(timer_id, 'all')

    day_text = format_timedelta_stats(day_time)
    week_text = format_timedelta_stats(week_time)
    month_text = format_timedelta_stats(month_time)
    all_text = format_timedelta_stats(all_time)

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(f"🗓 День: {day_text}", callback_data=f"none"))
    markup.row(InlineKeyboardButton(f"🗓 Неделя: {week_text}", callback_data=f"none"))
    markup.row(InlineKeyboardButton(f"🗓 Месяц: {month_text}", callback_data=f"none"))
    markup.row(InlineKeyboardButton(f"🗓 За всё время: {all_text}", callback_data=f"none"))
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data=f"return_to_timer_{timer_id}"))  # Оставлено "Назад"

    caption = "Статистика:"
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=caption),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении меню статистики {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении меню статистики {timer_id}: {e2}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("stats_menu_"))
def handle_stats_menu(call):
    timer_id = int(call.data.split("_")[-1])
    show_stats_menu(call, timer_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("return_to_timer_"))
def handle_return_to_timer(call):
    timer_id = int(call.data.split("_")[-1])
    with timer_conn:
        timer_cursor.execute("SELECT is_running, is_paused FROM timers WHERE timer_id = ?", (timer_id,))
        status = timer_cursor.fetchone()
        if status:
            is_running, is_paused = status
            timer_name = get_timer_name(timer_id)
            if not is_running and not is_paused:
                show_timer_screen_1(call, timer_id, timer_name)
            elif is_paused:
                show_timer_screen_3(call, timer_id, timer_name)
            else:
                show_timer_screen_2(call, timer_id, timer_name)


@bot.callback_query_handler(func=lambda call: call.data == "timer_main")
def timer_main_menu(call_or_chat_id, message_id=None):
    if isinstance(call_or_chat_id, types.CallbackQuery):
        call = call_or_chat_id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = call.from_user.id
    else:
        chat_id = call_or_chat_id
        user_id = None

    register_user(user_id)
    markup = InlineKeyboardMarkup()
    timer_cursor.execute('SELECT name FROM timers WHERE user_id = ?', (chat_id,))
    timers = timer_cursor.fetchall()

    for timer in timers:
        markup.add(InlineKeyboardButton(timer[0], callback_data=f"select_timer_{timer[0]}"))

    markup.row(InlineKeyboardButton("Добавить таймер ➕", callback_data="add_timer"))
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))
    text = ("✨ Study Counter✨\n\n"
            "⏳ Настраивайте время для эффективной подготовки.\n"
            "➡️ Выберите действие с таймерами:")
    try:
        bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=InputMediaPhoto(photo_timers, caption=text),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении меню таймеров: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(photo, caption="⏳ Управление таймерами:"),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении меню таймеров: {e2}")


@bot.callback_query_handler(func=lambda call: call.data == "add_timer")
def add_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    user_timer_data[user_id] = {
        "chat_id": call.message.chat.id,
        "message_id": call.message.message_id
    }

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data="timer_main"))

    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption="📝 Введите название для нового таймера:"),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении экрана добавления таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption="📝 Введите название для нового таймера:"),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении экрана добавления таймера: {e2}")

    bot.register_next_step_handler(call.message, process_timer_name, call.from_user.id)


def process_timer_name(message, user_id):
    name = message.text.strip()
    user_data = user_timer_data.get(user_id)
    if not user_data:
        return

    chat_id = user_data["chat_id"]
    message_id = user_data["message_id"]

    try:
        timer_cursor.execute(
            'INSERT INTO timers (user_id, name, is_running, is_paused, start_time, pause_time, accumulated_time) VALUES (?, ?, ?, ?, NULL, NULL, 0)',
            (user_id, name, False, False)
        )
        timer_conn.commit()
        # Очищаем старую статистику для нового таймера, если это новый timer_id
        timer_cursor.execute(
            'DELETE FROM stats WHERE timer_id = (SELECT timer_id FROM timers WHERE user_id = ? AND name = ?)',
            (user_id, name))
        timer_conn.commit()
        logging.info(f"Таймер создан: имя = {name}, user_id = {user_id}")

        bot.delete_message(chat_id, message.message_id)
        timer_main_menu(chat_id, message_id)
    except sqlite3.IntegrityError:
        logging.error(f"Таймер с именем {name} уже существует для другого пользователя, но это разрешено.")
        timer_cursor.execute(
            'INSERT INTO timers (user_id, name, is_running, is_paused, start_time, pause_time, accumulated_time) VALUES (?, ?, ?, ?, NULL, NULL, 0)',
            (user_id, name, False, False)
        )
        timer_conn.commit()
        # Очищаем старую статистику для нового таймера, если это новый timer_id
        timer_cursor.execute(
            'DELETE FROM stats WHERE timer_id = (SELECT timer_id FROM timers WHERE user_id = ? AND name = ?)',
            (user_id, name))
        timer_conn.commit()
        logging.info(f"Таймер создан с дублирующим именем: имя = {name}, user_id = {user_id}")

        bot.delete_message(chat_id, message.message_id)
        timer_main_menu(chat_id, message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("select_timer_"))
def handle_timer_selection(call):
    user_id = call.from_user.id
    register_user(user_id)
    timer_name = call.data.split("_", 2)[2]
    timer_cursor.execute("SELECT timer_id FROM timers WHERE user_id = ? AND name = ?", (call.from_user.id, timer_name))
    timer_data = timer_cursor.fetchone()

    if timer_data:
        timer_id = timer_data[0]
        show_timer_screen_1(call, timer_id, timer_name)
    else:
        try:
            bot.answer_callback_query(call.id, "❌ Таймер не найден", show_alert=False)  # Убрано уведомление
        except Exception as e:
            logging.error(f"Ошибка при уведомлении о таймере: {e}")
            if "ConnectionResetError" in str(e):
                time.sleep(1)
                bot.answer_callback_query(call.id, "❌ Таймер не найден", show_alert=False)  # Убрано уведомление


@bot.callback_query_handler(func=lambda call: call.data.startswith("launch_timer_"))
def handle_launch_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if start_timer(timer_id):
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_2(call, timer_id, timer_name)
                update_thread = Thread(target=update_timer_display,
                                       args=(call.message.chat.id, call.message.message_id, timer_id, timer_name))
                update_thread.daemon = True
                update_thread.start()
                logging.info(f"Поток обновления запущен для таймера {timer_id}")
                # Обновляем статистику при запуске (начальное время 0)
                update_stats(timer_id, 0)
            else:
                pass
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при обработке запуска: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if start_timer(timer_id):
                    timer_name = get_timer_name(timer_id)
                    if timer_name:
                        show_timer_screen_2(call, timer_id, timer_name)
                        update_thread = Thread(target=update_timer_display, args=(
                        call.message.chat.id, call.message.message_id, timer_id, timer_name))
                        update_thread.daemon = True
                        update_thread.start()
                        logging.info(f"Поток обновления запущен после повторной попытки для таймера {timer_id}")
                        update_stats(timer_id, 0)
                    else:
                        pass
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при запуске таймера: {e2}")

def start_timer(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            # Убедимся, что start_time всегда устанавливается корректно
            start_time = int(time.time())
            cursor.execute('''
                UPDATE timers 
                SET is_running = 1, 
                    is_paused = 0,
                    start_time = ?,
                    accumulated_time = 0,
                    pause_time = NULL
                WHERE timer_id = ?''',
                           (start_time, timer_id))
            timer_conn.commit()
            logging.debug(f"Таймер {timer_id} запущен с start_time={start_time}")
        logging.info(f"Таймер {timer_id} успешно запущен, начав с 00:00:00")
        timer_thread = Thread(target=run_timer, args=(timer_id,))
        timer_thread.daemon = True
        timer_thread.start()
        return True
    except Exception as e:
        logging.error(f"Ошибка запуска таймера: {e}")
        return False

def run_timer(timer_id):
    while True:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute('SELECT is_running, is_paused FROM timers WHERE timer_id = ?', (timer_id,))
            status = cursor.fetchone()

            if not status or (not status[0] and not status[1]):
                logging.info(f"Таймер {timer_id} завершил работу")
                break

            time.sleep(1)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pause_timer_"))
def handle_pause_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if pause_timer(timer_id):
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_3(call, timer_id, timer_name)
                # Обновляем статистику, используя текущее время из get_current_time
                current_time = get_current_time(timer_id)
                update_stats(timer_id, current_time)
            else:
                pass
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при паузе таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if pause_timer(timer_id):
                    timer_name = get_timer_name(timer_id)
                    if timer_name:
                        show_timer_screen_3(call, timer_id, timer_name)
                        current_time = get_current_time(timer_id)
                        update_stats(timer_id, current_time)
                    else:
                        pass
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при паузе таймера: {e2}")

def pause_timer(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute('SELECT start_time, accumulated_time, is_paused, is_running FROM timers WHERE timer_id = ?',
                           (timer_id,))
            timer_data = cursor.fetchone()
            if timer_data and timer_data[3] == 1 and timer_data[2] == 0:  # Проверяем, что таймер запущен и не на паузе
                start_time = timer_data[0]
                accumulated_time = timer_data[1] or 0
                current_time = int(time.time())
                elapsed = current_time - start_time if start_time else 0
                new_accumulated_time = accumulated_time + elapsed  # Сохраняем общее время, включая паузу

                cursor.execute('''
                    UPDATE timers 
                    SET is_paused = 1,
                        is_running = 0,
                        pause_time = ?,
                        accumulated_time = ?
                WHERE timer_id = ? AND is_running = 1''',
                               (current_time, new_accumulated_time, timer_id))
                timer_conn.commit()
                logging.debug(
                    f"Таймер {timer_id} поставлен на паузу, accumulated_time={new_accumulated_time}, elapsed={elapsed}")
            else:
                logging.warning(f"Таймер {timer_id} уже на паузе, не запущен или не найден, пропускаем обновление")
            logging.info(f"Таймер {timer_id} поставлен на паузу с временем {new_accumulated_time} секунд")
        return True
    except Exception as e:
        logging.error(f"Ошибка паузы таймера {timer_id}: {e}")
        return False

@bot.callback_query_handler(func=lambda call: call.data.startswith("stop_timer_"))
def handle_stop_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if stop_timer(timer_id):
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_1(call, timer_id, timer_name)
                # Обновляем статистику перед сбросом, используя текущее время из get_current_time
                current_time = get_current_time(timer_id)
                # Если current_time = 0, пытаемся восстановить время, используя accumulated_time + elapsed
                if current_time == 0:
                    with timer_conn:
                        cursor = timer_conn.cursor()
                        cursor.execute('SELECT start_time, accumulated_time FROM timers WHERE timer_id = ?',
                                       (timer_id,))
                        timer_data = cursor.fetchone()
                        if timer_data:
                            start_time = timer_data[0] or 0
                            accumulated_time = timer_data[1] or 0
                            if start_time:
                                current_time = int(time.time()) - start_time + accumulated_time
                                logging.debug(
                                    f"Восстановлено время для таймера {timer_id}: current_time={current_time} (start_time={start_time}, accumulated_time={accumulated_time})")
                            else:
                                # Если start_time отсутствует, используем только accumulated_time
                                current_time = accumulated_time
                                logging.debug(
                                    f"Восстановлено время для таймера {timer_id} из accumulated_time: current_time={current_time}")
                            # Если всё ещё 0, используем elapsed как запасное значение
                            if current_time == 0 and start_time:
                                elapsed = int(time.time()) - start_time
                                current_time = elapsed
                                logging.debug(
                                    f"Восстановлено время для таймера {timer_id} из elapsed: current_time={current_time} (start_time={start_time})")
                # Обновляем статистику, если восстановленное время больше 0
                if current_time > 0:
                    update_stats(timer_id, current_time)
                else:
                    logging.warning(
                        f"Статистика для таймера {timer_id} не обновлена, так как восстановленное время = 0 после всех попыток")
            else:
                pass
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при остановке таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if stop_timer(timer_id):
                    timer_name = get_timer_name(timer_id)
                    if timer_name:
                        show_timer_screen_1(call, timer_id, timer_name)
                        current_time = get_current_time(timer_id)
                        if current_time == 0:
                            with timer_conn:
                                cursor = timer_conn.cursor()
                                cursor.execute('SELECT start_time, accumulated_time FROM timers WHERE timer_id = ?',
                                               (timer_id,))
                                timer_data = cursor.fetchone()
                                if timer_data:
                                    start_time = timer_data[0] or 0
                                    accumulated_time = timer_data[1] or 0
                                    if start_time:
                                        current_time = int(time.time()) - start_time + accumulated_time
                                        logging.debug(
                                            f"Восстановлено время для таймера {timer_id} после повторной попытки: current_time={current_time} (start_time={start_time}, accumulated_time={accumulated_time})")
                                    else:
                                        current_time = accumulated_time
                                        logging.debug(
                                            f"Восстановлено время для таймера {timer_id} из accumulated_time после повторной попытки: current_time={current_time}")
                                    if current_time == 0 and start_time:
                                        elapsed = int(time.time()) - start_time
                                        current_time = elapsed
                                        logging.debug(
                                            f"Восстановлено время для таймера {timer_id} из elapsed после повторной попытки: current_time={current_time} (start_time={start_time})")
                        if current_time > 0:
                            update_stats(timer_id, current_time)
                        else:
                            logging.warning(
                                f"Статистика для таймера {timer_id} не обновлена после повторной попытки, так как восстановленное время = 0")
                    else:
                        pass
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при остановке таймера: {e2}")

def stop_timer(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute('SELECT start_time, accumulated_time FROM timers WHERE timer_id = ?', (timer_id,))
            timer_data = cursor.fetchone()
            if timer_data:
                start_time = timer_data[0] or 0
                accumulated_time = timer_data[1] or 0
                if start_time:
                    current_time = int(time.time())
                    elapsed = current_time - start_time
                    new_accumulated_time = accumulated_time + elapsed  # Общее время для статистики
                    logging.debug(
                        f"Таймер {timer_id} остановлен, accumulated_time={new_accumulated_time}, elapsed={elapsed}")

                    # Обновляем статистику перед сбросом таймера
                    update_stats(timer_id, new_accumulated_time)

                cursor.execute('''
                    UPDATE timers 
                    SET is_running = 0,
                        is_paused = 0,
                        start_time = NULL,
                        pause_time = NULL,
                        accumulated_time = 0  -- Сбрасываем accumulated_time на 0 для отображения 00:00:00
                    WHERE timer_id = ?''',
                               (timer_id,))
                timer_conn.commit()
                logging.debug(
                    f"Таймер {timer_id} остановлен, статистика обновлена с временем {new_accumulated_time} сек")
            else:
                cursor.execute('''
                    UPDATE timers 
                    SET is_running = 0,
                        is_paused = 0,
                        start_time = NULL,
                        pause_time = NULL,
                        accumulated_time = 0  -- Сбрасываем accumulated_time на 0
                    WHERE timer_id = ?''',
                               (timer_id,))
                timer_conn.commit()
        logging.info(f"Таймер {timer_id} остановлен, время на кнопке сброшено на 00:00:00")
        return True
    except Exception as e:
        logging.error(f"Ошибка остановки таймера {timer_id}: {e}")
        return False

@bot.callback_query_handler(func=lambda call: call.data.startswith("resume_timer_"))
def handle_resume_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if resume_timer(timer_id):
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_2(call, timer_id, timer_name)
                update_thread = Thread(target=update_timer_display,
                                       args=(call.message.chat.id, call.message.message_id, timer_id, timer_name))
                update_thread.daemon = True
                update_thread.start()
                logging.info(f"Поток обновления запущен для таймера {timer_id} после возобновления")
                # Обновляем статистику при возобновлении (используем текущее время из get_current_time)
                update_stats(timer_id, get_current_time(timer_id))
            else:
                pass
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при возобновлении таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if resume_timer(timer_id):
                    timer_name = get_timer_name(timer_id)
                    if timer_name:
                        show_timer_screen_2(call, timer_id, timer_name)
                        update_thread = Thread(target=update_timer_display, args=(
                        call.message.chat.id, call.message.message_id, timer_id, timer_name))
                        update_thread.daemon = True
                        update_thread.start()
                        logging.info(f"Поток обновления запущен после повторной попытки для таймера {timer_id}")
                        update_stats(timer_id, get_current_time(timer_id))
                    else:
                        pass
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при возобновлении таймера: {e2}")

def resume_timer(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute('SELECT accumulated_time, is_paused, is_running FROM timers WHERE timer_id = ?', (timer_id,))
            result = cursor.fetchone()
            if result and result[1] == 1 and result[2] == 0:  # Проверяем, что таймер на паузе и не запущен
                accumulated_time = result[0] or 0  # Сохраняем текущее накопленное время

                cursor.execute('''
                    UPDATE timers 
                    SET is_paused = 0,
                        pause_time = NULL,
                        start_time = ?,
                        is_running = 1,
                        accumulated_time = ?  -- Сохраняем накопленное время для продолжения
                    WHERE timer_id = ?''',
                               (int(time.time()), accumulated_time, timer_id))
                timer_conn.commit()
            else:
                logging.warning(f"Таймер {timer_id} не на паузе, запущен или не найден, пропускаем возобновление")
            logging.info(f"Таймер {timer_id} возобновлен, продолжив с {accumulated_time} секунд")
        return True
    except Exception as e:
        logging.error(f"Ошибка возобновления таймера {timer_id}: {e}")
        return False

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_timer_"))
def handle_timer_delete(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        timer_name = get_timer_name(timer_id)
        if not timer_name:
            bot.answer_callback_query(call.id, "❌ Таймер не найден", show_alert=False)  # Убрано уведомление
            return
        show_delete_confirmation(call, timer_id, timer_name)
    except Exception as e:
        logging.error(f"Ошибка при удалении таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                timer_name = get_timer_name(timer_id)
                if not timer_name:
                    bot.answer_callback_query(call.id, "❌ Таймер не найден", show_alert=False)  # Убрано уведомление
                    return
                show_delete_confirmation(call, timer_id, timer_name)
            except Exception as e2:
                logging.error(f"Повторная ошибка при удалении таймера: {e2}")


def show_delete_confirmation(call, timer_id, timer_name):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Да", callback_data=f"confirm_delete_{timer_id}"),
        InlineKeyboardButton("Нет", callback_data=f"cancel_delete_{timer_id}")
    )
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=f"❓ Вы действительно хотите удалить таймер {timer_name}?"),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при отображении подтверждения удаления таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=f"❓ Вы действительно хотите удалить таймер {timer_name}?"),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при отображении подтверждения удаления таймера {timer_id}: {e2}")


def delete_timer(timer_id):
    try:
        timer_cursor.execute('DELETE FROM timers WHERE timer_id = ?', (timer_id,))
        timer_cursor.execute('DELETE FROM stats WHERE timer_id = ?', (timer_id,))
        timer_conn.commit()
        return True
    except Exception as e:
        logging.error(f"Ошибка удаления таймера: {e}")
        return False


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_"))
def handle_confirm_delete(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if delete_timer(timer_id):
            # Убрано уведомление: bot.answer_callback_query(call.id, "🗑 Таймер удалён", show_alert=True)
            timer_main_menu(call)
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при подтверждении удаления таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if delete_timer(timer_id):
                    # Убрано уведомление
                    timer_main_menu(call)
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при подтверждении удаления таймера: {e2}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_delete_"))
def handle_cancel_delete(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        timer_name = get_timer_name(timer_id)
        show_timer_screen_1(call, timer_id, timer_name)
    except Exception as e:
        logging.error(f"Ошибка при отмене удаления таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                timer_name = get_timer_name(timer_id)
                show_timer_screen_1(call, timer_id, timer_name)
            except Exception as e2:
                logging.error(f"Повторная ошибка при отмене удаления таймера: {e2}")


# Функция для автоматической остановки таймера через 3 часа с отправкой нового сообщения
def auto_stop_timer(chat_id, message_id, timer_id, name):
    try:
        stop_timer(timer_id)  # Останавливаем таймер
        # Удаляем предыдущее сообщение с таймером
        bot.delete_message(chat_id, message_id)
        # Отправляем новое сообщение
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 Запустить заново", callback_data=f"restart_timer_{timer_id}"),
            InlineKeyboardButton("◀️ Не запускать", callback_data="main_back_call")
        )
        caption = f"⏳ Таймер: {name}\n\n⏹ Таймер проработал 3 часа!\nПрошло времени: 03:00:00"
        bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=markup
        )
        logging.info(f"Таймер {timer_id} автоматически остановлен через 3 часа, новое сообщение отправлено")
    except Exception as e:
        logging.error(f"Ошибка при автоматической остановке таймера {timer_id}: {e}")
        # В случае ошибки попробуем отправить сообщение без удаления старого
        try:
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔄 Запустить заново", callback_data=f"restart_timer_{timer_id}"),
                InlineKeyboardButton("◀️ Не запускать", callback_data="main_back_call")
            )
            bot.send_message(
                chat_id=chat_id,
                text=f"⏳ Таймер: {name}\n\n⏹ Таймер проработал 3 часа!\nПрошло времени: 03:00:00",
                reply_markup=markup
            )
        except Exception as e2:
            logging.error(f"Ошибка при отправке нового сообщения для таймера {timer_id}: {e2}")


# Обновлённая функция update_timer_display с проверкой на 3 часа
def update_timer_display(chat_id, message_id, timer_id, name):
    local_conn = sqlite3.connect('timers.db', check_same_thread=False)
    last_caption = None
    last_time = None
    try:
        logging.info(f"Запуск потока обновления для таймера {timer_id}")
        while True:
            with local_conn:
                cursor = local_conn.cursor()
                cursor.execute('SELECT is_running, is_paused FROM timers WHERE timer_id = ?', (timer_id,))
                status = cursor.fetchone()

                if not status or (not status[0] and not status[1]):
                    logging.info(f"Таймер {timer_id} завершил работу, завершение потока обновления")
                    break

                is_running, is_paused = status
                current_time = get_current_time(timer_id)

                # Проверка на 3 часа (10800 секунд)
                if current_time >= 10800:  # 3 часа в секундах
                    auto_stop_timer(chat_id, message_id, timer_id, name)
                    break

                time_text = format_timedelta_stats(current_time)
                caption = f"⏳ Таймер: {name}\n\n{'⏸ На паузе' if is_paused else '▶️ Запущен'}"
                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton("▶️ Возобновить" if is_paused else "⏸ Пауза",
                                         callback_data=f"{'resume' if is_paused else 'pause'}_timer_{timer_id}"),
                    InlineKeyboardButton("⏹ Остановить", callback_data=f"stop_timer_{timer_id}")
                )
                markup.row(
                    InlineKeyboardButton(time_text, callback_data="none")
                )

                if caption != last_caption or time_text != last_time:
                    try:
                        bot.edit_message_media(
                            chat_id=chat_id,
                            message_id=message_id,
                            media=InputMediaPhoto(photo, caption=caption),
                            reply_markup=markup
                        )
                        last_caption = caption
                        last_time = time_text
                        logging.debug(f"Обновлён дисплей для таймера {timer_id}: {caption}, Время: {time_text}")
                    except Exception as e:
                        if "message is not modified" not in str(e):
                            logging.error(f"Ошибка при обновлении таймера {timer_id}: {e}")
                            if "ConnectionResetError" in str(e):
                                time.sleep(1)
                                try:
                                    bot.edit_message_media(
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        media=InputMediaPhoto(photo, caption=caption),
                                        reply_markup=markup
                                    )
                                    logging.info(f"Дисплей обновлён после повторной попытки для таймера {timer_id}")
                                except Exception as e2:
                                    logging.error(f"Повторная ошибка при обновлении таймера {timer_id}: {e2}")
                    except telebot.apihelper.ApiTelegramException as api_err:
                        if api_err.error_code == 400 and "canceled by new editMessageMedia request" in str(api_err):
                            logging.warning(f"Пропущена ошибка Telegram API для таймера {timer_id}: {api_err}")
                        else:
                            logging.error(f"Неожиданная ошибка Telegram API для таймера {timer_id}: {api_err}")
                time.sleep(0.5)
            time.sleep(0.5)
    except Exception as e:
        logging.error(f"Критическая ошибка в потоке обновления таймера {timer_id}: {e}")
    finally:
        local_conn.close()
        logging.info(f"Поток обновления для таймера {timer_id} завершён")


# Обработчик для перезапуска таймера
@bot.callback_query_handler(func=lambda call: call.data.startswith("restart_timer_"))
def handle_restart_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if start_timer(timer_id):  # Перезапускаем таймер
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_2(call, timer_id, timer_name)
                update_thread = Thread(target=update_timer_display,
                                       args=(call.message.chat.id, call.message.message_id, timer_id, timer_name))
                update_thread.daemon = True
                update_thread.start()
                logging.info(f"Таймер {timer_id} перезапущен, поток обновления запущен")
                update_stats(timer_id, 0)  # Сбрасываем статистику при перезапуске
            else:
                bot.answer_callback_query(call.id, "❌ Ошибка при перезапуске таймера")
        else:
            bot.answer_callback_query(call.id, "❌ Не удалось перезапустить таймер")
    except Exception as e:
        logging.error(f"Ошибка при перезапуске таймера: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка при перезапуске")


def update_stats(timer_id, current_time):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            current_date = time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
            cursor.execute('SELECT total_time FROM stats WHERE timer_id = ? AND date = ?', (timer_id, current_date))
            existing_time = cursor.fetchone()
            existing_time = existing_time[0] if existing_time else 0

            # Суммируем существующее время с текущим временем
            new_total_time = existing_time + current_time
            logging.debug(
                f"Обновление статистики для таймера {timer_id}: existing_time={existing_time}, current_time={current_time}, new_total_time={new_total_time}")

            if current_time > 0:  # Обновляем только если есть реальное время
                cursor.execute('''
                    INSERT INTO stats (timer_id, date, total_time)
                    VALUES (?, ?, ?)
                    ON CONFLICT(timer_id, date) DO UPDATE SET total_time = ?
                ''', (timer_id, current_date, new_total_time, new_total_time))
                timer_conn.commit()
                logging.info(
                    f"Статистика обновлена: timer_id={timer_id}, date={current_date}, total_time={new_total_time} сек")
            else:
                logging.warning(f"Статистика для таймера {timer_id} не обновлена, так как current_time = 0")
    except Exception as e:
        logging.error(f"Ошибка обновления статистики для таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                with timer_conn:
                    cursor = timer_conn.cursor()
                    current_date = time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
                    cursor.execute('SELECT total_time FROM stats WHERE timer_id = ? AND date = ?',
                                   (timer_id, current_date))
                    existing_time = cursor.fetchone()
                    existing_time = existing_time[0] if existing_time else 0

                    new_total_time = existing_time + current_time
                    logging.debug(
                        f"Повторное обновление статистики для таймера {timer_id}: existing_time={existing_time}, current_time={current_time}, new_total_time={new_total_time}")

                    if current_time > 0:
                        cursor.execute('''
                            INSERT INTO stats (timer_id, date, total_time)
                            VALUES (?, ?, ?)
                            ON CONFLICT(timer_id, date) DO UPDATE SET total_time = ?
                        ''', (timer_id, current_date, new_total_time, new_total_time))
                        timer_conn.commit()
                        logging.info(
                            f"Статистика обновлена после повторной попытки: timer_id={timer_id}, date={current_date}, total_time={new_total_time} сек")
                    else:
                        logging.warning(
                            f"Статистика для таймера {timer_id} не обновлена после повторной попытки, так как current_time = 0")
            except Exception as e2:
                logging.error(f"Повторная ошибка обновления статистики для таймера {timer_id}: {e2}")


def restore_active_timers():
    with timer_conn:
        timer_cursor.execute('SELECT timer_id, name, is_running FROM timers WHERE is_running = 1')
        active_timers_data = timer_cursor.fetchall()
        for timer_id, name, _ in active_timers_data:
            timer_thread = Thread(target=run_timer, args=(timer_id,))
            timer_thread.daemon = True
            timer_thread.start()
            logging.info(f"Восстановлен активный таймер: timer_id={timer_id}, name={name}")


restore_active_timers()

def view_all_data_timers():
    conn = sqlite3.connect("timers.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM timers")
    data = cursor.fetchall()

    if not data:
        print("📭 Таблица пустая!")
    else:
        print("📊 Данные из таблицы 'timers':")
        for row in data:
            print(row)
    conn.close()


def view_all_data_stats():
    conn = sqlite3.connect("timers.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stats")
    data = cursor.fetchall()

    if not data:
        print("📭 Таблица stats пуста!")
    else:
        print("📊 Данные из таблицы 'stats':")
        for row in data:
            print(row)
    conn.close()
view_all_data_timers()
view_all_data_stats()

# ================== Обработчики команд ==================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.username
    user_id = message.from_user.id
    chat_id = message.chat.id
    register_user(user_id, username)

    # Отправляем новое приветственное сообщение
    text = (
        "👋 Добро пожаловать!\n\n"
        "🧠 Я — ваш помощник в подготовке к ЕГЭ по профильной математике.\n"
        "📖 Вместе мы разберём задания и сделаем процесс обучения проще и эффективнее.\n"
        "➡️ Выберите действие:"
    )
    msg = bot.send_photo(
        chat_id=chat_id,
        photo=photo_main,
        caption=text,
        reply_markup=main_screen()
    )
    user_messages[user_id] = msg.message_id  # Сохраняем ID нового сообщения
    logging.info(f"Отправлено приветственное сообщение для {user_id}: {msg.message_id}")

def get_username(user_id):
    try:
        with users_conn:
            users_cursor.execute('SELECT username FROM users WHERE user_id = ?', (user_id,))
            result = users_cursor.fetchone()
            if result and result[0]:
                return f"@{result[0]}"
            else:
                return f"User ID: {user_id}"
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении username для user_id={user_id}: {e}")
        return f"User ID: {user_id}"

# Список ID администраторов
ADMIN_IDS = {1035828828}  # Ваш ID
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # Без str(), так как сравниваем с int в ADMIN_IDS

    # Проверяем, что это администратор
    if user_id not in ADMIN_IDS:
        bot.send_message(chat_id, "Эта команда доступна только администратору.")
        return

    # Получаем статистику
    total_users = get_total_users()
    active_today = get_active_users_today()

    # Формируем текст
    text = f"📊 Общая статистика:\nВсего пользователей: {total_users}\nАктивных сегодня: {active_today}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📋 Заявки", callback_data="stats_requests"))

    # Отправляем сообщение
    bot.send_message(chat_id, text, reply_markup=markup)
    logging.info(f"Статистика отправлена администратору {user_id}: {total_users} пользователей")
# Обновляем callback_query_handler для обработки статистики
@bot.callback_query_handler(func=lambda call: call.data in ["stats_requests", "stats_back"] or call.data.startswith("stats_user_") or call.data.startswith("stats_request_"))
def handle_stats_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id
    data = call.data

    # Проверка на администратора
    if user_id not in ADMIN_IDS:
        bot.edit_message_text(
            "⛔ Доступ к этой команде есть только у администраторов!",
            chat_id=chat_id,
            message_id=message_id
        )
        return

    if data == "stats_requests":
        # Показываем список пользователей с заявками
        try:
            with users_conn:
                users_cursor.execute('''
                    SELECT DISTINCT tr.user_id, u.username
                    FROM tutor_requests tr
                    LEFT JOIN users u ON tr.user_id = u.user_id
                ''')
                users = users_cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при загрузке пользователей с заявками: {e}")
            bot.edit_message_text("Ошибка при загрузке статистики заявок.", chat_id, message_id)
            return

        if not users:
            text = "📋 Заявки на репетитора:\n\nПока нет заявок."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_back"))
        else:
            text = "📋 Заявки на репетитора:\n\nВыберите пользователя:"
            markup = InlineKeyboardMarkup(row_width=1)
            for user in users:
                user_id, username = user
                display_name = f"@{username}" if username else f"User ID: {user_id}"
                markup.add(InlineKeyboardButton(display_name, callback_data=f"stats_user_{user_id}"))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_back"))

        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    elif data.startswith("stats_user_"):
        # Показываем все заявки выбранного пользователя
        selected_user_id = data.split("_")[2]
        try:
            with users_conn:
                users_cursor.execute('''
                    SELECT tr.user_id, tr.name, tr.school_class, tr.test_score, tr.expected_price, tr.timestamp, u.username
                    FROM tutor_requests tr
                    LEFT JOIN users u ON tr.user_id = u.user_id
                    WHERE tr.user_id = ?
                    ORDER BY tr.timestamp DESC
                ''', (selected_user_id,))
                requests = users_cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при загрузке заявок для user_id {selected_user_id}: {e}")
            bot.edit_message_text("Ошибка при загрузке заявок.", chat_id, message_id)
            return

        if not requests:
            text = f"📋 Заявки от {get_display_name(selected_user_id, chat_id)}\n\nЗаявок не найдено."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_requests"))
        else:
            text = f"📋 Заявки от {get_display_name(selected_user_id, chat_id)}\n\nВыберите заявку:"
            markup = InlineKeyboardMarkup(row_width=1)
            for req in requests:
                user_id, _, _, _, _, timestamp, username = req
                display_name = get_display_name(user_id, chat_id)
                markup.add(InlineKeyboardButton(
                    f"{display_name} | {timestamp[:19]}",
                    callback_data=f"stats_request_{user_id}_{timestamp}"
                ))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_requests"))

        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    elif data.startswith("stats_request_"):
        # Просмотр конкретной заявки
        parts = data.split("_")
        req_user_id = parts[2]
        req_timestamp = "_".join(parts[3:])
        try:
            with users_conn:
                users_cursor.execute('''
                    SELECT tr.user_id, tr.name, tr.school_class, tr.test_score, tr.expected_price, tr.timestamp, u.username
                    FROM tutor_requests tr
                    LEFT JOIN users u ON tr.user_id = u.user_id
                    WHERE tr.user_id = ? AND tr.timestamp = ?
                ''', (req_user_id, req_timestamp))
                request = users_cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при загрузке заявки для user_id {req_user_id}: {e}")
            bot.edit_message_text("Ошибка при загрузке данных заявки.", chat_id, message_id)
            return

        if not request:
            text = f"📋 Заявка от User ID: {req_user_id}\n\nЗаявка не найдена."
        else:
            user_id, name, school_class, test_score, expected_price, timestamp, username = request
            display_name = f"@{username}" if username else f"User ID: {user_id}"
            text = (
                f"📋 Заявка от {display_name}\n\n"
                f"👤 Имя: {name}\n"
                f"🏫 Класс: {school_class}\n"
                f"📈 Пробный балл: {test_score}\n"
                f"💰 Ожидаемая цена: {expected_price}\n"
                f"⏰ Дата: {timestamp}"
            )

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"stats_user_{req_user_id}"))

        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    elif data == "stats_back":
        # Возврат к общей статистике
        total_users = get_total_users()
        active_today = get_active_users_today()
        text = f"📊 Общая статистика:\nВсего пользователей: {total_users}\nАктивных сегодня: {active_today}"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📋 Заявки", callback_data="stats_requests"))
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
# ================== Теория по темам ==================

def theory_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Теория по заданиям", callback_data="tasks_call"),
        InlineKeyboardButton("Теория по темам", callback_data="tasks_by_topic_call")
    )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))
    return markup
# Создаёт экран "Теория по темам"
def tasks_by_topic_screen():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Алгебра", callback_data="topics_algebra_call"),
        InlineKeyboardButton("Геометрия", callback_data="topics_geometry_call")
    )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="theory_call"))
    return markup
# Создаёт экран со списком тем Алгебры для выбора пользователем
def algebra_topics_screen():
    markup = InlineKeyboardMarkup(row_width=2)
    algebra_topics = [
        ("Теория вероятностей", "probability"),
        ("ФСУ", "fsu"),
        ("Квадратные уравнения", "quadratic"),
        ("Степени", "powers"),
        ("Корни", "roots"),
        ("Тригонометрическая окружность", "trigonometric_circle"),
        ("Тригонометрические определения", "definitions"),
        ("Тригонометрические формулы", "trigonometric_formulas"),
        ("Формулы приведения", "reduction_formulas"),
        ("Логарифмы", "logarithms"),
        ("Модули", "modules"),
        ("Обычная функция и производная", "usual_function_and_derivative"),
        ("Производная", "derivative"),
        ("Функция корня", "root_function"),
        ("Показательная функция", "exponential_function"),
        ("Логарифмическая функция", "logarithmic_function"),
        ("Метод рационализации", "rationalization")
    ]
    for theme_name, theme_code in algebra_topics:
        markup.add(InlineKeyboardButton(theme_name, callback_data=f"topic_{theme_code}_call"))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="tasks_by_topic_call"))
    return markup
# Создаёт экран со списком тем Геометрии для выбора пользователем
def geometry_topics_screen():
    markup = InlineKeyboardMarkup(row_width=2)
    geometry_topics = [
        ("Биссектриса, медиана", "triangle_lines"),
        ("Прямоугольный треугольник", "right_triangle"),
        ("Равнобедренный/Равносторонний треугольник", "isosceles_equilateral_triangle"),
        ("Равенство/Подобие треугольников", "triangle_similarity"),
        ("Треугольник", "triangle"),
        ("Окружность", "circle"),
        ("Параллелограмм", "parallelogram"),
        ("Равносторонний шестиугольник", "regular_hexagon"),
        ("Ромб и Трапеция", "rhombus_trapezoid"),
        ("Углы", "angles"),
        ("Вектор", "vector"),
        ("Стереометрия", "stereometry"),
        ("Прямая", "direct"),
        ("Парабола", "parabola"),
        ("Гипербола", "hyperbola")
    ]
    for theme_name, theme_code in geometry_topics:
        markup.add(InlineKeyboardButton(theme_name, callback_data=f"topic_{theme_code}_call"))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="tasks_by_topic_call"))
    return markup

# ================== Quiz ==================
quiz_conn = sqlite3.connect('quiz.db', check_same_thread=False)
quiz_cursor = quiz_conn.cursor()

# Словарь для преобразования первичных баллов во вторичные
primary_to_secondary = {
    1: 6,
    2: 11,
    3: 17,
    4: 22,
    5: 27,
    6: 34,
    7: 40,
    8: 46,
    9: 52,
    10: 58,
    11: 64,
    12: 70
}
# Функция для получения вторичных баллов
def get_secondary_score(primary_score):
    return primary_to_secondary.get(primary_score, 0)

# Инициализация базы данных для Quize
def init_quiz_db():
    global quiz_conn, quiz_cursor
    try:
        logging.info("Инициализация базы данных quiz.db")
        quiz_conn = sqlite3.connect("quiz.db", check_same_thread=False)
        quiz_cursor = quiz_conn.cursor()

        # Удаляем только таблицу quiz_tasks, чтобы задачи могли быть загружены заново
        quiz_cursor.execute('DROP TABLE IF EXISTS quiz_tasks')
        quiz_conn.commit()
        logging.info("Таблица quiz_tasks сброшена")

        # Создаём таблицу quiz_tasks, если её нет
        quiz_cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                option INTEGER,
                day INTEGER,
                task_number INTEGER,
                image_url TEXT,
                correct_answer TEXT
            )''')
        logging.info("Таблица quiz_tasks создана")

        # Удаляем старую таблицу user_quiz_progress, чтобы пересоздать с правильной схемой
        quiz_cursor.execute('DROP TABLE IF EXISTS user_quiz_progress')
        quiz_conn.commit()

        # Создаём таблицу user_quiz_progress с правильной схемой
        quiz_cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quiz_progress (
                user_id INTEGER,
                quiz_id INTEGER,
                task_number INTEGER,
                user_answer TEXT,
                attempt_id INTEGER,  -- Добавляем столбец attempt_id
                option INTEGER,
                timestamp TEXT,
                PRIMARY KEY (user_id, quiz_id, task_number, attempt_id, option)
            )''')

        # Создаём таблицу user_quiz_state, если её нет
        quiz_cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quiz_state (
                user_id INTEGER,
                option INTEGER,
                day INTEGER,
                task_number INTEGER,
                attempt_id INTEGER,
                primary_score INTEGER DEFAULT 0,
                secondary_score INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                timestamp TEXT,
                username TEXT,
                PRIMARY KEY (user_id, option, day, attempt_id)
            )''')

        # Создаём таблицу user_data_temp для хранения состояния user_data
        quiz_cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data_temp (
                user_id INTEGER PRIMARY KEY,
                data TEXT
            )''')

        # Проверяем, существует ли столбец username, и добавляем его, если отсутствует
        quiz_cursor.execute('PRAGMA table_info(user_quiz_state)')
        columns = {col[1] for col in quiz_cursor.fetchall()}
        if 'username' not in columns:
            quiz_cursor.execute('ALTER TABLE user_quiz_state ADD COLUMN username TEXT')
            quiz_conn.commit()
            logging.info("Столбец username добавлен в таблицу user_quiz_state")

        quiz_conn.commit()
        logging.info("✅ База данных quiz.db успешно инициализирована")
    except sqlite3.Error as e:
        logging.error(f"❌ Ошибка при инициализации базы данных quiz.db: {e}")
        raise

# Проверяем, что таблица существует и задачи загружены
try:
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM quiz_tasks')
    task_count = cursor.fetchone()[0]
    cursor.close()
    if task_count == 0:
        logging.error("Критическая ошибка: задачи не загружены в таблицу quiz_tasks!")
    else:
        logging.info(f"Успешно загружено {task_count} задач в таблицу quiz_tasks.")
except sqlite3.OperationalError as e:
    logging.error(f"Ошибка при проверке таблицы quiz_tasks: {e}")
    logging.info("Таблица quiz_tasks еще не создана или недоступна. Продолжаем выполнение.")

# Функция для очистки задач (больше не удаляем старые варианты)
def clear_quiz_tasks():
    try:
        quiz_cursor.execute('DELETE FROM quiz_tasks')  # Очищаем все задачи перед загрузкой новых
        quiz_conn.commit()
        logging.info("Очищены все задачи перед загрузкой новых")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при очистке задач: {e}")

# Функция для загрузки задач из CSV
def load_quiz_from_csv(filename):
    try:
        # Очищаем старые задачи
        logging.info("Очищены все задачи перед загрузкой новых")
        clear_quiz_tasks()
        # Проверяем, существует ли файл
        if not os.path.exists(filename):
            logging.error(f"Файл {filename} не найден!")
            return False

        # Открываем файл и загружаем задачи
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)  # Загружаем все строки в список для проверки
            if not rows:
                logging.error(f"Файл {filename} пуст или не содержит данных!")
                return False

            # Загружаем задачи в базу данных
            cursor = quiz_conn.cursor()
            for row in rows:
                option = int(row['option'])  # Номер варианта
                day = option  # Вариант и день совпадают (1 вариант = 1 день)
                task_number = int(row['task_number'])
                image_url = row['image_url']  # URL фото задания
                correct_answer = row['correct_answer']
                cursor.execute('''
                    INSERT INTO quiz_tasks (option, day, task_number, image_url, correct_answer)
                    VALUES (?, ?, ?, ?, ?)
                ''', (option, day, task_number, image_url, correct_answer))
            quiz_conn.commit()
            cursor.close()
            logging.info(f"Загружено {len(rows)} задач из {filename}")

            # Проверяем, что задачи загружены
            cursor = quiz_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM quiz_tasks')
            task_count = cursor.fetchone()[0]
            cursor.close()
            if task_count == 0:
                logging.error("Критическая ошибка: задачи не загружены в таблицу quiz_tasks!")
                return False
            else:
                logging.info(f"Успешно загружено {task_count} задач в таблицу quiz_tasks.")
                return True
    except Exception as e:
        logging.error(f"Ошибка при загрузке задач из {filename}: {e}")
        return False
# Инициализация базы данных и загрузка задач
try:
    init_quiz_db()
    # Загружаем задачи только один раз
    if not load_quiz_from_csv('week.csv'):
        logging.error("Не удалось загрузить задачи из week.csv. Бот может работать некорректно.")
    else:
        logging.info("Все задачи успешно загружены.")
except Exception as e:
    logging.error(f"Ошибка при инициализации quiz: {e}")

# Экран "Quize" с выбором варианта
def quiz_screen(page=1):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Получаем все доступные варианты
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT DISTINCT option FROM quiz_tasks')
    options = sorted([row[0] for row in cursor.fetchall()])
    cursor.close()
    total_variants = len(options)

    # Пагинация: показываем до 10 вариантов на странице
    variants_per_page = 10
    start_idx = (page - 1) * variants_per_page
    end_idx = min(start_idx + variants_per_page, total_variants)
    visible_variants = options[start_idx:end_idx]

    # Добавляем кнопки для видимых вариантов
    for option in visible_variants:
        markup.add(types.InlineKeyboardButton(f"Вариант {option}", callback_data=f"start_quiz_{option}"))

    # Добавляем кнопки пагинации, если нужно
    if total_variants > variants_per_page:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(types.InlineKeyboardButton("◀️", callback_data=f"quiz_page_{page - 1}"))
        if end_idx < total_variants:
            pagination_buttons.append(types.InlineKeyboardButton("▶️", callback_data=f"quiz_page_{page + 1}"))
        markup.add(*pagination_buttons)
    # Кнопка "Статистика" и "Назад"
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="quiz_stats"))
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))
    return markup
# Экран статистики с выбором варианта
def stats_screen(user_id, page=1):  # Добавляем user_id как параметр
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Получаем все завершённые варианты для конкретного пользователя
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT DISTINCT option FROM user_quiz_state WHERE user_id = ? AND completed = 1', (user_id,))
    variants = sorted([row[0] for row in cursor.fetchall()])
    cursor.close()
    total_variants = len(variants)

    # Пагинация: показываем до 10 вариантов на странице
    variants_per_page = 10
    start_idx = (page - 1) * variants_per_page
    end_idx = min(start_idx + variants_per_page, total_variants)
    visible_variants = variants[start_idx:end_idx]

    # Добавляем кнопки для видимых вариантов
    for variant in visible_variants:
        markup.add(types.InlineKeyboardButton(f"Вариант {variant}", callback_data=f"stats_variant_{variant}"))

    # Добавляем кнопки пагинации, если нужно
    if total_variants > variants_per_page:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(types.InlineKeyboardButton("◀️", callback_data=f"stats_page_{page - 1}"))
        if end_idx < total_variants:
            pagination_buttons.append(types.InlineKeyboardButton("▶️", callback_data=f"stats_page_{page + 1}"))
        markup.add(*pagination_buttons)

    # Кнопка "Назад"
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_call"))
    return markup
# Экран статистики с выбором попытки для варианта
def stats_attempts_screen(user_id, variant, page=1):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Получаем все завершённые попытки для данного варианта (отсортированы по времени, от старых к новым)
    cursor = quiz_conn.cursor()
    cursor.execute('''
        SELECT attempt_id, timestamp 
        FROM user_quiz_state 
        WHERE user_id = ? AND option = ? AND completed = 1 
        ORDER BY timestamp ASC
    ''', (user_id, variant))
    attempts = cursor.fetchall()
    cursor.close()
    total_attempts = len(attempts)

    logging.info(f"Найдено {total_attempts} попыток для пользователя {user_id}, вариант {variant}")

    # Пагинация: показываем до 10 попыток на странице
    attempts_per_page = 10
    start_idx = (page - 1) * attempts_per_page
    end_idx = min(start_idx + attempts_per_page, total_attempts)
    visible_attempts = attempts[start_idx:end_idx]

    # Нумерация попыток: самая старая попытка — "Попытка 1"
    for index, (attempt_id, timestamp) in enumerate(visible_attempts, start=start_idx + 1):
        try:
            attempt_id = int(attempt_id)
        except ValueError:
            logging.error(f"Некорректный attempt_id: {attempt_id}, пропускаем попытку")
            continue
        callback_data = f"stats_attempt_{variant}_{attempt_id}"  # Изменили на подчёркивание
        logging.info(f"Формирование callback_data для попытки: {callback_data}")
        markup.add(types.InlineKeyboardButton(f"Попытка {index}", callback_data=callback_data))

    # Добавляем кнопки пагинации, если нужно
    if total_attempts > attempts_per_page:
        pagination_buttons = []
        if page > 1:
            callback_prev = f"stats_attempts_page_{variant}_{page - 1}"  # Используем подчёркивание
            pagination_buttons.append(types.InlineKeyboardButton("◀️", callback_data=callback_prev))
            logging.info(f"Добавлена кнопка '◀️' с callback_data: {callback_prev}")
        if end_idx < total_attempts:
            callback_next = f"stats_attempts_page_{variant}_{page + 1}"  # Используем подчёркивание
            pagination_buttons.append(types.InlineKeyboardButton("▶️", callback_data=callback_next))
            logging.info(f"Добавлена кнопка '▶️' с callback_data: {callback_next}")
        markup.add(*pagination_buttons)

    # Кнопка "Назад"
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_stats"))
    return markup

# ================== Математический квест  ==================
challenge ={
    "6": {
        "lin": {
            "name": "Линейные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/4NQpUhK",
                    "homework_photo": "https://i.imgur.com/h5aUj2B",
                    "hint": ["https://imgur.com/L4cZoLE", "https://imgur.com/gE2YTd6", "https://imgur.com/pQaYooP", "https://imgur.com/ZrIUaUf", "https://imgur.com/kc0sFah", "https://imgur.com/L4yDIHX", "https://imgur.com/K7blD33"],
                    "answer": "-17",
                    "analog": {"photo": "https://imgur.com/cNfMQA1", "answer": "-18"},
                    "homework": {"photo": "https://imgur.com/775gKq1", "answer": "6,3"}
                },
                {
                    "photo": "https://imgur.com/0JQujsF",
                    "hint": ["https://imgur.com/BDZSIEF", "https://imgur.com/2CRzthQ", "https://imgur.com/saPamdV", "https://imgur.com/DomEXt8", "https://imgur.com/h7hUDg0", "https://imgur.com/8TTg6B1"],
                    "answer": "3.5",
                    "analog": {"photo": "https://imgur.com/T5POcl8", "answer": "7"},
                    "homework": {"photo": "https://imgur.com/7Pbxuw2", "answer": "3"}
                },
                {
                    "photo": "https://imgur.com/ZhFvCpw",
                    "hint": ["https://imgur.com/Ghb9naw", "https://imgur.com/jFau90k", "https://imgur.com/ngqLbFu", "https://imgur.com/3ezX1DC", "https://imgur.com/PtSyN35"],
                    "answer": "3",
                    "analog": {"photo": "https://imgur.com/YbyWm33", "answer": "1.9"},
                    "homework": {"photo": "https://imgur.com/dCHjOe1", "answer": "1"}
                }
            ]
        },
        "quad": {
            "name": "Квадратные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/Rzfc7L2",
                    "homework_photo": "https://i.imgur.com/GdfR8sK",
                    "hint": ["https://imgur.com/eEhPowi", "https://imgur.com/1JXFcGN", "https://imgur.com/B8RogGN", "https://imgur.com/5lNqfbF"],
                    "answer": "9",
                    "analog": {"photo": "https://imgur.com/yRYV33Q", "answer": "6"},
                    "homework": {"photo": "https://imgur.com/7yDbs2t", "answer": "-3"}
                },
                {
                    "photo": "https://imgur.com/fnYsNWZ",
                    "hint": ["https://imgur.com/c2rhW30", "https://imgur.com/LkIsKKr", "https://imgur.com/6lJai7G", "https://imgur.com/wXKj0Wz", "https://imgur.com/76cu2zF"],
                    "answer": "7",
                    "analog": {"photo": "https://imgur.com/c8osUfW", "answer": "12"},
                    "homework": {"photo": "https://imgur.com/y1LAAK8", "answer": "18"}
                },
                {
                    "photo": "https://imgur.com/DhRaVsd",
                    "hint": ["https://imgur.com/OVRBMJT", "https://imgur.com/JtMSN10", "https://imgur.com/8ZwH9rA", "https://imgur.com/upsse3b", "https://imgur.com/fdPVe8r"],
                    "answer": "-4",
                    "analog": {"photo": "https://imgur.com/xoG9YsP", "answer": "-4"},
                    "homework": {"photo": "https://imgur.com/yww27op", "answer": "-2"}
                }
            ]
        },
        "odd": {
            "name": "Уравнения нечётных степеней",
            "tasks": [
                {
                    "photo": "https://imgur.com/wHOWnt5",
                    "homework_photo": "https://i.imgur.com/b1pNjxT",
                    "hint": ["https://imgur.com/h0jJ1Ew", "https://imgur.com/4uHDGBb", "https://imgur.com/BRxwuEi"],
                    "answer": "1",
                    "analog": {"photo": "https://imgur.com/myTyMdj", "answer": "0"},
                    "homework": {"photo": "https://imgur.com/BngCzDi", "answer": "-4"}
                }
            ]
        },
        "frac": {
            "name": "Дробно-рациональные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/9q8GbH3",
                    "homework_photo": "https://i.imgur.com/b1pNjxT",
                    "hint": ["https://imgur.com/hFjIgRS", "https://imgur.com/Erb50IQ", "https://imgur.com/oLwZt6U", "https://imgur.com/aZaR4WL", "https://imgur.com/rDgsCKY"],
                    "answer": "0.45",
                    "analog": {"photo": "https://imgur.com/CF8cD5a", "answer": "0.875"},
                    "homework": {"photo": "https://imgur.com/ZlDIypW", "answer": "-0.6875"}
                },
                {
                    "photo": "https://imgur.com/sNUY4tV",
                    "hint": ["https://imgur.com/5HFweRZ", "https://imgur.com/TWSptG4", "https://imgur.com/2MNOcYR", "https://imgur.com/g1rCj6K", "https://imgur.com/cALRPwV"],
                    "answer": "4",
                    "analog": {"photo": "https://imgur.com/K8KuJRo", "answer": "6"},
                    "homework": {"photo": "https://imgur.com/P9KQhVI", "answer": "2,4"}
                },
                {
                    "photo": "https://imgur.com/VJFQvZG",
                    "hint": ["https://imgur.com/3sgncXW", "https://imgur.com/M9lOT6K", "https://imgur.com/LkFp2Pk", "https://imgur.com/zlYkjAY", "https://imgur.com/p8bPGHB"],
                    "answer": "15",
                    "analog": {"photo": "https://imgur.com/7NTpN7f", "answer": "29"},
                    "homework": {"photo": "https://imgur.com/XJKug8M", "answer": "9"}
                },
                {
                    "photo": "https://imgur.com/hH7qdVl",
                    "hint": ["https://imgur.com/60AYjuN", "https://imgur.com/WwYf2V4", "https://imgur.com/miopmey", "https://imgur.com/6eX76I4", "https://imgur.com/fBVeCbz", "https://imgur.com/U18Isdr"],
                    "answer": "4",
                    "analog": {"photo": "https://imgur.com/LaH0csS", "answer": "4"},
                    "homework": {"photo": "https://imgur.com/aeDV8iD", "answer": "10"}
                },
                {
                    "photo": "https://imgur.com/sRQnt6K",
                    "hint": ["https://imgur.com/ZjJWEzb", "https://imgur.com/NzOSjBe", "https://imgur.com/6Ng8vIp", "https://imgur.com/neUC8qw", "https://imgur.com/OXmCdrg", "https://imgur.com/rrf2URv", "https://imgur.com/Tze5uqC", "https://imgur.com/y1jc1wY"],
                    "answer": "-8",
                    "analog": {"photo": "https://imgur.com/IenzECq", "answer": "-5"},
                    "homework": {"photo": "https://imgur.com/OtPX1ia", "answer": "-3,5"}
                }
            ]
        },
        "irr": {
            "name": "Иррациональные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/Ip0TUQC",
                    "homework_photo": "https://i.imgur.com/7qZeVsW",
                    "hint": ["https://imgur.com/3MU4mFu", "https://imgur.com/XkUMRf4", "https://imgur.com/Z4M94Tj", "https://imgur.com/6aMGDOV"],
                    "answer": "12",
                    "analog": {"photo": "https://imgur.com/35MK172", "answer": "4"},
                    "homework": {"photo": "https://imgur.com/xDOtDdW", "answer": "9"}
                },
                {
                    "photo": "https://imgur.com/5ZdpMIi",
                    "hint": ["https://imgur.com/N4IGBvC", "https://imgur.com/yfxlbvm"],
                    "answer": "19",
                    "analog": {"photo": "https://imgur.com/cNTIHp0", "answer": "28"},
                    "homework": {"photo": "https://imgur.com/wkHEBve", "answer": "62"}
                },
                {
                    "photo": "https://imgur.com/QmQGLYj",
                    "hint": ["https://imgur.com/3rxVmIN", "https://imgur.com/nx07HS1", "https://imgur.com/2bW7SG7", "https://imgur.com/q6yjjcB", "https://imgur.com/ERo0BoR", "https://imgur.com/5c39Lb6"],
                    "answer": "20",
                    "analog": {"photo": "https://imgur.com/J0OhUv3", "answer": "5"},
                    "homework": {"photo": "https://imgur.com/YnOT1um", "answer": "9"}
                },
                {
                    "photo": "https://imgur.com/M5LMPbe",
                    "hint": ["https://imgur.com/PiS29MY", "https://imgur.com/gHAMKaz", "https://imgur.com/vKMqLx2", "https://imgur.com/jVO313F", "https://imgur.com/h7fBPjo", "https://imgur.com/ybYtEkV"],
                    "answer": "-8",
                    "analog": {"photo": "https://imgur.com/Wgp1vQh", "answer": "-12"},
                    "homework": {"photo": "https://imgur.com/hreMMUh", "answer": "-8,5"}
                }
            ]
        },
        "log": {
            "name": "Логарифмические уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/NZqLSwp",
                    "homework_photo": "https://i.imgur.com/xY9tPqB",
                    "hint": ["https://imgur.com/6OsYCxE", "https://imgur.com/PBZ1IYp", "https://imgur.com/a33ByAX"],
                    "answer": "-6",
                    "analog": {"photo": "https://imgur.com/nWH5CMb", "answer": "-5"},
                    "homework": {"photo": "https://imgur.com/AOhuKPi", "answer": "1"}
                },
                {
                    "photo": "https://imgur.com/2RcdQTf",
                    "hint": ["https://imgur.com/WMElPaz", "https://imgur.com/6mPePlu", "https://imgur.com/a4zhJvO", "https://imgur.com/doel9Ro"],
                    "answer": "-7",
                    "analog": {"photo": "https://imgur.com/NEVciY8", "answer": "-6"},
                    "homework": {"photo": "https://imgur.com/4hWyrM6", "answer": "-71"}
                },
                {
                    "photo": "https://imgur.com/CspBO7d",
                    "hint": ["https://imgur.com/p9Y9Ylp", "https://imgur.com/Wqfb4jW", "https://imgur.com/3beIbAP", "https://imgur.com/7XM0fz8", "https://imgur.com/vGvQ4Pv"],
                    "answer": "85",
                    "analog": {"photo": "https://imgur.com/XwnbO6A", "answer": "-4"},
                    "homework": {"photo": "https://imgur.com/ZdUwBQA", "answer": "93"}
                },
                {
                    "photo": "https://imgur.com/MRWlYjO",
                    "hint": ["https://imgur.com/5nSBDtH", "https://imgur.com/knHiJZQ", "https://imgur.com/1yByr0h", "https://imgur.com/des8TR3"],
                    "answer": "3",
                    "analog": {"photo": "https://imgur.com/Flz6mly", "answer": "3"},
                    "homework": {"photo": "https://imgur.com/Sj8S3aX", "answer": "3"}
                },
                {
                    "photo": "https://imgur.com/m0SmA8I",
                    "hint": ["https://imgur.com/apJZ3cU", "https://imgur.com/XAPCGbE", "https://imgur.com/yA1GPHV", "https://imgur.com/vfzRgtb", "https://imgur.com/zrTw5PD"],
                    "answer": "-20",
                    "analog": {"photo": "https://imgur.com/VFy0H17", "answer": "0"},
                    "homework": {"photo": "https://imgur.com/NuD7q1J", "answer": "-8"}
                },
                {
                    "photo": "https://imgur.com/r7YIn94",
                    "hint": ["https://imgur.com/GPYe9hW", "https://imgur.com/wR4AU0r", "https://imgur.com/wJQ2PyP", "https://imgur.com/7ODxTzb"],
                    "answer": "2",
                    "analog": {"photo": "https://imgur.com/dhSDJfV", "answer": "-0.2"},
                    "homework": {"photo": "https://imgur.com/OMtU0qV", "answer": "-2"}
                },
                {
                    "photo": "https://imgur.com/SnBlk8t",
                    "hint": ["https://imgur.com/LGAt5ta", "https://imgur.com/9v8idFn", "https://imgur.com/MvEII24", "https://imgur.com/tSxpSXr", "https://imgur.com/ahL3sQx"],
                    "answer": "0",
                    "analog": {"photo": "https://imgur.com/lkKpvIZ", "answer": "0"},
                    "homework": {"photo": "https://imgur.com/PIHrPYO", "answer": "1,25"}
                },
                {
                    "photo": "https://imgur.com/cZ1WfqQ",
                    "hint": ["https://imgur.com/NN6FCjF", "https://imgur.com/BVDxE0j", "https://imgur.com/zhMuMUl", "https://imgur.com/QE4lDKZ", "https://imgur.com/JWxPvy3", "https://imgur.com/9qdbs5a"],
                    "answer": "1",
                    "analog": {"photo": "https://imgur.com/Xb2Vjc0", "answer": "1"},
                    "homework": {"photo": "https://imgur.com/cYljXWg", "answer": "1"}
                },
                {
                    "photo": "https://imgur.com/RZW1y8X",
                    "hint": ["https://imgur.com/UgTz0U5", "https://imgur.com/q0VTSjH", "https://imgur.com/zplCbbp", "https://imgur.com/YssB1LG", "https://imgur.com/XN5LlE7"],
                    "answer": "6",
                    "analog": {"photo": "https://imgur.com/q26bYlk", "answer": "6"},
                    "homework": {"photo": "https://imgur.com/U18Zoie", "answer": "7"}
                }
            ]
        },
        "exp": {
            "name": "Показательные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/2OkH42p",
                    "homework_photo": "https://i.imgur.com/m3wFp4L",
                    "hint": ["https://imgur.com/h2aIuOz", "https://imgur.com/kf0a3fk", "https://imgur.com/WWaxPu5"],
                    "answer": "-5",
                    "analog": {"photo": "https://imgur.com/Ho28Hqu", "answer": "-6"},
                    "homework": {"photo": "https://imgur.com/JZeBEnO", "answer": "-3,5"}
                },
                {
                    "photo": "https://imgur.com/5MgRIzz",
                    "hint": ["https://imgur.com/PXNCQPU", "https://imgur.com/dEp50cS", "https://imgur.com/ufEp8E6", "https://imgur.com/uuoKfhR", "https://imgur.com/ZN3qvph"],
                    "answer": "1.25",
                    "analog": {"photo": "https://imgur.com/jXGrttf", "answer": "7"},
                    "homework": {"photo": "https://imgur.com/tyMsyig", "answer": "0,8"}
                },
                {
                    "photo": "https://imgur.com/JrwTbFI",
                    "hint": ["https://imgur.com/c8NtG0y", "https://imgur.com/xBBtmI1", "https://imgur.com/smKETZx", "https://imgur.com/EiNUHwP", "https://imgur.com/f4eBHlU"],
                    "answer": "2.5",
                    "analog": {"photo": "https://imgur.com/44ZZq5n", "answer": "2.5"},
                    "homework": {"photo": "https://imgur.com/ZmkKkI2", "answer": "0,3"}
                },
                {
                    "photo": "https://imgur.com/ln93w42",
                    "hint": ["https://imgur.com/dTmFSmJ", "https://imgur.com/1mPXuOm", "https://imgur.com/Q9ZdDTJ", "https://imgur.com/IpH0mbj", "https://imgur.com/bTBCrhM", "https://imgur.com/2gyD7mb"],
                    "answer": "1",
                    "analog": {"photo": "https://imgur.com/839oweU", "answer": "0.6"},
                    "homework": {"photo": "https://imgur.com/rxofpvz", "answer": "0,8"}
                },
                {
                    "photo": "https://imgur.com/AGH84E0",
                    "hint": ["https://imgur.com/JIBGx9g", "https://imgur.com/B9o3fjv", "https://imgur.com/DGsLTUG", "https://imgur.com/WB6G1dq", "https://imgur.com/nEvgEAC", "https://imgur.com/ZAGHL6b"],
                    "answer": "31",
                    "analog": {"photo": "https://imgur.com/RevlHe5", "answer": "125.5"},
                    "homework": {"photo": "https://imgur.com/lmVkhcT", "answer": "16,75"}
                },
                {
                    "photo": "https://imgur.com/m9Po1PX",
                    "hint": ["https://imgur.com/hhVzHo5", "https://imgur.com/2LmRxJH", "https://imgur.com/JBIn95G", "https://imgur.com/eaHrCe6", "https://imgur.com/tzjIf6Z", "https://imgur.com/aaldMwO", "https://imgur.com/6miJi10", "https://imgur.com/nb55pIT", "https://imgur.com/aqm0zx1"],
                    "answer": "3.25",
                    "analog": {"photo": "https://imgur.com/2NXP3IY", "answer": "8"},
                    "homework": {"photo": "https://imgur.com/Rn1GIj1", "answer": "2"}
                },
                {
                    "photo": "https://imgur.com/d9fQTX7",
                    "hint": ["https://imgur.com/ci1nc88", "https://imgur.com/Ue4Y4ca", "https://imgur.com/PDEsmwM", "https://imgur.com/MwrnAtO", "https://imgur.com/4v2V1vs"],
                    "answer": "1",
                    "analog": {"photo": "https://imgur.com/5OVse3v", "answer": "0.2"},
                    "homework": {"photo": "https://imgur.com/l9arGB5", "answer": "0,6"}
                }
            ]
        }
    }
}

# Определение миров для квеста
QUEST_WORLDS = [
    {
        "id": 6,
        "name": "🌍 6. Мир Простейших Уравнений",
        "description": "🌍 6. Мир Простейших Уравнений",
        "image": "https://i.imgur.com/Z0Io2Jf.jpg",
        "loaded_image": "https://i.imgur.com/Z0Io2Jf.jpg",
        "unlocked": True
    },
    {
        "id": 0,
        "name": "🌀 Мир находится в разработке... 🌀",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    }
]

def init_quest_db():
    """Инициализация базы данных для квеста"""
    conn = sqlite3.connect('quest.db')
    cursor = conn.cursor()
    
    # Таблица для хранения прогресса пользователей в квесте
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS world_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        world_id INTEGER NOT NULL,
        completed_tasks INTEGER DEFAULT 0,
        total_tasks INTEGER DEFAULT 0,
        date_updated TEXT NOT NULL,
        UNIQUE(user_id, world_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("✅ Таблица 'world_progress' создана или уже существует!")
    
    # Инициализируем таблицу избранного
    init_favorites_db()

# Примечание: функция init_favorites_db уже определена выше и создает таблицу с правильной структурой
# (содержит challenge_num вместо world_id)

def get_world_progress(user_id, world_id):
    """Получение прогресса пользователя в конкретном мире"""
    conn = sqlite3.connect('quest.db')
    cursor = conn.cursor()
    cursor.execute("SELECT completed_tasks, total_tasks FROM world_progress WHERE user_id = ? AND world_id = ?", 
                  (user_id, world_id))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"completed": row[0], "total": row[1]}
    else:
        # Если записи нет, подсчитываем общее количество заданий в мире
        total_tasks = 0
        world_challenges = challenge.get(str(world_id), {})
        for category in world_challenges.values():
            total_tasks += len(category['tasks'])
        
        # Создаем запись в базе данных
        conn = sqlite3.connect('quest.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO world_progress (user_id, world_id, completed_tasks, total_tasks, date_updated) VALUES (?, ?, ?, ?, ?)",
            (user_id, world_id, 0, total_tasks, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
        
        return {"completed": 0, "total": total_tasks}

def update_world_progress(user_id, world_id, completed=None):
    """Обновление прогресса пользователя в конкретном мире"""
    conn = sqlite3.connect('quest.db')
    cursor = conn.cursor()
    
    if completed is not None:
        cursor.execute(
            "UPDATE world_progress SET completed_tasks = ?, date_updated = ? WHERE user_id = ? AND world_id = ?",
            (completed, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, world_id)
        )
    else:
        # Обновляем только дату
        cursor.execute(
            "UPDATE world_progress SET date_updated = ? WHERE user_id = ? AND world_id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, world_id)
        )
    
    conn.commit()
    conn.close()

def handle_mathquest_call(call):
    """Обработчик для математического квеста"""
    from instance import photo_quest_main
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        # Отправляем главный экран математического квеста
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="🎮 Математический квест\n\nДобро пожаловать в математический квест! Выберите действие:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=math_quest_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} открыл математический квест")
    except Exception as e:
        logging.error(f"Ошибка при открытии математического квеста: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки математического квеста.")

def handle_quest_select_world(call):
    """Обработчик выбора мира в квесте"""
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем текущий индекс или устанавливаем 0, если это первый вызов
    data_parts = call.data.split('_')
    
    # Проверяем, не является ли вызов из кнопки "Назад"
    if data_parts[-1] == "worlds":
        current_index = 0  # По умолчанию показываем первый мир
    else:
        # Получаем индекс из параметра, если он есть
        current_index = int(data_parts[-1]) if len(data_parts) > 3 else 0
    
    try:
        # Получаем текущий мир для отображения
        world = QUEST_WORLDS[current_index]
        
        # Отображаем список миров с изображением текущего мира
        bot.edit_message_media(
            media=InputMediaPhoto(world["image"], caption=f"Выберите мир для исследования:\n\n{world['name']}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_worlds_screen(current_index, len(QUEST_WORLDS))
        )
        logging.info(f"Пользователь {call.from_user.id} просматривает список миров")
    except Exception as e:
        logging.error(f"Ошибка при отображении списка миров: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки списка миров.")

def handle_quest_profile(call):
    """Обработчик просмотра профиля героя"""
    from instance import photo_quest_profile
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        # Временная заглушка для профиля
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_profile, caption="👤 Профиль героя\n\n🌀 Профиль находится в разработке... 🌀\n\n🔧 Этот раздел сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_profile_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} открыл профиль героя")
    except Exception as e:
        logging.error(f"Ошибка при отображении профиля героя: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки профиля героя.")

def handle_quest_trophies(call):
    """Обработчик просмотра хранилища трофеев"""
    from instance import photo_quest_trophies
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        # Временная заглушка для трофеев
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_trophies, caption="🏆 Хранилище трофеев\n\n🌀 Хранилище находится в разработке... 🌀\n\n🔧 Этот раздел сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_trophies_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} открыл хранилище трофеев")
    except Exception as e:
        logging.error(f"Ошибка при отображении хранилища трофеев: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки хранилища трофеев.")

def handle_quest_shop(call):
    """Обработчик просмотра лавки скинов"""
    from instance import photo_quest_shop
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        # Временная заглушка для магазина
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_shop, caption="👕 Лавка скинов\n\n🌀 Лавка находится в разработке... 🌀\n\n🔧 Этот раздел сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_shop_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} открыл лавку скинов")
    except Exception as e:
        logging.error(f"Ошибка при отображении лавки скинов: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки лавки скинов.")

def handle_quest_navigation(call):
    """Обработчик навигации по списку миров"""
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        # Определяем направление и текущий индекс
        data_parts = call.data.split('_')
        direction = data_parts[-2]
        current_index = int(data_parts[-1])
        
        # Вычисляем новый индекс в зависимости от направления
        if direction == "next":
            new_index = current_index + 1
            if new_index >= len(QUEST_WORLDS):
                new_index = 0
        else:  # "prev"
            new_index = current_index - 1
            if new_index < 0:
                new_index = len(QUEST_WORLDS) - 1
        
        # Получаем новый мир для отображения
        world = QUEST_WORLDS[new_index]
        
        # Обновляем экран выбора мира
        bot.edit_message_media(
            media=InputMediaPhoto(world["image"], caption=f"Выберите мир для исследования:\n\n{world['name']}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_worlds_screen(new_index, len(QUEST_WORLDS))
        )
        logging.info(f"Пользователь {call.from_user.id} навигирует по списку миров ({direction}, индекс: {new_index})")
    except Exception as e:
        logging.error(f"Ошибка при навигации по списку миров: {e}")
        bot.answer_callback_query(call.id, "Ошибка при навигации по списку миров.")

def handle_quest_enter_world(call):
    """Обработчик входа в выбранный мир"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем ID выбранного мира из колбэка (текущий индекс в списке)
    world_index = int(call.data.split('_')[-1])
    
    # Найти соответствующий мир по индексу из общего массива
    if world_index >= 0 and world_index < len(QUEST_WORLDS):
        world = QUEST_WORLDS[world_index]
    else:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return
    
    # Проверяем доступность мира
    if not world["unlocked"]:
        bot.answer_callback_query(call.id, "⚠️ Этот мир пока недоступен")
        return
    
    # Анимация загрузки мира
    # Согласно требованиям должна быть первая строка "Загрузка мира..." и 
    # вторая строка с прогресс-баром и тематическим сообщением
    
    loading_bars = [
        "[███░░░░░░░░░░░░░░░░] 17%",
        "[██████░░░░░░░░░░░░] 33%",
        "[█████████░░░░░░░░░] 51%",
        "[████████████░░░░░░] 68%",
        "[███████████████░░] 85%",
        "[█████████████████] 100%"
    ]
    
    loading_messages = [
        "Всё делится. Даже ты.",
        "Скидка на здравый смысл: -50%.",
        "Числа растут. Ценность — нет.",
        "Контракт подписан. Мелкий шрифт — на крови.",
        "Проценты сложились. Ты — нет.",
        "Добро пожаловать. Всё уже не твоё."
    ]
    
    # Отправляем серию сообщений с анимацией загрузки
    for i in range(6):
        caption = f"Загрузка мира...\n\n{loading_bars[i]}\n{loading_messages[i]}"
        
        bot.edit_message_media(
            media=InputMediaPhoto(world["image"], caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None
        )
        
        # Задержка для анимации (0.5 секунд между кадрами)
        time.sleep(0.5)
    
    # Загрузка завершена, показываем мир
    world_id = world["id"]  # Получаем ID мира для БД
    
    # Логируем описание мира, чтобы увидеть, что передается боту
    logging.info(f"Вход в мир, загрузка описания: '{world['description']}'")
    
    bot.edit_message_media(
        media=InputMediaPhoto(world["loaded_image"], caption=world['description']),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=loaded_world_screen(world_id)
    )
    
    # Обновляем прогресс пользователя
    get_world_progress(user_id, world_id)  # Это создаст запись, если её нет

def handle_quest_loaded_world(call):
    """Обработчик загруженного мира"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем ID мира из колбэка
    world_id = int(call.data.split('_')[-1])
    world = next((w for w in QUEST_WORLDS if w["id"] == world_id), None)
    
    if not world:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return
    
    # Сохраняем ID текущего мира в данных пользователя для использования в домашних заданиях и т.д.
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["current_world_id"] = world_id
    
    # Обновляем экран мира
    # Загружаем мир с правильным оформлением и логируем
    logging.info(f"Загрузка описания мира: '{world['description']}'")
    
    bot.edit_message_media(
        media=InputMediaPhoto(world["loaded_image"], caption=f"{world['name'].replace('🌍 ', '')}"),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=loaded_world_screen(world_id)
    )
    logging.info(f"Пользователь {user_id} вошел в мир {world_id} с названием: '{world['name']}'")


def handle_quest_back_to_worlds(call):
    """Обработчик возврата к списку миров из загруженного мира - без анимации загрузки"""
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Получаем первый мир для отображения
        world = QUEST_WORLDS[0]
        
        # Отображаем список миров с изображением первого мира без анимации
        bot.edit_message_media(
            media=InputMediaPhoto(world["image"], caption=f"Выберите мир для исследования:\n\n{world['name']}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_worlds_screen(0, len(QUEST_WORLDS))
        )
        logging.info(f"Пользователь {user_id} вернулся к списку миров")
    except Exception as e:
        logging.error(f"Ошибка при возврате к списку миров: {e}")
        # В случае ошибки, просто вызываем обычную функцию
        handle_quest_select_world(call)

def handle_mathquest_back(call):
    """Обработчик возврата в главное меню из квеста"""
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Очищаем данные пользователя, как это делается в main_back_call
    if user_id in user_data:
        del user_data[user_id]
    
    # Текст приветствия такой же, как в main_back_call
    text = (
        "👋 Добро пожаловать!\n\n"
        "🧠 Я — ваш помощник в подготовке к ЕГЭ по профильной математике.\n"
        "📖 Вместе мы разберём задания и сделаем процесс обучения проще и эффективнее.\n"
        "➡️ Выберите действие:"
    )
    
    try:
        # Возвращаемся в главное меню с нужным текстом
        from instance import photo_main
        from telebot.types import InputMediaPhoto
        
        bot.edit_message_media(
            media=InputMediaPhoto(photo_main, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=main_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} вернулся в главное меню из квеста")
    except Exception as e:
        logging.error(f"Ошибка при возвращении в главное меню: {e}")
        bot.answer_callback_query(call.id, "Ошибка при возвращении в главное меню.")

def handle_quest_theory(call):
    """Обработчик просмотра теории в мире (Книга знаний)"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Получаем ID мира из колбэка
    parts = call.data.split('_')
    world_id = int(parts[-1])
    world = next((w for w in QUEST_WORLDS if w["id"] == world_id), None)
    
    if not world:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return
    
    # Отображаем экран книги знаний с разделами
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Формулы Сокращённого Умножения", callback_data=f"theory_fsu_{world_id}"),
        InlineKeyboardButton("Квадратные уравнения", callback_data=f"theory_quadratic_{world_id}"),
        InlineKeyboardButton("Степени", callback_data=f"theory_powers_{world_id}"),
        InlineKeyboardButton("Корни", callback_data=f"theory_roots_{world_id}"),
        InlineKeyboardButton("Тригонометрия", callback_data=f"theory_trigonometry_{world_id}"),
        InlineKeyboardButton("Логарифмы", callback_data=f"theory_logarithms_{world_id}"),
        InlineKeyboardButton("Модули", callback_data=f"theory_modules_{world_id}"),
        InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
    )
    
    bot.edit_message_media(
        media=InputMediaPhoto(photo_quest_book, caption=f"Книга знаний - {world['name']}\n\nВыберите раздел для изучения:"),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )

def handle_quest_task_list(call):
    """Обработчик просмотра списка заданий в мире"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Логируем информацию
    logging.info(f"Открытие списка заданий, пользователь {user_id}")
    
    # Инициализируем данные пользователя
    ensure_user_data(user_id)
    
    # Сохраняем текущую категорию перед переходом в список заданий
    if "current_task" in user_data[user_id]:
        current_task = user_data[user_id]["current_task"]
        if 'world_id' in current_task and 'cat_code' in current_task:
            # Сохраняем информацию о последней просмотренной категории
            user_data[user_id]["last_category"] = {
                "world_id": current_task["world_id"],
                "cat_code": current_task["cat_code"]
            }
            logging.info(f"Сохранена информация о категории {current_task['world_id']}_{current_task['cat_code']} для пользователя {user_id}")
        
        # Важно: НЕ удаляем текущую задачу, чтобы сохранить целостность навигации
        # Это позволит вернуться к той же категории после выхода в меню и обратно
        # del user_data[user_id]["current_task"]
        # logging.info(f"Удалена информация о текущей задаче для пользователя {user_id}")
    
    # Получаем ID мира из колбэка
    parts = call.data.split('_')
    world_id = int(parts[-1])
    
    # Сохраняем текущее положение пользователя
    user_data[user_id]["current_screen"] = "task_list"
    user_data[user_id]["current_world_id"] = world_id
    
    world = next((w for w in QUEST_WORLDS if w["id"] == world_id), None)
    
    if not world:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return
    
    # Экран выбора категорий
    photo = photo_quest_quests  # Используем изображение для квестов
    caption = f"{world['name'].replace('🌍 ', '')}\n\nЗадачи\n\nВыберите категорию:"
    
    # Создаем клавиатуру для выбора категории
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Получаем доступные категории для этого мира из challenge
    world_challenges = challenge.get(str(world_id), {})
    
    if world_challenges:
        # Добавляем кнопки для категорий из challenge
        for cat_code, category in world_challenges.items():
            markup.add(
                InlineKeyboardButton(f"{category['name']}", 
                                    callback_data=f"quest_category_{world_id}_{cat_code}")
            )
    else:
        # Если категории для мира не найдены, показываем сообщение
        markup.add(
            InlineKeyboardButton("📝 Категории в разработке", callback_data=f"quest_loaded_world_{world_id}")
        )
    
    # Кнопка назад
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
    )
    
    try:
        # Отображаем экран задач с категориями
        bot.edit_message_media(
            media=InputMediaPhoto(photo, caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка при отображении списка задач: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при загрузке заданий")

def handle_quest_category(call):
    """Обработчик просмотра заданий категории"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем параметры из колбэка
    parts = call.data.split('_')
    world_id = int(parts[-2])
    cat_code = parts[-1]
    
    # Логируем информацию для отладки
    logging.info(f"Обработка категории: world_id={world_id}, cat_code={cat_code}, user_id={user_id}")
    
    # Сначала убедимся, что данные пользователя инициализированы
    ensure_user_data(user_id)
    
    # Сохраняем информацию о последней посещенной категории
    user_data[user_id]["last_category"] = {
        "world_id": world_id,
        "cat_code": cat_code
    }
    
    # НЕ очищаем информацию о текущей задаче, чтобы сохранить возможность навигации
    # if "current_task" in user_data[user_id]:
    #     del user_data[user_id]["current_task"]
    
    world = next((w for w in QUEST_WORLDS if w["id"] == world_id), None)
    if not world:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return
    
    # Если это опция "Все задания", показываем оригинальную кнопку с task_1_call и категории из challenge
    if cat_code == "all":
        # Экран всех задач
        photo = "https://i.imgur.com/aZ5tK3Q.jpg"  # Изображение экрана с задачами
        caption = "Задачи\n\nВыберите задание:"
        
        # Создаем клавиатуру для выбора задания (как на скриншоте)
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Кнопка "Все задания" с оригинальным callback_data
        markup.add(
            InlineKeyboardButton("📚 Все задания", callback_data="task_1_call")
        )
        
        # Получаем доступные категории для этого мира из challenge и добавляем их
        world_challenges = challenge.get(str(world_id), {})
        
        if world_challenges:
            # Добавляем заголовок для категорий из challenge
            markup.add(
                InlineKeyboardButton("📋 Категории задач:", callback_data=f"quest_task_list_{world_id}")
            )
            # Добавляем кнопки для каждой категории из challenge
            for category_code, category in world_challenges.items():
                markup.add(
                    InlineKeyboardButton(f"📘 {category['name']}", 
                                        callback_data=f"quest_category_{world_id}_{category_code}")
                )
        
        # Кнопка домашка
        markup.add(
            InlineKeyboardButton("📝 Домашка", callback_data="quest_homework")
        )
        
        # Кнопка избранное
        markup.add(
            InlineKeyboardButton("⭐ Избранное", callback_data="quest_favorites")
        )
        
        # Кнопка назад
        markup.add(
            InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
        )
        
        # Отображаем экран задач
        bot.edit_message_media(
            media=InputMediaPhoto(photo, caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        return
    
    # Стандартная обработка категории
    # Получаем категорию
    world_challenges = challenge.get(str(world_id), {})
    category = world_challenges.get(cat_code)
    
    if not category:
        bot.answer_callback_query(call.id, "Ошибка: категория не найдена")
        return
    
    # Всегда показываем первое задание из категории, а не проверяем уже выбрана ли эта категория
    # Этот подход делает навигацию проще для пользователя - категория всегда загружается,
    # даже если пользователь повторно нажимает на неё
    
    # Убираем проверку already_selected, которая мешала повторному открытию категории
    logging.info(f"Загружаем категорию {world_id}_{cat_code} для пользователя {user_id}")
    
    # Сохраняем информацию о текущей категории для дальнейшего использования
    user_data[user_id]["current_category"] = {
        "world_id": world_id,
        "cat_code": cat_code
    }
    
    # Всегда показываем первое задание
    task_idx = 0
    
    # Создаем новый call с правильными параметрами
    import copy
    new_call = copy.deepcopy(call)
    new_call.data = f"quest_task_{world_id}_{cat_code}_{task_idx}"
    handle_quest_task(new_call)
    return
    
    # Этот код никогда не будет выполнен из-за ранее добавленного return
    # Удаляем его полностью, чтобы не создавать путаницу в коде

def handle_quest_task(call):
    """Обработчик просмотра конкретного задания"""
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = str(call.from_user.id)
        
        # Получаем параметры из колбэка
        parts = call.data.split('_')
        world_id = int(parts[-3])
        cat_code = parts[-2]
        task_idx = int(parts[-1])
        
        # Проверяем, не дублируется ли запрос с одинаковыми message_id
        if (user_id in user_data and 
            'last_task_request' in user_data[user_id] and 
            message_id is not None):
            last_request = user_data[user_id]['last_task_request']
            if (last_request['world_id'] == world_id and 
                last_request['cat_code'] == cat_code and 
                last_request['task_idx'] == task_idx and
                last_request['message_id'] == message_id and
                (datetime.now().timestamp() - last_request['timestamp']) < 1.0):  # Защита от повторных запросов в течение 1 секунды
                # Это повторный запрос того же задания с тем же message_id - отменяем
                bot.answer_callback_query(
                    call.id, 
                    "Задание уже отображается"
                )
                return
        
        # Сохраняем текущий запрос
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['last_task_request'] = {
            'world_id': world_id,
            'cat_code': cat_code,
            'task_idx': task_idx,
            'message_id': message_id,
            'timestamp': datetime.now().timestamp()
        }
        
        # Получаем информацию о задании
        world_challenges = challenge.get(str(world_id), {})
        category = world_challenges.get(cat_code)
        
        if not category or task_idx >= len(category['tasks']):
            bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
            return
        
        task = category['tasks'][task_idx]
        
        # Получаем ссылку на изображение задания
        photo_url = task['photo']
        if not photo_url.startswith("http"):
            photo_url = f"https://i.imgur.com/{photo_url}.jpeg"  # Формируем URL для imgur
        
        # Создаем клавиатуру
        markup = InlineKeyboardMarkup(row_width=2)
        
        # Кнопки навигации
        # Получаем общее количество задач в категории
        total_tasks = len(category['tasks'])
        
        # Добавляем кнопки навигации
        navigation_buttons = []
        if task_idx > 0:
            navigation_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx-1}"))
        else:
            navigation_buttons.append(InlineKeyboardButton(" ", callback_data="no_action"))
            
        navigation_buttons.append(InlineKeyboardButton(f"{task_idx+1}/{total_tasks}", callback_data="no_action"))
        
        if task_idx < total_tasks - 1:
            navigation_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx+1}"))
        else:
            navigation_buttons.append(InlineKeyboardButton(" ", callback_data="no_action"))
        
        markup.row(*navigation_buttons)
        
        # Кнопка для просмотра решения/подсказки
        markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_solution_{world_id}_{cat_code}_{task_idx}"))
        
        # Получаем избранные задания пользователя
        favorites = get_user_favorites(user_id)
        is_favorite = any(f['challenge_num'] == str(world_id) and f['cat_code'] == cat_code and f['task_idx'] == task_idx for f in favorites)
        
        # Логируем для отладки
        logging.info(f"Задание {world_id}_{cat_code}_{task_idx}, в избранном: {is_favorite}, количество избранных: {len(favorites)}")
        
        # Кнопка для добавления/удаления из избранного
        if is_favorite:
            markup.add(InlineKeyboardButton("🗑 Удалить из избранного", callback_data=f"quest_favorite_remove_{world_id}_{cat_code}_{task_idx}"))
        else:
            markup.add(InlineKeyboardButton("⭐️ Добавить в избранное", callback_data=f"quest_favorite_add_{world_id}_{cat_code}_{task_idx}"))
        
        # Кнопка возврата в меню выбора тем
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_list_{world_id}"))
        
        # Проверяем, решал ли пользователь эту задачу
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status FROM task_progress WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
            (user_id, str(world_id), cat_code, task_idx)
        )
        result = cursor.fetchone()
        conn.close()
        
        status_text = "❔ Не решено"
        answer_text = ""
        if result:
            status = result[0]
            if status == "correct":
                status_text = "✅ Верно"
                # Всегда добавляем правильный ответ, если задача решена правильно и ответ известен
                if 'answer' in task:
                    answer_text = f"\n\nПравильный ответ: {task['answer']}"
                    
                # Обязательно сохраняем в информации для пользователя, что задача уже решена верно
                # это предотвратит случайное изменение статуса при последующих ответах
                if 'user_solutions' not in user_data[user_id]:
                    user_data[user_id]['user_solutions'] = {}
                user_data[user_id]['user_solutions'][f"{world_id}_{cat_code}_{task_idx}"] = "correct"
            elif status == "wrong":
                status_text = "❌ Неверно"
        
        # Отображаем задание
        # Добавляем текст "Введите ответ в чат:" для нерешенных заданий
        # Используем "№6" вместо "Задача N"
        caption = f"№{world_id}\n{category['name']}\n{status_text}{answer_text}"
        if status_text == "❔ Не решено" or status_text == "❌ Неверно":
            caption += "\n\nВведите ответ в чат:"
            
        # Сохраняем ID сообщения для последующего обновления при ответе
        if user_id not in user_data:
            user_data[user_id] = {}
        
        try:
            # Пытаемся редактировать существующее сообщение
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            # Если редактирование прошло успешно, сохраняем ID сообщения
            user_data[user_id]['quest_message_id'] = message_id
        except Exception as e:
            # Если не удалось отредактировать сообщение, отправляем новое
            if "message to edit not found" in str(e) or "message to be edited" in str(e):
                try:
                    # Отправляем новое сообщение
                    new_message = bot.send_photo(
                        chat_id=chat_id,
                        photo=photo_url,
                        caption=caption,
                        reply_markup=markup
                    )
                    # Сохраняем ID нового сообщения
                    user_data[user_id]['quest_message_id'] = new_message.message_id
                    logging.info(f"Отправлено новое сообщение с заданием (message_id={new_message.message_id}) вместо редактирования старого (message_id={message_id})")
                except Exception as send_err:
                    logging.error(f"Не удалось отправить новое сообщение с заданием: {send_err}")
            elif "message is not modified" not in str(e):
                # Логируем ошибку только если это не предупреждение о том, что сообщение не изменилось
                logging.error(f"Ошибка при редактировании сообщения с заданием: {e}")
        
        # Сохраняем информацию о текущем задании пользователя для обработки ответа
        user_data[user_id]['current_task'] = {
            'world_id': world_id,
            'cat_code': cat_code,
            'task_idx': task_idx,
            'answer': task.get('answer')
        }
    except Exception as e:
        logging.error(f"Критическая ошибка в handle_quest_task: {e}")
        try:
            bot.answer_callback_query(call.id, "Произошла ошибка при обработке задания.")
        except:
            pass

def handle_quest_answer(call):
    """Обработчик для ввода ответа на задание"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем параметры из колбэка
    parts = call.data.split('_')
    world_id = int(parts[-3])
    cat_code = parts[-2]
    task_idx = int(parts[-1])
    
    logging.info(f"===== НАЧАЛО ВВОДА ОТВЕТА =====")
    logging.info(f"Запрос на ввод ответа: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")
    
    # Проверяем, решено ли уже задание
    conn = sqlite3.connect('task_progress.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM task_progress WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
        (user_id, str(world_id), cat_code, task_idx)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == 1:
        # Если задание уже решено, просто тихо отвечаем на колбэк без изменения сообщения
        logging.info(f"Пользователь повторно запросил ввод ответа для уже решенного задания")
        bot.answer_callback_query(call.id, "Вы уже решили это задание", show_alert=False)
        return
    
    # Сохраняем состояние пользователя для обработки ответа
    if user_id not in user_data:
        user_data[user_id] = {}
    
    user_data[user_id]['state'] = 'quest_answer'
    user_data[user_id]['quest_world_id'] = world_id
    user_data[user_id]['quest_cat_code'] = cat_code
    user_data[user_id]['quest_task_idx'] = task_idx
    user_data[user_id]['quest_message_id'] = message_id
    user_data[user_id]['current_screen'] = 'quest_task'  # Установка current_screen для обработки ответа
    
    # Получаем информацию о задании
    world_challenges = challenge.get(str(world_id), {})
    category = world_challenges.get(cat_code)
    
    if not category or task_idx >= len(category['tasks']):
        bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
        return
    
    task = category['tasks'][task_idx]
    
    # Получаем ссылку на изображение задания
    photo_url = task['photo']
    if not photo_url.startswith("http"):
        photo_url = f"https://i.imgur.com/{photo_url}.jpeg"  # Формируем URL для imgur
    
    # Отправляем сообщение с запросом ввода ответа
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Отмена", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx}"))
    
    logging.info(f"Отправка формы для ввода ответа на задание")
    
    bot.edit_message_media(
        media=InputMediaPhoto(photo_url, caption=f"📝 {category['name']} - {task.get('title', f'Задание {task_idx+1}')}\n\n✏️ Введите ваш ответ:"),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )

def handle_quest_solution(call):
    """Обработчик для просмотра решения задания"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    logging.info(f"===== ВЫЗОВ ПРОСМОТРА РЕШЕНИЯ: {call.data} =====")
    logging.info(f"Тип данных call.data: {type(call.data)}")
    
    try:
        # Получаем параметры из колбэка
        parts = call.data.split('_')
        logging.info(f"Части callback data для решения: {parts}")
        
        # Проверяем формат данных
        if len(parts) < 4:
            logging.error(f"Неверный формат callback data для просмотра решения: {call.data}")
            bot.answer_callback_query(call.id, "Ошибка при загрузке решения")
            return
            
        world_id = int(parts[-3])
        cat_code = parts[-2]
        task_idx = int(parts[-1])
        logging.info(f"Параметры решения: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")
        
        # ИЗМЕНЕНО: Теперь отмечаем использование подсказки сразу при просмотре решения
        # Это решит проблему с условием "верный ответ + подсказка" для добавления в Ритуал повторения
        logging.info(f"Открыта первая страница подсказки для задачи {world_id}_{cat_code}_{task_idx}")
        
        # Отмечаем, что пользователь использовал подсказку для этой задачи
        # Эта метка будет использоваться при проверке ответа для добавления в "Ритуал повторения"
        if user_id not in user_data:
            user_data[user_id] = {}
        if 'viewed_hints' not in user_data[user_id]:
            user_data[user_id]['viewed_hints'] = {}
            
        # Формируем ключ для отслеживания использования подсказки
        task_key = f"{world_id}_{cat_code}_{task_idx}"
        user_data[user_id]['viewed_hints'][task_key] = True
        
        # Сохраняем состояние в долговременную память - критически важно для работы "Ритуала повторения"
        save_user_data(user_id)
        
        logging.info(f"⚠️ Отмечено использование подсказки для задачи {task_key} пользователем {user_id}")
        logging.info(f"✅✅✅ Сохранен флаг использования подсказки для задачи {task_key} пользователем {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при разборе callback data для решения: {e}, данные: {call.data}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке решения")
        return
    
    # Получаем информацию о задании
    world_challenges = challenge.get(str(world_id), {})
    category = world_challenges.get(cat_code)
    
    if not category or task_idx >= len(category['tasks']):
        bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
        return
    
    task = category['tasks'][task_idx]
    
    # Проверяем наличие подсказок/решения
    if not task.get('hint'):
        bot.answer_callback_query(call.id, "Решение для этого задания недоступно")
        return
    
    # Получаем первую подсказку (шаг решения)
    hint_url = task['hint'][0]
    if not hint_url.startswith("http"):
        hint_url = f"https://i.imgur.com/{hint_url}.jpeg"  # Формируем URL для imgur
    
    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Кнопки навигации по шагам решения
    if len(task['hint']) > 1:
        # Первая кнопка будет пустой, т.к. это первый шаг
        prev_button = InlineKeyboardButton(" ", callback_data=f"quest_empty")
        
        # Важная модификация: используем строковый формат для всех компонентов,
        # включая числовые значения. Это необходимо для корректной обработки.
        step = "0"  # Используем строку вместо числа
        next_callback = f"quest_hint_next_{world_id}_{cat_code}_{task_idx}_{step}"
        
        # Отладочная информация для контроля правильности данных
        logging.info(f"ПОДСКАЗКИ: создаем кнопки навигации. Всего шагов: {len(task['hint'])}")
        logging.info(f"ПАРАМЕТРЫ КНОПКИ: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}, step={step}")
        logging.info(f"КНОПКА ВПЕРЕД: {next_callback}")
        logging.info(f"ДЛИНА: длина callback_data = {len(next_callback)}")
        logging.info(f"СОСТАВ: {next_callback.split('_')}")
        
        # Создаем кнопку с правильно сформированным callback_data
        next_button = InlineKeyboardButton("▶️", callback_data=next_callback)
        markup.add(prev_button, next_button)
    
    # Кнопка возврата
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx}"))
    
    try:
        # Пытаемся редактировать существующее сообщение
        bot.edit_message_media(
            media=InputMediaPhoto(hint_url, caption=f"💡 Подсказка - Шаг 1/{len(task['hint'])}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        # Если редактирование прошло успешно, сохраняем ID сообщения
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['quest_message_id'] = message_id
    except Exception as e:
        # Если не удалось отредактировать сообщение, отправляем новое
        if "message to edit not found" in str(e) or "message to be edited" in str(e):
            try:
                # Отправляем новое сообщение с подсказкой
                new_message = bot.send_photo(
                    chat_id=chat_id,
                    photo=hint_url,
                    caption=f"💡 Подсказка - Шаг 1/{len(task['hint'])}",
                    reply_markup=markup
                )
                # Сохраняем ID нового сообщения для последующих обновлений
                if user_id not in user_data:
                    user_data[user_id] = {}
                user_data[user_id]['quest_message_id'] = new_message.message_id
                logging.info(f"Отправлено новое сообщение с решением (message_id={new_message.message_id}) вместо редактирования старого (message_id={message_id})")
            except Exception as send_err:
                logging.error(f"Не удалось отправить новое сообщение с решением: {send_err}")
                bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте вернуться к списку заданий и начать заново.")
        elif "message is not modified" not in str(e):
            # Логируем ошибку только если это не предупреждение о том, что сообщение не изменилось
            logging.error(f"Ошибка при отображении решения: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка при загрузке решения.")

def handle_hint_direct(call):
    """Обработчик прямого перехода к шагу решения/подсказки"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    logging.info(f"++++ ОБРАБОТКА ПРЯМОГО ПЕРЕХОДА: {call.data} ++++")
    
    try:
        # Получаем параметры из колбэка
        parts = call.data.split('_')
        logging.info(f"Части callback data прямого перехода: {parts}")
        
        # Проверка формата данных
        if len(parts) < 7:
            logging.error(f"ОШИБКА: Неверный формат callback data для прямого перехода: {call.data}")
            bot.answer_callback_query(call.id, "Ошибка формата данных для навигации")
            return
            
        # Извлекаем параметры
        world_id = int(parts[3])
        cat_code = parts[4]
        task_idx = int(parts[5])
        target_step = int(parts[6])
        
        logging.info(f"ПАРАМЕТРЫ: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}, target_step={target_step}")
        
        # Получаем данные задания
        world_challenges = challenge.get(str(world_id), {})
        category = world_challenges.get(cat_code, {})
        
        if not category or 'tasks' not in category:
            logging.error(f"ОШИБКА: Категория не найдена: {cat_code} в мире {world_id}")
            bot.answer_callback_query(call.id, "Категория задания не найдена")
            return
            
        if task_idx >= len(category['tasks']):
            logging.error(f"ОШИБКА: Индекс задания вне диапазона: {task_idx} >= {len(category['tasks'])}")
            bot.answer_callback_query(call.id, "Задание не найдено")
            return
        
        # Получаем задание
        task = category['tasks'][task_idx]
        
        # Проверяем наличие подсказок
        if not task.get('hint'):
            logging.error(f"ОШИБКА: У задания нет подсказок")
            bot.answer_callback_query(call.id, "У задания нет подсказок")
            return
        
        total_steps = len(task['hint'])
        
        if target_step >= total_steps:
            logging.error(f"ОШИБКА: Шаг подсказки вне диапазона: {target_step} >= {total_steps}")
            bot.answer_callback_query(call.id, "Шаг подсказки не найден")
            return
        
        logging.info(f"ПЕРЕХОД: на шаг {target_step} из {total_steps} шагов")
        
        # Получаем URL изображения
        hint_url = task['hint'][target_step]
        if not hint_url.startswith("http"):
            hint_url = f"https://i.imgur.com/{hint_url}.jpeg"
        
        logging.info(f"URL подсказки: {hint_url}")
        
        # Создаем клавиатуру
        markup = InlineKeyboardMarkup(row_width=2)
        
        # Кнопки навигации
        prev_callback = f"quest_hint_prev_{world_id}_{cat_code}_{task_idx}_{target_step}"
        next_callback = f"quest_hint_next_{world_id}_{cat_code}_{task_idx}_{target_step}"
        
        # Если первый шаг - кнопка "назад" пустая
        if target_step == 0:
            prev_button = InlineKeyboardButton(" ", callback_data="quest_empty")
            logging.info("Первый шаг - кнопка назад пустая")
        else:
            prev_button = InlineKeyboardButton("◀️", callback_data=prev_callback)
        
        # Если последний шаг - кнопка "вперед" пустая
        if target_step == total_steps - 1:
            next_button = InlineKeyboardButton(" ", callback_data="quest_empty")
            logging.info("Последний шаг - кнопка вперед пустая")
        else:
            next_button = InlineKeyboardButton("▶️", callback_data=next_callback)
        
        # Добавляем кнопки
        markup.add(prev_button, next_button)
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx}"))
        
        # Отправляем сообщение
        try:
            logging.info(f"Отправляем изображение: {hint_url} с caption: 💡 Подсказка - Шаг {target_step+1}/{total_steps}")
            
            bot.edit_message_media(
                media=InputMediaPhoto(hint_url, caption=f"💡 Подсказка - Шаг {target_step+1}/{total_steps}"),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['quest_message_id'] = message_id
            
            # Отмечаем, что пользователь использовал подсказку для этой задачи
            try:
                # Создаем ключ для отслеживания использования подсказки
                task_key = f"{world_id}_{cat_code}_{task_idx}"
                
                # Инициализируем структуру данных, если она еще не существует
                if 'viewed_hints' not in user_data[user_id]:
                    user_data[user_id]['viewed_hints'] = {}
                
                # Отмечаем, что пользователь просмотрел подсказку
                user_data[user_id]['viewed_hints'][task_key] = True
                
                logging.info(f"Отмечено использование подсказки для задачи {task_key} пользователем {user_id}")
                logging.info(f"ОТЛАДКА ПОДСКАЗОК: текущие подсказки для пользователя {user_id}: {user_data[user_id]['viewed_hints']}")
                
                # Сохраняем состояние подсказок в долговременной памяти (сериализация)
                # Это критически важно для корректной работы "Ритуала повторения"
                save_user_data(user_id)
                
                # Дополнительное сообщение для отладки
                logging.info(f"✅✅✅ Сохранен флаг использования подсказки для задачи {task_key} пользователем {user_id}")
                
                # Теперь не добавляем задачу в домашнюю работу сразу.
                # Это будет сделано только при ответе на задачу в handle_task_answer
                # согласно новым правилам: верно+подсказка, неверно+подсказка, неверно без подсказки
            except Exception as err:
                logging.error(f"Ошибка при отметке использования подсказки: {err}")
            
            logging.info(f"УСПЕХ: Сообщение обновлено, показан шаг {target_step+1}")
            
        except Exception as e:
            logging.error(f"ОШИБКА редактирования сообщения: {e}")
            
            # Если сообщение не найдено, отправляем новое
            if "message to edit not found" in str(e) or "message to be edited" in str(e):
                try:
                    new_message = bot.send_photo(
                        chat_id=chat_id,
                        photo=hint_url,
                        caption=f"💡 Подсказка - Шаг {target_step+1}/{total_steps}",
                        reply_markup=markup
                    )
                    
                    if user_id not in user_data:
                        user_data[user_id] = {}
                    user_data[user_id]['quest_message_id'] = new_message.message_id
                    
                    logging.info(f"УСПЕХ: Отправлено новое сообщение, показан шаг {target_step+1}")
                    
                except Exception as send_err:
                    logging.error(f"ОШИБКА отправки нового сообщения: {send_err}")
                    bot.answer_callback_query(call.id, "Ошибка отправки сообщения")
            elif "message is not modified" not in str(e):
                logging.error(f"ОШИБКА обновления сообщения: {e}")
                bot.answer_callback_query(call.id, "Ошибка обновления сообщения")
                
    except Exception as e:
        logging.error(f"КРИТИЧЕСКАЯ ОШИБКА обработки перехода: {e}")
        import traceback
        logging.error(traceback.format_exc())
        bot.answer_callback_query(call.id, "Произошла ошибка при обработке")

def handle_quest_hint_navigation(call):
    """Обработчик навигации по шагам решения/подсказкам"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    logging.info(f"======== НАВИГАЦИЯ ПО ПОДСКАЗКАМ =======")
    logging.info(f"ДАННЫЕ: {call.data}")
    logging.info(f"ТИП: {type(call.data)}")
    logging.info(f"ДЛИНА: {len(call.data)}")
    
    try:
        # Получаем параметры из колбэка
        parts = call.data.split('_')
        logging.info(f"РАЗБОР: {parts}")
        
        # Проверяем достаточно ли частей в колбэке
        if len(parts) < 7:
            logging.error(f"ОШИБКА ФОРМАТА: {call.data} - недостаточно частей")
            bot.answer_callback_query(call.id, "Ошибка формата данных")
            return
        
        # Извлекаем параметры
        action = parts[2]  # next или prev
        world_id = int(parts[3])
        cat_code = parts[4]
        task_idx = int(parts[5])
        
        # Важно: преобразуем текущий шаг в целое число 
        # и проверяем корректность преобразования
        try:
            current_step = int(parts[6])
            logging.info(f"ТЕКУЩИЙ ШАГ: {current_step} (успешно преобразован)")
        except ValueError:
            logging.error(f"ОШИБКА ПРЕОБРАЗОВАНИЯ: {parts[6]} не является числом")
            bot.answer_callback_query(call.id, "Ошибка формата шага")
            return
        
        # Отмечаем, что пользователь использовал подсказку для этой задачи
        # Эта метка будет использоваться при проверке ответа для добавления в "Ритуал повторения"
        if user_id not in user_data:
            user_data[user_id] = {}
        if 'viewed_hints' not in user_data[user_id]:
            user_data[user_id]['viewed_hints'] = {}
            
        # Формируем ключ для отслеживания использования подсказки
        task_key = f"{world_id}_{cat_code}_{task_idx}"
        user_data[user_id]['viewed_hints'][task_key] = True
        
        # Сохраняем состояние в долговременную память - критически важно для работы "Ритуала повторения"
        save_user_data(user_id)
        
        logging.info(f"⚠️ Отмечено использование подсказки для задачи {task_key} пользователем {user_id}")
        logging.info(f"✅✅✅ Сохранен флаг использования подсказки для задачи {task_key} пользователем {user_id}")
        
        # Уведомляем пользователя только при первом просмотре подсказки
        # чтобы не спамить сообщениями при переходе между шагами
        # Убрано уведомление о добавлении задачи в "Ритуал повторения"
        # Пользователь видит только подсказку, без дополнительных сообщений
        # Сохраняем информацию о текущей задаче для корректного возврата
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['current_task'] = {
            "challenge_num": str(world_id),
            "cat_code": cat_code,
            "task_idx": task_idx,
            "screen": "quest_task"
        }
        logging.info(f"Сохранен текущий контекст задачи для пользователя {user_id}")
        
        logging.info(f"ПАРАМЕТРЫ: action={action}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}, current_step={current_step}")
    except Exception as e:
        logging.error(f"ОШИБКА при разборе данных: {e}, данные: {call.data}")
        bot.answer_callback_query(call.id, "Ошибка разбора данных")
        return
    
    # Получаем информацию о задании
    world_challenges = challenge.get(str(world_id), {})
    category = world_challenges.get(cat_code, {})
    
    if not category or 'tasks' not in category:
        logging.error(f"ОШИБКА: Категория не найдена: {cat_code} в мире {world_id}")
        bot.answer_callback_query(call.id, "Категория не найдена")
        return
        
    if task_idx >= len(category['tasks']):
        logging.error(f"ОШИБКА: Индекс задания вне диапазона: {task_idx} >= {len(category['tasks'])}")
        bot.answer_callback_query(call.id, "Задание не найдено")
        return
    
    task = category['tasks'][task_idx]
    
    # Проверяем наличие подсказок
    if not task.get('hint'):
        logging.error(f"ОШИБКА: У задания нет подсказок")
        bot.answer_callback_query(call.id, "У задания нет подсказок")
        return
    
    total_steps = len(task['hint'])
    
    if total_steps <= 1:
        logging.error(f"ОШИБКА: У задания только одна подсказка")
        bot.answer_callback_query(call.id, "Нет дополнительных шагов")
        return
    
    # Вычисляем новый шаг
    new_step = current_step
    
    # Добавим подробное логирование для отладки
    logging.info(f"ТЕКУЩИЙ ШАГ: {current_step}, ВСЕГО ШАГОВ: {total_steps}")
    
    # Проверяем возможность перехода
    if action == "next":
        if current_step < total_steps - 1:
            new_step = current_step + 1
            logging.info(f"ПЕРЕХОД: Вперед с шага {current_step} на {new_step}")
            # Пишем подробную информацию о шагах
            logging.info(f"ПОДСКАЗКИ: {len(task['hint'])} шт, текущий шаг: {current_step}, новый шаг: {new_step}")
            
            # ИСПРАВЛЕНИЕ: При переходе к следующему шагу подсказки НЕ добавляем задачу в домашнюю работу
            # Теперь задачи добавляются в домашнюю работу только при ответе пользователя
            # согласно правилам: 
            # 1. Верный ответ + подсказка -> Добавить в домашние задания
            # 2. Неверный ответ (с подсказкой или без) -> Добавить в домашние задания
            # 3. Верный ответ без подсказки -> НЕ добавлять в домашние задания
            
            # Проверяем текущий статус задачи для логирования
            try:
                conn = sqlite3.connect('task_progress.db')
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT status FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
                """, (user_id, str(world_id), cat_code, task_idx))
                result = cursor.fetchone()
                
                # Только логирование для отладки
                main_status = result[0] if result else None
                logging.info(f"ВАЖНО: При навигации подсказок - текущий статус задачи {world_id}_{cat_code}_{task_idx}: {main_status}")
                
                conn.close()
                logging.info(f"✅ Просмотр подсказки для задачи {world_id}_{cat_code}_{task_idx} отмечен в профиле пользователя {user_id}")
            except Exception as e:
                logging.error(f"Ошибка при логировании использования подсказки: {e}")
        else:
            logging.error(f"ОШИБКА: Невозможно перейти вперед, уже последний шаг ({current_step}/{total_steps-1})")
            bot.answer_callback_query(call.id, "Это последний шаг")
            return
    elif action == "prev":
        if current_step > 0:
            new_step = current_step - 1
            logging.info(f"ПЕРЕХОД: Назад с шага {current_step} на {new_step}")
        else:
            logging.error(f"ОШИБКА: Невозможно перейти назад, уже первый шаг")
            bot.answer_callback_query(call.id, "Это первый шаг")
            return
    else:
        logging.error(f"ОШИБКА: Неизвестное действие: {action}")
        bot.answer_callback_query(call.id, "Неизвестное действие")
        return
    
    logging.info(f"РЕЗУЛЬТАТ: Переход с шага {current_step} на шаг {new_step} из {total_steps} шагов")
    
    # Получаем URL изображения для нового шага
    hint_url = task['hint'][new_step]
    if not hint_url.startswith("http"):
        hint_url = f"https://i.imgur.com/{hint_url}.jpeg"
    
    logging.info(f"URL подсказки: {hint_url}")
    
    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Кнопки навигации
    # Используем строковый формат для шага
    str_step = str(new_step)
    logging.info(f"ШАГ КАК СТРОКА: {str_step}")
    
    prev_callback = f"quest_hint_prev_{world_id}_{cat_code}_{task_idx}_{str_step}"
    next_callback = f"quest_hint_next_{world_id}_{cat_code}_{task_idx}_{str_step}"
    
    # Добавление задачи в домашнюю работу выполнено ранее в коде, не нужно делать это повторно
    
    logging.info(f"CALLBACK PREV: {prev_callback}, ДЛИНА: {len(prev_callback)}")
    logging.info(f"CALLBACK NEXT: {next_callback}, ДЛИНА: {len(next_callback)}")
    
    # Если первый шаг - кнопка "назад" пустая
    if new_step == 0:
        prev_button = InlineKeyboardButton(" ", callback_data="quest_empty")
        logging.info("Первый шаг - кнопка назад пустая")
    else:
        prev_button = InlineKeyboardButton("◀️", callback_data=prev_callback)
        logging.info(f"Кнопка НАЗАД: {prev_callback}")
    
    # Если последний шаг - кнопка "вперед" пустая
    if new_step == total_steps - 1:
        next_button = InlineKeyboardButton(" ", callback_data="quest_empty")
        logging.info("Последний шаг - кнопка вперед пустая")
    else:
        next_button = InlineKeyboardButton("▶️", callback_data=next_callback)
        logging.info(f"Кнопка ВПЕРЕД: {next_callback}")
    
    # Добавляем кнопки
    markup.add(prev_button, next_button)
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx}"))
    
    try:
        logging.info(f"Отправляем изображение: {hint_url} с caption: 💡 Подсказка - Шаг {new_step+1}/{total_steps}")
        
        bot.edit_message_media(
            media=InputMediaPhoto(hint_url, caption=f"💡 Подсказка - Шаг {new_step+1}/{total_steps}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['quest_message_id'] = message_id
        
        logging.info(f"УСПЕХ: Сообщение обновлено, показан шаг {new_step+1}")
        
    except Exception as e:
        logging.error(f"ОШИБКА редактирования сообщения: {e}")
        
        # Если сообщение не найдено, отправляем новое
        if "message to edit not found" in str(e) or "message to be edited" in str(e):
            try:
                new_message = bot.send_photo(
                    chat_id=chat_id,
                    photo=hint_url,
                    caption=f"💡 Подсказка - Шаг {new_step+1}/{total_steps}",
                    reply_markup=markup
                )
                
                if user_id not in user_data:
                    user_data[user_id] = {}
                user_data[user_id]['quest_message_id'] = new_message.message_id
                
                logging.info(f"УСПЕХ: Отправлено новое сообщение с шагом {new_step+1}")
                
            except Exception as send_err:
                logging.error(f"ОШИБКА отправки нового сообщения: {send_err}")
                bot.answer_callback_query(call.id, "Ошибка отправки сообщения")
        elif "message is not modified" not in str(e):
            logging.error(f"ОШИБКА обновления сообщения: {e}")
            bot.answer_callback_query(call.id, "Ошибка обновления сообщения")

def handle_quest_favorite(call):
    """Обработчик добавления/удаления задания в/из избранное(го)"""
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    
    # Получаем параметры из колбэка
    parts = call.data.split('_')
    
    # Проверяем, содержит ли callback_data "view" - это для просмотра избранного
    if "view" in parts:
        logging.info(f"Перенаправляем на соответствующий обработчик: {call.data}")
        # Перенаправляем на соответствующий обработчик
        if "ordered" in parts:
            handle_quest_favorite_view_ordered(call)
        elif "random" in parts:
            handle_quest_favorite_view_random(call)
        elif "by_category" in parts:
            handle_quest_favorite_view_by_category(call)
        return
    
    try:
        # Новый формат: quest_favorite_[challenge_num]_[cat_code]_[task_idx]
        # Используем для переключения добавления/удаления из избранного при просмотре избранного
        if len(parts) >= 5 and not parts[2] in ["add", "remove"]:
            challenge_num = parts[2]
            cat_code = parts[3] 
            task_idx = int(parts[4])
            
            # Проверяем, находится ли задание в избранном
            favorites = get_user_favorites(user_id)
            is_favorite = False
            
            for fav in favorites:
                if fav['challenge_num'] == challenge_num and fav['cat_code'] == cat_code and int(fav['task_idx']) == task_idx:
                    is_favorite = True
                    break
            
            if is_favorite:
                # Удаляем из избранного
                conn = sqlite3.connect('favorites.db')
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM favorites WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
                    (user_id, challenge_num, cat_code, task_idx)
                )
                rows_affected = cursor.rowcount
                conn.commit()
                conn.close()
                
                bot.answer_callback_query(call.id, "✅ Задание удалено из избранного")
                logging.info(f"Задание удалено из избранного: user_id={user_id}, world_id={challenge_num}, cat_code={cat_code}, task_idx={task_idx}, rows_affected={rows_affected}")
                
                # Обновляем список избранных заданий и переходим на следующее задание если возможно
                favorites = get_user_favorites(user_id)
                tasks = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in favorites]
                if user_id in user_data:
                    user_data[user_id]["favorite_tasks"] = tasks
                    if not tasks:  # Если заданий больше нет
                        world_id = user_data[user_id].get("current_world_id", "")
                        markup = InlineKeyboardMarkup().add(
                            InlineKeyboardButton("↩️ Назад", callback_data=f"quest_favorite_world_{world_id}")
                        )
                        bot.edit_message_media(
                            media=InputMediaPhoto(photo_quest_main, caption="⭐ Избранные задания\n\nВ вашем избранном не осталось заданий для этого мира."),
                            chat_id=chat_id,
                            message_id=call.message.message_id,
                            reply_markup=markup
                        )
                        return
                    # Если индекс выходит за пределы нового списка, корректируем его
                    current_index = user_data[user_id].get("current_index", 0)
                    if current_index >= len(tasks):
                        user_data[user_id]["current_index"] = max(0, len(tasks) - 1)
                
                # Отображаем текущее задание
                send_favorite_task(chat_id, call.message.message_id)
            else:
                # В режиме просмотра избранного этот случай не должен происходить,
                # но добавляем обработку на всякий случай
                conn = sqlite3.connect('favorites.db')
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO favorites (user_id, challenge_num, cat_code, task_idx) VALUES (?, ?, ?, ?)",
                        (user_id, challenge_num, cat_code, task_idx)
                    )
                    conn.commit()
                    bot.answer_callback_query(call.id, "✅ Задание добавлено в избранное")
                    logging.info(f"Задание добавлено в избранное: user_id={user_id}, world_id={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
                except sqlite3.IntegrityError:
                    bot.answer_callback_query(call.id, "⚠️ Задание уже в избранном")
                    logging.warning(f"Задание уже в избранном: user_id={user_id}, world_id={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
                finally:
                    conn.close()
                
                # Обновляем список избранных заданий
                favorites = get_user_favorites(user_id)
                tasks = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in favorites]
                if user_id in user_data:
                    user_data[user_id]["favorite_tasks"] = tasks
                
                # Отображаем текущее задание
                send_favorite_task(chat_id, call.message.message_id)
            
            return
        
        # Старый формат с явным указанием действия
        action = parts[2]  # add или remove
        world_id = int(parts[-3])
        cat_code = parts[-2]
        task_idx = int(parts[-1])
        
        # Лог для отладки
        logging.info(f"Обработка избранного: action={action}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")
        
        if action == "add":
            # Добавляем задание в избранное
            conn = sqlite3.connect('favorites.db')
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO favorites (user_id, challenge_num, cat_code, task_idx) VALUES (?, ?, ?, ?)",
                    (user_id, str(world_id), cat_code, task_idx)
                )
                conn.commit()
                bot.answer_callback_query(call.id, "✅ Задание добавлено в избранное")
                logging.info(f"Задание добавлено в избранное: user_id={user_id}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")
            except sqlite3.IntegrityError:
                bot.answer_callback_query(call.id, "⚠️ Задание уже в избранном")
                logging.warning(f"Задание уже в избранном: user_id={user_id}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")
            finally:
                conn.close()
        else:  # remove
            # Удаляем задание из избранного
            conn = sqlite3.connect('favorites.db')
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM favorites WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
                (user_id, str(world_id), cat_code, task_idx)
            )
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            bot.answer_callback_query(call.id, "✅ Задание удалено из избранного")
            logging.info(f"Задание удалено из избранного: user_id={user_id}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}, rows_affected={rows_affected}")
        
        # Обновляем отображение задания
        handle_quest_task(call)
    except Exception as e:
        logging.error(f"Ошибка при обработке избранного: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при обработке избранного задания")

def handle_quest_favorites_with_simple_animation(call):
    """Обработчик просмотра избранных заданий в квесте с простой анимацией загрузки"""
    from instance import photo_quest_main
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    import time
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Сначала отображаем анимацию загрузки
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n0%\nПодготовка данных..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)
        
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n25%\nПолучение списка заданий..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)
        
        # Фото для экрана избранного
        favorites_image = "https://imgur.com/b9u6HER.jpg"
        
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n50%\nОбработка избранных заданий..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)
        
        # Получаем избранные задания пользователя
        favorites = get_user_favorites(user_id)
        logging.info(f"Получено избранное для user_id={user_id}: {len(favorites)} задач")
        
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n75%\nФормирование интерфейса..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)
        
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n100%\nЗавершение..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)
        
        if not favorites:
            # Если у пользователя нет избранных заданий
            bot.edit_message_media(
                media=InputMediaPhoto(favorites_image, caption="⭐ Избранные задания\n\nУ вас пока нет избранных заданий.\nДобавьте задания в избранное, нажав на звёздочку в задачах квеста."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call")
                )
            )
            return
            
        # Группируем задания по мирам
        grouped = {}
        for item in favorites:
            world_id = item['challenge_num']
            if world_id not in grouped:
                grouped[world_id] = []
            grouped[world_id].append(item)
        
        logging.info(f"Обработка избранного для пользователя {user_id}. Найдено {len(favorites)} заданий")
        logging.info(f"Сгруппировано по мирам: {list(grouped.keys())}")
        
        # Создаем клавиатуру для выбора мира
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для каждого мира
        for world_id in sorted(grouped.keys()):
            # Находим информацию о мире в списке миров
            try:
                world_id_int = int(world_id)
                world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
            except ValueError:
                world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id), None)
                
            if world:
                # Используем имя мира из списка
                world_name = world["name"]
                count = len(grouped[world_id])
                markup.add(InlineKeyboardButton(
                    f"🌍 {world_name} ({count})",
                    callback_data=f"quest_favorite_world_{world_id}"
                ))
                logging.info(f"Добавлена кнопка для мира {world_id}: {world_name} ({count})")
            else:
                # Если мир не найден, используем ID как имя
                count = len(grouped[world_id])
                markup.add(InlineKeyboardButton(
                    f"🌍 {world_id}. Мир ({count})",
                    callback_data=f"quest_favorite_world_{world_id}"
                ))
                logging.warning(f"Мир с ID {world_id} не найден в списке миров")
        
        # Кнопка возврата
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call"))
        
        # Отображаем окончательный экран с избранными заданиями
        bot.edit_message_media(
            media=InputMediaPhoto(favorites_image, caption="⭐ Избранные задания\n\nВыберите мир для просмотра избранных заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображен список избранных заданий для пользователя {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при обработке избранных заданий: {e}")
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo_quest_main, caption="Произошла ошибка при загрузке избранных заданий. Пожалуйста, попробуйте позже."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call")
                )
            )
        except Exception as e2:
            logging.error(f"Не удалось отобразить сообщение об ошибке: {e2}")

# Сохраняем старую функцию для обратной совместимости
def handle_quest_favorites_no_animation(call):
    """Обработчик просмотра избранных заданий в квесте без анимации загрузки"""
    from instance import photo_quest_main
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Фото для экрана избранного
        favorites_image = "https://imgur.com/b9u6HER.jpg"
        
        # Получаем избранные задания пользователя
        favorites = get_user_favorites(user_id)
        logging.info(f"Получено избранное для user_id={user_id}: {len(favorites)} задач")
        
        if not favorites:
            # Если у пользователя нет избранных заданий
            bot.edit_message_media(
                media=InputMediaPhoto(favorites_image, caption="⭐ Избранные задания\n\nУ вас пока нет избранных заданий.\nДобавьте задания в избранное, нажав на звёздочку в задачах квеста."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call")
                )
            )
            return
            
        # Группируем задания по мирам
        grouped = {}
        for item in favorites:
            world_id = item['challenge_num']
            if world_id not in grouped:
                grouped[world_id] = []
            grouped[world_id].append(item)
        
        logging.info(f"Обработка избранного для пользователя {user_id}. Найдено {len(favorites)} заданий")
        logging.info(f"Сгруппировано по мирам: {list(grouped.keys())}")
        
        # Создаем клавиатуру для выбора мира
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для каждого мира
        for world_id in sorted(grouped.keys()):
            # Находим информацию о мире в списке миров
            try:
                world_id_int = int(world_id)
                world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
            except ValueError:
                world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id), None)
                
            if world:
                # Используем имя мира из списка
                world_name = world["name"]
                count = len(grouped[world_id])
                markup.add(InlineKeyboardButton(
                    f"🌍 {world_name} ({count})",
                    callback_data=f"quest_favorite_world_{world_id}"
                ))
                logging.info(f"Добавлена кнопка для мира {world_id}: {world_name} ({count})")
            else:
                # Если мир не найден, используем ID как имя
                count = len(grouped[world_id])
                markup.add(InlineKeyboardButton(
                    f"🌍 {world_id}. Мир ({count})",
                    callback_data=f"quest_favorite_world_{world_id}"
                ))
                logging.warning(f"Мир с ID {world_id} не найден в списке миров")
        
        # Кнопка возврата
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call"))
        
        # Отображаем окончательный экран с избранными заданиями
        bot.edit_message_media(
            media=InputMediaPhoto(favorites_image, caption="⭐ Избранные задания\n\nВыберите мир для просмотра избранных заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображен список избранных заданий для пользователя {user_id}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке избранных заданий: {e}")
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(favorites_image, caption="Произошла ошибка при загрузке избранных заданий. Пожалуйста, попробуйте позже."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call")
                )
            )
        except Exception as e2:
            logging.error(f"Не удалось отобразить сообщение об ошибке: {e2}")

# Обработчик для просмотра избранных заданий с красивой анимацией загрузки
def handle_quest_favorites(call):
    """Обработчик просмотра избранных заданий в квесте с красивой анимацией загрузки"""
    from instance import photo_quest_main
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Фото для экрана избранного - всегда определяем, чтобы избежать предупреждений LSP
        favorites_image = "https://imgur.com/b9u6HER.jpg"
        import time
        
        # Первый этап загрузки
        loading_text_1 = "[███░░░░░░░░░░░░░░░░] 17% \nСобираем данные избранных заданий..."
        bot.edit_message_media(
            media=InputMediaPhoto(favorites_image, caption=loading_text_1),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.7)
        
        # Второй этап загрузки
        loading_text_2 = "[██████░░░░░░░░░░░░] 33%\nАнализируем ваши предпочтения..."
        bot.edit_message_caption(
            caption=loading_text_2,
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.7)
        
        # Третий этап загрузки
        loading_text_3 = "[█████████░░░░░░░░░] 51% \nГотовим материалы к просмотру..."
        bot.edit_message_caption(
            caption=loading_text_3,
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.7)
        
        # Четвертый этап загрузки
        loading_text_4 = "[████████████░░░░░░] 68% \nФормируем структуру навигации..."
        bot.edit_message_caption(
            caption=loading_text_4,
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.7)
        
        # Пятый этап загрузки
        loading_text_5 = "[███████████████░░] 85%\nПочти готово, ещё немного..."
        bot.edit_message_caption(
            caption=loading_text_5,
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.7)
        
        # Последний этап загрузки
        loading_text_6 = "[█████████████████] 100% \nВсё готово! Открываем избранное..."
        bot.edit_message_caption(
            caption=loading_text_6,
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.5)
        
        # Получаем список избранных заданий
        favorites = get_user_favorites(user_id)
        
        if not favorites:
            # Если избранных заданий нет
            bot.answer_callback_query(call.id, "У вас пока нет избранных заданий")
            # Обновляем сообщение, чтобы сообщить об отсутствии избранных заданий
            bot.edit_message_caption(
                caption="⭐ Избранные задания\n\nВ вашем избранном пока нет сохраненных заданий.\n\nЧтобы добавить задание в избранное, нажмите на звездочку в меню задания.",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="quest_back_to_worlds"))
            )
            return
        
        # Отладочная информация
        logging.info(f"Обработка избранного для пользователя {user_id}. Найдено {len(favorites)} заданий")
        
        # Группируем избранные задания по мирам
        favorited_by_world = {}
        for fav in favorites:
            world_id_str = fav['challenge_num']
            if world_id_str not in favorited_by_world:
                favorited_by_world[world_id_str] = []
            favorited_by_world[world_id_str].append(fav)
        
        # Отладочная информация
        logging.info(f"Сгруппировано по мирам: {list(favorited_by_world.keys())}")
        
        # Создаем клавиатуру для выбора мира с избранными заданиями
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для миров с избранными заданиями
        for world_id_str in favorited_by_world:
            # Преобразуем строковый world_id в число для поиска в QUEST_WORLDS
            try:
                world_id_int = int(world_id_str)
                world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
                
                if world:
                    # Формируем название мира без дублирования иконки 🌍
                    raw_name = world['name'].replace('🌍 ' + str(world_id_int) + '. ', '')
                    world_name = f"🌍 {world_id_int}. {raw_name}"
                    button_text = world_name
                    
                    markup.add(InlineKeyboardButton(
                        button_text,
                        callback_data=f"quest_favorite_world_{world_id_int}"
                    ))
                    logging.info(f"Добавлена кнопка для мира {world_id_str}: {button_text}")
                else:
                    # Если мир не найден, используем ID как название
                    markup.add(InlineKeyboardButton(
                        f"🌍 Мир {world_id_str}",
                        callback_data=f"quest_favorite_world_{world_id_str}"
                    ))
                    logging.warning(f"Мир с ID {world_id_str} не найден в QUEST_WORLDS")
            except ValueError:
                # Если не удалось преобразовать ID в число
                logging.error(f"Не удалось преобразовать ID мира {world_id_str} в число")
                markup.add(InlineKeyboardButton(
                    f"🌍 Мир {world_id_str}",
                    callback_data=f"quest_favorite_world_{world_id_str}"
                ))
        
        # Кнопка возврата
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_back_to_worlds"))
        
        # Небольшая задержка для имитации загрузки
        import time
        time.sleep(0.5)
        
        # Отображаем список миров с избранными заданиями
        header_text = "⭐ Избранные задания"
        subheader_text = "Здесь собраны ваши избранные задания из всех миров"
        description_text = "Выберите мир для просмотра избранных заданий:"
        
        caption = f"{header_text}\n\n{subheader_text}\n\n{description_text}"
        
        bot.edit_message_media(
            media=InputMediaPhoto("https://imgur.com/b9u6HER.jpg", caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображен список избранных заданий для пользователя {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при отображении избранных заданий: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки избранных заданий.")

def handle_quest_favorite_world(call):
    """Обработчик просмотра избранных заданий конкретного мира"""
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Получаем ID мира из колбэка
        world_id_str = call.data.split("_")[-1]
        
        try:
            # Пробуем преобразовать в число, так как в QUEST_WORLDS id хранятся как числа
            world_id_int = int(world_id_str)
            world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
        except ValueError:
            # Если не удалось преобразовать в число, пытаемся найти мир с id в строковом формате
            logging.warning(f"Не удалось преобразовать world_id {world_id_str} в число")
            world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id_str), None)
        
        if not world:
            bot.answer_callback_query(call.id, "Ошибка: мир не найден")
            logging.error(f"Мир с ID {world_id_str} не найден в QUEST_WORLDS")
            return
        
        # Используем строковое представление world_id для сравнения с challenge_num из БД
        world_id_for_db = str(world["id"])
        
        # Получаем избранные задания для этого мира
        all_favorites = get_user_favorites(user_id)
        logging.info(f"Получены все избранные задания для пользователя {user_id}: {len(all_favorites)}")
        
        # Фильтруем задания для текущего мира, с преобразованием типов
        world_favorites = [f for f in all_favorites if f['challenge_num'] == world_id_for_db]
        logging.info(f"Отфильтрованы задания для мира {world_id_for_db}: {len(world_favorites)}")
        
        if not world_favorites:
            bot.answer_callback_query(call.id, "Нет избранных заданий в этом мире")
            return
        
        # Сохраняем избранные задания для этого мира в user_data
        if user_id not in user_data:
            user_data[user_id] = {}
        
        # Подготавливаем данные для просмотра заданий
        favorite_tasks = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in world_favorites]
        user_data[user_id]["favorite_tasks"] = favorite_tasks
        user_data[user_id]["current_index"] = 0
        user_data[user_id]["current_world_id"] = world["id"]
        user_data[user_id]["current_screen"] = "favorite_view"
        
        # Создаем клавиатуру с кнопками просмотра
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для разных режимов просмотра без индикации количества заданий
        markup.add(InlineKeyboardButton(
            "🔢 Подряд", 
            callback_data=f"quest_favorite_view_ordered_{world['id']}"
        ))
        
        # Только если есть больше одного задания, добавляем кнопку "Вперемежку"
        if len(world_favorites) > 1:
            markup.add(InlineKeyboardButton(
                "🔁 Вперемежку", 
                callback_data=f"quest_favorite_view_random_{world['id']}"
            ))
        
        # Добавляем кнопку "По темам" для просмотра по категориям
        markup.add(InlineKeyboardButton(
            "📚 По темам", 
            callback_data=f"quest_favorite_world_categories_{world['id']}"
        ))
        
        # Кнопка возврата - используем специальный callback для возврата без анимации
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_favorites_no_animation"))
        
        # Отображаем меню выбора способа просмотра
        bot.edit_message_media(
            media=InputMediaPhoto(world["loaded_image"], caption=f"⭐ Избранные задания - {world['name']}\n\nВыберите способ просмотра заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображено меню просмотра избранных заданий для мира {world['name']}")
    except Exception as e:
        logging.error(f"Ошибка при обработке избранных заданий для мира: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке избранных заданий")

def handle_quest_favorite_category(call):
    """Обработчик просмотра избранных заданий конкретной категории"""
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Получаем параметры из колбэка
        parts = call.data.split("_")
        world_id_str = parts[-2]
        cat_code = parts[-1]
        
        logging.info(f"Обработка избранных заданий категории для пользователя {user_id}, мир: {world_id_str}, категория: {cat_code}")
        
        try:
            # Пробуем преобразовать в число, так как в QUEST_WORLDS id хранятся как числа
            world_id_int = int(world_id_str)
            world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
        except ValueError:
            # Если не удалось преобразовать в число, пытаемся найти мир с id в строковом формате
            logging.warning(f"Не удалось преобразовать world_id {world_id_str} в число")
            world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id_str), None)
        
        if not world:
            bot.answer_callback_query(call.id, "Ошибка: мир не найден")
            logging.error(f"Мир с ID {world_id_str} не найден в QUEST_WORLDS")
            return
        
        # Используем строковое представление world_id для сравнения с challenge_num из БД
        world_id_for_db = str(world["id"])
        
        # Получаем информацию о категориях в этом мире
        world_challenges = challenge.get(world_id_for_db, {})
        category = world_challenges.get(cat_code)
        
        if not category:
            bot.answer_callback_query(call.id, "Ошибка: категория не найдена")
            logging.error(f"Категория с кодом {cat_code} не найдена в мире {world_id_for_db}")
            return
        
        # Получаем избранные задания для этой категории
        all_favorites = get_user_favorites(user_id)
        logging.info(f"Получены все избранные задания для пользователя {user_id}: {len(all_favorites)}")
        
        # Фильтруем задания для текущей категории, с преобразованием типов
        category_favorites = [f for f in all_favorites if f['challenge_num'] == world_id_for_db and f['cat_code'] == cat_code]
        logging.info(f"Отфильтрованы задания для категории {cat_code} в мире {world_id_for_db}: {len(category_favorites)}")
        
        if not category_favorites:
            bot.answer_callback_query(call.id, "Нет избранных заданий в этой категории")
            return
        
        # Сохраняем избранные задания для этой категории в user_data
        if user_id not in user_data:
            user_data[user_id] = {}
        
        # Подготавливаем данные для просмотра заданий
        favorite_tasks = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in category_favorites]
        user_data[user_id]["favorite_tasks"] = favorite_tasks
        user_data[user_id]["current_index"] = 0
        user_data[user_id]["current_world_id"] = world["id"]
        user_data[user_id]["current_screen"] = "favorite_category_view"
        
        # Создаем клавиатуру с кнопками просмотра
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для разных режимов просмотра без индикации количества заданий
        markup.add(InlineKeyboardButton(
            "🔢 Подряд", 
            callback_data=f"quest_favorite_view_ordered_{world['id']}"
        ))
        
        # Только если есть больше одного задания, добавляем кнопку "Вперемежку"
        if len(category_favorites) > 1:
            markup.add(InlineKeyboardButton(
                "🔁 Вперемежку", 
                callback_data=f"quest_favorite_view_random_{world['id']}"
            ))
        
        # Кнопка возврата - используем специальный callback для возврата к категориям
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_favorite_world_categories_{world['id']}"))
        
        # Отображаем меню выбора способа просмотра
        bot.edit_message_media(
            media=InputMediaPhoto(world["loaded_image"], caption=f"⭐ Избранные задания - {world['name']}\nКатегория: {category['name']}\n\nВыберите способ просмотра заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображено меню просмотра избранных заданий категории {category['name']} для пользователя {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при обработке избранных заданий категории: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке избранных заданий")

    # Здесь был дублирующийся блок except - код должен работать корректно после удаления дублирования
        
def handle_quest_homework(call):
    """Обработчик просмотра домашних заданий в квесте (Ритуал повторения)"""
    from instance import photo_quest_ritual
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Инициализируем данные пользователя при необходимости
    if user_id not in user_data:
        user_data[user_id] = {}
    
    # Извлекаем ID мира из callback-данных
    data = call.data.split('_')
    if len(data) > 3:
        world_id = data[3]
        logging.info(f"Получен мир из callback: {world_id}")
    else:
        # Используем мир 6 (Мир Простейших Уравнений) по умолчанию
        world_id = '6'
        logging.info(f"Используем мир по умолчанию: {world_id}")
    
    user_data[user_id]['current_world_id'] = world_id
    
    # Получаем все категории для этого мира
    world_categories = challenge.get(world_id, {})
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Принудительно синхронизируем домашние задания перед отображением
    try:
        from fix_ritual_homework import force_sync_homework_tasks
        logging.info(f"🔄 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Запуск принудительной синхронизации домашних заданий перед отображением")
        sync_result = force_sync_homework_tasks()
        logging.info(f"🔄 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Результат синхронизации: {sync_result}")
    except Exception as e:
        logging.error(f"❌ ОШИБКА СИНХРОНИЗАЦИИ: Не удалось синхронизировать домашние задания: {e}")
        # Продолжаем работу, даже если синхронизация не удалась
    
    # Получаем АКТУАЛЬНЫЙ список домашних заданий для пользователя (после синхронизации)
    homework_tasks = []
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        logging.info(f"Подключение к базе данных task_progress.db для Ритуала повторения")
        
        # Получаем все домашние задания
        # Удалена сортировка, чтобы позиция заданий не менялась в зависимости от статуса
        cursor.execute("""
            SELECT cat_code, task_idx FROM task_progress 
            WHERE user_id = ? AND type = 'homework'
        """, (user_id,))
        
        homework_tasks = cursor.fetchall()
        
        # Выводим отладочную информацию
        logging.info(f"✅ Найдено {len(homework_tasks)} домашних заданий для пользователя {user_id}")
        logging.info(f"✅ Все домашние задания: {homework_tasks}")
        
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении домашних заданий: {e}")
    
    # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: Если все еще нет домашних заданий, проверяем наличие заданий с неверными ответами
    # Это запасной вариант, на случай если force_sync_homework_tasks не сработал
    if not homework_tasks:
        logging.info(f"⚠️ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: Нет домашних заданий после синхронизации, пробуем резервный метод")
        try:
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            
            # Получаем все задания с неверными ответами
            cursor.execute("""
                SELECT challenge_num, cat_code, task_idx FROM task_progress 
                WHERE (user_id = ? AND type = 'main' AND status = 'wrong')
                OR (user_id = ? AND type = 'main' AND status = '0')
            """, (user_id, user_id))
            
            wrong_tasks = cursor.fetchall()
            
            # Если есть задания с неверными ответами, добавляем их в домашнюю работу
            if wrong_tasks:
                logging.info(f"✅ РЕЗЕРВНЫЙ МЕТОД: Найдено {len(wrong_tasks)} заданий с неверными ответами")
                for task in wrong_tasks:
                    challenge_num, cat_code, task_idx = task
                    cursor.execute("""
                        INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, challenge_num, cat_code, task_idx, "homework", "wrong"))
                
                conn.commit()
                
                # Повторно получаем список домашних заданий
                cursor.execute("""
                    SELECT cat_code, task_idx FROM task_progress 
                    WHERE user_id = ? AND type = 'homework'
                """, (user_id,))
                
                homework_tasks = cursor.fetchall()
                logging.info(f"⚠️ РЕЗЕРВНЫЙ МЕТОД: После добавления найдено {len(homework_tasks)} домашних заданий")
                
            conn.close()
        except sqlite3.Error as e:
            logging.error(f"❌ ОШИБКА РЕЗЕРВНОГО МЕТОДА: {e}")
            
    # Если все еще нет домашних заданий
    if not homework_tasks:
        bot.edit_message_media(
            media=InputMediaPhoto(
                photo_quest_ritual,
                caption="Ритуал повторения\n\nУ вас пока нет домашних заданий.\n\nЗадания появятся здесь, если вы ответите неверно или воспользуетесь подсказкой при решении задач."
            ),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
            )
        )
        bot.answer_callback_query(call.id)
        return
    
    # Группируем домашние задания по категориям
    categories_dict = {}
    for task in homework_tasks:
        # Если это кортеж с двумя элементами (cat_code, task_idx)
        if len(task) == 2:
            cat_code, task_idx = task
            if cat_code not in categories_dict:
                categories_dict[cat_code] = []
            categories_dict[cat_code].append(task_idx)
        # Если это кортеж с тремя элементами (challenge_num, cat_code, task_idx)
        elif len(task) == 3:
            challenge_num, cat_code, task_idx = task
            if cat_code not in categories_dict:
                categories_dict[cat_code] = []
            categories_dict[cat_code].append(task_idx)
        
    # Выводим отладочную информацию
    logging.info(f"Сгруппированные категории: {categories_dict}")
    
    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Определяем порядок категорий как в квесте 
    # (соответствует порядку в словаре challenge)
    ordered_categories = []
    
    # Добавляем категории в том же порядке, что и в словаре challenge
    for world_id_str in challenge:
        for cat_code in challenge[world_id_str]:
            if cat_code in categories_dict and cat_code not in [c for c, _ in ordered_categories]:
                ordered_categories.append((cat_code, challenge[world_id_str][cat_code]['name']))
    
    # Добавляем оставшиеся категории, которые могут быть не в списке challenge
    for cat_code in categories_dict:
        if cat_code not in [c for c, _ in ordered_categories]:
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Улучшаем обработку неизвестных категорий
            # Если категория не найдена, используем специализированные имена
            if cat_code == 'quad':
                name = "Квадратичная функция"
            elif cat_code == 'frac':
                name = "Дробно-рациональные выражения"
            elif cat_code == 'log':
                name = "Логарифмические выражения"
            elif cat_code == 'exp':
                name = "Показательные функции"
            elif cat_code == 'odd':
                name = "Разные задания"
            elif cat_code == 'lin':
                name = "Линейные функции"
            else:
                name = world_categories.get(cat_code, {}).get('name', f"Тип: {cat_code}")
            
            logging.info(f"⚠️ КАТЕГОРИЯ НЕ НАЙДЕНА В МИРЕ: {cat_code}, используем имя: {name}")
            ordered_categories.append((cat_code, name))
    
    # Добавляем кнопки для каждой категории в правильном порядке
    for cat_code, category_name in ordered_categories:
        tasks = categories_dict[cat_code]
        markup.add(
            InlineKeyboardButton(
                f"{category_name} ({len(tasks)})",
                callback_data=f"quest_homework_cat_{world_id}_{cat_code}"
            )
        )
    
    # Добавляем кнопку "Назад"
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
    )
    
    # Отправляем сообщение
    bot.edit_message_media(
        media=InputMediaPhoto(
            photo_quest_ritual,
            caption="Ритуал повторения\n\nЗдесь собраны задания, которые требуют повторения.\nВыберите тему для практики:"
        ),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )
    
    bot.answer_callback_query(call.id)

favorites = load_favorites()
for user_id, favs in favorites.items():
    if user_id not in user_data:
        user_data[user_id] = {
            "favorite_tasks": [],
            "current_index": 0,
            "message_id": None,
            "current_mode": None,
            "challenge_num": None,
            "navigation_stack": [],
            "current_screen": None
        }
    user_data[user_id]["favorite_tasks"] = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in favs]
logging.info("Избранное загружено при старте бота из базы данных")

def save_favorite(user_id, challenge_num, cat_code, task_idx):
    """Добавляет задачу в избранное в базе данных."""
    try:
        favorites_cursor.execute('''
            INSERT OR IGNORE INTO favorites (user_id, challenge_num, cat_code, task_idx)
            VALUES (?, ?, ?, ?)
        ''', (str(user_id), challenge_num, cat_code, task_idx))
        favorites_conn.commit()
        logging.info(f"Задача ({challenge_num}, {cat_code}, {task_idx}) добавлена в избранное для user_id={user_id}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении избранного: {e}")

def remove_favorite(user_id, challenge_num, cat_code, task_idx):
    """Удаляет задачу из избранного в базе данных."""
    try:
        favorites_cursor.execute('''
            DELETE FROM favorites 
            WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?
        ''', (str(user_id), challenge_num, cat_code, task_idx))
        favorites_conn.commit()
        logging.info(f"Задача ({challenge_num}, {cat_code}, {task_idx}) удалена из избранного для user_id={user_id}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при удалении из избранного: {e}")

# Групирует задачи
def group_favorites_by_challenge(favorites):
    grouped = defaultdict(list)
    for task in favorites:
        challenge_num = task["challenge_num"]
        cat_code = task["cat_code"]
        task_idx = task["task_idx"]
        grouped[challenge_num].append((cat_code, task_idx))
    logging.info(f"Сгруппированные избранные задачи: {dict(grouped)}")
    return dict(grouped)

# Функция для отображения задачи (используется для возврата из подсказки)
def display_task(chat_id, message_id, challenge_num, cat_code, task_idx):
    """
    Отображает задачу с указанными параметрами.
    """
    user_id = str(chat_id)
    logging.info(f"Вызов display_task: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
    
    try:
        # Проверяем существование задачи
        if challenge_num not in challenge:
            logging.error(f"display_task: challenge_num={challenge_num} не существует!")
            return False
            
        if cat_code not in challenge[challenge_num]:
            logging.error(f"display_task: cat_code={cat_code} для challenge_num={challenge_num} не существует!")
            return False
            
        tasks = challenge[challenge_num][cat_code].get("tasks", [])
        if not tasks or task_idx >= len(tasks):
            logging.error(f"display_task: task_idx={task_idx} вне диапазона для challenge_num={challenge_num}, cat_code={cat_code}!")
            return False
            
        # Получаем информацию о задаче
        task = tasks[task_idx]
        total_tasks = len(tasks)
        
        # Получаем статус задачи
        users_cursor.execute("""
            SELECT status FROM task_progress 
            WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
        """, (user_id, challenge_num, cat_code, task_idx))
        result = users_cursor.fetchone()
        
        # Формируем текст
        caption = f"Задача {challenge_num}\n{challenge[challenge_num][cat_code]['name']} {task_idx + 1}/{total_tasks}"
        
        # Добавляем статус
        if not result:
            status_text = "❔ Не решено"
            caption += f"\n{status_text}\nВведите ответ в чат:"
        elif result[0] == "correct":
            caption += f"\n✅ Верно\n\nПравильный ответ: {task['answer']}"
        else:
            status_text = "❌ Не верно"
            caption += f"\n{status_text}\nВведите ответ в чат:"
        
        # Создаем клавиатуру
        markup = types.InlineKeyboardMarkup()
        
        # Кнопки навигации между задачами
        nav_buttons = []
        if task_idx > 0:
            nav_buttons.append(
                types.InlineKeyboardButton("⬅️", callback_data=f"category_{challenge_num}_{cat_code}_{task_idx - 1}")
            )
        if task_idx < total_tasks - 1:
            nav_buttons.append(
                types.InlineKeyboardButton("➡️", callback_data=f"category_{challenge_num}_{cat_code}_{task_idx + 1}")
            )
        if nav_buttons:
            markup.row(*nav_buttons)
        
        # Кнопка подсказки
        if "hint" in task and task["hint"]:
            hint_count = len(task["hint"])
            markup.add(
                types.InlineKeyboardButton(f"💡 Подсказка (Шаги: {hint_count})", callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0")
            )
        
        # Кнопка избранного
        favorites = get_user_favorites(user_id)
        is_favorite = any(
            f["challenge_num"] == challenge_num and f["cat_code"] == cat_code and f["task_idx"] == task_idx 
            for f in favorites
        )
        markup.add(
            types.InlineKeyboardButton(
                "🗑️ Удалить из избранного" if is_favorite else "⭐ Добавить в избранное",
                callback_data=f"{'remove' if is_favorite else 'add'}_favorite_{challenge_num}_{cat_code}_{task_idx}"
            )
        )
        
        # Кнопка назад
        markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=f"challenge_{challenge_num}"))
        
        # Отправляем сообщение
        bot.edit_message_media(
            media=types.InputMediaPhoto(task["photo"], caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        
        # Обновляем данные о текущей задаче пользователя
        user_task_data[user_id] = {
            "challenge_num": challenge_num,
            "cat_code": cat_code,
            "task_idx": task_idx,
            "message_id": message_id,
            "type": "main",
            "task": task,
            "current_caption": caption,
            "status": result[0] if result else None,
            "is_favorite": is_favorite
        }
        
        return True
    except Exception as e:
        logging.error(f"Ошибка в display_task: {e}")
        return False

def init_task_progress_db():
    connection = sqlite3.connect('task_progress.db')
    cursor = connection.cursor()
    logging.info(f"Инициализация базы данных task_progress.db")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_progress (
            user_id TEXT,
            challenge_num TEXT, -- Используем challenge_num вместо world_id для совместимости
            cat_code TEXT,
            task_idx INTEGER,
            status TEXT,  -- 'correct', 'wrong', 'unresolved'
            type TEXT DEFAULT 'main', -- 'main', 'homework'
            PRIMARY KEY (user_id, challenge_num, cat_code, task_idx, type)
        )''')
    connection.commit()
    
    # Для отладки: посмотреть все записи в таблице
    cursor.execute("SELECT * FROM task_progress")
    all_records = cursor.fetchall()
    print(f"Текущие записи в task_progress: {all_records}")
    
    connection.close()
    print("✅ Таблица 'task_progress' создана или уже существует!")
init_task_progress_db()

# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавляем функцию для принудительного перемещения неверных ответов в домашнюю работу
def force_sync_homework_tasks():
    """Синхронизирует задания с неверными ответами с заданиями в домашней работе"""
    try:
        import sqlite3
        import logging
        import time
        
        # Выводим текущее состояние для диагностики
        conn_diag = sqlite3.connect('task_progress.db')
        cursor_diag = conn_diag.cursor()
        cursor_diag.execute("SELECT * FROM task_progress WHERE type='main'")
        main_tasks = cursor_diag.fetchall()
        cursor_diag.execute("SELECT * FROM task_progress WHERE type='homework'")
        homework_tasks_diag = cursor_diag.fetchall()
        conn_diag.close()
        
        logging.info(f"⚠️ ДИАГНОСТИКА ПЕРЕД СИНХРОНИЗАЦИЕЙ: Основные задания (main): {main_tasks}")
        logging.info(f"⚠️ ДИАГНОСТИКА ПЕРЕД СИНХРОНИЗАЦИЕЙ: Домашние задания (homework): {homework_tasks_diag}")
        
        # Основная синхронизация
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        logging.info("⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Запуск синхронизации домашних заданий...")
        
        # Получаем все задачи с неверными ответами основного типа
        # ИСПРАВЛЕНИЕ: используем строгое сравнение с 'wrong' для поля status
        cursor.execute("""
            SELECT user_id, challenge_num, cat_code, task_idx FROM task_progress 
            WHERE status = 'wrong' AND type = 'main'
        """)
        wrong_tasks = cursor.fetchall()
        logging.info(f"⚠️ ДИАГНОСТИКА: Найдено {len(wrong_tasks)} задач с неверными ответами: {wrong_tasks}")
        
        # Получаем все задачи из домашней работы
        cursor.execute("""
            SELECT user_id, challenge_num, cat_code, task_idx FROM task_progress 
            WHERE type = 'homework'
        """)
        homework_tasks = cursor.fetchall()
        logging.info(f"⚠️ ДИАГНОСТИКА: Найдено {len(homework_tasks)} задач в домашней работе: {homework_tasks}")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Очищаем домашнюю работу и заново добавляем все неверные ответы
        # Это гарантирует, что у нас будут только актуальные задания
        try:
            # Сначала очищаем таблицу домашних заданий
            cursor.execute("DELETE FROM task_progress WHERE type='homework'")
            conn.commit()
            logging.info("🔄 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Таблица homework полностью очищена")
            
            # Теперь добавляем все задания с неверными ответами в домашнюю работу
            cursor.execute("""
                INSERT INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                SELECT user_id, challenge_num, cat_code, task_idx, 'homework', 'wrong'
                FROM task_progress
                WHERE status = 'wrong' AND type = 'main'
            """)
            
            # Записываем изменения
            conn.commit()
            
            # Проверяем, сколько записей добавлено
            cursor.execute("SELECT COUNT(*) FROM task_progress WHERE type='homework'")
            count = cursor.fetchone()[0]
            logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Одним запросом добавлено {count} заданий в домашнюю работу")
            
            # Проверяем результат синхронизации
            cursor.execute("SELECT * FROM task_progress WHERE type='homework'")
            after_sync = cursor.fetchall()
            logging.info(f"⚠️ ДИАГНОСТИКА ПОСЛЕ СИНХРОНИЗАЦИИ: Домашние задания (homework): {after_sync}")
        except Exception as bulk_e:
            logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Ошибка при массовом добавлении: {bulk_e}")
            
            # Альтернативный подход - добавляем каждое задание по отдельности
            count = 0
            for user_id, challenge_num, cat_code, task_idx in wrong_tasks:
                logging.info(f"⚠️ ЗАПАСНОЙ ВАРИАНТ: Добавляем задание в ДЗ: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
                try:
                    cursor.execute("""
                        INSERT INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, challenge_num, cat_code, task_idx, "homework", "wrong"))
                    count += 1
                    logging.info(f"✅ Задание добавлено в ДЗ: {user_id}_{challenge_num}_{cat_code}_{task_idx}")
                except Exception as e:
                    logging.error(f"❌ Ошибка добавления задания: {e}")
                    
            conn.commit()
            logging.info(f"✅ ЗАПАСНОЙ ВАРИАНТ: Добавлено {count} заданий в домашнюю работу по одному.")
        
        # Дополнительное резервное добавление для абсолютной надежности
        try:
            # Получаем все задачи, которые нужно добавить в домашнюю работу, но еще не добавлены
            cursor.execute("""
                SELECT user_id, challenge_num, cat_code, task_idx
                FROM task_progress
                WHERE status = 'wrong' AND type = 'main'
                AND (user_id, challenge_num, cat_code, task_idx) NOT IN 
                    (SELECT user_id, challenge_num, cat_code, task_idx FROM task_progress WHERE type = 'homework')
            """)
            missing_tasks = cursor.fetchall()
            
            # Добавляем недостающие задачи
            for user_id, challenge_num, cat_code, task_idx in missing_tasks:
                cursor.execute("""
                    INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, challenge_num, cat_code, task_idx, "homework", "wrong"))
                logging.info(f"✅ РЕЗЕРВНОЕ ДОБАВЛЕНИЕ: Задание {user_id}_{challenge_num}_{cat_code}_{task_idx} добавлено в ДЗ")
            
            conn.commit()
        except Exception as reserve_e:
            logging.error(f"❌ РЕЗЕРВНОЕ ДОБАВЛЕНИЕ: Ошибка: {reserve_e}")
            
        # Финальная проверка
        try:
            # Итоговая проверка
            cursor.execute("SELECT * FROM task_progress WHERE type='homework'")
            final_homework = cursor.fetchall()
            
            # Проверяем, все ли неверные ответы добавлены в домашнюю работу
            cursor.execute("""
                SELECT COUNT(*) FROM task_progress
                WHERE status = 'wrong' AND type = 'main'
                AND (user_id, challenge_num, cat_code, task_idx) NOT IN 
                    (SELECT user_id, challenge_num, cat_code, task_idx FROM task_progress WHERE type = 'homework')
            """)
            missing_count = cursor.fetchone()[0]
            
            if missing_count > 0:
                logging.error(f"⚠️ ВНИМАНИЕ: {missing_count} заданий с неверными ответами не добавлены в домашнюю работу!")
            else:
                logging.info("✅ ПОДТВЕРЖДЕНИЕ: Все задания с неверными ответами успешно добавлены в домашнюю работу")
                
            logging.info(f"✅ ИТОГОВАЯ ПРОВЕРКА: Домашние задания (homework): {final_homework}")
        except Exception as final_e:
            logging.error(f"❌ ФИНАЛЬНАЯ ПРОВЕРКА: Ошибка: {final_e}")
            
        conn.close()
                
    except Exception as e:
        logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Ошибка при синхронизации домашних заданий: {e}")

# Запускаем синхронизацию при старте бота
force_sync_homework_tasks()

# Обработка данных из избранного
def is_favorite(user_id, challenge_num, cat_code, task_idx, favorites):
    """Проверяет, находится ли задание в избранном у пользователя
    
    Параметры:
        user_id - ID пользователя (строка или число)
        challenge_num - номер задания (строка или число) 
        cat_code - код категории (строка)
        task_idx - индекс задания (число)
        favorites - словарь с избранными заданиями
    """
    # Преобразуем все критические параметры к строкам для корректного сравнения
    user_id_str = str(user_id)
    challenge_num_str = str(challenge_num)
    task_idx_int = int(task_idx) if not isinstance(task_idx, int) else task_idx
    
    # Проверка наличия пользователя в списке избранного
    if not favorites:
        logging.debug(f"Проверка избранного: список избранного пуст")
        return False
    
    # Оптимизированная проверка
    result = any(
        f["challenge_num"] == challenge_num_str and
        f["cat_code"] == cat_code and
        int(f["task_idx"]) == task_idx_int
        for f in favorites
    )
    
    logging.debug(f"Проверка избранного: world_id={challenge_num_str}, cat_code={cat_code}, task_idx={task_idx_int}, результат={result}")
    return result
# Отправка избранной задачи
def send_favorite_task(chat_id, message_id):
    user_id = str(chat_id)
    if user_id not in user_data or "favorite_tasks" not in user_data[user_id]:
        text = "Ошибка! Выберите задачу из избранного."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="quest_favorites_no_animation"))
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        return
        
    # Отмечаем, что мы находимся в режиме просмотра избранного
    user_data[user_id]["current_screen"] = "favorite_view"

    tasks = user_data[user_id]["favorite_tasks"]
    current_index = user_data[user_id]["current_index"]
    if current_index >= len(tasks) or current_index < 0:
        text = "Все избранные задачи просмотрены!"
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="quest_favorites_no_animation"))
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        return

    challenge_num, cat_code, task_idx = tasks[current_index]
    task_idx = int(task_idx) if isinstance(task_idx, str) else task_idx
    
    # Получаем информацию о задаче
    try:
        task = challenge[challenge_num][cat_code]["tasks"][task_idx]
        category_name = challenge[challenge_num][cat_code]["name"]
        total_tasks = len(tasks)

        # Проверяем статус в базе - проверка наличия таблицы
        try:
            users_cursor.execute("""
                SELECT status FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
            """, (user_id, challenge_num, cat_code, task_idx))
            result = users_cursor.fetchone()
            
            if result:
                if result[0] == "correct":
                    status_text = "✅ Верно"
                    answer_text = f"\n\nПравильный ответ: {task['answer']}"
                elif result[0] == "wrong":
                    status_text = "❌ Неверно"
                    answer_text = "\n\nВведите ответ в чат:"
                else:
                    status_text = "❔ Не решено"
                    answer_text = "\n\nВведите ответ в чат:"
            else:
                status_text = "❔ Не решено"
                answer_text = "\n\nВведите ответ в чат:"
                
        except sqlite3.OperationalError as e:
            # Если таблица не существует, инициализируем её
            if "no such table" in str(e):
                init_task_progress_db()
                status_text = "❔ Не решено"
                answer_text = "\n\nВведите ответ в чат:"
                result = None
            else:
                logging.error(f"Ошибка при получении статуса задачи: {e}")
                status_text = "❔ Не решено"
                answer_text = "\n\nВведите ответ в чат:"
                result = None
        
        # Формируем текст для отображения в соответствии с требованиями
        caption = f"№{challenge_num}\n{category_name}\n{status_text}\n{answer_text}"

        # Создаем клавиатуру с кнопками навигации
        markup = InlineKeyboardMarkup(row_width=3)
        
        # Формируем навигационные кнопки: всегда 3 кнопки с разными обработчиками в зависимости от страницы
        # На первой странице левая кнопка пустая (не отвечает на нажатие)
        # На последней странице правая кнопка пустая (не отвечает на нажатие)
        
        nav_buttons = []
        
        if current_index == 0:
            # Первая страница: пустая стрелка, счетчик, стрелка вперед
            nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
            nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
        elif current_index == total_tasks - 1:
            # Последняя страница: стрелка назад, счетчик, пустая стрелка
            nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
            nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
            nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
        else:
            # Промежуточная страница: стрелка назад, счетчик, стрелка вперед
            nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
            nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
            nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
        
        # Добавляем все кнопки в одном ряду
        markup.row(*nav_buttons)
        
        # Получаем количество подсказок для задания
        hint_count = len(task.get("hint", []))
        if hint_count > 0:
            # Добавляем кнопку подсказки без указания количества шагов (будет добавлено при показе подсказки)
            markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0"))
        
        # Добавляем кнопку удаления из избранного
        markup.add(InlineKeyboardButton("🗑 Удалить из избранного", callback_data=f"quest_favorite_{challenge_num}_{cat_code}_{task_idx}"))
        
        # Кнопка возврата - используем callback в зависимости от текущего режима
        world_id = user_data[user_id].get("current_world_id", "")
        back_callback = f"quest_favorite_world_{world_id}"
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=back_callback))
        
        # Сохраняем информацию о задаче для обработки ответа
        user_task_data[user_id] = {
            "challenge_num": challenge_num,
            "cat_code": cat_code,
            "task_idx": task_idx,
            "message_id": message_id,
            "correct_answer": task["answer"],
            "task": task,
            "from_favorites": True,
            "favorite_mode": user_data[user_id].get("current_mode"),
            "type": "main"
        }
        
        # Отображаем задачу
        bot.edit_message_media(
            media=InputMediaPhoto(task["photo"], caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        
        logging.info(f"Отображена задача из избранного: world={challenge_num}, cat={cat_code}, task={task_idx}, index={current_index+1}/{total_tasks}")
        
    except Exception as e:
        logging.error(f"Ошибка при отображении задачи из избранного: {e}")
        error_text = "Произошла ошибка при загрузке задачи. Пожалуйста, попробуйте позже."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="quest_favorites_no_animation"))
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption=error_text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
# Отправка задачи
def send_challenge_task(chat_id, photo, challenge_num, cat_code, task_idx):
    user_id = str(chat_id)
    if user_id not in user_data:
        user_data[user_id] = {
            "favorite_tasks": [],
            "current_index": 0,
            "message_id": None,
            "current_mode": None,
            "challenge_num": None,
            "navigation_stack": [],
            "current_screen": None
        }

    task = challenge[challenge_num][cat_code]["tasks"][task_idx]
    category_name = challenge[challenge_num][cat_code]["name"]
    total_tasks = len(challenge[challenge_num][cat_code]["tasks"])

    users_cursor.execute("""
        SELECT status FROM task_progress 
        WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
    """, (user_id, challenge_num, cat_code, task_idx))
    result = users_cursor.fetchone()
    status_text = "❔ Не решено" if not result else (
        "✅ Верно\n\nПравильный ответ: " + str(task["answer"]) if result[0] == "correct" else "❌ Не верно")

    # Проверяем, в избранном ли задача
    is_favorite = (challenge_num, cat_code, task_idx) in user_data[user_id]["favorite_tasks"]
    favorite_indicator = "★ " if is_favorite else ""

    caption = (
        f"Задача {challenge_num}\n"
        f"{favorite_indicator}{category_name} {task_idx + 1}/{total_tasks}\n"
        f"{status_text}\n"
        "Введите ответ в чат:"
    )

    markup = types.InlineKeyboardMarkup()
    nav_buttons = []
    if task_idx > 0:
        nav_buttons.append(
            types.InlineKeyboardButton("⬅️", callback_data=f"category_{challenge_num}_{cat_code}_{task_idx - 1}"))
    if task_idx < total_tasks - 1:
        nav_buttons.append(
            types.InlineKeyboardButton("➡️", callback_data=f"category_{challenge_num}_{cat_code}_{task_idx + 1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
    # Получаем количество подсказок для задания
    hint_count = len(task.get("hint", []))
    if hint_count > 0:
        # Добавляем кнопку подсказки
        markup.add(types.InlineKeyboardButton("💡 Подсказка", callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0"))

    # Динамическая кнопка для избранного
    if is_favorite:
        markup.add(types.InlineKeyboardButton("Удалить из избранного",
                                              callback_data=f"remove_favorite_{challenge_num}_{cat_code}_{task_idx}"))
    else:
        markup.add(types.InlineKeyboardButton("⭐ Добавить в избранное",
                                              callback_data=f"add_favorite_{challenge_num}_{cat_code}_{task_idx}"))

    markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=f"challenge_{challenge_num}"))

    # Отправляем или редактируем сообщение
    if user_data[user_id]["message_id"] is None:
        sent_message = bot.send_photo(chat_id, task["photo"], caption=caption, reply_markup=markup)
        user_data[user_id]["message_id"] = sent_message.message_id
    else:
        bot.edit_message_media(
            media=types.InputMediaPhoto(task["photo"], caption=caption),
            chat_id=chat_id,
            message_id=user_data[user_id]["message_id"],
            reply_markup=markup
        )

    user_task_data[user_id] = {
        "challenge_num": challenge_num,
        "cat_code": cat_code,
        "task_idx": task_idx,
        "correct_answer": task["answer"],
        "message_id": user_data[user_id]["message_id"],
        "type": "main"
    }
    user_data[user_id]["current_screen"] = f"category_{challenge_num}_{cat_code}_{task_idx}"
    logging.info(
        f"Задача отображена: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
# Обработчик для выбора категории домашнего задания
def handle_quest_homework_category(call):
    """Обработчик выбора категории домашних заданий в квесте"""
    from instance import photo_quest_ritual
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем параметры из колбэка
    parts = call.data.split('_')
    
    # Формат: quest_homework_cat_world_id_cat_code
    world_id = parts[3]
    cat_code = parts[4]
    
    # Для отладки
    print(f"handle_quest_homework_category - данные колбэка: {call.data}, мир: {world_id}, категория: {cat_code}")
    
    # Получаем категорию
    world_challenges = challenge.get(world_id, {})
    category = world_challenges.get(cat_code)
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обработка неизвестных категорий
    # Добавляем специальную обработку для категорий 'quad' и других,
    # которые могут отсутствовать в challenge, но быть в домашних заданиях
    if not category:
        logging.info(f"⚠️ КАТЕГОРИЯ НЕ НАЙДЕНА в challenge: {cat_code} для мира {world_id}, но продолжаем обработку")
        # Создаем фиктивную категорию для отображения заданий
        
        # Задаем имя категории
        if cat_code == 'quad':
            category_name = "Квадратичная функция"
        elif cat_code == 'frac':
            category_name = "Дробно-рациональные выражения"
        elif cat_code == 'log':
            category_name = "Логарифмические выражения"
        elif cat_code == 'exp':
            category_name = "Показательные функции"
        elif cat_code == 'odd':
            category_name = "Разные задания"
        elif cat_code == 'lin':
            category_name = "Линейные функции"
        else:
            category_name = f"Тип: {cat_code}"
        
        # Вместо прерывания обработки, создаем фиктивную структуру категории
        # для дальнейшей обработки. Важно: используем пустой список задач, так как
        # нам всё равно понадобятся только записи из БД
        category = {
            'name': category_name,
            'tasks': []  # Пустой список задач - для совместимости с интерфейсом
        }
    
    # Получаем список домашних заданий для этой категории из базы данных
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        logging.info(f"Подключение к базе данных task_progress.db для получения домашних заданий категории")
        
        # Проверяем все записи для отладки
        cursor.execute("SELECT * FROM task_progress")
        all_records = cursor.fetchall()
        print(f"handle_quest_homework_category - Все записи: {all_records}")
        
        # Получаем домашние задания для данного пользователя в этой категории (независимо от мира)
        cursor.execute("""
            SELECT task_idx FROM task_progress 
            WHERE user_id = ? AND cat_code = ? AND type = 'homework'
        """, (user_id, cat_code))
        
        homework_tasks = cursor.fetchall()
        conn.close()
        
        print(f"Домашние задания для пользователя {user_id} в категории {cat_code} (все миры): {homework_tasks}")
        
        # Если нет домашних заданий
        if not homework_tasks:
            bot.answer_callback_query(call.id, "В этой категории нет домашних заданий")
            return
        
        # Отображаем первое задание сразу, вместо списка
        task_idx = homework_tasks[0][0]
        
        # ИСПРАВЛЕНИЕ: Добавляем заглушку при загрузке фото задания из ДЗ
        # В случае отсутствия задания в списке категории, создаем заглушку
        if task_idx >= len(category['tasks']):
            # При фиктивных/пустых категориях создаем заглушку задания
            task = {
                'photo': 'https://i.imgur.com/nWJzXKX.jpeg',  # Изображение по умолчанию
                'answer': 'Не указан',
                'hint': [],
                'homework': {
                    'photo': 'https://i.imgur.com/nWJzXKX.jpeg',
                    'answer': 'Не указан'
                },
                'homework_photo': 'https://i.imgur.com/nWJzXKX.jpeg'
            }
            logging.info(f"🔄 СОЗДАНА ЗАГЛУШКА ДЛЯ ЗАДАНИЯ ДЗ {cat_code}_{task_idx}")
        else:
            task = category['tasks'][task_idx]
        
        # Получаем статус задания
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        logging.info(f"Подключение к базе данных task_progress.db для получения статуса домашнего задания")
        cursor.execute("""
            SELECT status FROM task_progress 
            WHERE user_id = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
        """, (user_id, cat_code, task_idx))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            bot.answer_callback_query(call.id, "Ошибка: домашнее задание не найдено в базе данных")
            return
        
        status = result[0]
        
        # Получаем ссылку на изображение задания
        # Для домашней работы используем специальное фото, если оно есть
        if 'homework_photo' in task and task['homework_photo']:
            photo_url = task['homework_photo']
        else:
            photo_url = task['photo']
            
        if not photo_url.startswith("http"):
            photo_url = f"https://i.imgur.com/{photo_url}.jpeg"  # Формируем URL для imgur
        
        # Маппинг статусов
        status_emoji = {"correct": "✅", "wrong": "❌"}
        if status not in status_emoji:
            status = "wrong"  # По умолчанию считаем задание непройденным
        
        # Создаем клавиатуру
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Навигационные кнопки между заданиями
        nav_buttons = []
        
        # Список индексов заданий
        task_indices = [t[0] for t in homework_tasks]
        total_tasks = len(task_indices)
        current_index = task_indices.index(task_idx)
        
        # Кнопки навигации (влево/вправо) и счетчик - всегда видимы
        nav_buttons = []
        
        # Если первое задание, добавляем фантомную кнопку влево
        if current_index > 0:
            prev_task_idx = task_indices[current_index - 1]
            nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{prev_task_idx}"))
        else:
            # Фантомная кнопка без функционала и без текста
            nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
        
        # Счетчик текущего положения
        nav_buttons.append(InlineKeyboardButton(f"{current_index + 1}/{total_tasks}", callback_data="quest_empty"))
        
        # Если последнее задание, добавляем фантомную кнопку вправо
        if current_index < total_tasks - 1:
            next_task_idx = task_indices[current_index + 1]
            nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{next_task_idx}"))
        else:
            # Фантомная кнопка без функционала и без текста
            nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
        
        markup.row(*nav_buttons)
        
        # Убираем кнопку "Ответить", так как ответ будет приниматься автоматически
        
        # Кнопка для просмотра подсказки, если она есть
        if task.get('hint'):
            markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_hint_direct_{world_id}_{cat_code}_{task_idx}_0"))
        
        # Проверка избранного и добавление кнопки избранного
        try:
            favorites = get_user_favorites(user_id)
            is_favorite = any(
                f["challenge_num"] == world_id and f["cat_code"] == cat_code and f["task_idx"] == task_idx for f in favorites
            )
            
            # Кнопка добавления/удаления из избранного
            markup.add(
                InlineKeyboardButton(
                    "🗑️ Удалить из избранного" if is_favorite else "⭐️ Добавить в избранное",
                    callback_data=f"{'remove' if is_favorite else 'add'}_favorite_{world_id}_{cat_code}_{task_idx}"
                )
            )
        except Exception as e:
            logging.error(f"Ошибка при проверке избранного: {e}")
        
        # Кнопка возврата
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_homework"))
        
        # Статус и текст
        status_text = {
            "correct": "✅ Верно",
            "wrong": "❌ Неверно",
            "unresolved": "❔ Нерешено"
        }.get(status, "❔ Нерешено")
        
        caption = f"№6 Домашняя работа\n{category['name']}\n{status_text}\n\nВведите ответ в чат:"
        
        # Добавляем правильный ответ, если он указан в задании и задача решена правильно
        correct_answer = task.get('answer')
        if status == "correct" and correct_answer:
            caption = f"№6 Домашняя работа\n{category['name']}\n{status_text}\n\nПравильный ответ: {correct_answer}"
        
        # Отображаем первое домашнее задание категории сразу
        bot.edit_message_media(
            media=InputMediaPhoto(photo_url, caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        
        # Сохраняем состояние для обработки ответа
        if user_id not in user_data:
            user_data[user_id] = {}
        
        # Проверяем, есть ли ответ в задании
        answer = task.get('answer', '')
        
        user_data[user_id]["current_homework"] = {
            "world_id": world_id,
            "cat_code": cat_code,
            "task_idx": task_idx,
            "message_id": message_id,
            "answer": answer
        }
        
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении домашних заданий: {e}")
        bot.answer_callback_query(call.id, "Ошибка при получении домашних заданий")
        return

# Обработчик для просмотра конкретного домашнего задания
def handle_quest_homework_task(call):
    """Обработчик для просмотра конкретного домашнего задания в квесте"""
    from instance import photo_quest_ritual
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем параметры из колбэка
    parts = call.data.split('_')
    # Формат: quest_homework_task_world_id_cat_code_task_idx
    world_id = parts[3]
    cat_code = parts[4]
    task_idx = int(parts[5])
    
    # Для отладки
    logging.info(f"handle_quest_homework_task - данные колбэка: {call.data}, мир: {world_id}, категория: {cat_code}, задание: {task_idx}")
    
    # Получаем информацию о задании
    world_challenges = challenge.get(world_id, {})
    category = world_challenges.get(cat_code)
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обработка неизвестных категорий в конкретных домашних заданиях
    if not category:
        logging.info(f"⚠️ КАТЕГОРИЯ НЕ НАЙДЕНА при выборе задания: {cat_code} для мира {world_id}, но продолжаем обработку")
        # Создаем фиктивную категорию для отображения заданий
        
        # Задаем имя категории
        if cat_code == 'quad':
            category_name = "Квадратичная функция"
        elif cat_code == 'frac':
            category_name = "Дробно-рациональные выражения"
        elif cat_code == 'log':
            category_name = "Логарифмические выражения"
        elif cat_code == 'exp':
            category_name = "Показательные функции"
        elif cat_code == 'odd':
            category_name = "Разные задания"
        elif cat_code == 'lin':
            category_name = "Линейные функции"
        else:
            category_name = f"Тип: {cat_code}"
        
        # Создаем фиктивную структуру категории с фиктивными задачами
        # Для учёта всех задач в БД, создаем список задач с запасом
        fake_tasks = []
        for i in range(100):  # Создаем 100 фиктивных заданий для запаса
            fake_tasks.append({
                'photo': 'https://i.imgur.com/nWJzXKX.jpeg',  # Заглушка изображения
                'answer': 'Не указан',
                'hint': []
            })
        
        category = {
            'name': category_name,
            'tasks': fake_tasks
        }
        logging.info(f"✅ Создана фиктивная категория: {category_name} с {len(fake_tasks)} заданиями")
    
    # Проверяем существование задания
    if task_idx >= len(category['tasks']):
        bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
        return
    
    task = category['tasks'][task_idx]
    
    # Проверяем наличие задания в базе данных с типом homework (не зависимо от мира)
    conn = sqlite3.connect('task_progress.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status FROM task_progress 
        WHERE user_id = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
    """, (user_id, cat_code, task_idx))
    result = cursor.fetchone()
    
    if not result:
        bot.answer_callback_query(call.id, "Ошибка: домашнее задание не найдено в базе данных")
        logging.error(f"Домашнее задание не найдено: user_id={user_id}, cat_code={cat_code}, task_idx={task_idx}")
        conn.close()
        return
    
    status = result[0]
    logging.info(f"Статус задания {world_id}_{cat_code}_{task_idx} для пользователя {user_id}: {status}")
    
    # Получаем ссылку на изображение задания
    # ИСПРАВЛЕНО: Используем фото из поля "homework" для домашних заданий (более приоритетно)
    if 'homework' in task and task['homework'] and 'photo' in task['homework']:
        photo_url = task['homework']['photo']
        logging.info(f"✅ ИСПОЛЬЗОВАНА СПЕЦИАЛЬНАЯ ФОТОГРАФИЯ ДЛЯ ДЗ: {photo_url}")
    elif 'homework_photo' in task and task['homework_photo']:
        photo_url = task['homework_photo']
        logging.info(f"✅ ИСПОЛЬЗОВАНА ФОТОГРАФИЯ homework_photo: {photo_url}")
    else:
        photo_url = task['photo']
        logging.info(f"⚠️ ДЛЯ ДОМАШНЕЙ РАБОТЫ ИСПОЛЬЗУЕТСЯ ОБЫЧНАЯ ФОТОГРАФИЯ: {photo_url}")
        
    if not photo_url.startswith("http"):
        photo_url = f"https://i.imgur.com/{photo_url}.jpeg"  # Формируем URL для imgur
    
    # Маппинг статусов
    status_emoji = {"correct": "✅", "wrong": "❌"}
    if status not in status_emoji:
        status = "wrong"  # По умолчанию считаем задание непройденным
    
    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Получаем все домашние задания для отображения навигации
    try:
        conn_nav = sqlite3.connect('task_progress.db')
        cursor_nav = conn_nav.cursor()
        cursor_nav.execute("""
            SELECT task_idx FROM task_progress 
            WHERE user_id = ? AND cat_code = ? AND type = 'homework'
        """, (user_id, cat_code))
        
        homework_tasks = cursor_nav.fetchall()
        conn_nav.close()
        
        if homework_tasks:
            # Список индексов заданий
            task_indices = [t[0] for t in homework_tasks]
            total_tasks = len(task_indices)
            current_index = task_indices.index(task_idx)
            
            # Кнопки навигации (влево/вправо) и счетчик - всегда видимы
            nav_buttons = []
            
            # Если первое задание, добавляем фантомную кнопку влево
            if current_index > 0:
                prev_task_idx = task_indices[current_index - 1]
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{prev_task_idx}"))
            else:
                # Фантомная кнопка без функционала и без текста
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            
            # Счетчик текущего положения
            nav_buttons.append(InlineKeyboardButton(f"{current_index + 1}/{total_tasks}", callback_data="quest_empty"))
            
            # Если последнее задание, добавляем фантомную кнопку вправо
            if current_index < total_tasks - 1:
                next_task_idx = task_indices[current_index + 1]
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{next_task_idx}"))
            else:
                # Фантомная кнопка без функционала и без текста
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            
            markup.row(*nav_buttons)
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении данных для навигации: {e}")
    
    # Убираем кнопку "Ответить", так как ответ будет приниматься автоматически
    
    # Кнопка для просмотра подсказки, если она есть
    if task.get('hint'):
        # ИСПРАВЛЕНИЕ: Используем специальный формат callback_data для подсказок из ДЗ,
        # чтобы при возврате из подсказки попадать обратно в ДЗ, а не в обычное задание
        markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_homework_hint_{world_id}_{cat_code}_{task_idx}_0"))
        logging.info(f"🔄 ДОБАВЛЕНА КНОПКА ПОДСКАЗКИ ДЛЯ ДОМАШКИ с callback: quest_homework_hint_{world_id}_{cat_code}_{task_idx}_0")
    
    # ИСПРАВЛЕНИЕ: Убираем кнопку "Добавить в избранное" в ДЗ
    # Это избыточная функциональность для домашней работы и может путать пользователей
    # При необходимости, пользователь может добавить задание в избранное из основного раздела заданий
    logging.info(f"💡 ИСПРАВЛЕНИЕ: Кнопка добавления в избранное удалена из домашней работы")
    
    # Кнопка возврата
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_homework"))
    
    # Отображаем домашнее задание
    status_text = {
        "correct": "✅ Верно",
        "wrong": "❌ Неверно",
        "unresolved": "❔ Нерешено"
    }.get(status, "❔ Нерешено")
    
    caption = f"№6 Домашняя работа\n{category['name']}\n{status_text}\n\nВведите ответ в чат:"
    
    # Добавляем правильный ответ, если он указан в задании и задача решена правильно
    correct_answer = task.get('answer')
    if status == "correct" and correct_answer:
        caption = f"№6 Домашняя работа\n{category['name']}\n{status_text}\n\nПравильный ответ: {correct_answer}"
    
    bot.edit_message_media(
        media=InputMediaPhoto(photo_url, caption=caption),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )
    
    # Сохраняем состояние для обработки ответа
    if user_id not in user_data:
        user_data[user_id] = {}
    
    # Проверяем, есть ли ответ в задании
    answer = task.get('answer', '')
    
    user_data[user_id]["current_homework"] = {
        "world_id": world_id,
        "cat_code": cat_code,
        "task_idx": task_idx,
        "answer": answer,
        "message_id": message_id
    }
    # Устанавливаем current_screen в homework для корректной обработки текстовых ответов
    user_data[user_id]["current_screen"] = "homework"
    
    conn.close()

# Отправка домашней работы (устаревшая функция)
def send_homework_task(chat_id):
    user_id = str(chat_id)
    session = user_data.get(user_id)
    if not session or "homework_tasks" not in session:
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, "Ошибка! Начните заново."),
            chat_id=chat_id,
            message_id=session["message_id"],
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="homework_menu"))
        )
        return
    tasks = session["homework_tasks"]
    idx = session["current_index"]
    if idx >= len(tasks):
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, "Домашка завершена!"),
            chat_id=chat_id,
            message_id=session["message_id"],
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="homework_menu"))
        )
        del user_data[user_id]
        return
    task = tasks[idx]
    # Проверяем статус в базе
    users_cursor.execute("""
        SELECT status FROM task_progress 
        WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
    """, (user_id, session["challenge_num"], session["cat_code"], idx))
    result = users_cursor.fetchone()
    status = result[0] if result else "unresolved"
    status_icon = {"correct": "✅ Верно", "wrong": "❌ Неверно", "unresolved": "❔ Нерешенно"}[status]

    caption = f"№{idx + 1} Домашняя работа\n{status_icon}\n\n{challenge[session['challenge_num']][session['cat_code']]['name']} {idx + 1}/{len(tasks)}\nВведите ответ в чат:"
    markup = InlineKeyboardMarkup()
    
    # Всегда добавляем навигационные кнопки
    # Первая кнопка - либо функциональная "назад", либо пустая неактивная
    if idx > 0:
        markup.add(InlineKeyboardButton("◀️", callback_data=f"homework_nav_{idx - 1}"))
    else:
        markup.add(InlineKeyboardButton(" ", callback_data="quest_empty"))
        
    # Вторая кнопка - либо функциональная "вперед", либо пустая неактивная
    if idx < len(tasks) - 1:
        markup.add(InlineKeyboardButton("▶️", callback_data=f"homework_nav_{idx + 1}"))
    else:
        markup.add(InlineKeyboardButton(" ", callback_data="quest_empty"))
    
    # Проверяем, находится ли задание в избранном
    is_fav = is_favorite(user_id, session['challenge_num'], session['cat_code'], idx, load_favorites(user_id))
    fav_button_text = "❌ Удалить из избранного" if is_fav else "⭐️ Добавить в избранное"
    fav_callback = f"remove_favorite_{session['challenge_num']}_{session['cat_code']}_{idx}" if is_fav else f"save_favorite_{session['challenge_num']}_{session['cat_code']}_{idx}" 
    markup.add(InlineKeyboardButton(fav_button_text, callback_data=fav_callback))
    
    # Получаем количество подсказок
    homework_hints = task["homework"].get("hint", [])
    hint_count = len(homework_hints)
    if hint_count > 0:
        markup.add(InlineKeyboardButton("💡 Подсказка",
                                      callback_data=f"hint_{session['challenge_num']}_{session['cat_code']}_{idx}_0"))
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data="homework_menu"))
    
    # Используем фото из поля "homework" для домашнего задания
    photo_url = task["homework"]["photo"]
    
    bot.edit_message_media(
        media=types.InputMediaPhoto(photo_url, caption=caption),
        chat_id=chat_id,
        message_id=session["message_id"],
        reply_markup=markup
    )
    user_task_data[user_id] = {
        "challenge_num": session["challenge_num"],
        "cat_code": session["cat_code"],
        "task_idx": idx,
        "message_id": session["message_id"],
        "correct_answer": task["homework"]["answer"],
        "type": "homework",
        "used_hints": False
    }


@bot.callback_query_handler(func=lambda call: call.data in [
    "next_task", "homework_menu", "stats_call", "favorites", "all_challenges"
] or call.data.startswith("challenge_") or call.data.startswith("category_") or
                                              call.data.startswith("hint_") or call.data.startswith("homework_cat_") or
                                              call.data.startswith("homework_order_") or call.data.startswith(
                                              "homework_nav_") or call.data.startswith("reinforce_") or call.data.startswith(
                                              "favorites_challenge_") or call.data.startswith("favorites_by_category_") or call.data.startswith(
                                              "favorites_categories_") or call.data.startswith("favorites_order_") or call.data.startswith(
                                              "favorite_nav_") or call.data.startswith("add_favorite_") or call.data.startswith(
                                              "remove_favorite_") or call.data.startswith("analog_"))
def handle_tasks_callback(call):
    bot.answer_callback_query(call.id)  # Подтверждаем обработку callback
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    # Инициализация данных пользователя
    if user_id not in user_data:
        user_data[user_id] = {
            "favorite_tasks": [],
            "current_index": 0,
            "message_id": None,
            "current_mode": None,
            "challenge_num": None,
            "navigation_stack": [],
            "current_screen": None
        }

    logging.debug(f"Получен callback: {call.data} от user_id={user_id}")
    try:
        # Обработка "Все задания"
        if data == "all_challenges":
            markup = types.InlineKeyboardMarkup()
            # Используем правильный callback_data для кнопки "6 задание"
            markup.add(types.InlineKeyboardButton("6 задание", callback_data="challenge_6"))
            markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data="challenge_call"))
            
            try:
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption="Выберите задание:"),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            except telebot.apihelper.ApiTelegramException as e:
                logging.error(f"Ошибка при открытии меню задач: {e}")
                bot.answer_callback_query(call.id, "Ошибка загрузки меню задач.")
                
        # Выбор задания
        elif data.startswith("challenge_"):
            challenge_num = call.data.split("_")[1]
            text = f"Задача {challenge_num}\n\nВыберите категорию:"
            markup = InlineKeyboardMarkup(row_width=1)
            try:
                categories = challenge[challenge_num]
                if not categories:
                    text += "\n\nКатегории для этой задачи пока не добавлены."
                else:
                    for cat_code, cat_data in categories.items():
                        # Проверяем, что категория содержит ключ "name" и задачи
                        if "name" in cat_data and "tasks" in cat_data and cat_data["tasks"]:
                            markup.add(
                                InlineKeyboardButton(cat_data["name"],
                                                    callback_data=f"category_{challenge_num}_{cat_code}"))
                    
                    # Если нет доступных категорий с задачами, сообщаем об этом
                    if len(markup.keyboard) == 0:
                        text += "\n\nНет доступных категорий с задачами."
            except KeyError as e:
                logging.error(f"Ошибка при обработке challenge_{challenge_num}: {e}")
                text += "\n\nЗадача временно недоступна."
                
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="challenge_call"))
            
            try:
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
            except Exception as e:
                logging.error(f"Ошибка отправки сообщения в challenge_{challenge_num}: {e}")
                bot.answer_callback_query(call.id, "Ошибка загрузки категорий.")

        # Возврат к задаче из подсказки
        elif data.startswith("challenge_task_"):
            try:
                logging.info(f"Обработка кнопки 'Назад' из подсказки: {data}")
                # Разбираем callback_data, формат: challenge_task_НОМЕР_КОД_ИНДЕКС
                parts = data.split("_")
                
                # Проверяем, достаточно ли частей в callback_data
                if len(parts) < 5:
                    logging.error(f"Некорректный формат callback_data: {data}, не хватает частей. Ожидаем минимум 5 частей.")
                    bot.answer_callback_query(call.id, "Ошибка в данных кнопки!")
                    return
                
                # Извлекаем номер задачи, код категории и индекс задачи
                # Формат: challenge_task_НОМЕР_КОД_ИНДЕКС
                # Части: 0            1    2      3    4
                challenge_num = parts[2]  # Третья часть (индекс 2)
                cat_code = parts[3]       # Четвертая часть (индекс 3)
                
                # Проверяем, что индекс задачи - число
                try:
                    task_idx = int(parts[4])  # Пятая часть (индекс 4)
                except ValueError:
                    logging.error(f"Индекс задачи не является числом: {parts[4]}")
                    bot.answer_callback_query(call.id, "Ошибка в данных кнопки (индекс задачи)!")
                    return
                
                logging.info(f"Возврат к задаче из подсказки: challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
                
                # Используем обработчик category_ для отображения задачи
                # вместо прямой реализации логики здесь
                call.data = f"category_{challenge_num}_{cat_code}_{task_idx}"
                data = call.data
                logging.info(f"Перенаправление на обработчик: {call.data}")
                
                # Дальше код перейдет к обработчику category_
                
            except Exception as e:
                logging.error(f"Ошибка при обработке challenge_task: {e}")
                bot.answer_callback_query(call.id, "Произошла ошибка при возврате к задаче")
                # В случае ошибки возвращаемся в главное меню задач
                call.data = "challenge_call"
                data = call.data
            
        # Выбор категории
        elif data.startswith("category_"):
            parts = call.data.split("_")
            if len(parts) < 3:  # Ошибка: недостаточно данных
                bot.answer_callback_query(call.id, "Ошибка в данных кнопки!")
                return
            challenge_num = parts[1]
            cat_code = parts[2]
            task_idx = int(parts[3]) if len(parts) > 3 else 0  # Если task_idx не указан, начинаем с 0

            user_id = str(call.from_user.id)
            try:
                task = challenge[challenge_num][cat_code]["tasks"][task_idx]
                total_tasks = len(challenge[challenge_num][cat_code]["tasks"])

                users_cursor.execute("""
                    SELECT status FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
                """, (user_id, challenge_num, cat_code, task_idx))
                result = users_cursor.fetchone()
                status_text = "❔ Не решено" if not result else (
                    f"✅ Верно\n\nПравильный ответ: {task['answer']}" if result[0] == "correct" else "❌ Не верно"
                )
                caption = f"Задача {challenge_num}\n{challenge[challenge_num][cat_code]['name']} {task_idx + 1}/{total_tasks}\n{status_text}"
                if not result or result[0] != "correct":
                    caption += "\nВведите ответ в чат:"

                markup = types.InlineKeyboardMarkup()
                nav_buttons = []
                if task_idx > 0:
                    nav_buttons.append(
                        types.InlineKeyboardButton("⬅️",
                                                   callback_data=f"category_{challenge_num}_{cat_code}_{task_idx - 1}")
                    )
                if task_idx < total_tasks - 1:
                    nav_buttons.append(
                        types.InlineKeyboardButton("➡️",
                                                   callback_data=f"category_{challenge_num}_{cat_code}_{task_idx + 1}")
                    )
                if nav_buttons:
                    markup.row(*nav_buttons)
                if "hint" in task and task["hint"]:
                    markup.add(
                        types.InlineKeyboardButton("💡 Подсказка",
                                                   callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0")
                    )
                # Проверка избранного
                favorites = get_user_favorites(user_id)
                is_favorite = any(
                    f["challenge_num"] == challenge_num and f["cat_code"] == cat_code and f["task_idx"] == task_idx for
                    f in
                    favorites)
                markup.add(
                    types.InlineKeyboardButton(
                        "🗑️ Удалить из избранного" if is_favorite else "⭐ Добавить в избранное",
                        callback_data=f"{'remove' if is_favorite else 'add'}_favorite_{challenge_num}_{cat_code}_{task_idx}"
                    )
                )
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"challenge_{challenge_num}"))

                bot.edit_message_media(
                    media=types.InputMediaPhoto(task["photo"], caption=caption),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                user_task_data[user_id] = {
                    "challenge_num": challenge_num,
                    "cat_code": cat_code,
                    "task_idx": task_idx,
                    "message_id": message_id,
                    "type": "main",
                    "task": task,
                    "current_caption": caption,
                    "status": result[0] if result else None,
                    "is_favorite": is_favorite
                }
            except KeyError as e:
                bot.answer_callback_query(call.id, f"Ошибка: данные для задачи отсутствуют ({e})")
            except IndexError:
                bot.answer_callback_query(call.id, "Ошибка: задача не найдена в категории")

        # Обработка "Подсказка"
        elif data.startswith("hint_"):
            try:
                parts = data.split("_")
                if len(parts) != 5 or not parts[4].isdigit():  # Проверяем формат
                    raise ValueError(f"Invalid hint callback_data format: {data}")

                challenge_num = parts[1]
                cat_code = parts[2]
                task_idx = int(parts[3])
                hint_idx = int(parts[4])
                
                # Сохраняем информацию о текущем задании для корректного возврата
                if user_id not in user_data:
                    user_data[user_id] = {}
                
                # Определяем, открыт ли этот hint из избранного или из обычных задач
                is_favorite_view = False
                
                # Проверяем текущий экран в user_data
                current_screen = user_data.get(user_id, {}).get("current_screen", "")
                logging.info(f"Получаем current_screen={current_screen} для user_id={user_id}")
                
                # Проверяем на основе current_screen
                if current_screen == "favorite_view":
                    is_favorite_view = True
                    logging.info(f"Подсказка открыта из избранного (определено по current_screen={current_screen})")
                else:
                    # Если мы не в режиме избранного, логируем это
                    logging.info(f"Подсказка открыта из обычного режима (current_screen={current_screen})")
                
                user_data[user_id]["current_task"] = {
                    "challenge_num": challenge_num,
                    "cat_code": cat_code,
                    "task_idx": task_idx,
                    "from_favorites": is_favorite_view
                }
                
                # Логируем для отладки
                logging.info(f"Сохранили информацию о задании для возврата: challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}, from_favorites={is_favorite_view}")

                # Получаем задачу
                task = challenge[challenge_num][cat_code]["tasks"][task_idx]
                hints = task.get("hint", [])  # Исправлено с "hints" на "hint"
                
                # Формируем текст подсказки
                hint_count = len(hints)
                hint_text = f"Подсказка {hint_idx + 1}/{hint_count}"
                
                if hints and hint_idx < len(hints):
                    # Создаём клавиатуру
                    markup = types.InlineKeyboardMarkup()
                    
                    # Добавляем кнопки навигации между подсказками
                    nav_buttons = []
                    if hint_idx > 0:
                        nav_buttons.append(
                            types.InlineKeyboardButton("⬅️", 
                                                     callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_{hint_idx - 1}")
                        )
                    if hint_idx < hint_count - 1:
                        nav_buttons.append(
                            types.InlineKeyboardButton("➡️", 
                                                     callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_{hint_idx + 1}")
                        )
                    if nav_buttons:
                        markup.row(*nav_buttons)
                    
                        # Добавляем кнопку "Назад" с соответствующей callback_data, в зависимости от источника
                    back_callback = f"category_{challenge_num}_{cat_code}_{task_idx}"
                    
                    # Если подсказка открыта из избранного, добавим специальный флаг
                    if user_data[user_id].get("current_task", {}).get("from_favorites", False):
                        logging.info(f"Создаём кнопку возврата в избранное для задачи challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
                        # Используем имеющиеся параметры для возврата к избранному
                        if "favorite_tasks" in user_data[user_id] and user_data[user_id].get("current_index", -1) >= 0:
                            back_callback = f"favorite_nav_{challenge_num}_{cat_code}_{user_data[user_id]['current_index']}"
                    
                    markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=back_callback))
                    
                    # Отправляем подсказку как изображение
                    hint_url = hints[hint_idx]
                    try:
                        bot.edit_message_media(
                            media=types.InputMediaPhoto(hint_url, caption=hint_text),
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            reply_markup=markup
                        )
                    except Exception as img_err:
                        logging.error(f"Ошибка при отправке изображения подсказки: {img_err}")
                        bot.answer_callback_query(call.id, "Ошибка загрузки изображения подсказки!")
                else:
                    bot.answer_callback_query(call.id, "Больше подсказок нет!")
            except Exception as e:
                logging.error(f"Error in hint_: {e}")
                bot.answer_callback_query(call.id, "Ошибка: подсказка не найдена!")

        # Показ следующего задания
        elif data == "next_task":
            logging.info(f"Пользователь {user_id} перешёл к следующей задаче")
            try:
                if user_id not in user_data or "favorite_tasks" not in user_data[user_id]:
                    bot.answer_callback_query(call.id, "Сначала выберите задачу из избранного!")
                    return

                user_data[user_id]["current_index"] += 1
                if user_data[user_id]["current_index"] >= len(user_data[user_id]["favorite_tasks"]):
                    bot.edit_message_media(
                        media=types.InputMediaPhoto(photo, caption="Все задачи решены!"),
                        chat_id=chat_id,
                        message_id=call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("↩️ Назад", callback_data="favorites")
                        )
                    )
                    user_data[user_id]["current_screen"] = "favorites_complete"
                    return

                send_favorite_task(chat_id, photo)
            except Exception as e:
                logging.error(f"Ошибка в next_task: {e}")
                bot.answer_callback_query(call.id, "Ошибка при переходе к следующей задаче.")

        elif data == "homework_menu":
            markup = types.InlineKeyboardMarkup()
            try:
                categories = challenge["6"]  # Используем строковый ключ
                if not categories:
                    caption = "Выберите категорию домашки:\n\nКатегории пока не добавлены."
                else:
                    caption = "Выберите категорию домашки:"
                    for cat_code, cat_data in categories.items():
                        if "tasks" in cat_data and any("homework" in task for task in cat_data["tasks"]):
                            markup.add(
                                types.InlineKeyboardButton(cat_data["name"], callback_data=f"homework_cat_{cat_code}"))
            except KeyError:
                caption = "Данные для домашки отсутствуют."
            markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data="challenge_call"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )

        elif data.startswith("homework_cat_"):
            cat_code = call.data.split("_")[2]
            text = f"Выберите порядок выполнения для '{challenge[6][cat_code]['name']}':"
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔢 Подряд", callback_data=f"homework_order_sequential_{cat_code}"),
                InlineKeyboardButton("🔁 Вперемежку", callback_data=f"homework_order_mixed_{cat_code}")
            )
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="homework_menu"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )

        elif data.startswith("homework_order_"):
            data = call.data.split("_")
            order_type = data[2]
            cat_code = data[3]
            tasks = [task for task in challenge[6][cat_code]["tasks"] if "homework" in task]
            if not tasks:
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, "Домашка не найдена."),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("↩️ Назад", callback_data="homework_menu"))
                )
                return
            shuffle = (order_type == "mixed")
            if shuffle:
                random.shuffle(tasks)
            user_data[user_id] = {
                "homework_tasks": tasks,
                "current_index": 0,
                "message_id": message_id,
                "cat_code": cat_code,
                "challenge_num": 6
            }
            send_homework_task(chat_id)

        elif data.startswith("homework_nav_"):
            idx = int(call.data.split("_")[2])
            user_data[user_id]["current_index"] = idx
            send_homework_task(chat_id)

        elif data.startswith("reinforce_"):
            challenge_num, cat_code, task_idx, action = call.data.split("_")
            challenge_num = int(challenge_num)
            task_idx = int(task_idx)
            if action == "analog" and "analog" in challenge[challenge_num][cat_code]["tasks"][task_idx]:
                bot.edit_message_media(
                    media=types.InputMediaPhoto(
                        challenge[challenge_num][cat_code]["tasks"][task_idx]["analog"]["photo"],
                        caption=f"Аналог задачи\n{challenge[challenge_num][cat_code]['name']} {task_idx + 1}/{len(challenge[challenge_num][cat_code]['tasks'])}\nВведите ответ в чат:"),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("↩️ Назад", callback_data=f"challenge_{challenge_num}"))
                )
                user_task_data[user_id] = {
                    "challenge_num": challenge_num,
                    "cat_code": cat_code,
                    "task_idx": task_idx,
                    "message_id": message_id,
                    "correct_answer": challenge[challenge_num][cat_code]["tasks"][task_idx]["analog"]["answer"],
                    "type": "analog",
                    "used_hints": False
                }
            else:
                next_idx = task_idx + 1 if task_idx + 1 < len(challenge[challenge_num][cat_code]["tasks"]) else 0
                bot.edit_message_media(
                    media=types.InputMediaPhoto(challenge[challenge_num][cat_code]["tasks"][next_idx]["photo"],
                                                caption=f"{challenge[challenge_num][cat_code]['name']} {next_idx + 1}/{len(challenge[challenge_num][cat_code]['tasks'])}\n❔ Введите ответ в чат:"),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("↩️ Назад", callback_data=f"challenge_{challenge_num}"))
                )
                user_task_data[user_id] = {
                    "challenge_num": challenge_num,
                    "cat_code": cat_code,
                    "task_idx": next_idx,
                    "message_id": message_id,
                    "correct_answer": challenge[challenge_num][cat_code]["tasks"][next_idx]["answer"],
                    "type": "main",
                    "used_hints": False
                }

        elif data == "stats_call":
            users_cursor.execute("""
                SELECT type, status, COUNT(*) FROM task_progress 
                WHERE user_id = ? 
                GROUP BY type, status
            """, (user_id,))
            results = users_cursor.fetchall()

            main_total = sum(r[2] for r in results if r[0] == "main")
            analog_total = sum(r[2] for r in results if r[0] == "analog")
            homework_total = sum(r[2] for r in results if r[0] == "homework")
            main_correct = sum(r[2] for r in results if r[0] == "main" and r[1] == "correct")
            analog_correct = sum(r[2] for r in results if r[0] == "analog" and r[1] == "correct")
            homework_correct = sum(r[2] for r in results if r[0] == "homework" and r[1] == "correct")

            total = main_total + analog_total + homework_total
            if total == 0:
                caption = "📊 Статистика\n\nВы ещё не решали задачи!"
            else:
                main_percent = (main_correct / main_total * 100) if main_total > 0 else 0
                analog_percent = (analog_correct / analog_total * 100) if analog_total > 0 else 0
                homework_percent = (homework_correct / homework_total * 100) if homework_total > 0 else 0
                weighted_percent = (main_percent * 0.7 + analog_percent * 0.15 + homework_percent * 0.15)
                caption = (f"📊 Статистика\n\n"
                           f"Основные задачи: {main_correct}/{main_total} ({main_percent:.1f}%)\n"
                           f"Аналоги: {analog_correct}/{analog_total} ({analog_percent:.1f}%)\n"
                           f"Домашка: {homework_correct}/{homework_total} ({homework_percent:.1f}%)\n"
                           f"Общий процент: {weighted_percent:.1f}%")

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="main_back_call"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )

        # Обработка Избранное
        elif data == "favorites":
            user_id = str(call.from_user.id)
            favorites = get_user_favorites(user_id)
            grouped_favorites = group_favorites_by_challenge(favorites)

            if not grouped_favorites:
                text = "⭐ Избранное\n\nУ вас пока нет избранных задач!"
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data="challenge_call"))
            else:
                text = "⭐ Избранное\n\nВыберите задание:"
                markup = InlineKeyboardMarkup(row_width=2)
                buttons = [
                    InlineKeyboardButton(f"Задание {num}", callback_data=f"favorites_challenge_{num}")
                    for num in sorted(grouped_favorites.keys())
                ]
                markup.add(*buttons)
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data="challenge_call"))

            bot.edit_message_media(
                media=InputMediaPhoto(photo, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        # Навигация в Избранном (Подряд, Вперемежку, По темам)
        elif data.startswith("favorites_challenge_"):
            bot.answer_callback_query(call.id, "Возврат в меню задания избранного")  # Отладка
            challenge_num = call.data.split("_")[2]
            user_id = str(call.from_user.id)
            
            # Устанавливаем режим просмотра избранного
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]["current_screen"] = "favorite_view"
            logging.info(f"Установлен режим просмотра избранного для user_id={user_id}")
            
            favorites = get_user_favorites(user_id)
            grouped_favorites = group_favorites_by_challenge(favorites)

            if not grouped_favorites or challenge_num not in grouped_favorites:
                text = f"⭐ Избранное - Задание {challenge_num}\n\nУ вас пока нет избранных задач для этого задания!"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data="favorites"))
            else:
                text = f"⭐ Избранное - Задание {challenge_num}\n\nВыберите режим просмотра:"
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("🔢 Подряд", callback_data=f"favorites_order_sequential_{challenge_num}"),
                    types.InlineKeyboardButton("🔁 Вперемежку", callback_data=f"favorites_order_mixed_{challenge_num}")
                )
                if challenge_num == "6":
                    markup.add(
                        types.InlineKeyboardButton("📚 По темам", callback_data=f"favorites_by_category_{challenge_num}")
                    )
                markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data="favorites"))

            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        # Обработка "По темам"
        elif data.startswith("favorites_by_category_"):
            challenge_num = call.data.split("_")[3]
            user_id = str(call.from_user.id)
            favorites = get_user_favorites(user_id)
            grouped_favorites = group_favorites_by_challenge(favorites)

            if challenge_num not in grouped_favorites:
                text = f"⭐ Избранное - Задание {challenge_num}\n\nЗадачи для этого задания не найдены!"
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorites_challenge_{challenge_num}"))
            else:
                text = f"⭐ Избранное - Задание {challenge_num}\n\nВыберите категорию:"
                markup = InlineKeyboardMarkup(row_width=1)
                categories = defaultdict(int)
                for cat_code, _ in grouped_favorites[challenge_num]:
                    categories[cat_code] += 1
                for cat_code, count in categories.items():
                    category_name = challenge[challenge_num][cat_code]["name"]
                    markup.add(
                        InlineKeyboardButton(f"{category_name} ({count})",
                                             callback_data=f"favorites_categories_{challenge_num}_{cat_code}")
                    )
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorites_challenge_{challenge_num}"))

            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        # Обработка "По темам" в избранном
        elif data.startswith("favorites_categories_"):
            parts = call.data.split("_")
            challenge_num, cat_code = parts[2], parts[3]
            user_id = str(call.from_user.id)
            favorites = get_user_favorites(user_id)
            tasks = [(c, t) for f in favorites
                     if f["challenge_num"] == challenge_num and f["cat_code"] == cat_code
                     for c, t in [(f["cat_code"], f["task_idx"])]]

            if not tasks:
                text = f"⭐ Избранное - Задание {challenge_num}\n\nЗадачи для этой категории не найдены!"
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorites_challenge_{challenge_num}"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                return

            user_data[user_id]["favorite_tasks"] = [(challenge_num, c, t) for c, t in tasks]
            user_data[user_id]["current_index"] = 0
            user_data[user_id]["current_mode"] = "category"
            user_data[user_id]["message_id"] = message_id

            task = challenge[challenge_num][cat_code]["tasks"][tasks[0][1]]
            total_tasks = len(tasks)
            users_cursor.execute("""
                    SELECT status FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
                """, (user_id, challenge_num, cat_code, tasks[0][1]))
            result = users_cursor.fetchone()
            status_text = "❔ Не решено" if not result else (
                f"✅ Верно\n\nПравильный ответ: {task['answer']}" if result[0] == "correct" else "❌ Не верно"
            )
            caption = f"Задача {challenge_num}\n{challenge[challenge_num][cat_code]['name']} 1/{total_tasks}\n{status_text}"
            if not result or result[0] != "correct":
                caption += "\nВведите ответ в чат:"

            markup = types.InlineKeyboardMarkup()
            nav_buttons = []
            if total_tasks > 1:
                nav_buttons.append(
                    types.InlineKeyboardButton("➡️", callback_data=f"favorite_nav_next_{challenge_num}_{cat_code}_1")
                )
            if nav_buttons:
                markup.row(*nav_buttons)
            if "hint" in task and task["hint"]:
                markup.add(
                    types.InlineKeyboardButton("💡 Подсказка",
                                               callback_data=f"hint_{challenge_num}_{cat_code}_{tasks[0][2]}_0")
                )
            markup.add(
                types.InlineKeyboardButton("🗑️ Удалить из избранного",
                                           callback_data=f"remove_favorite_{challenge_num}_{cat_code}_{tasks[0][2]}")
            )
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorites_challenge_{challenge_num}"))

            bot.edit_message_media(
                media=types.InputMediaPhoto(task["photo"], caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            user_task_data[user_id] = {
                "challenge_num": challenge_num,
                "cat_code": cat_code,
                "task_idx": tasks[0][2],
                "message_id": message_id,
                "type": "main",
                "from_favorites": True,
                "task": task,
                "current_caption": caption,
                "status": result[0] if result else None,
                "is_favorite": True
            }

        # Обработка "Подряд" и "Вперемежку" в избранном
        elif data.startswith("favorites_order_"):
            parts = call.data.split("_")
            order_type = parts[2]  # "sequential" или "mixed"
            challenge_num = parts[3]
            user_id = str(call.from_user.id)
            favorites = get_user_favorites(user_id)
            tasks = [(f["challenge_num"], f["cat_code"], f["task_idx"])
                     for f in favorites if f["challenge_num"] == challenge_num]

            if not tasks:
                text = f"⭐ Избранное - Задание {challenge_num}\n\nЗадачи не найдены!"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data="favorites"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, text),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                return

            if order_type == "mixed":
                random.shuffle(tasks)
            user_data[user_id] = {
                "favorite_tasks": tasks,
                "current_index": 0,
                "current_mode": order_type,
                "message_id": call.message.message_id,
                "current_screen": "favorite_view"  # Отмечаем, что мы в режиме просмотра избранного
            }

            task = challenge[tasks[0][0]][tasks[0][1]]["tasks"][tasks[0][2]]
            total_tasks = len(tasks)
            users_cursor.execute("""
                SELECT status FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
            """, (user_id, tasks[0][0], tasks[0][1], tasks[0][2]))
            result = users_cursor.fetchone()
            status_text = "❔ Не решено" if not result else (
                f"✅ Верно\n\nПравильный ответ: {task['answer']}" if result[0] == "correct" else "❌ Не верно"
            )
            caption = f"Задача {challenge_num}\n{challenge[tasks[0][0]][tasks[0][1]]['name']} 1/{total_tasks}\n{status_text}"
            if not result or result[0] != "correct":
                caption += "\nВведите ответ в чат:"

            markup = types.InlineKeyboardMarkup()
            nav_buttons = []
            if total_tasks > 1:
                # Добавляем кнопку вперед
                nav_buttons.append(
                    types.InlineKeyboardButton("➡️", callback_data=f"favorite_nav_next_{tasks[0][0]}_{tasks[0][1]}_1")
                )
            if nav_buttons:
                markup.row(*nav_buttons)
            if "hint" in task and task["hint"]:
                markup.add(
                    types.InlineKeyboardButton("💡 Подсказка",
                                               callback_data=f"hint_{challenge_num}_{tasks[0][1]}_{tasks[0][2]}_0")
                )
            markup.add(
                types.InlineKeyboardButton("🗑️ Удалить из избранного",
                                           callback_data=f"remove_favorite_{challenge_num}_{tasks[0][1]}_{tasks[0][2]}")
            )
            markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=f"favorites_challenge_{challenge_num}"))

            bot.edit_message_media(
                media=types.InputMediaPhoto(task["photo"], caption=caption),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            user_task_data[user_id] = {
                "challenge_num": tasks[0][0],
                "cat_code": tasks[0][1],
                "task_idx": tasks[0][2],
                "message_id": call.message.message_id,
                "type": "main",
                "from_favorites": True,
                "task": task,
                "current_caption": caption,
                "status": result[0] if result else None,
                "is_favorite": True
            }

        # Выбор в заданиях
        elif data.startswith("favorites_by_category_"):
            challenge_num = call.data.split("_")[3]
            user_id = str(call.from_user.id)
            favorites = get_user_favorites(user_id)
            grouped_favorites = group_favorites_by_challenge(favorites)

            if not favorites or challenge_num not in grouped_favorites:
                text = f"⭐ Избранное - Задание {challenge_num}\n\nЗадачи для этого задания не найдены!"
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorites_challenge_{challenge_num}"))
            else:
                text = f"⭐ Избранное - Задание {challenge_num}\n\nВыберите категорию:"
                markup = InlineKeyboardMarkup(row_width=1)
                categories = defaultdict(int)
                for cat_code, _ in grouped_favorites[challenge_num]:
                    categories[cat_code] += 1
                for cat_code, count in categories.items():
                    category_name = challenge[challenge_num][cat_code]["name"]
                    markup.add(
                        InlineKeyboardButton(f"{category_name} ({count})",
                                             callback_data=f"favorites_categories_{challenge_num}_{cat_code}")
                    )
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorites_challenge_{challenge_num}"))

            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        # Обработка "Навигация в избранном" (новый формат)
        elif data.startswith("favorite_nav_"):
            try:
                # Получаем целевой индекс из колбэка
                parts = data.split("_")
                new_index = int(parts[-1])
                
                # Обновляем текущий индекс для пользователя
                if user_id not in user_data or "favorite_tasks" not in user_data[user_id]:
                    bot.answer_callback_query(call.id, "Ошибка: список избранных задач не найден!")
                    return
                
                # Проверяем валидность нового индекса
                tasks = user_data[user_id]["favorite_tasks"]
                if new_index < 0 or new_index >= len(tasks):
                    bot.answer_callback_query(call.id, "Ошибка: указанный индекс вне допустимого диапазона!")
                    return
                
                # Обновляем текущий индекс
                user_data[user_id]["current_index"] = new_index
                
                # Отображаем задачу с новым индексом
                send_favorite_task(call.message.chat.id, call.message.message_id)
                
                return
            except Exception as e:
                logging.error(f"Ошибка при навигации по избранным заданиям: {e}")
                bot.answer_callback_query(call.id, "Произошла ошибка при навигации. Пожалуйста, попробуйте позже.")
                return
                
        # Сохраняем обработку старого формата навигации для совместимости
        elif data.startswith("favorite_nav_next_") or data.startswith("favorite_nav_prev_"):
            try:
                logging.info(f"Received callback_data in favorite_nav_old_format: {data}")
                parts = data.split("_")
                # Убираем ограничение на длину частей, так как cat_code может содержать подчеркивания
                challenge_num = parts[2]  # Изменено с parts[1] на parts[2]
                
                # Формируем cat_code, соединяя все части в середине
                cat_parts = parts[3:-1]  # Все части между challenge_num и индексом
                cat_code = "_".join(cat_parts)
                
                new_index = int(parts[-1])  # Последняя часть - индекс

                # Проверяем существование задачи
                if user_id not in user_data or "favorite_tasks" not in user_data[user_id]:
                    bot.answer_callback_query(call.id, "Ошибка: список избранных задач не найден!")
                    return

                tasks = user_data[user_id]["favorite_tasks"]
                if not (0 <= new_index < len(tasks)):
                    bot.answer_callback_query(call.id, "Нет больше задач!")
                    return

                # Логируем текущие задачи и индекс
                logging.debug(f"Current tasks: {tasks}, new_index: {new_index}")

                # Обновляем текущую задачу
                chal_num, task_cat_code, task_idx = tasks[new_index]
                total_tasks = len(tasks)
                users_cursor.execute("""
                    SELECT status FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
                """, (user_id, chal_num, task_cat_code, task_idx))
                result = users_cursor.fetchone()
                task = challenge[chal_num][task_cat_code]["tasks"][task_idx]

                # Формируем статус и подпись
                status_text = "❔ Не решено" if not result else (
                    "✅ Верно" if result[0] == "correct" else "❌ Не верно"
                )
                
                caption = (
                    f"№{chal_num}\n"
                    f"{challenge[chal_num][task_cat_code]['name']}\n"
                    f"{status_text}\n"
                )
                
                # Добавляем соответствующий текст в зависимости от статуса
                if not result or result[0] != 'correct':
                    caption += "\nВведите ответ в чат:"
                else:
                    caption += f"\n✅ Верно\n\nПравильный ответ: {task['answer']}"

                # Создаём клавиатуру
                markup = types.InlineKeyboardMarkup()
                nav_buttons = []
                
                # Добавляем левую кнопку навигации только если есть предыдущие задачи
                if new_index > 0:
                    prev_chal_num, prev_cat_code, prev_task_idx = tasks[new_index - 1]
                    nav_buttons.append(
                        types.InlineKeyboardButton("◀️",
                                                   callback_data=f"favorite_nav_prev_{prev_chal_num}_{prev_cat_code}_{new_index - 1}")
                    )
                    
                # Добавляем центральную кнопку с номером текущей задачи
                nav_buttons.append(
                    types.InlineKeyboardButton(f"{new_index + 1}/{total_tasks}", callback_data="no_action")
                )
                
                # Добавляем правую кнопку навигации только если есть следующие задачи
                if new_index < total_tasks - 1:
                    next_chal_num, next_cat_code, next_task_idx = tasks[new_index + 1]
                    nav_buttons.append(
                        types.InlineKeyboardButton("▶️",
                                                   callback_data=f"favorite_nav_next_{next_chal_num}_{next_cat_code}_{new_index + 1}")
                    )
                
                # Добавляем строку с кнопками навигации
                markup.row(*nav_buttons)

                if "hint" in task and task["hint"]:
                    markup.add(types.InlineKeyboardButton("💡 Подсказка",
                                                          callback_data=f"hint_{chal_num}_{task_cat_code}_{task_idx}_0"))

                markup.add(types.InlineKeyboardButton("🗑️ Удалить из избранного",
                                                      callback_data=f"remove_favorite_{chal_num}_{task_cat_code}_{task_idx}"))
                back_callback = f"favorites_challenge_{chal_num}"
                markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=back_callback))

                # Редактируем сообщение
                bot.edit_message_media(
                    media=types.InputMediaPhoto(task["photo"], caption=caption),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )

                # Обновляем данные пользователя
                user_task_data[user_id] = {
                    "challenge_num": chal_num,
                    "cat_code": task_cat_code,
                    "task_idx": task_idx,
                    "message_id": message_id,
                    "type": "main",
                    "from_favorites": True,
                    "task": task,
                    "current_caption": caption,
                    "status": result[0] if result else None,
                    "is_favorite": True
                }
                user_data[user_id]["current_index"] = new_index

            except Exception as e:
                logging.error(f"Error in favorite_nav_: {e}")
                bot.answer_callback_query(call.id, "Произошла ошибка при навигации.")

        # Добавление в избранное
        elif data.startswith("add_favorite_"):
            parts = call.data.split("_")
            challenge_num, cat_code, task_idx = parts[2], parts[3], int(parts[4])
            user_id = str(call.from_user.id)

            favorites_cursor.execute("""
                    INSERT OR IGNORE INTO favorites (user_id, challenge_num, cat_code, task_idx)
                    VALUES (?, ?, ?, ?)
                """, (user_id, challenge_num, cat_code, task_idx))
            favorites_conn.commit()
            logging.info(f"Задача добавлена в избранное: {challenge_num}_{cat_code}_{task_idx}")
            bot.answer_callback_query(call.id, "Добавлено в избранное!")

            task = challenge[challenge_num][cat_code]["tasks"][task_idx]
            category_name = challenge[challenge_num][cat_code]["name"]
            total_tasks = len(challenge[challenge_num][cat_code]["tasks"])

            users_cursor.execute("""
                    SELECT status FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
                """, (user_id, challenge_num, cat_code, task_idx))
            result = users_cursor.fetchone()
            status_text = "❔ Не решено" if not result else (
                f"✅ Верно\n\nПравильный ответ: {task['answer']}" if result[0] == "correct" else "❌ Не верно"
            )

            caption = f"Задача {challenge_num}\n{category_name} {task_idx + 1}/{total_tasks}\n{status_text}"
            if not result or result[0] != "correct":
                caption += "\nВведите ответ в чат:"

            markup = types.InlineKeyboardMarkup()
            nav_buttons = []
            if task_idx > 0:
                nav_buttons.append(
                    types.InlineKeyboardButton("⬅️",
                                               callback_data=f"category_{challenge_num}_{cat_code}_{task_idx - 1}")
                )
            if task_idx < total_tasks - 1:
                nav_buttons.append(
                    types.InlineKeyboardButton("➡️",
                                               callback_data=f"category_{challenge_num}_{cat_code}_{task_idx + 1}")
                )
            if nav_buttons:
                markup.row(*nav_buttons)
            if "hint" in task and task["hint"]:
                markup.add(
                    types.InlineKeyboardButton("💡 Подсказка",
                                               callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0")
                )
            markup.add(types.InlineKeyboardButton("🗑️ Удалить из избранного",
                                                  callback_data=f"remove_favorite_{challenge_num}_{cat_code}_{task_idx}"))
            from_favorites = user_task_data.get(user_id, {}).get("from_favorites", False)
            back_callback = f"favorites_challenge_{challenge_num}" if from_favorites else f"challenge_{challenge_num}"
            markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=back_callback))

            bot.edit_message_media(
                media=types.InputMediaPhoto(task["photo"], caption=caption),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        # Удаление из избранного
        elif data.startswith("remove_favorite_"):
            parts = call.data.split("_")
            challenge_num, cat_code, task_idx = parts[2], parts[3], int(parts[4])
            user_id = str(call.from_user.id)

            favorites_cursor.execute("""
                    DELETE FROM favorites 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?
                """, (user_id, challenge_num, cat_code, task_idx))
            favorites_conn.commit()
            logging.info(f"Задача удалена из избранного: {challenge_num}_{cat_code}_{task_idx}")
            bot.answer_callback_query(call.id, "Удалено из избранного!")

            task = challenge[challenge_num][cat_code]["tasks"][task_idx]
            category_name = challenge[challenge_num][cat_code]["name"]
            total_tasks = len(challenge[challenge_num][cat_code]["tasks"])

            users_cursor.execute("""
                    SELECT status FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
                """, (user_id, challenge_num, cat_code, task_idx))
            result = users_cursor.fetchone()
            status_text = "❔ Не решено" if not result else (
                f"✅ Верно\n\nПравильный ответ: {task['answer']}" if result[0] == "correct" else "❌ Не верно"
            )

            caption = f"Задача {challenge_num}\n{category_name} {task_idx + 1}/{total_tasks}\n{status_text}"
            if not result or result[0] != "correct":
                caption += "\nВведите ответ в чат:"

            markup = types.InlineKeyboardMarkup()
            nav_buttons = []
            if task_idx > 0:
                nav_buttons.append(
                    types.InlineKeyboardButton("⬅️",
                                               callback_data=f"category_{challenge_num}_{cat_code}_{task_idx - 1}")
                )
            if task_idx < total_tasks - 1:
                nav_buttons.append(
                    types.InlineKeyboardButton("➡️",
                                               callback_data=f"category_{challenge_num}_{cat_code}_{task_idx + 1}")
                )
            if nav_buttons:
                markup.row(*nav_buttons)
            if "hint" in task and task["hint"]:
                markup.add(
                    types.InlineKeyboardButton("💡 Подсказка",
                                               callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0")
                )
            markup.add(types.InlineKeyboardButton("⭐ Добавить в избранное",
                                                  callback_data=f"add_favorite_{challenge_num}_{cat_code}_{task_idx}"))
            from_favorites = user_task_data.get(user_id, {}).get("from_favorites", False)
            back_callback = f"favorites_challenge_{challenge_num}" if from_favorites else f"challenge_{challenge_num}"
            markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=back_callback))

            bot.edit_message_media(
                media=types.InputMediaPhoto(task["photo"], caption=caption),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

    except Exception as e:
        logging.error(f"Ошибка в обработчике задач: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при обработке запроса.")
# ================== Теория по заданиям и другие callback запросы ==================
@bot.callback_query_handler(func=lambda call: call.data == "quest_empty")
def handle_quest_empty(call):
    """Обработчик для пустой кнопки навигации"""
    # Просто отвечаем на callback без действий
    bot.answer_callback_query(call.id)
    return

@bot.callback_query_handler(func=lambda call: True)

def handle_callback(call):
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data
    username = call.from_user.username
    register_user(user_id, call.from_user.username)
    if user_id not in user_data:
        user_data[user_id] = {
            "favorite_tasks": [],
            "current_index": 0,
            "message_id": None,
            "current_mode": None,
            "challenge_num": None,
            "navigation_stack": [],
            "current_screen": None
        }
    logging.debug(f"Получен callback: {call.data} от user_id={user_id}")
    try:
        logging.info(f"Callback received: {data} from user_id={user_id}")
        
        # Уже обрабатывается отдельным хендлером выше
        # Оставляем эту проверку на всякий случай
        if data == "quest_empty":
            return
            
        # Подтверждаем обработку остальных callback
        bot.answer_callback_query(call.id)

        # Обработка колбэков математического квеста
        if data == "mathQuest_call":
            logging.info(f"Пользователь {user_id} открыл математический квест")
            handle_mathquest_call(call)
            return
        elif data == "mathQuest_back_call":
            handle_mathquest_back(call)
            return
        elif data == "quest_select_world":
            handle_quest_select_world(call)
            return
        elif data == "quest_profile":
            handle_quest_profile(call)
            return
        elif data == "quest_trophies":
            handle_quest_trophies(call)
            return
        elif data == "quest_shop":
            handle_quest_shop(call)
            return
        elif data.startswith("quest_world_next_") or data.startswith("quest_world_prev_"):
            handle_quest_navigation(call)
            return
        elif data.startswith("quest_enter_world_"):
            handle_quest_enter_world(call)
            return
        elif data.startswith("quest_loaded_world_"):
            handle_quest_loaded_world(call)
            return
        elif data == "quest_back_to_worlds":
            handle_quest_back_to_worlds(call)
            return
        elif data.startswith("quest_theory_"):
            handle_quest_theory(call)
            return
        elif data.startswith("theory_fsu_"):
            # Обработка фото "Формулы Сокращённого Умножения"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_fsy  # URL изображения ФСУ из instance.py
            
            text = ("Формулы сокращённого умножения\n\n"
                    "Математические выражения, упрощающие вычисления и преобразования многочленов, например:\n"
                    "квадрат суммы, разность квадратов, куб суммы и разности.")
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_quadratic_"):
            # Обработка фото "Квадратные уравнения"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_quadratic_equations  # URL изображения квадратных уравнений из instance.py
            
            text = (
                "Квадратные уравнения\n\n"
                "Уравнение вида ax² + bx + c = 0, где a ≠ 0. Для его решения используют дискриминант или метод разложения на множители."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_powers_"):
            # Обработка фото "Степени"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_powers  # URL изображения степеней из instance.py
            
            text = (
                "Степени\n\n"
                "Степень числа показывает, сколько раз число умножается само на себя."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_roots_"):
            # Обработка фото "Корни"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_roots  # URL изображения корней
            
            text = (
                "Корни\n\n"
                "Значение, которое, возведённое в степень, даёт исходное число."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trigonometry_"):
            # Обработка раздела "Тригонометрия"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("Тригонометрическая окружность", callback_data=f"theory_trig_circle_{world_id}"),
                InlineKeyboardButton("Определения", callback_data=f"theory_trig_definitions_{world_id}"),
                InlineKeyboardButton("Тригонометрические формулы", callback_data=f"theory_trig_formulas_{world_id}"),
                InlineKeyboardButton("Формулы приведения", callback_data=f"theory_trig_reduction_{world_id}"),
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            # Используем изображение книги знаний
            photo_url = photo_quest_book
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption="Тригонометрия\n\nВыберите подраздел:"),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_circle_"):
            # Обработка фото "Тригонометрическая окружность"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_trigonometric_circle  # URL изображения тригонометрической окружности
            
            text = (
                "Единичная окружность с центром в начале координат, используемая для геометрического представления тригонометрических функций."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_definitions_"):
            # Обработка фото "Определения"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_definition  # URL изображения определений
            
            text = (
                "Основные определения тригонометрии включают синус, косинус, тангенс и котангенс угла, основанные на отношениях сторон прямоугольного треугольника."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_formulas_"):
            # Обработка фото "Тригонометрические формулы"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_trigonometric_formulas  # URL изображения тригонометрических формул
            
            text = (
                "Тригонометрические формулы включают тождества, такие как формулы сложения, двойного угла, половинного угла и преобразования произведения."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_reduction_"):
            # Обработка фото "Формулы приведения"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_reduction_formulas  # URL изображения формул приведения
            
            text = (
                "Формулы приведения - правила для вычисления значений тригонометрических функций углов, выраженных через π/2, π, 3π/2."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_logarithms_"):
            # Обработка фото "Логарифмы"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            # Используем изображение логарифмов из instance.py
            photo_url = photo_logarithms
            
            text = (
                "Логарифмы\n\n"
                "Логарифм числа по основанию - это показатель степени, в которую нужно возвести основание, чтобы получить данное число."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_modules_"):
            # Обработка фото "Модули"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            # Используем изображение модулей из instance.py
            photo_url = photo_modules
            
            text = (
                "Модули\n\n"
                "Модуль числа - это его абсолютная величина (расстояние от нуля на числовой прямой). "
                "Для действительных чисел модуль всегда неотрицательный: |x| ≥ 0."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("quest_task_list_"):
            handle_quest_task_list(call)
            return
        elif data.startswith("quest_category_"):
            handle_quest_category(call)
            return
        elif data.startswith("quest_task_") and not data.startswith("quest_task_list"):
            handle_quest_task(call)
            return
        elif data.startswith("quest_answer_"):
            handle_quest_answer(call)
            return
        elif data.startswith("quest_solution_"):
            handle_quest_solution(call)
            return
        elif data.startswith("quest_hint_next_") or data.startswith("quest_hint_prev_"):
            handle_quest_hint_navigation(call)
            return
        elif data.startswith("quest_hint_direct_"):
            handle_hint_direct(call)
            return
        # НОВЫЙ УЛУЧШЕННЫЙ ОБРАБОТЧИК: Полностью переработанный обработчик для подсказок из ДЗ
        elif data.startswith("quest_homework_hint_"):
            # Извлекаем параметры
            parts = data.split("_")
            if len(parts) >= 6:
                # Формат: quest_homework_hint_world_id_cat_code_task_idx_step
                world_id = parts[3]
                cat_code = parts[4]
                task_idx = int(parts[5])
                step = int(parts[6]) if len(parts) > 6 else 0
                
                # Отмечаем, что пользователь использовал подсказку для этой задачи
                user_id = str(call.from_user.id)
                chat_id = call.message.chat.id
                message_id = call.message.message_id
                
                try:
                    # Создаем ключ для отслеживания использования подсказки
                    task_key = f"{world_id}_{cat_code}_{task_idx}"
                    
                    # Инициализируем структуру данных, если она еще не существует
                    if user_id not in user_data:
                        user_data[user_id] = {}
                    if 'viewed_hints' not in user_data[user_id]:
                        user_data[user_id]['viewed_hints'] = {}
                    
                    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Отмечаем, что пользователь просмотрел подсказку
                    user_data[user_id]['viewed_hints'][task_key] = True
                    
                    logging.info(f"⚡ ДОМАШКА: Отмечено использование подсказки для задачи {task_key} пользователем {user_id}")
                    logging.info(f"⚡ ТЕКУЩИЕ ПРОСМОТРЕННЫЕ ПОДСКАЗКИ: {user_data[user_id]['viewed_hints']}")
                    
                    # НОВОЕ: Прямое добавление в домашнюю работу при использовании подсказки
                    from fix_ritual_homework import auto_add_to_homework
                    
                    # Вызываем функцию auto_add_to_homework для гарантированного добавления в ДЗ
                    add_result = auto_add_to_homework(
                        user_id=user_id,
                        world_id=world_id,
                        cat_code=cat_code,
                        task_idx=task_idx,
                        is_correct=True,  # Предположим, что ответ будет верным
                        used_hint=True    # Подсказка точно использована
                    )
                    
                    logging.info(f"⚡ ДОМАШКА: Результат прямого добавления в ДЗ: {add_result}")
                    
                    # Сохраняем состояние подсказок в долговременной памяти
                    save_user_data(user_id)
                except Exception as e:
                    logging.error(f"❌ ОШИБКА при отметке использования подсказки в ДЗ: {e}")
                
                # ПОЛНОЕ ИСПРАВЛЕНИЕ: Теперь мы сами отображаем подсказку вместо вызова handle_hint_direct
                try:
                    world_challenges = challenge.get(world_id, {})
                    category = world_challenges.get(cat_code, {})
                    
                    if not category or 'tasks' not in category or task_idx >= len(category['tasks']):
                        bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
                        return
                    
                    task = category['tasks'][task_idx]
                    if not task or 'hint' not in task or not task['hint']:
                        bot.answer_callback_query(call.id, "Ошибка: подсказки не найдены")
                        return
                    
                    hints = task['hint']
                    if step >= len(hints):
                        step = 0  # Сбрасываем на первую подсказку, если индекс выходит за пределы
                    
                    current_hint = hints[step]
                    total_hints = len(hints)
                    
                    # Создаем клавиатуру для навигации по подсказкам
                    markup = InlineKeyboardMarkup(row_width=3)
                    
                    # Кнопки навигации по подсказкам
                    nav_buttons = []
                    
                    # Кнопка "Назад" к предыдущей подсказке
                    if step > 0:
                        prev_step = step - 1
                        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_homework_hint_{world_id}_{cat_code}_{task_idx}_{prev_step}"))
                    else:
                        # Пустая кнопка без функционала
                        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                    
                    # Индикатор текущей подсказки
                    nav_buttons.append(InlineKeyboardButton(f"{step + 1}/{total_hints}", callback_data="quest_empty"))
                    
                    # Кнопка "Вперед" к следующей подсказке
                    if step < total_hints - 1:
                        next_step = step + 1
                        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_homework_hint_{world_id}_{cat_code}_{task_idx}_{next_step}"))
                    else:
                        # Пустая кнопка без функционала
                        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                    
                    markup.row(*nav_buttons)
                    
                    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Кнопка возврата ведет обратно к домашнему заданию,
                    # а не к обычному заданию
                    markup.add(InlineKeyboardButton("↩️ Назад к заданию", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{task_idx}"))
                    
                    # Определяем тип подсказки (текст или изображение)
                    if current_hint.startswith("http") or current_hint.strip().endswith(".jpeg") or current_hint.strip().endswith(".jpg") or current_hint.strip().endswith(".png"):
                        # Если подсказка - ссылка на изображение
                        if not current_hint.startswith("http"):
                            current_hint = f"https://i.imgur.com/{current_hint}.jpeg"
                        
                        # Создаем заголовок для подсказки
                        caption = f"Подсказка {step + 1} из {total_hints}"
                        
                        # Отправляем подсказку как изображение
                        bot.edit_message_media(
                            media=InputMediaPhoto(current_hint, caption=caption),
                            chat_id=chat_id,
                            message_id=message_id,
                            reply_markup=markup
                        )
                    else:
                        # Если подсказка - текст, используем стандартное изображение
                        hint_photo = "https://i.imgur.com/ZTDhFdx.jpeg"  # Стандартное изображение для подсказок
                        
                        # Создаем текст подсказки
                        caption = f"Подсказка {step + 1} из {total_hints}\n\n{current_hint}"
                        
                        # Отправляем подсказку как изображение с текстом
                        bot.edit_message_media(
                            media=InputMediaPhoto(hint_photo, caption=caption),
                            chat_id=chat_id,
                            message_id=message_id,
                            reply_markup=markup
                        )
                    
                    logging.info(f"✅ ДОМАШКА: Успешно отображена подсказка {step + 1}/{total_hints} для задания {world_id}_{cat_code}_{task_idx}")
                except Exception as e:
                    logging.error(f"❌ ОШИБКА при отображении подсказки ДЗ: {e}")
                    bot.answer_callback_query(call.id, "Ошибка при загрузке подсказки")
            else:
                logging.error(f"❌ Некорректный формат callback для подсказки ДЗ: {data}")
            return
        elif data.startswith("quest_favorite_") and not data.startswith("quest_favorite_world_") and not data.startswith("quest_favorite_category_"):
            handle_quest_favorite(call)
            return
        elif data == "quest_favorites":
            # Используем версию с красивой анимацией загрузки
            handle_quest_favorites(call)
            return
        elif data == "quest_favorites_no_animation":
            # Версия без анимации загрузки для более быстрого ответа
            handle_quest_favorites_no_animation(call)
            return
        elif data.startswith("quest_favorite_world_"):
            handle_quest_favorite_world(call)
            return
        elif data.startswith("quest_favorite_category_"):
            handle_quest_favorite_category(call)
            return
        elif data.startswith("quest_favorite_view_ordered_"):
            handle_quest_favorite_view_ordered(call)
            return
        elif data.startswith("quest_favorite_view_random_"):
            handle_quest_favorite_view_random(call)
            return
        elif data.startswith("quest_favorite_view_by_category_"):
            handle_quest_favorite_view_by_category(call)
            return
        elif data.startswith("quest_favorite_world_categories_"):
            handle_quest_favorite_world_categories(call)
            return
        # Обработка подсказок в избранном
        elif data.startswith("hint_"):
            handle_favorite_hint(call)
            return
        # Обработка навигации по избранному
        elif data.startswith("favorite_nav_"):
            handle_favorite_navigation(call)
            return
        elif data == "quest_homework":
            # Проверяем, хочет ли пользователь посмотреть домашнюю работу или его просто автоматически перенаправляют
            # Если есть флаг homework_added, не перенаправляем пользователя автоматически
            if user_id in user_data and 'homework_added' in user_data[user_id]:
                # Получаем информацию о добавленной задаче
                homework_data = user_data[user_id].get('homework_added', {})
                message_reason = homework_data.get('reason', 'добавили задачу в ритуал повторения')
                
                # Удаляем флаг, чтобы пользователь мог вручную перейти к домашней работе
                del user_data[user_id]['homework_added']
                logging.info(f"Флаг homework_added удален для user_id={user_id}")
                
                # Отправляем сообщение пользователю вместо перенаправления
                # Убрана нотификация о добавлении в "Ритуал повторения"
                bot.answer_callback_query(call.id, "")
                # Убрано отправление сообщения пользователю о добавлении в ритуал повторения
                return
            else:
                # Если обычный переход - обрабатываем как обычно
                handle_quest_homework(call)
                return
        
        # Обработка "quest_homework_cat_*" - выбор категории домашних заданий
        elif data.startswith("quest_homework_cat_"):
            print(f"Обрабатываем callback для категории домашних заданий: {data}")
            handle_quest_homework_category(call)
            return
            
        # Обработка "quest_homework_task_*" - выбор конкретного домашнего задания
        elif data.startswith("quest_homework_task_"):
            print(f"Обрабатываем callback для задания домашней работы: {data}")
            handle_quest_homework_task(call)
            return
            
        # Обработка "Связь"
        elif data == "contact_call":
            text = (
                "📞 Связь и поддержка\n\n"
                "⬇️ Присоединяйтесь к нашему Telegram-каналу:\n"
                "@egenut\n"
                "💬 Если у вас есть вопросы или вам нужна помощь:\n"
                "@dmitriizamaraev\n"
            )
            photo_url = photo_contact
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=contact_screen()
            )

        # Обработка "Возврата в главное меню"
        elif data == "main_back_call":
            if user_id in user_data:
                del user_data[user_id]
            text = (
                "👋 Добро пожаловать!\n\n"
                "🧠 Я — ваш помощник в подготовке к ЕГЭ по профильной математике.\n"
                "📖 Вместе мы разберём задания и сделаем процесс обучения проще и эффективнее.\n"
                "➡️ Выберите действие:"
            )
            photo_url = photo_main
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=main_screen()
            )

        # Занятие с репетитором
        elif data == "tutor_call":
            text = (
                "Хотите уверенно сдать ЕГЭ по математике? Мы вам поможем! 🚀\n\n"
                "🔹 Гарантированно разберёмся в сложных темах — даже если сейчас кажется, что это невозможно.\n"
                "🔹 Подготовим к любым задачам ЕГЭ — от простых до самых сложных.\n"
                "🔹 Объясняю понятно и просто — без заумных терминов, только суть.\n\n"
                "💡 У нас уникальный метод подготовки — благодаря ему ты 100% встретишь на ЕГЭ задание, которое уже решал.\n\n"
                "P.S: Подробнее о форматах обучения и отзывах выпускников — по кнопкам ниже.\n\n"
                "🎯 Не откладывай на потом — начинай подготовку уже сегодня!"
            )
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("📚 Формат обучения", callback_data="tutor_formats"),
                InlineKeyboardButton("⭐ Отзывы", callback_data="tutor_reviews")
            )
            markup.add(InlineKeyboardButton("📩 Оставить заявку", callback_data="tutor_request"))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="main_back_call"))
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )

        # Формат обучения
        elif data == "tutor_formats":
            text = (
                "Теперь хотим тебе рассказать про самое классное в подготовке – наш подход к обучению, который помогает ученикам набирать высокие баллы на экзамене!\n\n"
                "💡 Мы не будем просто нарешивать варианты — при таком подходе в голове образуется каша из геометрии, логарифмов, производных и всего подряд. Это непродуктивно!\n\n"
                "По нашей методике мы берём одно конкретное задание и шаг за шагом разбираем все возможные прототипы. Попутно изучаем теорию и сразу закрепляем её на практике. Такой подход даёт структуру и понимание, а не механическое заучивание.\n\n"
                "Также готовиться будем на прототипах с реальных экзаменов прошлых лет. Разберём все типы заданий, которые могут встретиться на ЕГЭ, чтобы на экзамене тебе попалось 100% то, что мы уже разбирали."
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Подробнее о форматах", callback_data="tutor_format_details"))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="tutor_call"))
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )

        # Подробности о форматах
        elif data == "tutor_format_details":
            text = (
                "Какой формат подготовки тебе подойдёт больше всего? Давай разберёмся 🎯\n\n"
                "У всех свой ритм и стиль обучения: кому-то важна личная поддержка, а кто-то заряжается от командного духа. Мы учли всё и собрали несколько форматов подготовки — выбирай тот, который подходит именно тебе:\n\n"
                "✅ *Индивидуальные занятия со мной* — если хочешь, чтобы вся фокусировка была на тебе, твоих слабых местах и темпах. Разбираем всё до мельчайших деталей, пока ты не скажешь: “Теперь я это понял!”.\n\n"
                "✅ *Групповые занятия со мной* — если тебе важна динамика, поддержка и соревновательный дух. Вместе всегда проще держать темп и не сдаваться, когда лень подкрадывается.\n\n"
                "✅ *Индивидуальные занятия с топовыми преподами моей команды* — я собрал вокруг себя сильнейших преподавателей, которым сам доверяю. Ты в надёжных руках!\n\n"
                "P.S: Выбирай свой формат и заполняй анкету по кнопке «Оставить заявку»"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📩 Оставить заявку", callback_data="tutor_request"))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="tutor_formats"))
            bot.edit_message_media(
                media=InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            bot.edit_message_caption(
                caption=text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )

        # Оставить заявку
        elif data == "tutor_request":
            user_data[user_id] = {
                "tutor_step": 0,
                "tutor_answers": {},
                "message_id": message_id,
                "username": call.from_user.username
            }
            ask_tutor_question(chat_id, user_id, message_id)

        # Отзывы
        elif data == "tutor_reviews":
            user_data[user_id] = {
                "review_index": 0,
                "message_id": message_id
            }
            show_review(chat_id, user_id, message_id)

        elif data == "review_prev" or data == "review_next":
            if user_id not in user_data or "review_index" not in user_data[user_id]:
                bot.answer_callback_query(call.id, "Ошибка! Начните просмотр отзывов заново.")
                return
            current_index = user_data[user_id]["review_index"]
            if data == "review_prev" and current_index > 0:
                user_data[user_id]["review_index"] -= 1
            elif data == "review_next" and current_index < len(TUTOR_REVIEWS) - 1:
                user_data[user_id]["review_index"] += 1
            show_review(chat_id, user_id, message_id)

    #Задания
        elif data == "tasks_call" or data == "tasksBack_call":
            text = ("✨ Теория по заданиям ✨\n\n"
                    "🧠 Изучайте теоремы для решения конкретных задач.\n"
                    "➡️ Выберите номер задания и получите всё необходимое:")

            photo_url = photo_tasks

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=tasks_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "1 Задачи"
        elif data == "task_1_call":
            text = ("Задание 1 \n\n"
                "Здесь вы можете получить все теоремы для успешного решения задания"
                )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_1_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Биссектриса, медиана, серединный перпендикуляр"
        elif data == "task_triangle_lines_call":
            text = ("Биссектриса, медиана, серединный перпендикуляр\n\n"
                "Биссектриса делит угол пополам.\n"
                "Медиана соединяет вершину треугольника с серединой противоположной стороны.\n"
                "Серединный перпендикуляр проходит через середину стороны под прямым углом."
                    )
            photo_url = photo_task_triangle_lines

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Группы Треугольники"
        elif data == "task_groupTriangles_call":
            text = ("Треугольники\n\n"
                    "Здесь вы можете посмотреть все теоремы которые связаны с Треугольниками"
                    )
            photo_url = photo

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_groupTriangles_screen()
            )
        # Обработка "Прямоугольный треугольник"
        elif data == "task_right_triangle_call":
            text = ("Прямоугольный треугольник\n\n"
                    "Прямоугольный треугольник содержит прямой угол (90°).\n"
                    "Катеты — стороны, образующие прямой угол.\n"
                    "Гипотенуза — самая длинная сторона, противоположная прямому углу."
                    )
            photo_url = photo_task_right_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropTriangles_screen()
            )
        # Обработка "Равнобедренный/Равносторонний треугольник"
        elif data == "task_isosceles_equilateral_triangle_call":
            text = ("Равнобедренный и равносторонний треугольникит\n\n"
                    "Равнобедренный — две стороны равны, углы при основании тоже равны.\n"
                    "Равносторонний — все три стороны и углы (по 60°) равны.\n"
                    "В равностороннем треугольнике все медианы, высоты и биссектрисы совпадают.\n"
                    "В равнобедренном треугольнике высота, проведённая к основанию, является биссектрисой и медианой."
                    )
            photo_url = photo_task_isosceles_equilateral_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropTriangles_screen()
            )
        # Обработка "Равенство/Подобие треугольников"
        elif data == "task_triangle_similarity_call":
            text = ("Равенство/Подобие треугольников\n\n"
                    "Треугольники равны, если совпадают по 3 сторонам, 2 сторонам и углу между ними или 2 углам и стороне.\n"
                    "Треугольники подобны, если их углы равны или стороны пропорциональны."
                    )
            photo_url = photo_task_triangle_similarity

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropTriangles_screen()
            )
        # Обработка "Треугольник"
        elif data == "task_triangle_call":
            text = ("Треугольник\n\n"
                    "Сумма углов треугольника всегда 180°.\n"
                    "Сторона треугольника меньше суммы двух других сторон.\n"
                    "Высота, медиана и биссектриса, проведённые из одной вершины, могут совпадать в равнобедренном и равностороннем треугольнике."
                    )
            photo_url = photo_task_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropTriangles_screen()
            )
        # Обработка "Группы Окружность"
        elif data == "task_groupCircle_call":
            text = ("Окружность\n\n"
                    "Здесь вы можете посмотреть все теоремы которые связаны с Окружностями"
                    )
            photo_url = photo

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_groupCircle_screen()
            )
        # Обработка "Окружность 1"
        elif data == "task_circle_1_call":
            text = ("Окружность\n\n"
                    "Окружность — это множество точек, равноудалённых от центра.\n"
                    "Радиус соединяет центр окружности с её точкой.\n"
                    "Диаметр — это удвоенный радиус, проходит через центр окружности."
                    )
            photo_url = photo_task_circle_1

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropCircle_screen()
            )
        # Обработка "Окружность 2"
        elif data == "task_circle_2_call":
            text = ("Окружность\n\n"
                    "Окружность — это множество точек, равноудалённых от центра.\n"
                    "Радиус соединяет центр окружности с её точкой.\n"
                    "Диаметр — это удвоенный радиус, проходит через центр окружности."
                    )
            photo_url = photo_task_circle_2

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropCircle_screen()
            )
        # Обработка "Параллелограмм"
        elif data == "task_parallelogram_call":
            text = ("Параллелограмм\n\n"
                    "Параллелограмм — четырёхугольник, у которого противоположные стороны параллельны.\n"
                    "Противоположные стороны равны, противоположные углы равны.\n"
                    "Диагонали точкой пересечения делятся пополам."
                    )
            photo_url = photo_task_parallelogram

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()
            )
        # Обработка "Равносторонний шестиугольник"
        elif data == "task_regular_hexagon_call":
            text = ("Равносторонний шестиугольник\n\n"
                    "Равносторонний (правильный) шестиугольник — это многоугольник с шестью равными сторонами и углами.\n"
                    "Все внутренние углы равны 120°.\n"
                    "Его можно разделить на 6 равносторонних треугольников.\n"
                    "Радиус описанной окружности равен длине стороны."
                    )
            photo_url = photo_task_regular_hexagon

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()
            )
        # Обработка "Ромб и Трапеция"
        elif data == "task_rhombus_trapezoid_call":
            text = ("Ромб и Трапеция\n\n"
                    "Ромб — четырёхугольник, все стороны которого равны между собой.\n"
                    "Трапеция — четырёхугольник, у которого две стороны параллельны, а две другие — нет."
                    )
            photo_url = photo_task_rhombus_trapezoid

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()
            )
        # Обработка "Углы"
        elif data == "task_angles_call":
            text = ("Углы\n\n"
                    "Геометрическая фигура, образованная двумя лучами, выходящими из одной точки."
                    )
            photo_url = photo_task_angles

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()
            )
        # Обработка "Возврат в задания Треугольники"
        elif data == "back_to_task_gropTriangles_call":
            text = ("Треугольники\n\n"
                    "Здесь вы можете посмотреть все теоремы которые связаны с Треугольниками"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_groupTriangles_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Возврат в задания Окружность"
        elif data == "back_to_task_gropCircle_call":
            text = ("Окружность\n\n"
                    "Здесь вы можете посмотреть все теоремы которые связаны с Окружностями"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_groupCircle_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Возврат в задания 1"
        elif data == "taskBack_1_call":
            text = ("Задание 1 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_1_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "2 Задачи"
        elif data == "task_2_call":
            text = ("Задание 2 \n\n"
                    "Вектор — это направленный отрезок, то есть отрезок\n"
                    "для которого указано, какая из его граничных точек начало, а какая — конец."
                    )
            photo_url = photo_task2

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_2_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "3 Задачи"
        elif data == "task_3_call":

            text = ("Задание 3 \n\n"
                    "Стереометрия - раздел евклидовой геометрии, в котором изучаются свойства фигур в пространстве."
                    )
            photo_url = photo_task3

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_3_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "4,5 Задачи"
        elif data == "task_45_call":
            text = ("Задание 4,5 \n\n"
                    "Теория вероятностей — раздел математики, изучающий закономерности случайных явлений и их количественное описание с помощью вероятностей."
                    )
            photo_url = photo_task45

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_45_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "6,7,9 Задачи"
        elif data == "task_679_call":
            text = ("📘 Задание 6,7,9 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_679_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "ФСУ" +
        elif data == "task_fsu_call":
            text = "📘 Формулы сокращённого умножения\n\nМатематические выражения, упрощающие вычисления и преобразования многочленов, например:\nквадрат суммы, разность квадратов, куб суммы и разности."
            photo_url = photo_fsy # Ссылка на ваше изображение

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Квадратные уравнения"
        elif data == "task_quadratic_equations_call":
            text = (
                "📘 Квадратные уравнения\n\n"
                "Уравнение вида ax² + bx + c = 0, где a ≠ 0. Для его решения используют дискриминант или метод разложения на множители."
            )
            photo_url = photo_quadratic_equations #Замените на URL изображения квадратного уравнения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Степени" +
        elif data == "task_powers_call":
            text = (
                "📘 Степени\n\n"
                "Степень числа показывает, сколько раз число умножается само на себя."
            )
            photo_url = photo_powers  # Замените на URL изображения степеней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Корни"
        elif data == "task_roots_call":
            text = (
                "📘 Корни\n\n"
                "Значение, которое, возведённое в степень, даёт исходное число."
            )
            photo_url = photo_roots  # Замените на URL изображения корней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        # Обработка "Группа тригонометрия"
        elif data == "task_group_trigonometry_call":
            text = (
                "📘 Тригонометрия\n"
                "Раздел математики, изучающий свойства тригонометрических функций и их применение в решении задач."
            )
            photo_url = photo_trigonometry  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрическая окружность"
        elif data == "task_trigonometric_circle_call":
            text = (
                "📘 Тригонометрическая окружность\n\n"
                "Единичная окружность с центром в начале координат, используемая для геометрического представления тригонометрических функций."
            )
            photo_url = photo_trigonometric_circle  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Определения"
        elif data == "task_definitions_call":
            text = (
                "📘 Определения\n\n"
                "Основные определения тригонометрии включают синус, косинус, тангенс и котангенс угла, основанные на отношениях сторон прямоугольного треугольника."
            )
            photo_url = photo_definition  # Ссылка на изображение для определений

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрические формулы"
        elif data == "task_trigonometric_formulas_call":
            text = (
                "📘 Тригонометрические формулы\n\n"
                "Тригонометрические формулы включают тождества, такие как формулы сложения, двойного угла, половинного угла и преобразования произведения."
            )
            photo_url = photo_trigonometric_formulas  # Ссылка на изображение для тригонометрических формул

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Формулы приведения"
        elif data == "task_reduction_formulas_call":
            text = (
                "📘 Формулы приведения\n\n"
                "Формулы приведения позволяют преобразовывать тригонометрические функции от углов, превышающих 90° или 180°, в эквивалентные функции с углами из первого квадранта."
            )
            photo_url = photo_reduction_formulas  # Ссылка на изображение для формул приведения

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Логарифмы"+
        elif data == "task_logarithms_call":
            text = (
                "📘 Логарифмы\n\n"
                "Показатель степени, в которую нужно возвести основание логарифма, чтобы получить это число."
            )
            photo_url = photo_logarithms  # Укажите URL изображения для логарифмов

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Модули"
        elif data == "task_modules_call":
            text = (
                "📘 Модули\n\n"
                "Модуль числа показывает его расстояние от нуля на числовой прямой."
            )
            photo_url = photo_modules  # Укажите URL изображения для модулей

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Возврат в задания 6,7,9"
        elif data == "taskBack_679_call":
            text = ("📘 Задание 6,7,9 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
            )
            photo_url = photo
            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_679_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Возврат в задания тригонометрия"
        elif data == "trigonometryTaskBack_call":
            text = (
                "📘 Тригонометрия\n\n"
                "Раздел математики, изучающий свойства тригонометрических функций и их применение в решении задач."
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )


        #Обработка "8 Задачи"
        elif data == "task_8_call":
            text = ("Задание 8 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_8_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Обычная функция и производная"
        elif data == "task_usual_function_and_derivative_call":
            text = (
                "Обычная функция и производная\n\n"
                "Обычная функция показывает зависимость одной переменной от другой,\n"
                "а производная описывает скорость изменения этой зависимости в каждой точке."
            )
            photo_url = photo_task81  # Укажите URL изображения для модулей

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_8_screen()
            )
        # Обработка "Производная"
        elif data == "task_8_derivatives_call":
            text = (
                "Производная\n\n"
                "Производная функции в точке характеризует скорость изменения этой функции в данной точке."
            )
            photo_url = photo_task82  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_8_screen()
            )
        #Обработка "Возврат в задания 8"
        elif data == "taskBack_8_call":
            text = ("Задание 8 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_8_screen()  # Добавляем плашку с кнопками
            )


        #Обработка "10 Задачи"
        elif data == "task_10_call":
            text = ("Задание 10 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo_task10

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_10_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "11 Задачи"
        elif data == "task_11_call":
            text = ("Задание 11 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_11_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Прямая"+
        elif data == "task_direct_call":
            text = (
                "Прямая\n\n"
                "Это отрезок (линия), у которого нет ни начала ни конца."
            )
            photo_url = photo_direct  # Ссылка на ваше изображение

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Парабола"+
        elif data == "task_parabola_call":
            text = (
                "Парабола\n\n"
                "График квадратичной функции, у которой существует ось симметрии, "
                "и она имеет форму буквы U или перевёрнутой U."
            )
            photo_url = photo_parabola  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Гипербола" +
        elif data == "task_hyperbola_call":
            text = (
                "Гипербола\n\n"
                "Это множество точек на плоскости, для которых модуль разности расстояний от двух точек (фокусов) — величина постоянная и меньшая, чем расстояние между фокусами"
            )
            photo_url = photo_hyperbola  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Функция Корня"+
        elif data == "task_root_function_call":
            text = (
                "Функция Корня\n\n"
                r"Это функция вида y = √x, которая каждому неотрицательному значению x ставит в соответствие арифметическое значение корня"
            )
            photo_url = photo_root_function  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Показательная функция"+
        elif data == "task_exponential_function_call":
            text = (
                "Показательная функция\n\n"
                r"Функция вида y = a^x, где 'a' — положительное число, называемое основанием, а 'x' — переменная в показателе."
            )
            photo_url = photo_exponential_function  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Логарифмическая функция"+
        elif data == "task_logarithmic_function_call":
            text = (
                "Логарифмическая функция\n\n"
                r"Это функция, заданная формулой y = logax, где a > 0, a ≠ 1. Она определена при x > 0, а множество её значений — вся числовая ось."
            )
            photo_url = photo_logarithmic_function  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Возврат в задания 11"
        elif data == "taskBack_11_call":
            text = ("Задание 11 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_11_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "12 Задачи"
        elif data == "task_12_call":
            text = ("Задание 12 \n\n"
                    "Производная функции показывает скорость изменения её значения в каждой точке"
                    )
            photo_url = photo_task12

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_12_screen()  # Добавляем плашку с кнопками
            )

        # Обработка "13 Задачи"
        elif data == "task_13_call":
            text = ("Задание 13 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_13_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрическая окружность"
        elif data == "task13trigonometric_circle_call":
            text = (
                "📘 Тригонометрическая окружность\n\n"
                "Единичная окружность с центром в начале координат, используемая для геометрического представления тригонометрических функций."
            )
            photo_url = photo_trigonometric_circle  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Определения"
        elif data == "task13definitions_call":
            text = (
                "📘 Определения\n\n"
                "Основные определения тригонометрии включают синус, косинус, тангенс и котангенс угла, основанные на отношениях сторон прямоугольного треугольника."
            )
            photo_url = photo_definition  # Ссылка на изображение для определений

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрические формулы"
        elif data == "task13trigonometric_formulas_call":
            text = (
                "Тригонометрические формулы включают тождества, такие как формулы сложения, двойного угла, половинного угла и преобразования произведения."
            )
            photo_url = photo_trigonometric_formulas  # Ссылка на изображение для тригонометрических формул

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Формулы приведения"
        elif data == "task13reduction_formulas_call":
            text = (
                "Формулы приведения позволяют преобразовывать тригонометрические функции от углов, превышающих 90° или 180°, в эквивалентные функции с углами из первого квадранта."
            )
            photo_url = photo_reduction_formulas  # Ссылка на изображение для формул приведения

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Группа тригонометрия"
        elif data == "tasks13trigGroup_call":
            text = (
                "📘 Тригонометрия\n\n"
                "Раздел математики, изучающий свойства тригонометрических функций и их применение в решении задач."
            )
            photo_url = photo_trigonometry  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Логарифмы"
        elif data == "tasks13log_call":
            text = (
                "Логарифмы\n\n"
                "Показатель степени, в которую нужно возвести основание логарифма, чтобы получить это число."
            )
            photo_url = photo_logarithms  # Укажите URL изображения для логарифмов

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_13_screen()
            )
        # Обработка "Корни"
        elif data == "tasks13root_call":
            text = (
                "Корни\n\n"
                "Значение, которое, возведённое в степень, даёт исходное число."
            )
            photo_url = photo_roots  # Замените на URL изображения корней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_13_screen()
            )
        # Обработка "Степени"
        elif data == "tasks13powers_call":
            text = (
                "Степени\n\n"
                "Степень числа показывает, сколько раз число умножается само на себя."
            )
            photo_url = photo_powers  # Замените на URL изображения степеней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_13_screen()
            )
        #Обработка "ФСУ"
        elif data == "tasks13fcy_call":
            text = "Формулы сокращённого умножения"
            photo_url = photo_fsy # Ссылка на ваше изображение

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_13_screen()
            )
        # Обработка "Возврат в задания тригонометрия"
        elif data == "trigonometryTask13Back_call":
            text = (
                "Тригонометрия\n"
                "Раздел математики, изучающий свойства тригонометрических функций и их применение в решении задач."
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Возврат в задания 13"
        elif data == "taskBack_13_call":
            text = ("Задание 13 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_13_screen()  # Добавляем плашку с кнопками
            )

        # Обработка "14 Задачи"
        elif data == "task_14_call":
            text = ("Задание 14 \n\n"
                    "Здесь вы можете получить все теорию для успешного решения задания"
                    )

            photo_url = photo_task14

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_12_screen()  # Добавляем плашку с кнопками
            )

        # Обработка "15 Задачи"
        elif data == "task_15_call":
            text = ("Задание 15 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_15_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Логарифмы"
        elif data == "tasks15log_call":
            text = (
                "Логарифмы\n\n"
                "Показатель степени, в которую нужно возвести основание логарифма, чтобы получить это число."
            )
            photo_url = photo_logarithms  # Укажите URL изображения для логарифмов

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        # Обработка "Метод рационализации"
        elif data == "tasks15rationalization_call":
            text = (
                "📘 Метод рационализации\n\n"
                "Заключается в преобразовании иррациональных выражений или уравнений в рациональные для упрощения их анализа и решения."
            )
            photo_url = photo_rationalization  # Укажите URL изображения для логарифмов

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        # Обработка "Степени"
        elif data == "tasks15powers_call":
            text = (
                "Степени\n\n"
                "Степень числа показывает, сколько раз число умножается само на себя."
            )
            photo_url = photo_powers  # Замените на URL изображения степеней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        # Обработка "Корни"
        elif data == "tasks15roots_call":
            text = (
                "Корни\n\n"
                "Значение, которое, возведённое в степень, даёт исходное число."
            )
            photo_url = photo_roots  # Замените на URL изображения корней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        #Обработка "ФСУ"
        elif data == "tasks15fcy_call":
            text = "Формулы сокращённого умножения"
            photo_url = photo_fsy # Ссылка на ваше изображение

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        #Обработка "Квадратные уравнения"
        elif data == "task15quadratic_equations_call":
            text = "Квадратные уравнения"

            photo_url = photo_quadratic_equations #Замените на URL изображения квадратного уравнения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        #Обработка "Модули"
        elif data == "task15modules_call":
            text = (
                "📘 Модули\n\n"
                "Модуль числа показывает его расстояние от нуля на числовой прямой."
            )
            photo_url = photo_modules  # Укажите URL изображения для модулей

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        # Обработка "Возврат в задания 15"
        elif data == "taskBack_15_call":
            text = ("📘 Задание 15 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_15_screen()  # Добавляем плашку с кнопками
            )

        # Обработка "16 Задачи"
        elif data == "task_16_call":
            text = ("📘 Задание 16 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )

            photo_url = photo_task16

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_12_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "17 Задачи"
        elif data == "task_17_call":
            text = ("📘 Задание 17 \n\n"
                "Здесь вы можете получить все теоремы для успешного решения задания"
                )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_17_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Группы Треугольники"
        elif data == "task17groupTriangles_call":
            text = ("📘 Треугольники\n\n"
                    "Здесь вы можете посмотреть все теоремы которые связаны с Треугольниками"
                    )
            photo_url = photo

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17groupTriangles_screen()
            )
        # Обработка "Прямоугольный треугольник"
        elif data == "task17right_triangle_call":
            text = ("📘 Прямоугольный треугольник\n\n"
                    "Прямоугольный треугольник содержит прямой угол (90°).\n"
                    "Катеты — стороны, образующие прямой угол.\n"
                    "Гипотенуза — самая длинная сторона, противоположная прямому углу."
                    )
            photo_url = photo_task_right_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()
            )
        # Обработка "Равнобедренный/Равносторонний треугольник"
        elif data == "task17isosceles_equilateral_triangle_call":
            text = ("📘 Равнобедренный и равносторонний треугольникит\n\n"
                    "Равнобедренный — две стороны равны, углы при основании тоже равны.\n"
                    "Равносторонний — все три стороны и углы (по 60°) равны.\n"
                    "В равностороннем треугольнике все медианы, высоты и биссектрисы совпадают.\n"
                    "В равнобедренном треугольнике высота, проведённая к основанию, является биссектрисой и медианой."
                    )
            photo_url = photo_task_isosceles_equilateral_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()
            )
        # Обработка "Равенство/Подобие треугольников"
        elif data == "task17triangle_similarity_call":
            text = ("📘 Равенство/Подобие треугольников\n\n"
                    "Треугольники равны, если совпадают по 3 сторонам, 2 сторонам и углу между ними или 2 углам и стороне.\n"
                    "Треугольники подобны, если их углы равны или стороны пропорциональны."
                    )
            photo_url = photo_task_triangle_similarity

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()
            )
        # Обработка "Треугольник"
        elif data == "task17triangle_call":
            text = ("📘 Треугольник\n\n"
                    "Сумма углов треугольника всегда 180°.\n"
                    "Сторона треугольника меньше суммы двух других сторон.\n"
                    "Высота, медиана и биссектриса, проведённые из одной вершины, могут совпадать в равнобедренном и равностороннем треугольнике."
                    )
            photo_url = photo_task_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()
            )
        # Обработка "Биссектриса, медиана, серединный перпендикуляр"
        elif data == "task17triangle_lines_call":
            text = ("📘 Биссектриса, медиана, серединный перпендикуляр\n\n"
                "Биссектриса делит угол пополам.\n"
                "Медиана соединяет вершину треугольника с серединой противоположной стороны.\n"
                "Серединный перпендикуляр проходит через середину стороны под прямым углом."
                    )
            photo_url = photo_task_triangle_lines

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Группы Окружность"
        elif data == "task17groupCircle_call":
            text = ("📘 Окружность\n\n"
                    "Здесь вы можете посмотреть все теоремы которые связаны с Окружностями"
                    )
            photo_url = photo

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17groupCircle_screen()
            )
        # Обработка "Окружность 1"
        elif data == "task17circle_1_call":
            text = ("📘 Окружность\n\n"
                    "Окружность — это множество точек, равноудалённых от центра.\n"
                    "Радиус соединяет центр окружности с её точкой.\n"
                    "Диаметр — это удвоенный радиус, проходит через центр окружности."
                    )
            photo_url = photo_task_circle_1

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropCircle_screen()
            )
        # Обработка "Окружность 2"
        elif data == "task17circle_2_call":
            text = ("📘 Окружность\n\n"
                    "Окружность — это множество точек, равноудалённых от центра.\n"
                    "Радиус соединяет центр окружности с её точкой.\n"
                    "Диаметр — это удвоенный радиус, проходит через центр окружности."
                    )
            photo_url = photo_task_circle_2

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropCircle_screen()
            )
        # Обработка "Параллелограмм"
        elif data == "task17parallelogram_call":
            text = ("📘 Параллелограмм\n\n"
                    "Параллелограмм — четырёхугольник, у которого противоположные стороны параллельны.\n"
                    "Противоположные стороны равны, противоположные углы равны.\n"
                    "Диагонали точкой пересечения делятся пополам."
                    )
            photo_url = photo_task_parallelogram

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_17_screen()
            )
        # Обработка "Равносторонний шестиугольник"
        elif data == "task17regular_hexagon_call":
            text = ("📘 Равносторонний шестиугольник\n\n"
                    "Равносторонний (правильный) шестиугольник — это многоугольник с шестью равными сторонами и углами.\n"
                    "Все внутренние углы равны 120°.\n"
                    "Его можно разделить на 6 равносторонних треугольников.\n"
                    "Радиус описанной окружности равен длине стороны."
                    )
            photo_url = photo_task_regular_hexagon

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_17_screen()
            )
        # Обработка "Ромб и Трапеция"
        elif data == "task17rhombus_trapezoid_call":
            text = ("📘 Ромб и Трапеция\n\n"
                    "Ромб — четырёхугольник, все стороны которого равны между собой.\n"
                    "Трапеция — четырёхугольник, у которого две стороны параллельны, а две другие — нет."
                    )
            photo_url = photo_task_rhombus_trapezoid

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_17_screen()
            )
        # Обработка "Углы"
        elif data == "task17angles_call":
            text = ("📘 Углы\n\n"
                    "Геометрическая фигура, образованная двумя лучами, выходящими из одной точки."
                    )
            photo_url = photo_task_angles

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_17_screen()
            )
        # Обработка "Возврат в задания Треугольники"
        elif data == "back_to_task17gropTriangles_call":
            text = ("📘 Треугольники\n\n"
                    "Здесь вы можете посмотреть все теоремы которые связаны с Треугольниками"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17groupTriangles_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Возврат в задания Окружность"
        elif data == "back_to_task17gropCircle_call":
            text = ("📘 Окружность\n\n"
                    "Здесь вы можете посмотреть все теоремы которые связаны с Окружностями"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17groupCircle_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Группа тригонометрия"
        elif data == "task17group_trigonometry_call":
            text = (
                "Тригонометрия\n"
                "Раздел математики, изучающий свойства тригонометрических функций и их применение в решении задач."
            )
            photo_url = photo_trigonometry  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрическая окружность"
        elif data == "task17trigonometric_circle_call":
            text = (
                "Единичная окружность с центром в начале координат, используемая для геометрического представления тригонометрических функций."
            )
            photo_url = photo_trigonometric_circle  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Определения"
        elif data == "task17definitions_call":
            text = (
                "Основные определения тригонометрии включают синус, косинус, тангенс и котангенс угла, основанные на отношениях сторон прямоугольного треугольника."
            )
            photo_url = photo_definition  # Ссылка на изображение для определений

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрические формулы"
        elif data == "task17trigonometric_formulas_call":
            text = (
                "Тригонометрические формулы включают тождества, такие как формулы сложения, двойного угла, половинного угла и преобразования произведения."
            )
            photo_url = photo_trigonometric_formulas  # Ссылка на изображение для тригонометрических формул

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Формулы приведения"
        elif data == "task17reduction_formulas_call":
            text = (
                "Формулы приведения позволяют преобразовывать тригонометрические функции от углов, превышающих 90° или 180°, в эквивалентные функции с углами из первого квадранта."
            )
            photo_url = photo_reduction_formulas  # Ссылка на изображение для формул приведения

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Возврат в задания тригонометрия"
        elif data == "trigonometryTask17Back_call":
            text = (
                "Тригонометрия\n"
                "Раздел математики, изучающий свойства тригонометрических функций и их применение в решении задач."
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Возврат в задания 17"
        elif data == "taskBack_17_call":
            text = ("📘 Задание 17 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_17_screen()  # Добавляем плашку с кнопками
            )

        # Обрабатывает выбор "Теория по темам" и показывает начальный экран с разделами
        elif data == "tasks_by_topic_call":
            text = ("✨ Теория по темам ✨\n\n"
                    "📚 Погружайтесь в теорию по разделам математики.\n"
                    "➡️ Выберите тему и разберитесь в основах:")
            photo_url = photo_tasks
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=tasks_by_topic_screen()
            )
        # Обрабатывает выбор раздела "Алгебра" и показывает список тем алгебры
        elif data == "topics_algebra_call":
            text = ("📘 Темы Алгебры\n\n"
                    "Выберите тему для просмотра теории:")
            photo_url = photo
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=algebra_topics_screen()
            )
        # Обрабатывает выбор раздела "Геометрия" и показывает список тем геометрии
        elif data == "topics_geometry_call":
            text = ("📘 Темы Геометрии\n\n"
                    "Выберите тему для просмотра теории:")
            photo_url = photo
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=geometry_topics_screen()
            )

        # --- Темы Алгебры ---
        elif data == "topic_probability_call":
            text = ("📘 Теория вероятностей\n\n"
                    "Теория вероятностей — раздел математики, изучающий закономерности случайных явлений и их количественное описание с помощью вероятностей.")
            photo_url = photo_task45
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "ФСУ" из заданий 6,7,9
        elif data == "topic_fsu_call":
            text = ("Формулы сокращённого умножения\n\n"
                   "Математические выражения, упрощающие вычисления и преобразования многочленов, например:\n"
                   "квадрат суммы, разность квадратов, куб суммы и разности.")
            photo_url = photo_fsy
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=back_to_theory_screen()
            )
        elif data == "topic_quadratic_call":
            text = ("Квадратные уравнения\n\n"
                   "Уравнение вида ax² + bx + c = 0, где a ≠ 0. Для его решения используют дискриминант или метод разложения на множители.")
            photo_url = photo_quadratic_equations
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Степени" из заданий 6,7,9
        elif data == "topic_powers_call":
            text = ("Степени\n\n"
                   "Степень числа показывает, сколько раз число умножается само на себя.")
            photo_url = photo_powers
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Корни" из заданий 6,7,9
        elif data == "topic_roots_call":
            text = ("Корни\n\n"
                   "Значение, которое, возведённое в степень, даёт исходное число.")
            photo_url = photo_roots
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Тригонометрическая окружность" из заданий 6,7,9
        elif data == "topic_trigonometric_circle_call":
            text = ("Тригонометрическая окружность\n\n"
                   "Единичная окружность с центром в начале координат, используемая для геометрического представления тригонометрических функций.")
            photo_url = photo_trigonometric_circle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=back_to_theory_screen()
            )
        elif data == "topic_definitions_call":
            text = "Определения тригонометрических функций"
            photo_url = photo_definition
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=back_to_theory_screen()
            )
        elif data == "topic_definitions_call":
            text = "Определения тригонометрических функций"
            photo_url = photo_definitions
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=back_to_theory_screen()
            )
            photo_url = photo_trigonometric_formulas
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        elif data == "topic_trigonometric_formulas_call":
            text = "Основные тригонометрические формулы"
            photo_url = photo_trigonometric_formulas
            photo_url = photo_reduction_formulas
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Логарифмы" из заданий 6,7,9
        elif data == "topic_reduction_formulas_call":
            text = "Формулы приведения"
            photo_url = photo_reduction_formulas
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Модули" из заданий 6,7,9
        elif data == "topic_modules_call":
            text = "Модули"
            photo_url = photo_modules
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Обычная функция и производная" из задания 8
        elif data == "topic_usual_function_and_derivative_call":
            text = "Обычные функции и производные"
            photo_url = photo_usual_function_and_derivative
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="topics_algebra_call"))
            )
        elif data == "topic_modules_call":
            text = "Модули"
            photo_url = photo_modules
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Производная" из задания 8
        elif data == "topic_derivative_call":
            text = "Производная"
            photo_url = photo_derivative
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Функция корня" из задания 11
        elif data == "topic_root_function_call":
            text = ("📘 Функция корня\n\n"
                    r"Это функция вида y = √x, которая каждому неотрицательному значению x ставит в соответствие арифметическое значение корня.")
            photo_url = photo_root_function
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Показательная функция" из задания 11
        elif data == "topic_exponential_function_call":
            text = ("📘 Показательная функция\n\n"
                    r"Функция вида y = a^x, где 'a' — положительное число, называемое основанием, а 'x' — переменная в показателе.")
            photo_url = photo_exponential_function
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Логарифмическая функция" из задания 11
        elif data == "topic_logarithmic_function_call":
            text = ("📘 Логарифмическая функция\n\n"
                    r"Это функция, заданная формулой y = logax, где a > 0, a ≠ 1. Она определена при x > 0, а множество её значений — вся числовая ось.")
            photo_url = photo_logarithmic_function
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Метод рационализации" из задания 15
        elif data == "topic_rationalization_call":
            text = ("📘 Метод рационализации\n\n"
                    "Заключается в преобразовании иррациональных выражений или уравнений в рациональные для упрощения их анализа и решения.")
            photo_url = photo_rationalization
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )

        # --- Темы Геометрии ---
        elif data == "topic_triangle_lines_call":
            text = ("📘 Биссектриса, медиана, серединный перпендикуляр\n\n"
                    "Биссектриса делит угол пополам.\n"
                    "Медиана соединяет вершину треугольника с серединой противоположной стороны.\n"
                    "Серединный перпендикуляр проходит через середину стороны под прямым углом.")
            photo_url = photo_task_triangle_lines
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Прямоугольный треугольник" из задания 1
        elif data == "topic_right_triangle_call":
            text = ("📘 Прямоугольный треугольник\n\n"
                    "Прямоугольный треугольник содержит прямой угол (90°).\n"
                    "Катеты — стороны, образующие прямой угол.\n"
                    "Гипотенуза — самая длинная сторона, противоположная прямому углу.")
            photo_url = photo_task_right_triangle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Равнобедренный/Равносторонний треугольник" из задания 1
        elif data == "topic_isosceles_equilateral_triangle_call":
            text = ("📘 Равнобедренный и равносторонний треугольник\n\n"
                    "Равнобедренный — две стороны равны, углы при основании тоже равны.\n"
                    "Равносторонний — все три стороны и углы (по 60°) равны.\n"
                    "В равностороннем треугольнике все медианы, высоты и биссектрисы совпадают.\n"
                    "В равнобедренном треугольнике высота, проведённая к основанию, является биссектрисой и медианой.")
            photo_url = photo_task_isosceles_equilateral_triangle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Равенство/Подобие треугольников" из задания 1
        elif data == "topic_triangle_similarity_call":
            text = ("📘 Равенство/Подобие треугольников\n\n"
                    "Треугольники равны, если совпадают по 3 сторонам, 2 сторонам и углу между ними или 2 углам и стороне.\n"
                    "Треугольники подобны, если их углы равны или стороны пропорциональны.")
            photo_url = photo_task_triangle_similarity
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Треугольник" из задания 1
        elif data == "topic_triangle_call":
            text = ("📘 Треугольник\n\n"
                    "Сумма углов треугольника всегда 180°.\n"
                    "Сторона треугольника меньше суммы двух других сторон.\n"
                    "Высота, медиана и биссектриса, проведённые из одной вершины, могут совпадать в равнобедренном и равностороннем треугольнике.")
            photo_url = photo_task_triangle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Окружность" из задания 1
        elif data == "topic_circle_call":
            text = ("📘 Окружность\n\n"
                    "Окружность — это множество точек, равноудалённых от центра.\n"
                    "Радиус соединяет центр окружности с её точкой.\n"
                    "Диаметр — это удвоенный радиус, проходит через центр окружности.")
            photo_url = photo_task_circle_1
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Параллелограмм" из задания 1
        elif data == "topic_parallelogram_call":
            text = ("📘 Параллелограмм\n\n"
                    "Параллелограмм — четырёхугольник, у которого противоположные стороны параллельны.\n"
                    "Противоположные стороны равны, противоположные углы равны.\n"
                    "Диагонали точкой пересечения делятся пополам.")
            photo_url = photo_task_parallelogram
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Равносторонний шестиугольник" из задания 1
        elif data == "topic_regular_hexagon_call":
            text = ("📘 Равносторонний шестиугольник\n\n"
                    "Равносторонний (правильный) шестиугольник — это многоугольник с шестью равными сторонами и углами.\n"
                    "Все внутренние углы равны 120°.\n"
                    "Его можно разделить на 6 равносторонних треугольников.\n"
                    "Радиус описанной окружности равен длине стороны.")
            photo_url = photo_task_regular_hexagon
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Ромб и Трапеция" из задания 1
        elif data == "topic_rhombus_trapezoid_call":
            text = ("📘 Ромб и Трапеция\n\n"
                    "Ромб — четырёхугольник, все стороны которого равны между собой.\n"
                    "Трапеция — четырёхугольник, у которого две стороны параллельны, а две другие — нет.")
            photo_url = photo_task_rhombus_trapezoid
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Углы" из задания 1
        elif data == "topic_angles_call":
            text = ("📘 Углы\n\n"
                    "Геометрическая фигура, образованная двумя лучами, выходящими из одной точки.")
            photo_url = photo_task_angles
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Вектор" из задания 2
        elif data == "topic_vector_call":
            text = ("📘 Вектор\n\n"
                    "Вектор — это направленный отрезок, то есть отрезок,\n"
                    "для которого указано, какая из его граничных точек начало, а какая — конец.")
            photo_url = photo_task2
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Стереометрия" из задания 3
        elif data == "topic_stereometry_call":
            text = ("📘 Стереометрия\n\n"
                    "Стереометрия - раздел евклидовой геометрии, в котором изучаются свойства фигур в пространстве.")
            photo_url = photo_task3
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Прямая" из задания 11
        elif data == "topic_direct_call":
            text = ("📘 Прямая\n\n"
                    "Это отрезок (линия), у которого нет ни начала, ни конца.")
            photo_url = photo_direct
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Парабола" из задания 11
        elif data == "topic_parabola_call":
            text = ("📘 Парабола\n\n"
                    "График квадратичной функции, у которой существует ось симметрии,\n"
                    "и она имеет форму буквы U или перевёрнутой U.")
            photo_url = photo_parabola
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Гипербола" из задания 11
        elif data == "topic_hyperbola_call":
            text = ("📘 Гипербола\n\n"
                    "Это множество точек на плоскости, для которых модуль разности расстояний от двух точек (фокусов) — величина постоянная и меньшая, чем расстояние между фокусами.")
            photo_url = photo_hyperbola
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Обработка кнопки "Теория"
        elif data == "theory_call":
            text = ("✨ Теория для ЕГЭ ✨\n\n"
                    "🧑‍🏫 Осваивайте теорию для подготовки к экзамену.\n"
                    "➡️ Выберите удобный способ изучения:")
            photo_url = photo_tasks  # Можно использовать другое фото, если хотите
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=theory_screen()
            )

    # Quiz
        elif data == "quiz_call":
            text = ("✨ Варианты ЕГЭ ✨\n\n"
                    "📝 Практикуйтесь, решая реальные варианты ЕГЭ.\n"
                    "➡️ Выберите вариант и вводите ответы в чат:")
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo_quize, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=quiz_screen()
            )

        elif data.startswith("quiz_page_"):
            page = int(call.data.split("_")[-1])
            text = (
                "📝 Варианты\n\n"
                "Здесь вы можете решить вариант ЕГЭ .\n"
                "При решении задачи, введите ответ в чат.\n"
                "Выберите вариант:"
            )
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=quiz_screen(page=page)
            )

        elif data.startswith("start_quiz_"):
            day = int(call.data.split("_")[-1])  # Вариант = день
            current_option = day  # Вариант соответствует номеру варианта
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            user_id = str(call.from_user.id)
            username = call.from_user.username or call.from_user.first_name or "Unknown"

            # Проверяем, есть ли незавершённый прогресс
            cursor = quiz_conn.cursor()
            cursor.execute('''
                SELECT task_number, attempt_id, primary_score, secondary_score 
                FROM user_quiz_state 
                WHERE user_id = ? AND option = ? AND day = ? AND completed = 0
                ORDER BY timestamp DESC LIMIT 1
            ''', (user_id, current_option, day))
            state = cursor.fetchone()
            cursor.close()

            if state and user_id in user_data and "attempt_id" in user_data[user_id]:
                # Продолжаем незавершённую попытку
                task_number, attempt_id, primary_score, secondary_score = state
                user_data[user_id]["task_number"] = task_number
                user_data[user_id]["message_id"] = message_id
                user_data[user_id]["correct"] = primary_score
                user_data[user_id]["secondary_score"] = secondary_score
            else:
                # Начинаем новую попытку
                attempt_id = int(datetime.now().timestamp())
                user_data[user_id] = {
                    "task_number": 1,
                    "day": day,
                    "current_option": current_option,
                    "attempt_id": attempt_id,
                    "correct": 0,
                    "secondary_score": 0,
                    "results": [],
                    "message_id": message_id
                }
                logging.info(f"Новая попытка начата для пользователя {user_id}: attempt_id={attempt_id}")

            # Загружаем задание
            cursor = quiz_conn.cursor()
            cursor.execute('SELECT id, image_url FROM quiz_tasks WHERE option = ? AND day = ? AND task_number = ?',
                           (current_option, day, user_data[user_id]["task_number"]))
            task = cursor.fetchone()
            cursor.close()

            if task:
                quiz_id, image_url = task
                user_data[user_id]["quiz_id"] = quiz_id
                logging.info(
                    f"Загружена задача quiz_id={quiz_id}, option={current_option}, day={day}, task_number={user_data[user_id]['task_number']}")
                text = f"В-{day}, №{user_data[user_id]['task_number']:02d}\nВведите ответ:"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Начать с начала", callback_data=f"reset_quiz_{day}"))
                markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_back_call"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(image_url, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                # Сохраняем текущий прогресс
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, current_option, day, user_data[user_id]["task_number"], user_data[user_id]["attempt_id"],
                      user_data[user_id]["correct"], user_data[user_id]["secondary_score"], 0, datetime.now().isoformat(),
                      username))
                quiz_conn.commit()
                cursor.close()
                # Регистрируем обработчик для ответа
                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler_by_chat_id(chat_id, process_quiz_answer)
            else:
                logging.error(
                    f"Задача не найдена для option={current_option}, day={day}, task_number={user_data[user_id]['task_number']}")
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption="Ошибка! Задачи не найдены."),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=quiz_screen()
                )

        elif data == "quiz_back_call":
            text = ("✨ Варианты ЕГЭ ✨\n\n"
                    "📝 Практикуйтесь, решая реальные варианты ЕГЭ.\n"
                    "➡️ Выберите вариант и вводите ответы в чат:")
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=quiz_screen()
            )
            # Сохраняем прогресс, но не очищаем user_data полностью
            if user_id in user_data:
                # Получаем имя пользователя
                username = call.from_user.username or call.from_user.first_name or "Unknown"
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, user_data[user_id]["current_option"], user_data[user_id]["day"],
                    user_data[user_id]["task_number"],
                    user_data[user_id]["attempt_id"], user_data[user_id]["correct"], user_data[user_id]["secondary_score"],
                    0,
                    datetime.now().isoformat(), username))
                quiz_conn.commit()
                cursor.close()
                # Очищаем обработчик для текущего чата
                bot.clear_step_handler_by_chat_id(chat_id)

        elif data.startswith("reset_quiz_"):
            day = int(call.data.split("_")[-1])
            current_option = day
            # Удаляем текущий прогресс
            cursor = quiz_conn.cursor()
            cursor.execute('DELETE FROM user_quiz_state WHERE user_id = ? AND option = ? AND day = ? AND completed = 0',
                           (user_id, current_option, day))
            quiz_conn.commit()
            cursor.close()
            # Начинаем новую попытку
            attempt_id = int(datetime.now().timestamp())
            # Получаем имя пользователя
            username = call.from_user.username or call.from_user.first_name or "Unknown"
            user_data[user_id] = {
                "task_number": 1,
                "day": day,
                "current_option": current_option,
                "attempt_id": attempt_id,
                "correct": 0,
                "secondary_score": 0,
                "results": [],
                "message_id": message_id
            }
            # Загружаем первое задание
            cursor = quiz_conn.cursor()
            cursor.execute('SELECT id, image_url FROM quiz_tasks WHERE option = ? AND day = ? AND task_number = ?',
                           (current_option, day, user_data[user_id]["task_number"]))
            task = cursor.fetchone()
            cursor.close()
            if task:
                quiz_id, image_url = task
                user_data[user_id]["quiz_id"] = quiz_id
                logging.info(
                    f"Загружена задача после сброса quiz_id={quiz_id}, option={current_option}, day={day}, task_number={user_data[user_id]['task_number']}")
                text = f"В-{day}, №{user_data[user_id]['task_number']:02d}\nВведите ответ:"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Начать с начала", callback_data=f"reset_quiz_{day}"))
                markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_back_call"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(image_url, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                # Сохраняем текущий прогресс
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, current_option, day, user_data[user_id]["task_number"], user_data[user_id]["attempt_id"],
                      user_data[user_id]["correct"], user_data[user_id]["secondary_score"], 0, datetime.now().isoformat(),
                      username))
                quiz_conn.commit()
                cursor.close()
                # Очищаем предыдущие обработчики и регистрируем новый
                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler_by_chat_id(chat_id, process_quiz_answer)
            else:
                logging.error(
                    f"Задача не найдена после сброса для option={current_option}, day={day}, task_number={user_data[user_id]['task_number']}")
                bot.edit_message_text(
                    "❌ Задачи для этого варианта ещё не загружены!",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=quiz_screen()
                )

        elif data == "quiz_stats":
            text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=stats_screen(user_id, page=1)  # Передаём user_id
            )

        elif data.startswith("stats_page_"):
            page = int(call.data.split("_")[-1])
            text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=stats_screen(user_id, page=page)  # Передаём user_id
            )

        elif data.startswith("stats_variant_"):
            variant = int(call.data.split("_")[-1])
            text = f"📊 Статистика для Варианта {variant}\n\nВыберите попытку для просмотра:"
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=stats_attempts_screen(user_id, variant, page=1)
            )

        elif data.startswith("stats_attempt_"):
            parts = call.data.split("_")
            logging.info(f"Обработка stats_attempt_, call.data: {call.data}, parts: {parts}")
            if len(parts) != 4:  # Ожидаем ["stats", "attempt", variant, attempt_id]
                logging.error(f"Некорректный формат callback_data для stats_attempt_: {call.data}")
                text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=stats_screen(user_id, page=1)
                )
                return
            _, _, variant, attempt_id = parts
            try:
                variant = int(variant)
                attempt_id = int(attempt_id)
            except ValueError as e:
                logging.error(
                    f"Ошибка при преобразовании variant или attempt_id: variant={variant}, attempt_id={attempt_id}, ошибка: {e}")
                text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=stats_screen(user_id, page=1)
                )
                return
            # Получаем данные попытки
            cursor = quiz_conn.cursor()
            cursor.execute('''
                SELECT primary_score, secondary_score 
                FROM user_quiz_state 
                WHERE user_id = ? AND option = ? AND attempt_id = ?
            ''', (user_id, variant, attempt_id))
            state = cursor.fetchone()
            cursor.close()
            if state:
                primary_score, secondary_score = state
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    SELECT task_number, user_answer 
                    FROM user_quiz_progress 
                    WHERE user_id = ? AND attempt_id = ? AND option = ?
                    ORDER BY task_number
                ''', (user_id, attempt_id, variant))
                user_answers = cursor.fetchall()
                cursor.close()
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    SELECT task_number, correct_answer 
                    FROM quiz_tasks 
                    WHERE option = ? AND day = ?
                    ORDER BY task_number
                ''', (variant, variant))
                correct_answers = {row[0]: row[1] for row in cursor.fetchall()}
                cursor.close()
                result_text = []
                for task_number, user_answer in user_answers:
                    if task_number < 10:
                        spaces = "   "
                    else:
                        spaces = "  "
                    correct_answer = correct_answers.get(task_number, "")
                    is_correct = str(user_answer).lower() == str(correct_answer).lower()
                    if is_correct:
                        line = f"#️⃣ {task_number:02d}{spaces}✅"
                    else:
                        line = f"#️⃣ {task_number:02d}{spaces}❌ (Ответ: {correct_answer})"
                    result_text.append(line)
                full_text = "\n".join(result_text) if result_text else "Нет ответов."
                caption = (
                        f"⭐️ Первичных баллы: {primary_score}/12 ⭐️\n"
                        f"⭐️ Вторичные баллы: {secondary_score} ⭐️\n"
                        + full_text
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data=f"stats_variant_{variant}"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=caption),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
            else:
                logging.error(f"Попытка не найдена: user_id={user_id}, variant={variant}, attempt_id={attempt_id}")
                bot.edit_message_text(
                    "❌ Данные попытки не найдены.",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=stats_attempts_screen(user_id, variant)
                )

        elif data.startswith("stats-attempts-page-"):
            parts = call.data.split("-")
            logging.info(f"Обработка stats-attempts-page-, call.data: {call.data}, parts: {parts}")
            if len(parts) != 5:  # Ожидаем ["stats", "attempts", "page", variant, page]
                logging.error(f"Некорректный формат callback_data для stats-attempts-page-: {call.data}")
                text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=stats_screen(user_id, page=1)
                )
                return
            _, _, _, variant, page = parts
            variant = int(variant)
            page = int(page)
            text = f"📊 Статистика для Варианта {variant}\n\nВыберите попытку для просмотра:"
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=stats_attempts_screen(user_id, variant, page=page)
            )
    except AttributeError as e:
        logging.error(f"Ошибка в callback: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")
# ================== Quiz ==================
def save_user_data(user_id):
    """Сохраняет состояние user_data в базу данных."""
    try:
        cursor = quiz_conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_data_temp (user_id, data)
            VALUES (?, ?)
        ''', (user_id, json.dumps(user_data.get(user_id, {}))))
        quiz_conn.commit()
        logging.info(f"Состояние user_data для пользователя {user_id} сохранено в базе данных")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении user_data для пользователя {user_id}: {e}")
    finally:
        cursor.close()

def load_user_data():
    """Загружает состояние user_data из базы данных при запуске."""
    global user_data
    try:
        cursor = quiz_conn.cursor()
        cursor.execute('SELECT user_id, data FROM user_data_temp')
        rows = cursor.fetchall()
        for user_id, data in rows:
            user_data[user_id] = json.loads(data)
        logging.info("Состояние user_data загружено из базы данных")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при загрузке user_data: {e}")
    finally:
        cursor.close()

def process_quiz_answer(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id

    if user_id not in user_data or "quiz_id" not in user_data[user_id]:
        logging.error(f"Пользователь {user_id} не найден в user_data или отсутствует quiz_id")
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption="❌ Ошибка! Начните Quize заново."),
            chat_id=chat_id,
            message_id=user_data[user_id]["message_id"] if user_id in user_data else message.message_id,
            reply_markup=quiz_screen()
        )
        bot.delete_message(chat_id, message.message_id)
        return

    # Проверяем наличие attempt_id
    if "attempt_id" not in user_data[user_id]:
        logging.warning(f"attempt_id отсутствует для пользователя {user_id}, генерируем новый")
        user_data[user_id]["attempt_id"] = str(int(time.time()))

    quiz_id = user_data[user_id]["quiz_id"]
    task_number = user_data[user_id]["task_number"]
    day = user_data[user_id]["day"]
    current_option = user_data[user_id]["current_option"]
    attempt_id = user_data[user_id]["attempt_id"]
    message_id = user_data[user_id]["message_id"]
    user_answer = message.text.strip().replace(",", ".").lower()

    # Получаем правильный ответ
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT correct_answer FROM quiz_tasks WHERE id = ?', (quiz_id,))
    correct_answer_row = cursor.fetchone()
    correct_answer = correct_answer_row[0].strip().replace(",", ".").lower() if correct_answer_row else ""
    cursor.close()

    is_correct = user_answer == correct_answer
    user_data[user_id]["results"].append((is_correct, correct_answer))
    if is_correct:
        user_data[user_id]["correct"] += 1

    # Сохраняем ответ пользователя
    cursor = quiz_conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_quiz_progress (user_id, attempt_id, option, task_number, user_answer)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, attempt_id, current_option, task_number, user_answer))
    quiz_conn.commit()
    cursor.close()

    # Переходим к следующей задаче
    user_data[user_id]["task_number"] += 1
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT id, image_url FROM quiz_tasks WHERE option = ? AND day = ? AND task_number = ?',
                   (current_option, day, user_data[user_id]["task_number"]))
    next_task = cursor.fetchone()
    cursor.close()

    if next_task:
        quiz_id, image_url = next_task
        user_data[user_id]["quiz_id"] = quiz_id
        text = f"В-{day}, №{user_data[user_id]['task_number']:02d}\nВведите ответ:"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Начать с начала", callback_data=f"reset_quiz_{day}"))
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_back_call"))
        bot.edit_message_media(
            media=types.InputMediaPhoto(image_url, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        # Сохраняем текущий прогресс
        cursor = quiz_conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, current_option, day, user_data[user_id]["task_number"], attempt_id,
              user_data[user_id]["correct"], user_data[user_id]["secondary_score"], 0, datetime.now().isoformat(),
              message.from_user.username or message.from_user.first_name or "Unknown"))
        quiz_conn.commit()
        cursor.close()
        bot.register_next_step_handler_by_chat_id(chat_id, process_quiz_answer)
    else:
        # Завершаем викторину
        cursor = quiz_conn.cursor()
        cursor.execute('''
            UPDATE user_quiz_state 
            SET completed = 1, primary_score = ?, secondary_score = ?, timestamp = ?
            WHERE user_id = ? AND attempt_id = ? AND option = ?
        ''', (user_data[user_id]["correct"], get_secondary_score(user_data[user_id]["correct"]), datetime.now().isoformat(),
              user_id, attempt_id, current_option))
        quiz_conn.commit()
        cursor.close()
        show_quiz_result(chat_id, user_id, day, message_id)

    bot.delete_message(chat_id, message.message_id)
    save_user_data(user_id)  # Сохраняем состояние после каждого ответа
# Показ результата
def show_quiz_result(chat_id, user_id, day, message_id):
    if user_id not in user_data or "results" not in user_data[user_id]:
        logging.error(f"Данные пользователя {user_id} не найдены в user_data")
        bot.edit_message_text(
            "❌ Ошибка! Данные викторины отсутствуют.",
            chat_id=chat_id,
            message_id=message_id
        )
        return

    correct = user_data[user_id]["correct"]
    results = user_data[user_id]["results"]

    # Первичные баллы — это количество правильных ответов
    primary_score = correct

    # Вторичные баллы — функция от первичных баллов
    secondary_score = get_secondary_score(primary_score)

    # Формируем список всех задач (правильных и неправильных)
    result_text = []
    for i, (is_correct, correct_answer) in enumerate(results, 1):
        if i < 10:
            spaces = "   "  # Три пробела для 1–9
        else:
            spaces = "  "  # Два пробела для 10–12
        if is_correct:
            line = f"#️⃣ {i:02d}{spaces}✅"
        else:
            line = f"#️⃣ {i:02d}{spaces}❌"
        result_text.append(line)

    # Полный текст сообщения с баллами и списком ответов
    full_text = "\n".join(result_text)

    # Формируем итоговое сообщение
    caption = (
        f"⭐️ Первичных баллы: {primary_score}/12 ⭐️\n"
        f"⭐️ Вторичные баллы: {secondary_score} ⭐️\n"
        + full_text
    )

    # Логируем содержимое caption для отладки
    logging.info(f"Сформированное сообщение: {caption}")
    logging.info(f"Длина текста: {len(caption)} символов")

    # Проверяем длину текста и обрезаем, если превышает 1024 символа
    if len(caption) > 1024:
        header_length = len(
            f"⭐️ Первичных баллы: {primary_score}/12 ⭐️\n"
            f"⭐️ Вторичные баллы: {secondary_score} ⭐️\n"
        )
        max_result_length = 1024 - header_length - len("\n...") - 1

        truncated_result_text = []
        current_length = 0
        for line in result_text:
            new_length = current_length + len(line) + 1
            if new_length <= max_result_length:
                truncated_result_text.append(line)
                current_length = new_length
            else:
                break

        truncated_full_text = "\n".join(truncated_result_text) + "\n..."
        caption = (
            f"⭐️ Первичных баллы: {primary_score}/12 ⭐️\n"
            f"⭐️ Вторичные баллы: {secondary_score} ⭐️\n"
            + truncated_full_text
        )

    bot.edit_message_media(
        media=types.InputMediaPhoto(photo, caption=caption),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_call")
        )
    )

    # Логируем удаление user_data
    logging.info(f"Удаление user_data для пользователя {user_id} после завершения викторины")
    del user_data[user_id]  # Очищаем данные пользователя

# ================== Обработчик текстовых запросов ==================
@bot.message_handler(func=lambda message: str(message.from_user.id) in user_task_data)
def handle_task_answer(message):
    user_id = str(message.from_user.id)
    task_data = user_task_data.get(user_id)
    if not task_data:
        logging.error(f"Нет данных задачи для user_id={user_id}")
        bot.send_message(user_id, "Ошибка: задача не найдена. Попробуйте выбрать задачу заново.")
        return

    logging.info(f"Обработка ответа для user_id={user_id}: {message.text}, task_data={task_data}")
    user_answer = message.text.strip().replace(',', '.').replace(' ', '').lower()
    
    # Извлекаем информацию о задаче для быстрого доступа
    challenge_num = task_data["challenge_num"]
    cat_code = task_data["cat_code"]
    task_idx = task_data["task_idx"]
    
    # ДИАГНОСТИКА: выводим ID пользователя и детали задачи
    logging.info(f"🔍 ДИАГНОСТИКА ЗАДАНИЯ: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}, текст ответа='{user_answer}'")
    # Критическая проверка статуса задачи перед обработкой
    try:
        import sqlite3
        status_conn = sqlite3.connect('task_progress.db')
        status_cursor = status_conn.cursor()
        status_cursor.execute("""
            SELECT status, type FROM task_progress 
            WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?
        """, (user_id, challenge_num, cat_code, task_idx))
        status_results = status_cursor.fetchall()
        status_conn.close()
        if status_results:
            logging.info(f"🔍 ДИАГНОСТИКА: Текущие статусы задания: {status_results}")
        else:
            logging.info(f"🔍 ДИАГНОСТИКА: Задание ранее не решалось")
    except Exception as status_e:
        logging.error(f"❌ ОШИБКА при проверке статуса задания: {status_e}")

    # Удаление сообщения пользователя
    try:
        bot.delete_message(user_id, message.message_id)
    except Exception as e:
        logging.error(f"Ошибка удаления сообщения: {e}")

    # Проверяем, это задание из избранного или обычное
    from_favorites = task_data.get("from_favorites", False)
    
    total_tasks = len(challenge[task_data["challenge_num"]][task_data["cat_code"]]["tasks"])
    correct_answer = task_data["correct_answer"].strip().replace(',', '.').replace(' ', '').lower()
    category_name = challenge[task_data["challenge_num"]][task_data["cat_code"]]['name']
    
    # Формируем базовый текст в зависимости от типа задания
    if from_favorites:
        base_text = f"№{task_data['challenge_num']} Избранное\n{category_name}\n"
    else:
        base_text = (f"Задача {task_data['challenge_num']}\n"
                     f"{category_name} "
                     f"{task_data['task_idx'] + 1}/{total_tasks}\n")

    # Создаем клавиатуру
    markup = types.InlineKeyboardMarkup()
    
    # Для обычных заданий добавляем навигационные кнопки
    if not from_favorites:
        nav_buttons = []
        if task_data["task_idx"] > 0:
            nav_buttons.append(
                types.InlineKeyboardButton("⬅️",
                                          callback_data=f"category_{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx'] - 1}")
            )
        if task_data["task_idx"] < total_tasks - 1:
            nav_buttons.append(
                types.InlineKeyboardButton("➡️",
                                          callback_data=f"category_{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx'] + 1}")
            )
        if nav_buttons:
            markup.row(*nav_buttons)
    # Для избранных заданий добавляем свои кнопки навигации
    else:
        if user_id in user_data and "favorite_tasks" in user_data[user_id]:
            tasks = user_data[user_id]["favorite_tasks"]
            current_index = user_data[user_id].get("current_index", 0)
            total_tasks = len(tasks)
            
            nav_buttons = []
            if current_index == 0:
                # Первая страница: пустая стрелка, счетчик, стрелка вперед
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
            elif current_index == total_tasks - 1:
                # Последняя страница: стрелка назад, счетчик, пустая стрелка
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            else:
                # Промежуточная страница: стрелка назад, счетчик, стрелка вперед
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
            
            markup.row(*nav_buttons)
    
    # Добавляем кнопку подсказки для всех типов заданий
    if "hint" in task_data["task"] and task_data["task"]["hint"]:
        markup.add(
            types.InlineKeyboardButton("💡 Подсказка",
                                       callback_data=f"hint_{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx']}_0")
        )
    
    # Кнопка избранного
    if from_favorites:
        markup.add(types.InlineKeyboardButton("🗑 Удалить из избранного", 
                   callback_data=f"quest_favorite_{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx']}"))
    else:
        is_favorite = task_data.get("is_favorite", False)
        markup.add(types.InlineKeyboardButton(
            "🗑️ Удалить из избранного" if is_favorite else "⭐ Добавить в избранное",
            callback_data=f"{'remove' if is_favorite else 'add'}_favorite_{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx']}"
        ))
    
    # Кнопка "Назад" в зависимости от типа задания
    if from_favorites:
        world_id = user_data[user_id].get("current_world_id", "")
        back_callback = f"quest_favorite_world_{world_id}"
    else:
        back_callback = f"challenge_{task_data['challenge_num']}"
        
    markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=back_callback))

    # Проверяем текущий статус задачи
    current_status = task_data.get("status")
    
    # Проверяем ответ
    is_correct = False
    try:
        user_answer_num = float(user_answer)
        correct_answer_num = float(correct_answer)
        is_correct = abs(user_answer_num - correct_answer_num) < 0.01  # Допуск для чисел
    except ValueError:
        is_correct = user_answer == correct_answer  # Точное совпадение для строк
    
    # ВАЖНО: Добавляем подробное логирование при обработке ответа
    logging.info(f"ОБРАБОТКА ОТВЕТА: user_id={user_id}, задача={challenge_num}_{cat_code}_{task_idx}, введенный ответ={user_answer}, правильный ответ={correct_answer}, результат={is_correct}")
        
    # Проверка на наличие подсказок - важно для правила "верный ответ + подсказка"
    logging.info(f"Проверка подсказок для правила 'верный ответ + подсказка': user_id={user_id}")
    used_hint = False
    task_key = f"{challenge_num}_{cat_code}_{task_idx}"
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Значительно упрощаем и улучшаем логику проверки подсказок
    if user_id in user_data and 'viewed_hints' in user_data[user_id]:
        used_hint = user_data[user_id]['viewed_hints'].get(task_key, False)
        logging.info(f"Использование подсказки для задачи {task_key}: {used_hint} - user_data[{user_id}]['viewed_hints']={user_data[user_id]['viewed_hints']}")
    else:
        logging.info(f"ОТСУТСТВУЮТ ДАННЫЕ О ПОДСКАЗКАХ: user_id={user_id}, задача={task_key}")
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обрабатываем ВСЕ ответы пользователя, даже если задача уже решена
    # Это позволит добавлять задания в ДЗ при повторных неправильных ответах
    if False:  # Намеренно делаем это условие всегда ложным, чтобы всегда обрабатывать ответы
        # Если задача уже решена верно и нет подсказки, игнорируем ответ
        logging.info(f"Задача {task_key} уже решена верно, подсказка не использовалась - игнорируем ответ")
        return
    
    # ДОБАВЛЕНО: Дополнительное логирование для прозрачности работы механизма
    logging.info(f"ВАЖНО: Задача {task_key} будет обработана. current_status={current_status}, used_hint={used_hint}")

    if is_correct:
        if from_favorites:
            new_caption = base_text + f"✅ Верно\n\nПравильный ответ: {correct_answer}"
        else:
            new_caption = base_text + f"✅ Верно\n\nПравильный ответ: {correct_answer}"
        new_status = "correct"
    else:
        if from_favorites:
            new_caption = base_text + f"❌ Неверно\n\nВведите ответ в чат:"
        else:
            new_caption = base_text + "❌ Не верно\nВведите ответ в чат:"
        new_status = "incorrect"

    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обновляем статус в базе, если он изменился ИЛИ ответ неверный
    # Это гарантирует, что неверные ответы ВСЕГДА будут обрабатываться, даже если статус не меняется
    if current_status != new_status or not is_correct:
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Безусловно обрабатываем неверный ответ, даже если статус не изменился")
        try:
            # Используем прямое подключение к базе данных task_progress.db с правильным путем
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            logging.info(f"Подключение к базе данных task_progress.db успешно установлено")
            
            # ИСПРАВЛЕНИЕ: Статус должен сохраняться как correct, если ответ верен,
            # независимо от использования подсказки
            status_text = "correct" if is_correct else "wrong"
            
            # Обновляем основной статус задачи
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, challenge_num, cat_code, task_idx, "main", status_text))
            
            # Получаем информацию о том, использовал ли пользователь подсказку
            # Добавим детальное логирование для отладки механизма использования подсказок
            logging.info(f"Проверка использования подсказки для user_id={user_id}")
            if user_id in user_data:
                logging.info(f"Пользователь найден в user_data")
                if 'viewed_hints' in user_data[user_id]:
                    logging.info(f"Структура viewed_hints найдена: {user_data[user_id]['viewed_hints']}")
                    task_key = f"{challenge_num}_{cat_code}_{task_idx}"
                    logging.info(f"Проверка ключа {task_key} в viewed_hints")
                    used_hint = user_data[user_id]['viewed_hints'].get(task_key, False)
                    logging.info(f"Результат проверки использования подсказки: {used_hint}")
                else:
                    logging.info(f"Структура viewed_hints не найдена")
                    used_hint = False
            else:
                logging.info(f"Пользователь не найден в user_data")
                used_hint = False
                
            # Применяем правила для добавления задачи в домашнюю работу:
            # 1. Верный ответ + использование подсказки -> Добавить в ДЗ
            # 2. Неверный ответ + использование подсказки -> Добавить в ДЗ
            # 3. Неверный ответ + без подсказки -> Добавить в ДЗ
            # 4. Верный ответ + без подсказки -> НЕ добавлять в ДЗ
            
            logging.info(f"*** ИДЁТ ПРОВЕРКА ПРАВИЛ ДОБАВЛЕНИЯ В РИТУАЛ ПОВТОРЕНИЯ ***")
            logging.info(f"Задача: {challenge_num}_{cat_code}_{task_idx}, ответ правильный: {is_correct}, использована подсказка: {used_hint}")
            
            # Более детальное логирование для отладки
            logging.info(f"ОТЛАДКА ПОДСКАЗОК: user_id={user_id}, task={challenge_num}_{cat_code}_{task_idx}")
            if user_id in user_data:
                logging.info(f"ОТЛАДКА VIEWED_HINTS: структура user_data для {user_id} существует")
                if 'viewed_hints' in user_data[user_id]:
                    all_hints = user_data[user_id]['viewed_hints']
                    logging.info(f"ОТЛАДКА VIEWED_HINTS: все подсказки пользователя: {all_hints}")
                else:
                    logging.info(f"ОТЛАДКА VIEWED_HINTS: структура viewed_hints отсутствует для {user_id}")
            else:
                logging.info(f"ОТЛАДКА VIEWED_HINTS: пользователь {user_id} не найден в user_data")
            
            # Решаем добавлять ли в ДЗ строго по правилам:
            # 1. Верный ответ + использование подсказки -> Добавить в ДЗ
            # 2. Неверный ответ + использование подсказки -> Добавить в ДЗ
            # 3. Неверный ответ + без подсказки -> Добавить в ДЗ
            # 4. Верный ответ + без подсказки -> НЕ добавлять в ДЗ
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем ТОЛЬКО функцию auto_add_to_homework, которая
            # правильно обрабатывает правила и не забывает случай с неверным ответом без подсказки
            try:
                # Импортируем функцию для автоматического добавления в домашнюю работу
                from fix_ritual_homework import auto_add_to_homework
                
                # СУПЕР-ВАЖНАЯ ПРОВЕРКА: убедимся, что данные о подсказках в порядке
                # Если пользователь использовал подсказку, выводим дополнительные диагностические сообщения
                if used_hint:
                    logging.info(f"🔔 ПОЛЬЗОВАТЕЛЬ ИСПОЛЬЗОВАЛ ПОДСКАЗКУ и ответил {'верно' if is_correct else 'неверно'}")
                    logging.info(f"🔔 Обязательно должно быть выполнено правило: is_correct and used_hint = {is_correct and used_hint}")
                    # Если пользователь ответил верно и использовал подсказку - особенно важный случай!
                    if is_correct and used_hint:
                        logging.info(f"‼️ ОСОБЫЙ СЛУЧАЙ: верный ответ + использование подсказки - ДОЛЖНО БЫТЬ ДОБАВЛЕНО В ДЗ!")
                
                # Вызываем функцию и получаем результат: она СРАЗУ добавляет задание в ДЗ!
                was_added = auto_add_to_homework(
                    user_id=user_id,
                    world_id=challenge_num,
                    cat_code=cat_code,
                    task_idx=task_idx,
                    is_correct=is_correct,
                    used_hint=used_hint
                )
                
                # Дополнительная проверка "по горячим следам" для критического случая
                if is_correct and used_hint and not was_added:
                    logging.error(f"❓❓❓ КРИТИЧЕСКАЯ ОШИБКА: Задание с верным ответом и подсказкой НЕ добавлено в ДЗ!")
                    # Пробуем исправить это прямым добавлением в БД
                    try:
                        fix_conn = sqlite3.connect('task_progress.db')
                        fix_cursor = fix_conn.cursor()
                        fix_cursor.execute("""
                            INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (user_id, challenge_num, cat_code, task_idx, "homework", "wrong"))
                        fix_conn.commit()
                        fix_conn.close()
                        logging.info(f"✅ ИСПРАВЛЕНИЕ: Принудительное добавление задания {challenge_num}_{cat_code}_{task_idx} в ДЗ")
                        was_added = True
                    except Exception as fix_e:
                        logging.error(f"❌ ОШИБКА при принудительном добавлении в ДЗ: {fix_e}")
                
                # Логируем результат для отладки
                logging.info(f"✅✅✅ auto_add_to_homework результат: {'Добавлено в ДЗ' if was_added else 'НЕ добавлено в ДЗ'}")
                
                # Устанавливаем add_to_homework на основе результата
                add_to_homework = was_added
                
                # Проверяем, действительно ли задание добавилось
                if was_added:
                    try:
                        check_conn = sqlite3.connect('task_progress.db')
                        check_cursor = check_conn.cursor()
                        check_cursor.execute("""
                            SELECT * FROM task_progress 
                            WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
                        """, (user_id, challenge_num, cat_code, task_idx))
                        hw_record = check_cursor.fetchone()
                        check_conn.close()
                        
                        if hw_record:
                            logging.info(f"✅ ПОДТВЕРЖДЕНИЕ: Задание {challenge_num}_{cat_code}_{task_idx} успешно добавлено в ДЗ: {hw_record}")
                        else:
                            logging.error(f"⚠️ ОШИБКА ПРОВЕРКИ: Задание не найдено в 'homework' после добавления")
                    except Exception as check_e:
                        logging.error(f"⚠️ ОШИБКА ПРОВЕРКИ: Не удалось проверить добавление: {check_e}")
                
            except Exception as e:
                # В случае ошибки используем прямое добавление в БД
                logging.error(f"❌ Ошибка при вызове auto_add_to_homework: {e}")
                
                # Для неверных ответов гарантированно добавляем в ДЗ
                if not is_correct:
                    add_to_homework = True
                    logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Неверный ответ - безусловно добавляем в домашнее задание")
                    
                    # Добавляем задание в домашнюю работу напрямую
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (user_id, challenge_num, cat_code, task_idx, "homework", "wrong"))
                        
                        # Сразу делаем коммит, чтобы гарантировать сохранение
                        conn.commit()
                        
                        # Верификация
                        cursor.execute("SELECT * FROM task_progress WHERE user_id=? AND challenge_num=? AND cat_code=? AND task_idx=? AND type='homework'",
                                     (user_id, challenge_num, cat_code, task_idx))
                        verification = cursor.fetchone()
                        logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ПРЯМОЕ ДОБАВЛЕНИЕ В HOMEWORK: {verification}")
                    except Exception as e:
                        logging.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при прямом добавлении в ДЗ: {e}")
                elif used_hint:
                    add_to_homework = True
                    logging.info(f"⚠️ Верный ответ с подсказкой - добавляем в домашнее задание")
                    
                    # Добавляем задание в домашнюю работу напрямую
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (user_id, challenge_num, cat_code, task_idx, "homework", "wrong"))
                        conn.commit()
                    except Exception as e:
                        logging.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при добавлении верного ответа с подсказкой в ДЗ: {e}")
            
            # ВАЖНО: Если ответ был верным, не меняем его на неверный независимо от использования подсказки
            # Это исправляет баг, когда верно решенная задача помечалась как неверная после просмотра подсказок
            if is_correct:
                status_text = "correct"
                new_status = "correct"
                # Убедимся, что далее по коду статус не изменится на "wrong"
                logging.info(f"✅ Сохраняем статус 'correct' для верного ответа даже с подсказкой")
            
            logging.info(f"Решение о добавлении в ДЗ: add_to_homework={add_to_homework}")
            logging.info(f"Основания: used_hint={used_hint}, is_correct={is_correct}")
            logging.info(f"ПРОВЕРКА УСЛОВИЙ: 1.Верный+подсказка: {is_correct and used_hint}, 2.Неверный+подсказка: {not is_correct and used_hint}, 3.Неверный+не подсказка: {not is_correct and not used_hint}, 4.Верный+не подсказка: {is_correct and not used_hint}")
            
            if add_to_homework:
                # Отображаем информацию о результате для логирования
                if used_hint and is_correct:
                    reason = "верный ответ + использование подсказки"
                    message_reason = "правильно решили задачу, но использовали подсказку"
                elif used_hint and not is_correct:
                    reason = "неверный ответ + использование подсказки"
                    message_reason = "использовали подсказку, но ответили неверно"
                else:  # not is_correct and not used_hint
                    reason = "неверный ответ без подсказки"
                    message_reason = "ответили неверно"
                
                logging.info(f"✅ Задача добавлена в 'Ритуал повторения' для пользователя {user_id}, причина: {message_reason}")
                
                # Сохраняем состояние user_data для персистентности
                save_user_data(user_id)
            
            # Если задача решена верно, добавляем её в словарь решенных задач в памяти для быстрого доступа
            if is_correct:
                if 'user_solutions' not in user_data.get(user_id, {}):
                    if user_id not in user_data:
                        user_data[user_id] = {}
                    user_data[user_id]['user_solutions'] = {}
                task_key = f"{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx']}"
                user_data[user_id]['user_solutions'][task_key] = "correct"
            
            conn.commit()
            conn.close()
            logging.info(f"Статус обновлён на '{new_status}' (значение: {status_text}) для user_id={user_id}")
        except sqlite3.OperationalError as e:
            # Если таблица не существует, инициализируем её
            if "no such table" in str(e):
                init_task_progress_db()
                conn = sqlite3.connect('task_progress.db')
                cursor = conn.cursor()
                status_value = 1 if is_correct else 0
                cursor.execute("""
                    INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, task_data["challenge_num"], task_data["cat_code"], task_data["task_idx"], "main", status_value))
                conn.commit()
                conn.close()
                logging.info(f"Таблица task_progress инициализирована и статус обновлён на '{new_status}' (значение: {status_value}) для user_id={user_id}")
            else:
                logging.error(f"Ошибка при обновлении статуса задачи: {e}")

        try:
            # Эта логика теперь полностью содержится в блоке обработки viewed_hints выше,
            # поэтому здесь нет необходимости дублировать код - теперь используется единый механизм
            # добавления задач в домашнюю работу для всех случаев
            bot.edit_message_media(
                media=types.InputMediaPhoto(task_data["task"]["photo"], caption=new_caption),
                chat_id=user_id,
                message_id=task_data["message_id"],
                reply_markup=markup
            )
            task_data["current_caption"] = new_caption
            task_data["status"] = new_status
            user_task_data[user_id] = task_data
            
            # Сохраняем состояние экрана и текущую задачу для корректной навигации
            if user_id not in user_data:
                user_data[user_id] = {}
                
            user_data[user_id]['current_screen'] = 'quest_task'
            user_data[user_id]['current_task'] = {
                "challenge_num": task_data["challenge_num"],
                "cat_code": task_data["cat_code"],
                "task_idx": task_data["task_idx"],
                "screen": "quest_task"
            }
            logging.info(f"Сохранен контекст current_screen='quest_task' и текущая задача для user_id={user_id} после обработки ответа")
            
            logging.info(f"Сообщение успешно обновлено после ответа пользователя {user_id}")
        except Exception as e:
            logging.error(f"Ошибка обновления сообщения: {e}")
            bot.send_message(user_id, "Ошибка при обработке ответа. Попробуйте снова.")

@bot.message_handler(func=lambda message: str(message.from_user.id) in user_data and "quiz_id" in user_data[str(message.from_user.id)])
def handle_quiz_text(message):
    user_id = str(message.from_user.id)
    process_quiz_answer(message)  # Используем существующую функцию из вашего кода

# Обработчик ответов на задания из избранного
def handle_favorite_answer(message):
    """Обработчик ответов на задания из избранного"""
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    text = message.text.strip()
    
    # Логируем полученный ответ
    logging.info(f"Получен ответ на задание из избранного от пользователя {user_id}: '{text}'")
    logging.info(f"🔍 ДИАГНОСТИКА ИЗБРАННОГО: Обработка ответа пользователя {user_id}, текст='{text}'")
    
    # Проверяем, что у пользователя отображается задание из избранного
    if user_id not in user_data or "current_task" not in user_data[user_id]:
        bot.send_message(chat_id, "Ошибка: не найдено активное задание. Пожалуйста, перейдите в раздел избранного.")
        return
    
    # Получаем информацию о текущем задании
    current_task = user_data[user_id]["current_task"]
    challenge_num = current_task.get("challenge_num")
    cat_code = current_task.get("cat_code")
    task_idx = current_task.get("task_idx")
    message_id = current_task.get("message_id")
    
    if not challenge_num or not cat_code or task_idx is None or not message_id:
        bot.send_message(chat_id, "Ошибка: неполная информация о задании.")
        return
        
    # Получаем задачу из challenge
    world_challenges = challenge.get(str(challenge_num), {})
    if not world_challenges:
        bot.send_message(chat_id, "Ошибка: мир не найден.")
        return
        
    category = world_challenges.get(cat_code)
    if not category or 'tasks' not in category:
        bot.send_message(chat_id, "Ошибка: категория не найдена.")
        return
        
    # Находим задание
    if task_idx < 0 or task_idx >= len(category['tasks']):
        bot.send_message(chat_id, "Ошибка: задание не найдено.")
        return
        
    task = category['tasks'][task_idx]
    
    # Удаляем сообщение пользователя
    try:
        bot.delete_message(chat_id, message.message_id)
        logging.info(f"Сообщение {message.message_id} от пользователя {user_id} удалено")
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение {message.message_id} от пользователя {user_id}: {e}")
    
    # Проверяем ответ пользователя
    user_answer = text.strip().replace(',', '.').replace(' ', '').lower()
    correct_answer = str(task.get("answer", "")).strip().replace(',', '.').replace(' ', '').lower()
    
    # Проверяем точное совпадение
    is_correct = user_answer == correct_answer
    
    # Проверка с числами (если строгое сравнение не сработало)
    if not is_correct:
        try:
            user_answer_num = float(user_answer)
            correct_answer_num = float(correct_answer)
            is_correct = abs(user_answer_num - correct_answer_num) < 0.01  # Допуск для чисел
        except ValueError:
            # Если не удалось преобразовать в число, оставляем результат сравнения строк
            pass
    
    # Обновляем статус в базе данных
    new_status = "correct" if is_correct else "incorrect"
    status_value = 1 if is_correct else 0  # 1 - верно, 0 - неверно
    status_text = "correct" if is_correct else "wrong"
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Логирование неверного ответа  
    if not is_correct:
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ (favorites): Неверный ответ от пользователя {user_id} на задачу {challenge_num}_{cat_code}_{task_idx}")
        
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        # Обновляем статус задачи в основной таблице
        cursor.execute("""
            INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, str(challenge_num), cat_code, task_idx, "main", status_text))
        
        # Получаем информацию о том, использовал ли пользователь подсказку
        logging.info(f"Проверка использования подсказки для задачи из избранного, user_id={user_id}")
        used_hint = False
        task_key = f"{challenge_num}_{cat_code}_{task_idx}"
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Улучшаем логику проверки подсказок
        if user_id in user_data and 'viewed_hints' in user_data[user_id]:
            used_hint = user_data[user_id]['viewed_hints'].get(task_key, False)
            logging.info(f"Результат проверки использования подсказки: {used_hint} - user_data[{user_id}]['viewed_hints']={user_data[user_id]['viewed_hints']}")
        
        # ДОБАВЛЕНО: Дополнительное логирование для прозрачности работы механизма
        logging.info(f"ВАЖНО: Обрабатываем избранное задание {task_key}. used_hint={used_hint}, is_correct={is_correct}")
        
        # Применяем правила для добавления задачи в домашнюю работу:
        # 1. Верный ответ + использование подсказки -> Добавить в ДЗ
        # 2. Неверный ответ + использование подсказки -> Добавить в ДЗ 
        # 3. Неверный ответ + без подсказки -> Добавить в ДЗ
        # 4. Верный ответ + без подсказки -> НЕ добавлять в ДЗ
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем модуль fix_ritual_homework
        try:
            # Импортируем функцию для автоматического добавления в домашнюю работу
            from fix_ritual_homework import auto_add_to_homework
            
            # Вызываем функцию и получаем результат
            was_added = auto_add_to_homework(
                user_id=user_id,
                world_id=str(challenge_num),
                cat_code=cat_code,
                task_idx=task_idx,
                is_correct=is_correct,
                used_hint=used_hint
            )
            
            # Логируем результат для отладки
            logging.info(f"auto_add_to_homework результат для избранного: {'Добавлено в ДЗ' if was_added else 'НЕ добавлено в ДЗ'}")
            
            # Устанавливаем add_to_homework на основе результата
            add_to_homework = was_added
        except Exception as e:
            # В случае ошибки используем старую логику
            logging.error(f"Ошибка при вызове auto_add_to_homework: {e}")
            
            # ВАЖНО: Неверный ответ без подсказки должен всегда добавляться в домашнее задание
            # Поэтому явно устанавливаем это условие
            add_to_homework = used_hint or not is_correct
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Гарантируем добавление неверных ответов в ДЗ
            if not is_correct:
                add_to_homework = True  # Явно устанавливаем в True для неверного ответа
                logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ (избранное): Неверный ответ - безусловно добавляем в домашнее задание")
            elif used_hint:
                logging.info(f"⚠️ Верный ответ с подсказкой в избранном - добавляем в домашнее задание")
        
        # ВАЖНО: Если ответ был верным, не меняем его на неверный независимо от использования подсказки
        # Это исправляет баг, когда верно решенная задача помечалась как неверная после просмотра подсказок
        if is_correct:
            status_text = "correct"
            new_status = "correct"
            # Убедимся, что далее по коду статус не изменится на "wrong"
            logging.info(f"✅ Сохраняем статус 'correct' для верного ответа из избранного даже с подсказкой")
        
        logging.info(f"Решение о добавлении задания из избранного в ДЗ: add_to_homework={add_to_homework}")
        logging.info(f"Основания: used_hint={used_hint}, is_correct={is_correct}")
        logging.info(f"ПРОВЕРКА УСЛОВИЙ: 1.Верный+подсказка: {is_correct and used_hint}, 2.Неверный+подсказка: {not is_correct and used_hint}, 3.Неверный+не подсказка: {not is_correct and not used_hint}, 4.Верный+не подсказка: {is_correct and not used_hint}")
        
        if add_to_homework:
            # Отображаем информацию о результате для логирования
            if used_hint and is_correct:
                reason = "верный ответ + использование подсказки"
                message_reason = "правильно решили задачу, но использовали подсказку"
            elif used_hint and not is_correct:
                reason = "неверный ответ + использование подсказки"
                message_reason = "использовали подсказку, но ответили неверно"
            else:  # not is_correct and not used_hint
                reason = "неверный ответ без подсказки"
                message_reason = "ответили неверно"
            
            # Проверяем, действительно ли задание было добавлено в ДЗ
            try:
                check_conn = sqlite3.connect('task_progress.db')
                check_cursor = check_conn.cursor()
                check_cursor.execute("""
                    SELECT * FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
                """, (user_id, str(challenge_num), cat_code, task_idx))
                hw_record = check_cursor.fetchone()
                check_conn.close()
                
                if hw_record:
                    logging.info(f"✅ ПОДТВЕРЖДЕНИЕ (избранное): Задание {challenge_num}_{cat_code}_{task_idx} успешно добавлено в ДЗ: {hw_record}")
                else:
                    logging.error(f"⚠️ ОШИБКА ПРОВЕРКИ (избранное): Задание не найдено в 'homework' после добавления")
            except Exception as check_e:
                logging.error(f"⚠️ ОШИБКА ПРОВЕРКИ (избранное): Не удалось проверить добавление: {check_e}")
            
            # Для отладки
            print(f"ДОБАВЛЕНО В ДОМАШНЮЮ РАБОТУ ИЗ ИЗБРАННОГО: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}, причина: {reason}")
            
            # Логируем результат
            logging.info(f"✅ Задача из избранного добавлена в 'Ритуал повторения' для пользователя {user_id}, причина: {message_reason}")
        
        # Если задача решена верно, добавляем её в словарь решенных задач в памяти для быстрого доступа
        if is_correct:
            if 'user_solutions' not in user_data.get(user_id, {}):
                if user_id not in user_data:
                    user_data[user_id] = {}
                user_data[user_id]['user_solutions'] = {}
            task_key = f"{challenge_num}_{cat_code}_{task_idx}"
            user_data[user_id]['user_solutions'][task_key] = "correct"
        
        conn.commit()
        conn.close()
        logging.info(f"Статус задачи из избранного обновлён на '{new_status}' для user_id={user_id}")
    except sqlite3.OperationalError as e:
        # Если таблица не существует, инициализируем её
        if "no such table" in str(e):
            init_task_progress_db()
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, str(challenge_num), cat_code, task_idx, "main", status_text))
            
            # Добавляем в домашнюю работу если нужно
            if not is_correct:
                cursor.execute("""
                    INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, str(challenge_num), cat_code, task_idx, "homework", "wrong"))
                
                # Убрано оповещение пользователя о добавлении в "Ритуал повторения"
                # Только логируем операцию
                logging.info(f"✅ Задача добавлена в 'Ритуал повторения' для пользователя {user_id} из-за неверного ответа")
            
            conn.commit()
            conn.close()
            logging.info(f"Таблица task_progress инициализирована и статус обновлён на '{new_status}' для user_id={user_id}")
        else:
            logging.error(f"Ошибка при обновлении статуса задачи из избранного: {e}")
    
    # Получаем название категории
    category_name = category.get("name", "Неизвестная категория")
    
    # Получаем информацию о текущем индексе и общем количестве задач
    current_index = user_data[user_id].get("current_index", 0)
    total_tasks = len(user_data[user_id].get("favorite_tasks", []))
    
    # Формируем и обновляем сообщение с результатом
    if is_correct:
        status_text = "✅ Верно"
        answer_text = f"\n\nПравильный ответ: {task['answer']}"
    else:
        status_text = "❌ Неверно"
        answer_text = "\n\nВведите ответ в чат:"
    
    caption = f"Задача {challenge_num}\n{category_name}\n{status_text}{answer_text}"
    
    # Обновляем интерфейс
    # Создаем клавиатуру с кнопками навигации
    markup = InlineKeyboardMarkup(row_width=3)
    
    # Формируем навигационные кнопки: всегда 3 кнопки с разными обработчиками в зависимости от страницы
    nav_buttons = []
    
    if current_index == 0:
        # Первая страница: пустая стрелка, счетчик, стрелка вперед
        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
        nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
    elif current_index == total_tasks - 1:
        # Последняя страница: стрелка назад, счетчик, пустая стрелка
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
        nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
    else:
        # Промежуточная страница: стрелка назад, счетчик, стрелка вперед
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
        nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
    
    # Добавляем все кнопки в одном ряду
    markup.row(*nav_buttons)
    
    # Получаем количество подсказок для задания
    hint_count = len(task.get("hint", []))
    if hint_count > 0:
        # Добавляем кнопку подсказки без указания количества шагов
        markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0"))
    
    # Добавляем кнопку удаления из избранного
    markup.add(InlineKeyboardButton("🗑 Удалить из избранного", callback_data=f"quest_favorite_{challenge_num}_{cat_code}_{task_idx}"))
    
    # Кнопка возврата - используем callback в зависимости от текущего режима
    back_callback = f"quest_favorite_world_{challenge_num}"
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data=back_callback))
    
    bot.edit_message_media(
        media=InputMediaPhoto(task["photo"], caption=caption),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )
    
    logging.info(f"Обработан ответ на задачу из избранного: world={challenge_num}, cat={cat_code}, task={task_idx}, правильно: {is_correct}")

# Обработчик для репетитора
@bot.message_handler(func=lambda message: str(message.from_user.id) in user_data and "tutor_step" in user_data[str(message.from_user.id)])
def handle_tutor_text(message):
    user_id = str(message.from_user.id)
    if "tutor_step" not in user_data.get(user_id, {}) or "message_id" not in user_data.get(user_id, {}):
        bot.send_message(message.chat.id, "Процесс прерван. Начните заново.")
        if user_id in user_data:
            del user_data[user_id]
        return

    register_user(user_id, message.from_user.username)
    chat_id = message.chat.id
    step = user_data[user_id]["tutor_step"]
    message_id = user_data[user_id]["message_id"]

    questions = [
        "Ваше имя?",
        "Класс в школе?",
        "Писали пробники? Если да, то какой балл в среднем?",
        "Занятия по какой цене за час (60 минут) ожидаете?"
    ]

    if step >= len(questions):
        finish_tutor_questions(chat_id, user_id, message_id)
        return

    # Сохраняем ответы в зависимости от шага
    if step == 0:
        user_data[user_id]["tutor_answers"] = {"name": message.text}
    elif step == 1:
        user_data[user_id]["tutor_answers"]["school_class"] = message.text
    elif step == 2:
        user_data[user_id]["tutor_answers"]["test_score"] = message.text
    elif step == 3:
        user_data[user_id]["tutor_answers"]["expected_price"] = message.text

    user_data[user_id]["tutor_step"] += 1

    if user_data[user_id]["tutor_step"] < len(questions):
        text = questions[user_data[user_id]["tutor_step"]]
        markup = InlineKeyboardMarkup()
# Обработчик для текстовых сообщений (ответы на задачи)
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    import logging
    import sqlite3
    from datetime import datetime
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
    
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    text = message.text.strip()
    
    # Логируем полученное сообщение
    logging.info(f"Получено сообщение от пользователя {user_id}: '{text}'")
    
    # Используем встроенный обработчик ответов из избранного
    
    # Получаем текущий экран пользователя
    current_screen = user_data.get(user_id, {}).get("current_screen", "")
    
    # Обработка ответов на задания в математическом квесте
    if current_screen == "quest_task":
        handle_task_answer(message)
        return
    
    # Обработка ответов на задания в избранном
    elif current_screen == "favorite_view":
        handle_favorite_answer(message)
        return
    
    # Обработка ответов на задания из вариантов
    elif current_screen == "quiz":
        handle_quiz_text(message)
        return
        
    # Обработка ответов на домашние задания
    elif "current_homework" in user_data.get(user_id, {}) and user_data.get(user_id, {}).get("current_screen") == "homework":
        # Извлекаем данные о текущем домашнем задании
        homework_data = user_data[user_id]["current_homework"]
        user_answer = text.strip().replace(',', '.').replace(' ', '').lower()
        correct_answer = str(homework_data.get("answer", "")).strip().replace(',', '.').replace(' ', '').lower()
        
        # ДОБАВЛЕНО: Расширенное логирование начала обработки ответа на домашнее задание
        logging.info(f"🔍 ДИАГНОСТИКА ДОМАШНЕЙ РАБОТЫ: Получен ответ от user_id={user_id}, текст='{text}'")
        
        # Проверяем правильность ответа
        is_correct = False
        try:
            # Пробуем сравнить как числа
            user_answer_num = float(user_answer)
            correct_answer_num = float(correct_answer)
            is_correct = abs(user_answer_num - correct_answer_num) < 0.01  # Допуск для чисел
        except ValueError:
            # Если не числа, сравниваем как строки
            is_correct = user_answer == correct_answer
            
        # Добавляем дополнительную проверку, если числа не совпали
        if not is_correct and '/' in user_answer and '/' in correct_answer:
            # Пробуем преобразовать дроби и сравнить как десятичные
            try:
                user_num, user_denom = user_answer.split('/')
                correct_num, correct_denom = correct_answer.split('/')
                
                user_float = float(user_num) / float(user_denom)
                correct_float = float(correct_num) / float(correct_denom)
                
                is_correct = abs(user_float - correct_float) < 0.01
                logging.info(f"Дробное сравнение: {user_float} vs {correct_float} = {is_correct}")
            except (ValueError, ZeroDivisionError) as e:
                logging.info(f"Ошибка при сравнении дробей: {e}")
                
        status = "correct" if is_correct else "wrong"
        logging.info(f"Результат проверки ответа на домашнее задание: is_correct={is_correct}, status={status}")

        # Получаем параметры задачи
        world_id = homework_data["world_id"]
        cat_code = homework_data["cat_code"]
        task_idx = homework_data["task_idx"]

        # Добавляем подробное логирование текущего задания
        logging.info(f"ОТЛАДКА ДОМАШНЕЙ РАБОТЫ: user_id={user_id}, текущее задание={world_id}_{cat_code}_{task_idx}")
        logging.info(f"ОТЛАДКА ДОМАШНЕЙ РАБОТЫ: пользовательский ответ='{user_answer}', правильный ответ='{correct_answer}', is_correct={is_correct}")

        # Проверяем, использовал ли пользователь подсказку
        task_key = f"{world_id}_{cat_code}_{task_idx}"
        used_hint = False
        if 'viewed_hints' in user_data.get(user_id, {}):
            used_hint = user_data[user_id]['viewed_hints'].get(task_key, False)
            logging.info(f"Проверка использования подсказки для домашнего задания: task_key={task_key}, used_hint={used_hint}")
        
        # Удаляем сообщение пользователя с ответом
        try:
            bot.delete_message(chat_id, message.message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
        
        # Обновляем статус задания в базе данных
        try:
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            
            # Проверим, существует ли такая запись в домашней работе
            cursor.execute("""
                SELECT status FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
            """, (user_id, world_id, cat_code, task_idx))
            record_exists = cursor.fetchone()
            
            # Выводим информацию о наличии задания
            logging.info(f"Проверка существования задания {task_key} в домашних: {'Существует' if record_exists else 'Не существует'}")
            
            # Обновляем статус задания в домашней работе
            if record_exists:
                cursor.execute("""
                    UPDATE task_progress 
                    SET status = ? 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
                """, (status, user_id, world_id, cat_code, task_idx))
                logging.info(f"Обновлен статус задания {task_key} в домашних: status={status}")
            else:
                # Если задания нет в домашней работе, добавляем его
                cursor.execute("""
                    INSERT INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, world_id, cat_code, task_idx, "homework", status))
                logging.info(f"Создано задание {task_key} в домашних: status={status}")
            
            # Также обновляем статус в основной таблице, чтобы отражать последний ответ
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, world_id, cat_code, task_idx, "main", status))
            logging.info(f"Обновлен основной статус задания {task_key}: status={status}")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем функцию auto_add_to_homework для определения,
            # нужно ли добавлять/оставлять задание в домашней работе
            try:
                # Импортируем модуль fix_ritual_homework
                from fix_ritual_homework import auto_add_to_homework
                
                # Вызываем функцию и получаем результат
                was_added = auto_add_to_homework(
                    user_id=user_id,
                    world_id=world_id,
                    cat_code=cat_code,
                    task_idx=task_idx,
                    is_correct=is_correct,
                    used_hint=used_hint
                )
                
                # Логируем результат для отладки
                logging.info(f"🔍 auto_add_to_homework результат для домашнего задания: {'Добавлено/оставлено в ДЗ' if was_added else 'Удалено из ДЗ'}")
                
                # Если задание нужно удалить из ДЗ (is_correct=True и used_hint=False)
                if not was_added and is_correct and not used_hint:
                    # Удаляем из домашней работы
                    cursor.execute("""
                        DELETE FROM task_progress 
                        WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
                    """, (user_id, world_id, cat_code, task_idx))
                    logging.info(f"✅ Задание {task_key} удалено из домашней работы (верный ответ без подсказки)")
            except Exception as e:
                # В случае ошибки используем старую логику
                logging.error(f"❌ Ошибка при вызове auto_add_to_homework для домашнего задания: {e}")
                
                # Старая логика: Если пользователь решил задачу верно, но использовал подсказку, 
                # всё равно оставляем её в домашней работе для повторения
                if is_correct and used_hint:
                    logging.info(f"Задача решена верно, но с использованием подсказки. Оставляем в домашней работе.")
                    # Ничего не делаем, задача остается в домашней работе
            
            conn.commit()
            conn.close()
            logging.info(f"Статус домашнего задания обновлен: task={task_key}, status={status}, used_hint={used_hint}")
            
            # Проверяем статус после обновления для контроля
            check_conn = sqlite3.connect('task_progress.db')
            check_cursor = check_conn.cursor()
            check_cursor.execute("""
                SELECT status FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
            """, (user_id, world_id, cat_code, task_idx))
            check_status = check_cursor.fetchone()
            check_conn.close()
            
            logging.info(f"Финальная проверка статуса {task_key}: {'status=' + str(check_status[0]) if check_status else 'Не найден'}")
        except Exception as e:
            logging.error(f"Ошибка обновления статуса домашнего задания: {e}")
        
        # Отправляем сообщение о результате
        world_id = homework_data["world_id"]
        cat_code = homework_data["cat_code"]
        task_idx = homework_data["task_idx"]
        message_id = homework_data["message_id"]
        
        # Получаем задание и категорию
        category = challenge.get(world_id, {}).get(cat_code, {})
        task = category.get('tasks', [])[task_idx] if category and 'tasks' in category and task_idx < len(category['tasks']) else None
        
        if task:
            # Обновляем отображение задания с новым статусом
            status_text = "✅ Верно" if is_correct else "❌ Неверно"
            caption = f"№{task_idx + 1} Домашняя работа\n{category['name']}\n{status_text}\n"
            
            if is_correct:
                caption += f"\nПравильный ответ: {task.get('answer', '')}"
            else:
                caption += "\nПопробуйте ещё раз или воспользуйтесь подсказкой.\nВведите ответ в чат:"
            
            # Получаем URL изображения из поля "homework"
            photo_url = task["homework"]["photo"]
            if not photo_url.startswith("http"):
                photo_url = f"https://i.imgur.com/{photo_url}.jpeg"
                
            # Создаём клавиатуру
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            # Получаем все домашние задания для навигации
            try:
                conn_nav = sqlite3.connect('task_progress.db')
                cursor_nav = conn_nav.cursor()
                cursor_nav.execute("""
                    SELECT task_idx FROM task_progress 
                    WHERE user_id = ? AND cat_code = ? AND type = 'homework'
                """, (user_id, cat_code))
                
                homework_tasks = cursor_nav.fetchall()
                conn_nav.close()
                
                if homework_tasks:
                    # Список индексов заданий
                    task_indices = [t[0] for t in homework_tasks]
                    total_tasks = len(task_indices)
                    current_index = task_indices.index(task_idx)
                    
                    # Кнопки навигации (всегда видимы)
                    nav_buttons = []
                    
                    # Если первое задание, добавляем фантомную кнопку влево
                    if current_index > 0:
                        prev_task_idx = task_indices[current_index - 1]
                        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{prev_task_idx}"))
                    else:
                        # Фантомная кнопка без функционала и без текста
                        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                    
                    # Счетчик текущего положения
                    nav_buttons.append(InlineKeyboardButton(f"{current_index + 1}/{total_tasks}", callback_data="quest_empty"))
                    
                    # Если последнее задание, добавляем фантомную кнопку вправо
                    if current_index < total_tasks - 1:
                        next_task_idx = task_indices[current_index + 1]
                        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{next_task_idx}"))
                    else:
                        # Фантомная кнопка без функционала и без текста
                        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                    
                    markup.row(*nav_buttons)
            except Exception as e:
                logging.error(f"Ошибка при построении навигации домашнего задания: {e}")
            
            # Кнопка для просмотра подсказки, если она есть
            if task.get('hint'):
                markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_hint_direct_{world_id}_{cat_code}_{task_idx}_0"))
            
            # Проверка избранного и добавление кнопки избранного
            try:
                favorites = get_user_favorites(user_id)
                is_favorite = any(
                    f["challenge_num"] == world_id and f["cat_code"] == cat_code and f["task_idx"] == task_idx for f in favorites
                )
                
                # Кнопка добавления/удаления из избранного
                markup.add(
                    InlineKeyboardButton(
                        "🗑️ Удалить из избранного" if is_favorite else "⭐️ Добавить в избранное",
                        callback_data=f"{'remove' if is_favorite else 'add'}_favorite_{world_id}_{cat_code}_{task_idx}"
                    )
                )
            except Exception as e:
                logging.error(f"Ошибка при проверке избранного: {e}")
            
            # Кнопка возврата
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_homework"))
            
            # Отправляем обновленное сообщение
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
        
        return
    
    # Обработка сообщений для запроса репетитора
    elif current_screen == "tutor_questions":
        handle_tutor_text(message)
        return
    
    # Обработка ввода имени для таймера
    elif current_screen == "timer_name_input":
        process_timer_name(message, user_id)
        return
    
    # Обработка ввода имени группы карточек
    elif current_screen == "cards_group_name_input":
        process_group_name(message, user_id, user_messages.get(user_id, 0))
        return
        
    # Проверяем наличие задачи из избранного
    if user_id in user_task_data:
        task_data = user_task_data[user_id]
        # Проверяем, что это задача из избранного
        if task_data.get("from_favorites", False):
            logging.info(f"Обработка ответа для задачи из избранного: challenge_num={task_data['challenge_num']}, cat_code={task_data['cat_code']}, task_idx={task_data['task_idx']}")
            
            # Удаляем сообщение пользователя
            try:
                bot.delete_message(chat_id, message.message_id)
                logging.info(f"Сообщение {message.message_id} от пользователя {user_id} удалено")
            except Exception as e:
                logging.warning(f"Не удалось удалить сообщение {message.message_id} от пользователя {user_id}: {e}")
            
            # Проверяем ответ пользователя
            user_answer = text.strip().replace(',', '.').replace(' ', '').lower()
            correct_answer = str(task_data.get("correct_answer", "")).strip().replace(',', '.').replace(' ', '').lower()
            
            # Проверяем точное совпадение
            is_correct = user_answer == correct_answer
            
            # Проверка с числами (если строгое сравнение не сработало)
            if not is_correct:
                try:
                    user_answer_num = float(user_answer)
                    correct_answer_num = float(correct_answer)
                    is_correct = abs(user_answer_num - correct_answer_num) < 0.01  # Допуск для чисел
                except ValueError:
                    # Если не удалось преобразовать в число, оставляем результат сравнения строк
                    pass
            
            # Формируем текст сообщения
            world_id = task_data["challenge_num"]
            cat_code = task_data["cat_code"]
            task_idx = task_data["task_idx"]
            message_id = task_data["message_id"]
            task = task_data["task"]
            
            category_name = challenge[world_id][cat_code]["name"]
            current_index = user_data[user_id]["current_index"]
            total_tasks = len(user_data[user_id]["favorite_tasks"])
            
            # Обновляем статус в базе данных
            new_status = "correct" if is_correct else "incorrect"
            status_value = 1 if is_correct else 0  # 1 - верно, 0 - неверно
            try:
                conn = sqlite3.connect('task_progress.db')
                cursor = conn.cursor()
                # Обновляем статус задачи
                cursor.execute("""
                    INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, world_id, cat_code, task_idx, "main", status_value))
                
                # Если задача решена верно, добавляем её в словарь решенных задач в памяти для быстрого доступа
                if is_correct:
                    if 'user_solutions' not in user_data.get(user_id, {}):
                        if user_id not in user_data:
                            user_data[user_id] = {}
                        user_data[user_id]['user_solutions'] = {}
                    task_key = f"{world_id}_{cat_code}_{task_idx}"
                    user_data[user_id]['user_solutions'][task_key] = "correct"
                
                conn.commit()
                conn.close()
                logging.info(f"Статус задачи из избранного обновлён на '{new_status}' для user_id={user_id}")
            except sqlite3.OperationalError as e:
                # Если таблица не существует, инициализируем её
                if "no such table" in str(e):
                    init_task_progress_db()
                    conn = sqlite3.connect('task_progress.db')
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, world_id, cat_code, task_idx, "main", status_value))
                    conn.commit()
                    conn.close()
                    logging.info(f"Таблица task_progress инициализирована и статус обновлён на '{new_status}' для user_id={user_id}")
                else:
                    logging.error(f"Ошибка при обновлении статуса задачи из избранного: {e}")
            
            # Формируем и обновляем сообщение с результатом
            if is_correct:
                status_text = "✅ Верно"
                answer_text = f"\n\nПравильный ответ: {task['answer']}"
            else:
                status_text = "❌ Неверно"
                answer_text = "\n\nВведите ответ в чат:"
            
            caption = f"№{world_id}\n{category_name}\n{status_text}\n{answer_text}"
            
            # Обновляем интерфейс
            # Создаем клавиатуру с кнопками навигации
            markup = InlineKeyboardMarkup(row_width=3)
            
            # Формируем навигационные кнопки: всегда 3 кнопки с разными обработчиками в зависимости от страницы
            nav_buttons = []
            
            if current_index == 0:
                # Первая страница: пустая стрелка, счетчик, стрелка вперед
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
            elif current_index == total_tasks - 1:
                # Последняя страница: стрелка назад, счетчик, пустая стрелка
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            else:
                # Промежуточная страница: стрелка назад, счетчик, стрелка вперед
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
            
            # Добавляем все кнопки в одном ряду
            markup.row(*nav_buttons)
            
            # Получаем количество подсказок для задания
            hint_count = len(task.get("hint", []))
            if hint_count > 0:
                # Добавляем кнопку подсказки без указания количества шагов
                markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"hint_{world_id}_{cat_code}_{task_idx}_0"))
            
            # Добавляем кнопку удаления из избранного
            markup.add(InlineKeyboardButton("🗑 Удалить из избранного", callback_data=f"quest_favorite_{world_id}_{cat_code}_{task_idx}"))
            
            # Кнопка возврата - используем callback в зависимости от текущего режима
            back_callback = f"quest_favorite_world_{world_id}"
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data=back_callback))
            
            bot.edit_message_media(
                media=InputMediaPhoto(task["photo"], caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            
            logging.info(f"Обработан ответ на задачу из избранного: world={world_id}, cat={cat_code}, task={task_idx}, правильно: {is_correct}")
            return
            
    # Пытаемся удалить сообщение пользователя если сообщение не было обработано как ответ на избранное
    try:
        bot.delete_message(chat_id, message.message_id)
        logging.info(f"Сообщение {message.message_id} от пользователя {user_id} удалено")
    except Exception as e:
        # Если не удалось удалить сообщение, просто продолжаем работу
        logging.warning(f"Не удалось удалить сообщение {message.message_id} от пользователя {user_id}: {e}")
        
    # Сразу проверяем, есть ли в памяти данные о правильно решенных задачах
    task_already_solved = False
    current_task_key = None
    
    # Проверяем, если у пользователя есть текущая задача
    if user_id in user_data and 'current_task' in user_data[user_id]:
        current_task = user_data[user_id]['current_task']
        world_id = current_task.get('world_id')
        cat_code = current_task.get('cat_code')
        task_idx = current_task.get('task_idx')
        
        if world_id and cat_code is not None and task_idx is not None:
            current_task_key = f"{world_id}_{cat_code}_{task_idx}"
            
            # Проверяем, решена ли уже эта задача правильно
            if 'user_solutions' in user_data[user_id] and current_task_key in user_data[user_id]['user_solutions']:
                if user_data[user_id]['user_solutions'][current_task_key] == "correct":
                    task_already_solved = True
                    logging.info(f"Задача {current_task_key} уже была решена пользователем {user_id} ранее (из памяти)")
                    
            # Если не нашли в памяти, проверяем базу данных
            if not task_already_solved:
                try:
                    conn = sqlite3.connect('task_progress.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT status FROM task_progress WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
                        (user_id, str(world_id), cat_code, task_idx)
                    )
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result and result[0] == 1:
                        task_already_solved = True
                        # Добавляем в память для ускорения будущих проверок
                        if 'user_solutions' not in user_data[user_id]:
                            user_data[user_id]['user_solutions'] = {}
                        user_data[user_id]['user_solutions'][current_task_key] = "correct"
                        logging.info(f"Задача {current_task_key} уже была решена пользователем {user_id} ранее (из базы данных)")
                        
                        # Если задача уже решена, просто тихо удаляем ответ и завершаем обработку без уведомлений
                        logging.info(f"Пользователь повторно ответил на уже решенную задачу {current_task_key}")
                        return
                except Exception as e:
                    logging.error(f"Ошибка при проверке статуса задачи: {e}")
    
    try:
        # Проверяем, есть ли информация о текущей задаче у пользователя
        if user_id in user_data and "current_task" in user_data[user_id]:
            # Извлекаем данные о текущей задаче
            task_info = user_data[user_id]["current_task"]
            world_id = task_info["world_id"]
            cat_code = task_info["cat_code"]
            task_idx = task_info["task_idx"]
            
            # Получаем информацию о задаче
            world_challenge = challenge.get(str(world_id), {})
            category = world_challenge.get(cat_code, {"name": "Неизвестная категория", "tasks": []})
            tasks = category.get("tasks", [])
            
            if task_idx < 0 or task_idx >= len(tasks):
                bot.send_message(chat_id, "Ошибка: задача не найдена")
                return
            
            task = tasks[task_idx]
            correct_answer = str(task.get("answer", "")).strip()
            
            # Удаляем сообщение пользователя (если есть доступ)
            try:
                # Сохраняем ID сообщения для возможного использования в логах
                user_message_id = message.message_id
                
                # В этом месте сообщение пользователя может уже быть удалено
                # Безопасно пытаемся удалить его, игнорируя ошибки "сообщение не найдено"
                try:
                    bot.delete_message(chat_id, message.message_id)
                except Exception as delete_err:
                    if "message to delete not found" not in str(delete_err):
                        logging.error(f"Ошибка при удалении сообщения: {delete_err}")
                    # Если сообщение не найдено, просто продолжаем работу
            except Exception as e:
                logging.error(f"Ошибка при работе с сообщением пользователя: {e}")
            
            # Проверяем ответ пользователя - убираем лишние пробелы и переводим в нижний регистр
            user_answer = text.lower().strip()
            correct_answer_clean = correct_answer.lower().strip()
            
            # Проверяем точное совпадение
            is_correct = user_answer == correct_answer_clean
            
            # Проверяем отрицательные числа (например, "-17" и "17" с учётом минуса)
            if not is_correct and user_answer.replace('-', '', 1).isdigit() and correct_answer_clean.replace('-', '', 1).isdigit():
                # Если пользователь ввёл число без минуса, но правильный ответ отрицательный
                if user_answer.isdigit() and correct_answer_clean.startswith('-'):
                    is_correct = '-' + user_answer == correct_answer_clean
                # Если пользователь ввёл отрицательное число, но правильный ответ без минуса
                elif user_answer.startswith('-') and correct_answer_clean.isdigit():
                    is_correct = user_answer == '-' + correct_answer_clean
            
            # Если ответ не совпал, попробуем проверить числовой ответ
            if not is_correct:
                try:
                    # Проверяем, если это числа с разными форматами (например, "2.5" и "2,5")
                    user_num = user_answer.replace(',', '.').replace(' ', '')
                    correct_num = correct_answer_clean.replace(',', '.').replace(' ', '')
                    
                    # Проверяем, являются ли строки числами (учитывая возможные минусы)
                    if (user_num.replace('-', '', 1).replace('.', '', 1).isdigit() and 
                        correct_num.replace('-', '', 1).replace('.', '', 1).isdigit()):
                        user_float = float(user_num)
                        correct_float = float(correct_num)
                        is_correct = abs(user_float - correct_float) < 0.0001  # Допуск для сравнения чисел с плавающей точкой
                        
                        # Специальная проверка для случаев, когда ответы отличаются только знаком
                        if not is_correct and user_float == -correct_float:
                            logging.warning(f"Внимание: ответы отличаются только знаком: {user_float} и {correct_float}")
                except (ValueError, TypeError) as e:
                    # Если не удалось преобразовать в числа, оставляем is_correct = False
                    logging.debug(f"Не удалось сравнить как числа: {e}")
            
            # Логируем информацию о проверке ответа
            logging.info(f"Проверка ответа: пользователь ввел '{user_answer}', правильный ответ '{correct_answer_clean}', результат: {is_correct}")
            
            # Проверяем, была ли задача уже правильно решена ранее
            # ВАЖНАЯ ПРОВЕРКА: делаем ее ДО обновления статуса в базе
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            
            # Проверяем, есть ли уже запись для этой задачи
            cursor.execute(
                "SELECT status FROM task_progress WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
                (user_id, str(world_id), cat_code, task_idx)
            )
            existing_record = cursor.fetchone()
            
            # Определяем текущий статус и переменную "задача уже была решена ранее"
            task_was_correct_before = False
            if existing_record and existing_record[0] == "correct":
                task_was_correct_before = True
                logging.info(f"Задача {world_id}_{cat_code}_{task_idx} уже была правильно решена ранее пользователем {user_id}")
            
            # Определяем новый статус ТОЛЬКО если задача еще не была решена правильно
            if task_was_correct_before:
                # Если задача была решена ранее, оставляем статус "correct"
                new_status = "correct"
            else:
                # Иначе устанавливаем статус в зависимости от правильности ответа
                new_status = "correct" if is_correct else "wrong"
            
            # Теперь обновляем базу данных в соответствии с новой логикой
            if existing_record:
                # Обновляем существующую запись
                cursor.execute(
                    "UPDATE task_progress SET status = ? WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
                    (new_status, user_id, str(world_id), cat_code, task_idx)
                )
            else:
                # Создаем новую запись
                cursor.execute(
                    "INSERT INTO task_progress (user_id, challenge_num, cat_code, task_idx, status) VALUES (?, ?, ?, ?, ?)",
                    (user_id, str(world_id), cat_code, task_idx, new_status)
                )
            
            conn.commit()
            conn.close()
            
            try:
                # Получаем фото задания для любого исхода
                photo_url = task['photo']
                if not photo_url.startswith("http"):
                    photo_url = f"https://i.imgur.com/{photo_url}.jpeg"
                
                # Общие элементы интерфейса
                markup = InlineKeyboardMarkup(row_width=2)
                navigation_buttons = []
                total_tasks = len(tasks)
                
                if task_idx > 0:
                    navigation_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx-1}"))
                else:
                    navigation_buttons.append(InlineKeyboardButton(" ", callback_data="no_action"))
                    
                navigation_buttons.append(InlineKeyboardButton(f"{task_idx+1}/{total_tasks}", callback_data="no_action"))
                
                if task_idx < total_tasks - 1:
                    navigation_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx+1}"))
                else:
                    navigation_buttons.append(InlineKeyboardButton(" ", callback_data="no_action"))
                
                markup.row(*navigation_buttons)
                # Получаем количество подсказок для задания
                hint_count = len(task.get("hint", []))
                if hint_count > 0:
                    # Добавляем кнопку подсказки
                    markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_solution_{world_id}_{cat_code}_{task_idx}"))
                
                # Получаем избранные задания пользователя
                favorites = get_user_favorites(user_id)
                is_favorite = any(f['challenge_num'] == str(world_id) and f['cat_code'] == cat_code and f['task_idx'] == task_idx for f in favorites)
                
                # Кнопка для добавления/удаления из избранного
                if is_favorite:
                    markup.add(InlineKeyboardButton("🗑 Удалить из избранного", callback_data=f"quest_favorite_remove_{world_id}_{cat_code}_{task_idx}"))
                else:
                    markup.add(InlineKeyboardButton("⭐️ Добавить в избранное", callback_data=f"quest_favorite_add_{world_id}_{cat_code}_{task_idx}"))
                
                # Кнопка возврата в меню выбора тем
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_list_{world_id}"))
                
                # Используем переменную task_was_correct_before из предыдущей проверки выше в коде
                task_key = f"{world_id}_{cat_code}_{task_idx}"
                
                # Мы уже сделали проверку на правильность решения задачи ранее,
                # поэтому не повторяем эту проверку снова, а просто используем полученное значение
                
                # Если ответ верный или задача уже была решена правильно ранее - всегда показываем "Верно"
                if is_correct or task_was_correct_before or task_already_solved:
                    if is_correct and not task_was_correct_before and not task_already_solved:
                        logging.info(f"Пользователь {user_id} правильно решил задачу {world_id}_{cat_code}_{task_idx}")
                        
                        # Если задача решена верно впервые, сохраняем это в память
                        if 'user_solutions' not in user_data[user_id]:
                            user_data[user_id]['user_solutions'] = {}
                        user_data[user_id]['user_solutions'][f"{world_id}_{cat_code}_{task_idx}"] = "correct"
                    
                    # Всегда получаем статус "Верно" (даже если текущий ответ неверный, но задача ранее была решена верно)
                    status_text = "✅ Верно"
                    answer_text = ""
                    
                    # Добавляем правильный ответ если известен
                    if 'answer' in task:
                        answer_text = f"\n\nПравильный ответ: {task['answer']}"
                    
                    caption = f"№{world_id}\n{category['name']}\n{status_text}{answer_text}"
                else:
                    logging.info(f"Пользователь {user_id} дал неверный ответ на задачу {world_id}_{cat_code}_{task_idx}")
                    
                    # Только если задача ранее не была решена правильно, показываем статус "Неверно"
                    status_text = "❌ Неверно"
                    answer_text = ""
                    
                    caption = f"№{world_id}\n{category['name']}\n{status_text}{answer_text}\n\nВведите ответ в чат:"
                
                # Обновляем сообщение в чате
                message_id = user_data[user_id].get('quest_message_id', None)
                
                # Мы уже проверили статус задачи выше и сформировали правильный caption
                # Теперь просто определяем, нужно ли обновлять сообщение
                
                # Никогда не обновляем сообщение, если задача была правильно решена ранее
                # вне зависимости от текущего ответа
                if task_was_correct_before or task_already_solved:
                    logging.info(f"Пропускаем обновление сообщения для {task_key} - задача уже решена")
                    
                    # Для уже решенных заданий просто тихо удаляем сообщение пользователя 
                    # и НЕ отправляем никаких дополнительных сообщений
                    # Это предотвратит дублирование сообщений с заданием в чате
                    logging.info(f"Задача {task_key} была решена ранее, не отправляем новое сообщение")
                    
                    # Не делаем никаких дополнительных действий
                    return
                
                # Обновляем сообщение, только если задача ещё не была правильно решена
                if message_id:
                    try:
                        # Вместо обновления существующего сообщения, отправляем новое 
                        # с тем же содержимым, если предыдущее сообщение не найдено
                        try:
                            bot.edit_message_media(
                                media=InputMediaPhoto(photo_url, caption=caption),
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=markup
                            )
                        except Exception as edit_err:
                            if "message to edit not found" in str(edit_err) or "message to be edited" in str(edit_err):
                                # Отправляем новое сообщение, если предыдущее не найдено
                                new_message = bot.send_photo(
                                    chat_id=chat_id,
                                    photo=photo_url,
                                    caption=caption,
                                    reply_markup=markup
                                )
                                # Сохраняем ID нового сообщения для последующих обновлений
                                if user_id not in user_data:
                                    user_data[user_id] = {}
                                user_data[user_id]['quest_message_id'] = new_message.message_id
                                logging.info(f"Отправлено новое сообщение с задачей, message_id={new_message.message_id}")
                            elif "message is not modified" not in str(edit_err):
                                # Логируем, но игнорируем ошибку, если содержимое не изменилось
                                logging.error(f"Ошибка при обновлении сообщения: {edit_err}")
                            # Если сообщение не изменилось, просто продолжаем
                    except Exception as e:
                        logging.error(f"Критическая ошибка при работе с сообщением: {e}")
                        # В случае критической ошибки пытаемся отправить информационное сообщение
                        try:
                            bot.send_message(
                                chat_id=chat_id,
                                text="Возникла проблема при отображении задания. Пожалуйста, вернитесь в список заданий и попробуйте снова."
                            )
                        except:
                            pass
            except Exception as e:
                logging.error(f"Ошибка при обработке ответа: {e}")
                # При ошибке, отправляем поясняющее сообщение
                try:
                    bot.send_message(
                        chat_id=chat_id,
                        text="Произошла ошибка при обработке ответа. Попробуйте вернуться в задание заново."
                    )
                except Exception as send_err:
                    logging.error(f"Не удалось отправить сообщение об ошибке: {send_err}")
        else:
            # Если не ожидается ответ на задачу, игнорируем сообщение
            # Не отправляем никаких сообщений, просто логируем
            logging.info(f"Получено текстовое сообщение от пользователя {user_id}, но ответ на задачу не ожидался")
    except Exception as e:
        logging.error(f"Ошибка при обработке текстового сообщения от user_id={user_id}: {e}")
        bot.send_message(
            chat_id=chat_id,
            text="Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте еще раз."
        )

# Обработчики для просмотра избранных заданий

def handle_quest_favorite_view_ordered(call):
    """Обработчик просмотра избранных заданий подряд"""
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Получаем ID мира из колбэка
        world_id_str = call.data.split("_")[-1]
        
        try:
            # Пробуем преобразовать в число, так как в QUEST_WORLDS id хранятся как числа
            world_id_int = int(world_id_str)
            world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
        except ValueError:
            # Если не удалось преобразовать в число, пытаемся найти мир с id в строковом формате
            logging.warning(f"Не удалось преобразовать world_id {world_id_str} в число")
            world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id_str), None)
        
        if not world:
            bot.answer_callback_query(call.id, "Ошибка: мир не найден")
            logging.error(f"Мир с ID {world_id_str} не найден в QUEST_WORLDS")
            return
        
        # Получаем избранные задания для этого мира
        all_favorites = get_user_favorites(user_id)
        world_id_for_db = str(world["id"])
        
        # Фильтруем задания для текущего мира, с преобразованием типов
        world_favorites = [f for f in all_favorites if f['challenge_num'] == world_id_for_db]
        
        if not world_favorites:
            bot.answer_callback_query(call.id, "Нет избранных заданий в этом мире")
            return
        
        # Сохраняем избранные задания для этого мира в user_data
        if user_id not in user_data:
            user_data[user_id] = {}
        
        # Подготавливаем данные для просмотра заданий
        favorite_tasks = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in world_favorites]
        user_data[user_id]["favorite_tasks"] = favorite_tasks
        user_data[user_id]["current_index"] = 0
        user_data[user_id]["current_world_id"] = world["id"]
        user_data[user_id]["current_mode"] = "ordered"
        
        # Отправляем первое задание
        send_favorite_task(chat_id, message_id)
        logging.info(f"Начат просмотр избранных заданий подряд для пользователя {user_id}")
        
    except Exception as e:
        logging.error(f"Ошибка при запуске просмотра избранных заданий подряд: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке избранных заданий")

def handle_quest_favorite_view_random(call):
    """Обработчик просмотра избранных заданий в случайном порядке"""
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    import random
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Получаем ID мира из колбэка
        world_id_str = call.data.split("_")[-1]
        
        try:
            # Пробуем преобразовать в число, так как в QUEST_WORLDS id хранятся как числа
            world_id_int = int(world_id_str)
            world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
        except ValueError:
            # Если не удалось преобразовать в число, пытаемся найти мир с id в строковом формате
            logging.warning(f"Не удалось преобразовать world_id {world_id_str} в число")
            world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id_str), None)
        
        if not world:
            bot.answer_callback_query(call.id, "Ошибка: мир не найден")
            logging.error(f"Мир с ID {world_id_str} не найден в QUEST_WORLDS")
            return
        
        # Получаем избранные задания для этого мира
        all_favorites = get_user_favorites(user_id)
        world_id_for_db = str(world["id"])
        
        # Фильтруем задания для текущего мира, с преобразованием типов
        world_favorites = [f for f in all_favorites if f['challenge_num'] == world_id_for_db]
        
        if not world_favorites:
            bot.answer_callback_query(call.id, "Нет избранных заданий в этом мире")
            return
        
        # Сохраняем избранные задания для этого мира в user_data
        if user_id not in user_data:
            user_data[user_id] = {}
        
        # Подготавливаем данные для просмотра заданий в случайном порядке
        favorite_tasks = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in world_favorites]
        
        # Перемешиваем задания
        random.shuffle(favorite_tasks)
        
        user_data[user_id]["favorite_tasks"] = favorite_tasks
        user_data[user_id]["current_index"] = 0
        user_data[user_id]["current_world_id"] = world["id"]
        user_data[user_id]["current_mode"] = "random"
        
        # Отправляем первое задание
        send_favorite_task(chat_id, message_id)
        logging.info(f"Начат просмотр избранных заданий в случайном порядке для пользователя {user_id}")
        
    except Exception as e:
        logging.error(f"Ошибка при запуске просмотра избранных заданий в случайном порядке: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке избранных заданий")

def handle_quest_favorite_world_categories(call):
    """Обработчик просмотра избранных заданий конкретного мира по категориям"""
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Получаем ID мира из колбэка
        world_id_str = call.data.split("_")[-1]
        
        try:
            # Пробуем преобразовать в число, так как в QUEST_WORLDS id хранятся как числа
            world_id_int = int(world_id_str)
            world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
        except ValueError:
            # Если не удалось преобразовать в число, пытаемся найти мир с id в строковом формате
            logging.warning(f"Не удалось преобразовать world_id {world_id_str} в число")
            world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id_str), None)
        
        if not world:
            bot.answer_callback_query(call.id, "Ошибка: мир не найден")
            logging.error(f"Мир с ID {world_id_str} не найден в QUEST_WORLDS")
            return
        
        # Используем строковое представление world_id для сравнения с challenge_num из БД
        world_id_for_db = str(world["id"])
        
        # Получаем избранные задания для этого мира
        all_favorites = get_user_favorites(user_id)
        
        # Фильтруем задания для текущего мира
        world_favorites = [f for f in all_favorites if f['challenge_num'] == world_id_for_db]
        
        if not world_favorites:
            bot.answer_callback_query(call.id, "Нет избранных заданий в этом мире")
            return
        
        # Группируем задания по категориям
        by_category = {}
        for fav in world_favorites:
            cat_code = fav['cat_code']
            if cat_code not in by_category:
                by_category[cat_code] = []
            by_category[cat_code].append(fav)
        
        # Получаем информацию о категориях в этом мире
        world_challenges = challenge.get(world_id_for_db, {})
        
        # Создаем клавиатуру для выбора категории
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для категорий
        for cat_code in sorted(by_category.keys()):
            category = world_challenges.get(cat_code, {"name": f"Категория {cat_code}"})
            count = len(by_category[cat_code])
            button_text = f"{category.get('name', f'Категория {cat_code}')}"
            
            markup.add(InlineKeyboardButton(
                button_text,
                callback_data=f"quest_favorite_category_{world_id_for_db}_{cat_code}"
            ))
            logging.info(f"Добавлена кнопка для категории {cat_code}: {button_text}")
        
        # Кнопка возврата
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_favorite_world_{world_id_for_db}"))
        
        # Отображаем список категорий
        bot.edit_message_media(
            media=InputMediaPhoto(world["loaded_image"], caption=f"⭐ Избранные задания - {world['name']}\n\nВыберите категорию для просмотра заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображен список категорий избранных заданий для мира {world['name']}")
    except Exception as e:
        logging.error(f"Ошибка при отображении категорий избранных заданий: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки категорий")

def handle_favorite_hint(call):
    """Обработчик для просмотра подсказок в избранном.
    Формат callback: hint_world_cat_task_step"""
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Разбор callback-данных
        parts = call.data.split("_")
        if len(parts) < 5:
            bot.answer_callback_query(call.id, "Ошибка: неправильный формат данных для подсказки")
            return
            
        # Получаем компоненты callback
        world_id = parts[1]
        cat_code = parts[2]
        task_idx = int(parts[3])
        hint_idx = int(parts[4])
        
        # Получаем задание и подсказки
        world_challenges = challenge.get(world_id, {})
        category = world_challenges.get(cat_code, {"name": "Неизвестная категория", "tasks": []})
        tasks = category.get("tasks", [])
        
        if task_idx < 0 or task_idx >= len(tasks):
            bot.answer_callback_query(call.id, "Ошибка: задача не найдена")
            return
            
        task = tasks[task_idx]
        hints = task.get("hint", [])
        
        if not hints:
            bot.answer_callback_query(call.id, "Для этой задачи нет подсказок")
            return
            
        total_hints = len(hints)
        if hint_idx < 0 or hint_idx >= total_hints:
            bot.answer_callback_query(call.id, "Указанная подсказка не найдена")
            return
            
        # Добавляем задание в домашнюю работу при использовании подсказки
        try:
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, str(world_id), cat_code, task_idx, "homework", "wrong"))
            conn.commit()
            conn.close()
            logging.info(f"Задача {world_id}_{cat_code}_{task_idx} добавлена в домашнюю работу пользователя {user_id} из-за использования подсказки в избранном")
        except Exception as e:
            logging.error(f"Ошибка при добавлении задачи в домашнюю работу: {e}")
            
        # Создаем новую клавиатуру для просмотра подсказок
        markup = InlineKeyboardMarkup(row_width=3)
        
        # Кнопки навигации по подсказкам
        nav_buttons = []
        
        # Создаем кнопки навигации по логике: показываем только те кнопки, 
        # которые имеют смысл для текущего индекса подсказки
        if hint_idx > 0:
            nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"hint_{world_id}_{cat_code}_{task_idx}_{hint_idx-1}"))
        else:
            nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            
        nav_buttons.append(InlineKeyboardButton(f"{hint_idx+1}/{total_hints}", callback_data="quest_empty"))
        
        if hint_idx < total_hints - 1:
            nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"hint_{world_id}_{cat_code}_{task_idx}_{hint_idx+1}"))
        else:
            nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            
        markup.row(*nav_buttons)
        
        # Кнопка для возврата к задаче
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorite_nav_{user_data[user_id].get('current_index', 0)}"))
        
        # Получаем текущую подсказку
        hint_text = hints[hint_idx]
        
        # Формируем заголовок для подсказки
        hint_caption = f"💡 Подсказка - Шаг {hint_idx+1}/{total_hints}\n\n{hint_text}"
        
        # Обновляем сообщение с подсказкой
        bot.edit_message_media(
            media=InputMediaPhoto(task["photo"], caption=hint_caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        
        logging.info(f"Отображена подсказка {hint_idx+1}/{total_hints} для задачи {world_id}_{cat_code}_{task_idx}")
    except Exception as e:
        logging.error(f"Ошибка при отображении подсказки: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при загрузке подсказки")


def handle_favorite_navigation(call):
    """Обработчик навигации по избранным заданиям
    Формат callback: favorite_nav_index"""
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Разбираем callback_data и получаем новый индекс
        parts = call.data.split("_")
        if len(parts) < 3:
            bot.answer_callback_query(call.id, "Ошибка: неправильный формат данных для навигации")
            return
            
        new_index = int(parts[2])
        
        # Проверяем, есть ли у пользователя избранные задания
        if user_id not in user_data or "favorite_tasks" not in user_data[user_id] or not user_data[user_id]["favorite_tasks"]:
            bot.answer_callback_query(call.id, "Список избранных заданий пуст")
            return
            
        # Получаем список избранных заданий
        favorite_tasks = user_data[user_id]["favorite_tasks"]
        total_tasks = len(favorite_tasks)
        
        # Проверяем границы индекса
        if new_index < 0 or new_index >= total_tasks:
            bot.answer_callback_query(call.id, "Ошибка: выход за границы списка избранного")
            return
            
        # Обновляем текущий индекс
        user_data[user_id]["current_index"] = new_index
        
        # Отображаем задание по новому индексу
        send_favorite_task(chat_id, message_id)
        
        logging.info(f"Навигация по избранному: перешли к заданию {new_index+1}/{total_tasks}")
    except Exception as e:
        logging.error(f"Ошибка при навигации по избранным заданиям: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при навигации")


def handle_quest_favorite_view_by_category(call):
    """Обработчик просмотра избранных заданий по категориям"""
    try:
        # Получаем callback_data и логируем для отладки
        callback_data = call.data
        logging.info(f"Обработка handle_quest_favorite_view_by_category, callback_data: {callback_data}")
        
        # Извлекаем world_id из callback_data
        parts = call.data.split('_')
        
        # В формате "quest_favorite_view_by_category_X", где X - это ID мира
        # Последний элемент должен быть ID мира
        world_id = parts[-1]
        
        # Логируем извлеченный world_id
        logging.info(f"Извлеченный world_id: {world_id}")
        
        # Создаем новый callback_data для перенаправления на правильный обработчик
        new_data = f"quest_favorite_world_categories_{world_id}"
        logging.info(f"Перенаправление на {new_data}")
        
        # Преобразуем старый callback_data в новый формат
        call.data = new_data
        
        # Вызываем обработчик категорий
        handle_quest_favorite_world_categories(call)
    except Exception as e:
        logging.error(f"Ошибка при запуске просмотра избранных заданий по категориям: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке избранных заданий")


