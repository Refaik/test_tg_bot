from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Импортируем экраны для квеста
__all__ = ['tasks_screen', 'main_screen', 'contact_screen',
           'task_679_screen', 'task_10_screen', 'task_11_screen', 'task_12_screen',
           'task_45_screen', 'task_8_screen', 'task_1_screen', 'task_2_screen', 'task_3_screen',
           'back_to_task_679_screen', 'back_to_task_8_screen', 'back_to_task_gropCircle_screen',
           'back_to_task_11_screen', 'task_group_trigonometry_screen',
           'back_to_task_group_trigonometry_screen', 'back_to_task_1_screen', 'task_groupCircle_screen',
           'back_to_task_gropTriangles_screen', 'task_groupTriangles_screen', 'task_13_screen',
           'back_to_task_13_screen', 'task13group_trigonometry_screen', 'back_to_task13group_trigonometry_screen',
           'task_15_screen', 'back_to_task_15_screen', 'task_17_screen', 'back_to_task_17_screen',
           'task17groupTriangles_screen', 'back_to_task17gropTriangles_screen', 'back_to_task17gropCircle_screen',
           'task17groupCircle_screen', 'back_to_task17group_trigonometry_screen',
           'task17group_trigonometry_screen', 'math_quest_screen', 'quest_worlds_screen', 'coming_soon_screen',
           'loaded_world_screen', 'quest_profile_screen', 'quest_trophies_screen', 'quest_shop_screen']

#Обработка главного экрана
def main_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📚 Теория", callback_data="theory_call"),
        InlineKeyboardButton("⏰ Study Counter", callback_data="timer_main"),
        InlineKeyboardButton("📘 Метод карточек", callback_data="cards_method_call"),
        InlineKeyboardButton("📖 Варианты", callback_data="quiz_call"),
        InlineKeyboardButton("⚔️ Математический квест", callback_data="mathQuest_call"),
        InlineKeyboardButton("👨‍🏫 Занятия с репетитором", callback_data="tutor_call"),
        InlineKeyboardButton("📞 Контакты", callback_data="contact_call")
    )
    return markup

#Обработка экрана Связь
def contact_screen():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data="main_back_call"))
    return markup

#Обработка экрана Задания
def tasks_screen():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Задание 1", callback_data="task_1_call"),
        InlineKeyboardButton("Задание 2", callback_data="task_2_call"),
        InlineKeyboardButton("Задание 3", callback_data="task_3_call"),
        InlineKeyboardButton("Задание 4, 5", callback_data="task_45_call"),
        InlineKeyboardButton("Задание 6, 7, 9", callback_data="task_679_call"),
        InlineKeyboardButton("Задание 8", callback_data="task_8_call"),
        InlineKeyboardButton("Задание 10", callback_data="task_10_call"),
        InlineKeyboardButton("Задание 11", callback_data="task_11_call"),
        InlineKeyboardButton("Задание 12", callback_data="task_12_call"),
        InlineKeyboardButton("Задание 13", callback_data="task_13_call"),
        InlineKeyboardButton("Задание 14", callback_data="task_14_call"),
        InlineKeyboardButton("Задание 15", callback_data="task_15_call"),
        InlineKeyboardButton("Задание 16", callback_data="task_16_call"),
        InlineKeyboardButton("Задание 17", callback_data="task_17_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="theory_call")
)
    return markup

#Обработка экрана 1 Задания
def task_1_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Углы", callback_data="task_angles_call"),
        InlineKeyboardButton("Треугольники", callback_data="task_groupTriangles_call"),
        InlineKeyboardButton("Биссектриса, медиана", callback_data="task_triangle_lines_call"),
        InlineKeyboardButton("Параллелограмм", callback_data="task_parallelogram_call"),
        InlineKeyboardButton("Ромб и Трапеция", callback_data="task_rhombus_trapezoid_call"),
        InlineKeyboardButton("Равносторонний шестиугольник", callback_data="task_regular_hexagon_call"),
        InlineKeyboardButton("Окружность", callback_data="task_groupCircle_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup
#Обработка Окружности
def task_groupCircle_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Окружность №1", callback_data="task_circle_1_call"),
        InlineKeyboardButton("Окружность №2", callback_data="task_circle_2_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_1_call")
    )
    return markup
#Обработка Треугольники
def task_groupTriangles_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Треугольник", callback_data="task_triangle_call"),
        InlineKeyboardButton("Равенство/Подобие треугольников", callback_data="task_triangle_similarity_call"),
        InlineKeyboardButton("Прямоугольный треугольник", callback_data="task_right_triangle_call"),
        InlineKeyboardButton("Равнобедренный/Равносторонний треугольник",callback_data="task_isosceles_equilateral_triangle_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_1_call")
    )
    return markup
# Обработка возврат Окружности
def back_to_task_gropCircle_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="back_to_task_gropCircle_call")
    )
    return markup
# Обработка возврат Треугольники
def back_to_task_gropTriangles_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="back_to_task_gropTriangles_call")
    )
    return markup
#Обработка возврат в задания 1
def back_to_task_1_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_1_call")
    )
    return markup

#Обработка экрана 2 Задания
def task_2_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup

#Обработка экрана 3 Задания
def task_3_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        #InlineKeyboardButton("Куб", callback_data="task_cube_call"),
        #InlineKeyboardButton("Параллелепипед", callback_data="task_parallelepiped_call"),
        #InlineKeyboardButton("Цилиндр", callback_data="task_cylinder_call"),
        #InlineKeyboardButton("Конус", callback_data="task_cone_call"),
        #InlineKeyboardButton("Пирамида", callback_data="task_pyramid_call"),
        #InlineKeyboardButton("Шар", callback_data="task_sphere_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup

#Обработка экрана 4,5 Задания
def task_45_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup

#Обработка экрана 6,7,9 Задания
def task_679_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Формулы Сокращённого Умножения", callback_data="task_fsu_call"),
        InlineKeyboardButton("Квадратные уравнения", callback_data="task_quadratic_equations_call"),
        InlineKeyboardButton("Степени", callback_data="task_powers_call"),
        InlineKeyboardButton("Корни", callback_data="task_roots_call"),
        InlineKeyboardButton("Тригонометрия", callback_data="task_group_trigonometry_call"),
        InlineKeyboardButton("Логарифмы", callback_data="task_logarithms_call"),
        InlineKeyboardButton("Модули", callback_data="task_modules_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup
#Обработка возврат в задания 6,7,9
def back_to_task_679_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_679_call")
    )
    return markup
# Обработка экрана "Задания Тригонометрия"
def task_group_trigonometry_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Тригонометрическая окружность", callback_data="task_trigonometric_circle_call"),
        InlineKeyboardButton("Определения", callback_data="task_definitions_call"),
        InlineKeyboardButton("Тригонометрические формулы", callback_data="task_trigonometric_formulas_call"),
        InlineKeyboardButton("Формулы приведения", callback_data="task_reduction_formulas_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_679_call")
    )
    return markup
#Обработка возврат в Группу тригонометрия
def back_to_task_group_trigonometry_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="trigonometryTaskBack_call")
    )
    return markup

#Обработка экрана 8 Задания
def task_8_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Обычная функция/Производная", callback_data="task_usual_function_and_derivative_call"),
        InlineKeyboardButton("Производная", callback_data="task_8_derivatives_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup
#Обработка возврат в задания 8
def back_to_task_8_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_8_call")
    )
    return markup

#Обработка экрана 10 Задания
def task_10_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup

#Обработка экрана 11 Задания
def task_11_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Прямая", callback_data="task_direct_call"),
        InlineKeyboardButton("Парабола", callback_data="task_parabola_call"),
        InlineKeyboardButton("Гипербола", callback_data="task_hyperbola_call"),
        InlineKeyboardButton("Функция Корня", callback_data="task_root_function_call"),
        InlineKeyboardButton("Показательная функция", callback_data="task_exponential_function_call"),
        InlineKeyboardButton("Логарифмическая функция", callback_data="task_logarithmic_function_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup
#Обработка возврат в задания 11
def back_to_task_11_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_11_call")
    )
    return markup

#Обработка экрана 12 Задания
def task_12_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup

#Обработка экрана 13 Задания
def task_13_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Тригонометрия", callback_data="tasks13trigGroup_call"),
        InlineKeyboardButton("Логарифмы", callback_data="tasks13log_call"),
        InlineKeyboardButton("Корни", callback_data="tasks13root_call"),
        InlineKeyboardButton("Степени", callback_data="tasks13powers_call"),
        InlineKeyboardButton("Формулы сокращённого умножения", callback_data="tasks13fcy_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup
# Обработка экрана "Задания Тригонометрия"
def task13group_trigonometry_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Тригонометрическая окружность", callback_data="task13trigonometric_circle_call"),
        InlineKeyboardButton("Определения", callback_data="task13definitions_call"),
        InlineKeyboardButton("Тригонометрические формулы", callback_data="task13trigonometric_formulas_call"),
        InlineKeyboardButton("Формулы приведения", callback_data="task13reduction_formulas_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_13_call")
    )
    return markup
#Обработка возврат 13 задания
def back_to_task_13_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_13_call")
    )
    return markup
#Обработка возврат в Группу тригонометрия 13
def back_to_task13group_trigonometry_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="trigonometryTaskBack_13_call")
    )
    return markup

#Обработка экрана 15 Задания
def task_15_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup
#Обработка возврат в задания 15
def back_to_task_15_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_15_call")
    )
    return markup

#Обработка экрана 17 Задания
def task_17_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Треугольники", callback_data="task17_groupTriangles_call"),
        InlineKeyboardButton("Окружность", callback_data="task17_groupCircle_call"),
        InlineKeyboardButton("Тригонометрия", callback_data="task17_group_trigonometry_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="tasksBack_call")
    )
    return markup
#Обработка возврат в задания 17
def back_to_task_17_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_17_call")
    )
    return markup
# Обработка экрана "Задания Triangle"
def task17groupTriangles_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        #InlineKeyboardButton("Обычный треугольник", callback_data="task17triangle_call"),
        #InlineKeyboardButton("Прямоугольный треугольник", callback_data="task17right_triangle_call"),
        #InlineKeyboardButton("Вписанный/Описанный треугольник", callback_data="task17inscribed_circumscribed_triangle_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_17_call")
    )
    return markup
#Обработка возврат 17 Треугольник
def back_to_task17gropTriangles_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="back_to_task17gropTriangles_call")
    )
    return markup

# Обработка экрана "Задания Circle"
def task17groupCircle_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        #InlineKeyboardButton("Свойства окружности", callback_data="task17circle_property_call"),
        #InlineKeyboardButton("Касательная к окружности", callback_data="task17circle_tangent_call"),
        #InlineKeyboardButton("Площадь круга", callback_data="task17circle_area_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_17_call")
    )
    return markup
#Обработка возврат 17 Circle
def back_to_task17gropCircle_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="back_to_task17gropCircle_call")
    )
    return markup

# Обработка экрана "Задания Тригонометрия 17"
def task17group_trigonometry_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        #InlineKeyboardButton("Тригонометрическая окружность", callback_data="task17trigonometric_circle_call"),
        #InlineKeyboardButton("Определения", callback_data="task17definitions_call"),
        #InlineKeyboardButton("Тригонометрические формулы", callback_data="task17trigonometric_formulas_call"),
        #InlineKeyboardButton("Формулы приведения", callback_data="task17reduction_formulas_call"),
        InlineKeyboardButton("◀️ Назад", callback_data="taskBack_17_call")
    )
    return markup
#Обработка возврат в Группу тригонометрия 17
def back_to_task17group_trigonometry_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("◀️ Назад", callback_data="back_to_task17group_trigonometry_call")
    )
    return markup

# ================== Математический квест ==================
# Обработка главного экрана математического квеста
def math_quest_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🌀 Выбор мира", callback_data="quest_select_world"),
        InlineKeyboardButton("👤 Профиль героя", callback_data="quest_profile"),
        InlineKeyboardButton("🏆 Хранилище трофеев", callback_data="quest_trophies"),
        InlineKeyboardButton("👕 Лавка скинов", callback_data="quest_shop"),
        InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call")
    )
    return markup

# Обработка экрана выбора мира
def quest_worlds_screen(current_index=0, total_worlds=0):
    markup = InlineKeyboardMarkup(row_width=3)
    
    # Навигационные кнопки для перемещения между мирами
    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"quest_world_prev_{current_index}"))
    else:
        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_world_none"))
        
    nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_worlds}", callback_data="quest_world_none"))
    
    if current_index < total_worlds - 1:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"quest_world_next_{current_index}"))
    else:
        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_world_none"))
    
    markup.row(*nav_buttons)
    
    # Кнопка для входа в мир
    markup.add(InlineKeyboardButton("🚪 Войти в мир", callback_data=f"quest_enter_world_{current_index}"))
    
    # Добавляем кнопку избранного
    markup.add(InlineKeyboardButton("⭐️ Избранное", callback_data="quest_favorites"))
    
    # Кнопка возврата в меню квеста (не в главное меню)
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_call"))
    
    return markup

# Экран профиля героя
def quest_profile_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_call")
    )
    return markup

# Экран хранилища трофеев
def quest_trophies_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_call")
    )
    return markup

# Экран лавки скинов
def quest_shop_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_call")
    )
    return markup

# Экран "Coming Soon"
def coming_soon_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_call")
    )
    return markup

# Экран после загрузки мира
def loaded_world_screen(world_id):
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Новые кнопки в соответствии с обновлённым порядком
    markup.add(
        InlineKeyboardButton("📖 Книга знаний", callback_data=f"quest_theory_{world_id}")
    )
    
    markup.add(
        InlineKeyboardButton("⚔️ Квесты", callback_data=f"quest_task_list_{world_id}")
    )
    
    markup.add(
        InlineKeyboardButton("🕯️ Ритуал повторения", callback_data="quest_homework")
    )
    
    markup.add(
        InlineKeyboardButton("📜 Карта прогресса", callback_data="quest_empty")
    )
    
    # Кнопка возврата к выбору миров
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data="quest_back_to_worlds")
    )
    
    return markup
