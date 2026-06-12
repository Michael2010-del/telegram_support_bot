
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import re

# Импортируем модули
from database import init_db, add_request, get_all_requests, update_request_status, get_requests_by_department
from faq_data import find_answer, get_faq_list


BOT_TOKEN = ""

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Инициализируем базу данных при запуске
init_db()

# Клавиатуры и кнопки

def get_main_keyboard():
    """Главная клавиатура с кнопками"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("Частые вопросы"),
        KeyboardButton("Связаться с поддержкой")
    )
    keyboard.add(
        KeyboardButton("Программисты"),
        KeyboardButton("Отдел продаж")
    )
    keyboard.add(
        KeyboardButton("Информация о магазине")
    )
    return keyboard

def get_faq_keyboard():
    """Клавиатура с часто задаваемыми вопросами"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton("Как оформить заказ"),
        KeyboardButton("Статус заказа"),
        KeyboardButton("Отменить заказ"),
        KeyboardButton("Поврежденный товар"),
        KeyboardButton("Техподдержка"),
        KeyboardButton("Доставка"),
        KeyboardButton("Возврат товара"),
        KeyboardButton("Как оплатить")
    )
    keyboard.add(KeyboardButton("Назад в главное меню"))
    return keyboard

def get_admin_keyboard():
    """Клавиатура для администратора (скрытая команда)"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("Все запросы"),
        KeyboardButton("Запросы к программистам"),
        KeyboardButton("Запросы к продажам"),
        KeyboardButton("Назад в главное меню")
    )
    return keyboard

# Обработчики команд

@bot.message_handler(commands=['start'])
def start(message):
    """Приветственное сообщение"""
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"*Здравствуйте, {user_name}!*\n\n"
        f"Добро пожаложаловать в службу поддержки интернет-магазина *Продаем все на свете!* \n\n"
        f"Я помогу вам:\n"
        f"• Найти ответы на частые вопросы\n"
        f"• Связаться с нужным специалистом\n"
        f"• Решить вашу проблему\n\n"
        f"*Выберите действие на кнопках ниже*"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    """Скрытая команда /admin для администраторов"""
    # Проверяем, что это администратор 
    admin_ids = [123456789]  
    
    if message.from_user.id in admin_ids:
        bot.send_message(
            message.chat.id,
            "*Панель администратора*\n\nВыберите действие:",
            parse_mode="Markdown",
            reply_markup=get_admin_keyboard()
        )
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде!")

# Обработчик текстовых сообщений

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обрабатывает все текстовые сообщения"""
    text = message.text
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Главное меню
    if text == "Частые вопросы":
        bot.send_message(
            message.chat.id,
            "*Часто задаваемые вопросы*\n\nВыберите интересующий вас вопрос:",
            parse_mode="Markdown",
            reply_markup=get_faq_keyboard()
        )
    
    elif text == "Связаться с поддержкой":
        bot.send_message(
            message.chat.id,
            "*Как с нами связаться:*\n\n"
            "• Напишите 'Программисты' - если проблема с сайтом или оплатой\n"
            "• Напишите 'Отдел продаж' - если проблема с товаром\n"
            "• Или просто опишите вашу проблему, и я перенаправлю вас к нужному специалисту",
            parse_mode="Markdown"
        )
    
    # Отделы
    elif text == "Программисты":
        bot.send_message(
            message.chat.id,
            "*Отдел программистов*\n\n"
            "Опишите вашу проблему (сайт не работает, ошибка оплаты и т.д.), "
            "и я передам ваш запрос специалистам.\n\n"
            "Например: *'Не могу войти в личный кабинет'*",
            parse_mode="Markdown"
        )
        # Устанавливаем состояние ожидания проблемы
        bot.register_next_step_handler(message, handle_programmer_request)
    
    elif text == "Отдел продаж":
        bot.send_message(
            message.chat.id,
            "*Отдел продаж*\n\n"
            "Опишите вашу проблему с товаром (повреждение, брак, возврат и т.д.), "
            "и я передам ваш запрос нашим менеджерам.\n\n"
            "Например: *'Товар пришел с царапиной'*",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(message, handle_sales_request)
    
    # FAQ вопросы
    elif text == "Как оформить заказ":
        answer = find_answer("как оформить заказ")
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    
    elif text == "Статус заказа":
        answer = find_answer("статус заказа")
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    
    elif text == "Отменить заказ":
        answer = find_answer("отменить заказ")
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    
    elif text == "Поврежденный товар":
        answer = find_answer("товар пришел поврежденным")
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    
    elif text == "Техподдержка":
        answer = find_answer("техническая поддержка")
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    
    elif text == "Доставка":
        answer = find_answer("доставка")
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    
    elif text == "Возврат товара":
        answer = find_answer("возврат товара")
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    
    elif text == "Как оплатить":
        answer = find_answer("как оплатить")
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    
    # Информация
    elif text == "Информация о магазине":
        info_text = (
            "*О магазине 'Продаем все на свете'*\n\n"
            " Работаем с 2015 года\n"
            "Более 10 000 довольных клиентов\n"
            "Доставка по всей стране\n"
            "Онлайн-оплата и наличные\n\n"
            "Наш сайт: www.shop_we sell everything in the world.ru\n"
            "Горячая линия: 8-800-123-45-67"
        )
        bot.send_message(message.chat.id, info_text, parse_mode="Markdown")
    
    # Возврат в главное меню
    elif text == "Назад в главное меню":
        bot.send_message(
            message.chat.id,
            "*Главное меню*\n\nВыберите действие:",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    
    # Админская панель
    elif text == "Все запросы":
        show_all_requests(message)
    
    elif text == "Запросы к программистам":
        show_requests_by_department(message, "программисты")
    
    elif text == "Запросы к продажам":
        show_requests_by_department(message, "продажи")
    
    # Произвольный вопрос или FAQ
    else:
        # Ищем ответ в FAQ
        answer = find_answer(text)
        if answer:
            bot.send_message(message.chat.id, answer, parse_mode="Markdown")
            bot.send_message(
                message.chat.id,
                "Нужна еще помощь? Нажмите 'Частые вопросы' или свяжитесь со специалистом.",
                reply_markup=get_main_keyboard()
            )
        else:
            # Если не нашли в FAQ, предлагаем обратиться к специалисту
            bot.send_message(
                message.chat.id,
                "Я не уверен, что могу ответить на этот вопрос.\n\n"
                "Пожалуйста, выберите отдел для связи:\n"
                "• 'Программисты' - проблемы с сайтом/оплатой\n"
                "• 'Отдел продаж' - проблемы с товаром",
                reply_markup=get_main_keyboard()
            )

# Обработчик запросов к специалистам

def handle_programmer_request(message):
    """Обрабатывает запрос к программистам"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    question = message.text
    
    # Сохраняем в базу данных
    add_request(user_id, user_name, "программисты", question)
    
    bot.send_message(
        message.chat.id,
        "*Ваш запрос передан программистам!*\n\n"
        f"Текст запроса: *{question}*\n\n"
        "Специалисты свяжутся с вами в ближайшее время.\n"
        "Статус запроса можно отследить у администратора.",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    
    # Уведомление администратора 
    admin_ids = [123456789]  
    for admin_id in admin_ids:
        bot.send_message(
            admin_id,
            f"*Новый запрос к ПРОГРАММИСТАМ!*\n\n"
            f"Пользователь: {user_name} (ID: {user_id})\n"
            f"Вопрос: {question}\n"
            f"Время: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Для просмотра всех запросов используйте /admin",
            parse_mode="Markdown"
        )

def handle_sales_request(message):
    """Обрабатывает запрос к отделу продаж"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    question = message.text
    
    # Сохраняем в базу данных
    add_request(user_id, user_name, "продажи", question)
    
    bot.send_message(
        message.chat.id,
        "*Ваш запрос передан в отдел продаж!*\n\n"
        f"Текст запроса: *{question}*\n\n"
        "Наши менеджеры свяжутся с вами в ближайшее время.",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    
    # Уведомление администратора
    admin_ids = [123456789]
    for admin_id in admin_ids:
        bot.send_message(
            admin_id,
            f"*Новый запрос в ОТДЕЛ ПРОДАЖ!*\n\n"
            f"Пользователь: {user_name} (ID: {user_id})\n"
            f"Вопрос: {question}\n"
            f"Время: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )

# Админские функции

def show_all_requests(message):
    """Показывает все запросы из базы данных"""
    requests = get_all_requests()
    
    if not requests:
        bot.send_message(message.chat.id, "Пока нет ни одного запроса.")
        return
    
    for req in requests[:10]:  # Показывает последние 10
        req_text = (
            f"ID: {req[0]}\n"
            f"Пользователь: {req[2]}\n"
            f"Отдел: {req[3]}\n"
            f"Вопрос: {req[4]}\n"
            f"Статус: {req[5]}\n"
            f"Дата: {req[6]}\n"
            f"{'-'*30}"
        )
        bot.send_message(message.chat.id, req_text)

def show_requests_by_department(message, department):
    """Показывает запросы по отделу"""
    requests = get_requests_by_department(department)
    
    dept_name = "ПРОГРАММИСТАМ" if department == "программисты" else "ПРОДАЖИ"
    
    if not requests:
        bot.send_message(message.chat.id, f"Нет запросов к {dept_name}.")
        return
    
    bot.send_message(message.chat.id, f"*Запросы к {dept_name}:*", parse_mode="Markdown")
    
    for req in requests[:5]:  # Показывает последние 5
        req_text = (
            f"ID: {req[0]}\n"
            f"{req[2]}: {req[4]}\n"
            f"Статус: {req[5]}\n"
        )
        bot.send_message(message.chat.id, req_text)

# Запуск бота
if __name__ == "__main__":
    print("ВСЕ ОК И /admin")
    bot.infinity_polling()