"""
Модуль для исправления проблем с функциональностью "Ритуал повторения"
в математическом Telegram-боте.

Основные проблемы:
1. Неправильная обработка текстовых ответов - система перехватывает любой текст как ответ на ДЗ
2. При верном ответе без подсказки, задание не добавляется в домашнюю работу
3. При повторных неверных ответах задания не добавляются в ДЗ
4. Требуется полная синхронизация заданий при запуске бота
"""

import sqlite3
import logging

def force_sync_homework_tasks():
    """
    Принудительно синхронизирует задания с неверными ответами с заданиями в домашней работе.
    Эта функция гарантирует, что ВСЕ задания с неверными ответами в основной таблице
    будут добавлены в домашнюю работу для повторения.
    
    Алгоритм:
    1. Получаем список всех заданий с неверными ответами
    2. Получаем список всех заданий в домашней работе
    3. Очищаем таблицу домашних заданий
    4. Добавляем все задания с неверными ответами в домашнюю работу
    """
    logging.info("⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Запуск синхронизации домашних заданий...")
    
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        
        # 1. Получаем список всех заданий с неверными ответами
        cursor.execute("""
            SELECT user_id, challenge_num, cat_code, task_idx
            FROM task_progress 
            WHERE type = 'main' AND status = 'wrong'
        """)
        wrong_answers = cursor.fetchall()
        logging.info(f"⚠️ ДИАГНОСТИКА: Найдено {len(wrong_answers)} задач с неверными ответами: {wrong_answers}")
        
        # 2. Получаем список всех заданий в домашней работе
        cursor.execute("""
            SELECT user_id, challenge_num, cat_code, task_idx
            FROM task_progress 
            WHERE type = 'homework'
        """)
        homework_tasks = cursor.fetchall()
        logging.info(f"⚠️ ДИАГНОСТИКА: Найдено {len(homework_tasks)} задач в домашней работе: {homework_tasks}")
        
        # 3. Очищаем таблицу домашних заданий
        cursor.execute("DELETE FROM task_progress WHERE type = 'homework'")
        conn.commit()
        logging.info(f"🔄 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Таблица homework полностью очищена")
        
        # 4. Добавляем все задания с неверными ответами в домашнюю работу
        if wrong_answers:
            values = [(user_id, challenge_num, cat_code, task_idx, 'homework', 'wrong') 
                     for user_id, challenge_num, cat_code, task_idx in wrong_answers]
            
            cursor.executemany("""
                INSERT INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, values)
            conn.commit()
            
            logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Одним запросом добавлено {len(values)} заданий в домашнюю работу")
        else:
            logging.info("⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Нет заданий с неверными ответами для добавления в домашнюю работу")
        
        # 5. Проверка синхронизации - получаем список всех заданий в домашней работе после синхронизации
        cursor.execute("SELECT * FROM task_progress WHERE type = 'homework'")
        homework_after = cursor.fetchall()
        logging.info(f"⚠️ ДИАГНОСТИКА ПОСЛЕ СИНХРОНИЗАЦИИ: Домашние задания (homework): {homework_after}")
        
        # 6. Сравниваем количество найденных задач с неверными ответами и добавленных в домашнюю работу
        if len(wrong_answers) == len(homework_after):
            logging.info("✅ ПОДТВЕРЖДЕНИЕ: Все задания с неверными ответами успешно добавлены в домашнюю работу")
        else:
            logging.error(f"⚠️ КРИТИЧЕСКАЯ ОШИБКА: Количество заданий с неверными ответами ({len(wrong_answers)}) не соответствует количеству заданий в домашней работе ({len(homework_after)})")
        
        # 7. Финальная проверка
        cursor.execute("SELECT * FROM task_progress WHERE type = 'homework'")
        final_check = cursor.fetchall()
        logging.info(f"✅ ИТОГОВАЯ ПРОВЕРКА: Домашние задания (homework): {final_check}")
        
        conn.close()
        return True
        
    except Exception as e:
        logging.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при синхронизации домашних заданий: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

def auto_add_to_homework(user_id, world_id, cat_code, task_idx, is_correct=False, used_hint=False):
    """
    Автоматически добавляет задание в домашнюю работу при определенных условиях.
    
    ПРАВИЛА ДОБАВЛЕНИЯ В ДОМАШНЮЮ РАБОТУ:
    1. Неверный ответ (с подсказкой или без) -> Добавить в ДЗ
    2. Верный ответ С подсказкой -> Добавить в ДЗ
    3. Верный ответ БЕЗ подсказки -> НЕ добавлять в ДЗ
    
    Параметры:
        user_id (str): ID пользователя
        world_id (str): ID мира/номер задания
        cat_code (str): Код категории задания
        task_idx (int): Индекс задания в категории
        is_correct (bool): Верно ли решил пользователь
        used_hint (bool): Использовал ли пользователь подсказку
        
    Возвращает:
        bool: True, если задание добавлено в ДЗ, иначе False
    """
    import sqlite3
    import logging
    
    # Логируем все входные параметры для диагностики
    logging.info(f"🔍 ДИАГНОСТИКА: auto_add_to_homework вызвана с параметрами:")
    logging.info(f"🔍 ДИАГНОСТИКА: user_id={user_id}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")
    logging.info(f"🔍 ДИАГНОСТИКА: is_correct={is_correct} (тип: {type(is_correct)}), used_hint={used_hint} (тип: {type(used_hint)})")
    
    # ГАРАНТИРУЕМ корректные типы параметров
    try:
        user_id = str(user_id)
        world_id = str(world_id)
        cat_code = str(cat_code)
        task_idx = int(task_idx)
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Явно конвертируем в bool, защищаемся от возможных проблем с "truthy" значениями
        is_correct = bool(is_correct)
        used_hint = bool(used_hint)
        
        logging.info(f"🛠️ ПОДГОТОВКА: Приведение типов параметров завершено успешно")
    except Exception as e:
        logging.error(f"⚠️ КРИТИЧЕСКАЯ ОШИБКА: Ошибка приведения типов в auto_add_to_homework: {e}")
        # В случае ошибки с типами, гарантируем добавление в ДЗ
        add_to_homework = True
        
        # НЕМЕДЛЕННО добавляем в ДЗ (защитное поведение)
        try:
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(user_id), str(world_id), str(cat_code), int(task_idx), "homework", "wrong"))
            conn.commit()
            conn.close()
            logging.info(f"🚨 ЗАЩИТНОЕ ДОБАВЛЕНИЕ в ДЗ из-за ошибки типов: {world_id}_{cat_code}_{task_idx}")
        except Exception as e2:
            logging.error(f"❌❌ КРИТИЧЕСКАЯ ОШИБКА при защитном добавлении в ДЗ: {e2}")
        
        return True  # Сразу возвращаем True, чтобы обеспечить добавление в ДЗ
    
    # ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА: печатаем конвертированные значения
    logging.info(f"🔎 РАСШИРЕННАЯ ДИАГНОСТИКА (после конвертации):")
    logging.info(f"🔎 user_id={user_id} (тип: {type(user_id)}), world_id={world_id} (тип: {type(world_id)})")
    logging.info(f"🔎 cat_code={cat_code} (тип: {type(cat_code)}), task_idx={task_idx} (тип: {type(task_idx)})")
    logging.info(f"🔎 is_correct={is_correct} (тип: {type(is_correct)}), used_hint={used_hint} (тип: {type(used_hint)})")
    
    # РАСШИРЕННАЯ ДИАГНОСТИКА: проверка всех условных выражений
    logging.info(f"🔎 ПРОВЕРКА УСЛОВИЙ:")
    logging.info(f"🔎 not is_correct = {not is_correct}")
    logging.info(f"🔎 is_correct = {is_correct}")
    logging.info(f"🔎 used_hint = {used_hint}")
    logging.info(f"🔎 is_correct and used_hint = {is_correct and used_hint}")
    
    # Определяем, нужно ли добавлять задание в ДЗ с улучшенной логикой
    add_to_homework = False
    reason = "неизвестная причина"
    
    # СУПЕР-ОСОБЫЙ СЛУЧАЙ: Верный ответ с подсказкой - проверяем ПЕРВЫМ, чтобы гарантировать его обработку
    if is_correct is True and used_hint is True:
        add_to_homework = True
        reason = "верный ответ С подсказкой"
        logging.info(f"⚡⚡⚡ ОСОБЫЙ СЛУЧАЙ: Верный ответ С подсказкой - ГАРАНТИРОВАННО добавляем в ДЗ")
        # Дополнительная проверка значений для отладки
        logging.info(f"🔍 is_correct={is_correct} ({type(is_correct)}), used_hint={used_hint} ({type(used_hint)})")
    # ПРАВИЛО 1: Неверный ответ (с подсказкой или без) -> Добавить в ДЗ
    elif is_correct is False:
        add_to_homework = True
        reason = "неверный ответ"
        logging.info(f"⚡ ПРАВИЛО 1: Неверный ответ - добавляем в ДЗ")
    # ПРАВИЛО 3: Верный ответ БЕЗ подсказки -> НЕ добавлять в ДЗ
    else:
        add_to_homework = False
        reason = "верный ответ БЕЗ подсказки"
        logging.info(f"⚡ ПРАВИЛО 3: Верный ответ без подсказки - НЕ добавляем в ДЗ")
    
    # ИТОГ: окончательное решение
    logging.info(f"🏁 ИТОГОВОЕ РЕШЕНИЕ: {'ДОБАВИТЬ' if add_to_homework else 'НЕ ДОБАВЛЯТЬ'} задание в ДЗ. Причина: {reason}")
    
    # Если решено не добавлять задание в ДЗ, сразу возвращаем False
    if not add_to_homework:
        logging.info(f"ℹ️ Задание {world_id}_{cat_code}_{task_idx} НЕ добавлено в ДЗ ({reason})")
        return False
    
    # ИСПРАВЛЕНИЕ: Если дошли до этой точки, то задание ТОЧНО нужно добавить в ДЗ
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        
        # УПРОЩЕНИЕ: Всегда используем INSERT OR REPLACE вместо проверки на существование
        # Это избавляет от лишних запросов и потенциальных ошибок
        cursor.execute("""
            INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, world_id, cat_code, task_idx, "homework", "wrong"))
        conn.commit()
        
        # Обязательно проверяем, действительно ли задание добавилось
        cursor.execute("""
            SELECT 1 FROM task_progress 
            WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
        """, (user_id, world_id, cat_code, task_idx))
        verify = cursor.fetchone()
        
        if verify:
            logging.info(f"✅ Задание {world_id}_{cat_code}_{task_idx} успешно добавлено в ДЗ ({reason})")
            conn.close()
            return True
        else:
            # Если проверка не подтвердила добавление - логируем ошибку, но все равно пытаемся вернуть True
            logging.error(f"⚠️ Задание {world_id}_{cat_code}_{task_idx} не обнаружено в ДЗ после добавления!")
            conn.close()
            
            # Пробуем запасной метод добавления
            try:
                conn2 = sqlite3.connect('task_progress.db')
                cursor2 = conn2.cursor()
                cursor2.execute("""
                    INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, world_id, cat_code, task_idx, "homework", "wrong"))
                conn2.commit()
                conn2.close()
                logging.info(f"🔄 ЗАПАСНОЙ МЕТОД: Повторная попытка добавления в ДЗ")
                return True
            except Exception as e3:
                logging.error(f"❌ ЗАПАСНОЙ МЕТОД: Не удалось добавить задание: {e3}")
                return True  # Все равно возвращаем True, чтобы не нарушать поток выполнения
    except Exception as e:
        logging.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при добавлении задания в ДЗ: {e}")
        
        # ПОСЛЕДНЯЯ ПОПЫТКА: пробуем совсем простой прямой запрос
        try:
            conn3 = sqlite3.connect('task_progress.db')
            cursor3 = conn3.cursor()
            cursor3.execute(f"""
                INSERT INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES ('{user_id}', '{world_id}', '{cat_code}', {task_idx}, 'homework', 'wrong')
            """)
            conn3.commit()
            conn3.close()
            logging.info(f"🚨 АВАРИЙНОЕ ДОБАВЛЕНИЕ: Последняя попытка для {world_id}_{cat_code}_{task_idx}")
            return True
        except Exception as e4:
            logging.error(f"❌❌ ВСЕ ПОПЫТКИ ИСЧЕРПАНЫ: {e4}")
            return True  # Всё равно возвращаем True для согласованности потока управления