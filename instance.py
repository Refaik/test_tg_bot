from telebot import TeleBot
import os
from dotenv import load_dotenv


load_dotenv()
API_TOKEN = os.getenv("TOKEN")

if not API_TOKEN:
    raise ValueError("Токен не найден в файле .env")

bot = TeleBot(API_TOKEN)
photo_challenge = "https://i.imgur.com/WbDe7kx.jpg"
photo_trigonometry = "https://i.imgur.com/cVtpYkw.jpg"
photo_contact = "https://i.imgur.com/YARI6Jj.jpg"
photo = "https://i.imgur.com/cVtpYkw.jpg"
photo_arithmetic_progression = "https://i.imgur.com/vE5ZaGj.jpg" #Фото Арифметическая прогрессия -
photo_definition = "https://i.imgur.com/qjsaqlQ.jpg" #Фото Определение тригонометрических функций +
photo_trigonometric_circle = "https://i.imgur.com/Skw4dNM.jpg" #Фото тригонометрическая окружность +
photo_reduction_formulas = "https://i.imgur.com/O9MvRFF.jpg" #Фото формулы приведения +
photo_trigonometric_formulas = "https://i.imgur.com/AhkzrAH.jpg" #Фото тригонометрические формулы
photo_logarithms = "https://i.imgur.com/wFRwzZK.jpg" #Фото Логарифмов +
photo_derivatives = "https://i.imgur.com/QUo6GqX.jpg" #Фото Производные +
photo_powers = "https://i.imgur.com/SuSkA9C.jpg" #Фото Степени +
photo_roots = "https://i.imgur.com/TegZH8T.jpg" #Фото Корней -
photo_fsy = "https://i.imgur.com/VF49Qs9.jpg" #Фото ФСУ +
photo_modules = "https://i.imgur.com/qPbUQrP.jpg" #Фото Модулей +
photo_task14 = "https://i.imgur.com/g2PsTWB.jpg" #Фото для 14 задания
photo_task16 = "https://i.imgur.com/OkhZnez.jpg" #Фото для 16 задания
photo_rationalization = "https://i.imgur.com/piKhRwS.jpg" #Фото Метод рационализации
photo_quest = "https://i.imgur.com/tNzUW93.jpg" #Фото для главного меню квеста
# Фото для квеста (в разработке) - теперь используется photo_quest_coming_soon ниже
# (удалены дубликаты, используются переменные ниже)
photo_8 = "https://i.imgur.com/pza5UvH.jpg" #Фото Задание №8 -
photo_triangle_lines = "https://i.imgur.com/53JXn4h.jpg" #Фото Биссектриса, медиана, серединный перпендикуляр -
photo_angles = "https://i.imgur.com/YMxqnoh.jpg" #Фото Углы -
photo_triangle_equality = "https://i.imgur.com/bxNbWuQ.jpg" #Фото Признаки равенства треугольников -
photo_triangles = "https://i.imgur.com/VaAxB6W.jpg" #Фото Треугольник -
photo_right_triangle = "https://i.imgur.com/fh6mq6W.jpg" #Фото Прямоугольный треугольник -
photo_isosceles_triangle = "https://i.imgur.com/cgmG6aZ.jpg" #Фото Равнобедренный треугольник -
photo_equilateral_triangle = "https://i.imgur.com/ZtDSPM1.jpg" #Фото Равносторонний треугольник -
photo_similarity = "https://i.imgur.com/ZGwyWoP.jpg" #Фото Подобие
photo_parallelogram = "https://i.imgur.com/x3WltCj.jpg" #Фото Параллелограмм
photo_rhombus = "https://i.imgur.com/pDJkt43.jpg" #Фото Ромб
photo_trapezoid = "https://i.imgur.com/E2Y0BT3.jpg" #Фото Трапеция
photo_circle = "https://i.imgur.com/ziiLjSo.jpg" #Фото Окружность
photo_hexagon = "https://i.imgur.com/1Z5DbMb.jpg" #Фото Равносторонний шестиугольник
photo_ptolemy_menelaus_ceva_theorems = "https://i.imgur.com/DMYcVch.jpg" #Фото Теоремы Птолемея, Менелая, Чевы
photo_arbitrary_triangle = "https://i.imgur.com/GvLk8b8.jpg" #Фото Произвольный треугольник
photo_quadratic_equations = "https://i.imgur.com/pdEAENp.jpg" #Фото Квадратные уравнения +
photo_direct = "https://i.imgur.com/uVbAHV9.jpg" #Фото Прямая
photo_parabola = "https://i.imgur.com/PpEUZ5j.jpg" #Фото Парабола
photo_hyperbola = "https://i.imgur.com/asvg3q1.jpg" #Фото Гипербола
photo_root_function = "https://i.imgur.com/FqiBjmM.jpg" #Фото Функция Корня
photo_exponential_function = "https://i.imgur.com/8a00Pxf.jpg" #Фото Показательная функция
photo_logarithmic_function = "https://i.imgur.com/Zd4U0l0.jpg" #Фото Логарифмическая функция
photo_main = "https://i.imgur.com/aqiS2ps.jpg" #Фото Главного экрана
photo_task45 = "https://i.imgur.com/D4JTXwG.jpg" #Фото для заданий 4,5
photo_task10 = "https://i.imgur.com/plp3NLk.jpg" #Фото для 10 задания
photo_task2 = "https://i.imgur.com/Rwak2qb.jpg" #Фото для 2 задания
photo_task12 = "https://i.imgur.com/QUo6GqX.jpg" #Фото для 12 задания
photo_task3 = "https://i.imgur.com/0bxJxCS.jpg" #Фото для 3 задания
photo_task81 = "https://i.imgur.com/q1NDfsA.jpg" #Фото для 8,1 задания
photo_task82 = "https://i.imgur.com/yNbtJT9.jpg" #Фото для 8,2 задания
photo_task_triangle_lines = "https://i.imgur.com/jI5ltfc.jpg" #Фото для биссектрисы задания
photo_task_right_triangle = "https://i.imgur.com/QKgRA2H.jpg" #Фото для прямоугольного треугольника задания
photo_task_isosceles_equilateral_triangle = "https://i.imgur.com/CtjjIH3.jpg" #Фото для равнобедренного треугольник задания
photo_task_triangle_similarity = "https://i.imgur.com/C8VNkUN.jpg" #Фото для triangle_similarity задания
photo_task_triangle = "https://i.imgur.com/qpoWcQ3.jpg" #Фото для треугольника задания
photo_task_circle_1 = "https://i.imgur.com/QeypL5c.jpg" #Фото для окружности 1
photo_task_circle_2 = "https://i.imgur.com/01YBArJ.jpg" #Фото для окружности 2
photo_task_parallelogram = "https://i.imgur.com/7GdpSZA.jpg" #Фото для Параллелограмма задания
photo_task_regular_hexagon = "https://i.imgur.com/T6ZDJbx.jpg" #Фото для Равностороннего шестиугольника задания
photo_task_rhombus_trapezoid = "https://i.imgur.com/cSwZmMd.jpg" #Фото для Ромба и Трапеция задания
photo_task_angles = "https://i.imgur.com/c5FtPu7.jpg" #Фото для Углов задания
photo_tasks = "https://i.imgur.com/gFvyND2.jpg"
photo_cards = "https://i.imgur.com/cNxZul1.jpg"
photo_timers = "https://i.imgur.com/VEf3aNe.jpg"
photo_quize = "https://i.imgur.com/xb9wecj.jpg"
photo_quest_main = "https://i.imgur.com/tNzUW93.jpg" # Фото для главного экрана квеста
photo_quest_worlds = "https://imgur.com/dOEwecR.jpg" # Фото для недоступных миров (Coming soon)
photo_quest_profile = "https://imgur.com/PUDxjbd.jpg" # Фото для профиля героя
photo_quest_trophies = "https://imgur.com/slKz5ON.jpg" # Фото для хранилища трофеев
photo_quest_shop = "https://imgur.com/PPkL6cO.jpg" # Фото для лавки скинов
photo_quest_coming_soon = "https://i.imgur.com/JPGSypH.jpg" # Фото для заглушки "Coming soon"
photo_quest_ritual = "https://i.imgur.com/ywuoCTd.jpg" # Фото для ритуала повторения (домашних заданий)
photo_quest_quests = "https://imgur.com/eW70oce.jpg" # Фото для квестов
photo_quest_book = "https://imgur.com/SlKzoNt.jpg" # Фото для книги знаний

# Фотографии для домашних заданий (используются ссылки на соответствующие задачи, но с модификацией)
photo_homework_linear = "https://i.imgur.com/h5aUj2B.jpg" # Фото для домашней работы по линейным уравнениям
photo_homework_quadratic = "https://i.imgur.com/GdfR8sK.jpg" # Фото для домашней работы по квадратным уравнениям
photo_homework_rational = "https://i.imgur.com/b1pNjxT.jpg" # Фото для домашней работы по рациональным уравнениям
photo_homework_irrational = "https://i.imgur.com/7qZeVsW.jpg" # Фото для домашней работы по иррациональным уравнениям
photo_homework_exponential = "https://i.imgur.com/m3wFp4L.jpg" # Фото для домашней работы по показательным уравнениям
photo_homework_logarithmic = "https://i.imgur.com/xY9tPqB.jpg" # Фото для домашней работы по логарифмическим уравнениям
