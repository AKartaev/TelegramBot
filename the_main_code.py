import telebot
import webbrowser
from telebot import types
import sqlite3
# For sending verification code through email
import smtplib
import os
import random
from email.mime.text import MIMEText


bot = telebot.TeleBot('******')

email = None
code = None
file_path = None

conn = sqlite3.connect('test_bd.sql')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), tg_login varchar(50), email varchar(200))')
conn.commit()

cur.close()
conn.close()

@bot.message_handler(commands = ['start'])
def welcome(message):
    start_valid(message)


def send_email(message):
    global email
    global code
    sender = "***"
    email = message.text.strip()
    code = int(random.random()*10000)
    letter = f'For registration in Mealfit use this cide: {code}'
    # \\your password = "your password"
    #password = os.getenv("EMAIL_PASSWORD")
    password = '***'

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(sender, password)
    msg = MIMEText(letter)
    msg["Subject"] = "Your code for Mealfit"
    server.sendmail(sender, email, msg.as_string())


    bot.reply_to(message, 'На указанный адрес был выслан код. Введите его для подтверждения регистрации (проверьте папку "Спам")')
    bot.register_next_step_handler(message, email_check)


def email_check(message):
    global email
    global code
    if str(code) == message.text.strip():
        bot.reply_to(message, 'Код верный, теперь введите ваше Имя')
        bot.register_next_step_handler(message, user_name_reg)
    else:
        bot.reply_to(message, f'Код неверный, пройдите регистрацию еще раз {code}')
        bot.register_next_step_handler(message, start_valid)

def user_name_reg(message):
    global email
    name = message.text.strip()
    conn = sqlite3.connect('test_bd.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name,email,tg_login) VALUES ('%s','%s','%s')" % (name,email,message.from_user.username))
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id,f'Поздравляю {message.from_user.first_name}, Вы зарегестрированы! Ожидайте дальнейших инструкций, а пока можете ознакомится с продуктом', reply_markup=markup)



def start_valid(message):
    conn = sqlite3.connect('test_bd.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    p = 'необходимо зарегестрироваться'
    file = open('venv/HEALTHY_EATING_ch1.jpg', 'rb')
    for i in users:
            if i[2] == message.from_user.username:
                p = f'Имя:{i[1]}, Логин:{i[2]}, Почта:{i[3]}'
                break
                #bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}{message.from_user.last_name}. Рад тебя приветствовать в нашем сообществе вставших на путь исправления!', reply_markup=markup)
    if p == 'необходимо зарегестрироваться':
        bot.send_photo(message.chat.id, file,caption=f'Привет, {message.from_user.first_name} {message.from_user.last_name}. Рад тебя приветствовать в нашем сообществе вставших на путь исправления!',reply_markup=markup_reg)
    else:
        bot.send_message(message.chat.id, f'С возвращением, {message.from_user.first_name}! Сохраняй мотивацию и не сдавайся!', reply_markup=markup)

    cur.close()
    conn.close()



@bot.message_handler(content_types = ['document'])
def gry_doc(message):
    global file_path
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = os.path.join('****', f'{message.from_user.first_name}_{message.from_user.last_name}_{message.document.file_name}')

    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message,'Спасибо, файл получен ✅', reply_markup=markup2)


@bot.message_handler(content_types = ['photo'])
def gry_photo(message):
    global file_path
    file_id = message.photo[-1].file_id

    file_info = bot.get_file(file_id)

    original_filename, file_extension = os.path.splitext(file_info.file_path)
    original_filename = original_filename.split('/')[-1]

    downloaded_photo = bot.download_file(file_info.file_path)

    file_path = os.path.join('***', f'{message.from_user.first_name}_{message.from_user.last_name}_{original_filename}{file_extension}')

    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_photo)

    bot.reply_to(message,f'Спасибо, файл получен ✅', reply_markup=markup2)


markup_reg = types.InlineKeyboardMarkup()
markup_reg.add(types.InlineKeyboardButton('Зарегестрироваться', callback_data = 'regestration'))
markup_reg.add(types.InlineKeyboardButton('О программе', url = '****'))


markup = types.InlineKeyboardMarkup()
markup.add(types.InlineKeyboardButton('Перейти на сайт', url = '***'))
markup.add(types.InlineKeyboardButton('Записаться на бесплатную консультацию', url = '***'))
markup.add(types.InlineKeyboardButton('Подобрать прогрумму самостоятельно', url = '***'))

markup2 = types.InlineKeyboardMarkup()
markup2.add(types.InlineKeyboardButton('Удалить', callback_data = 'delete'))
markup2.add(types.InlineKeyboardButton('Заменить', callback_data = 'edit'))


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global file_path

    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id-1)
        if os.path.exists(file_path):
            os.remove(file_path)
            bot.reply_to(callback.message, 'Файл удален ❌')
        else:
            bot.reply_to(callback.message, 'Файл не найден, загрузите новый')

    if callback.data == 'edit':
        bot.edit_message_text(callback.message.chat.id, callback.message.message_id)
    if callback.data == 'regestration':
        bot.send_message(callback.message.chat.id, 'Введите полный aдрес электронной почты. Пример: <b>new_user@gmail.com</b>',parse_mode='html')
        bot.register_next_step_handler(callback.message, send_email)


@bot.message_handler()
def any_message(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, я еще не дорос до ChatGPT, поэтому ниже все, что я умею🙃', reply_markup = markup)

bot.polling(none_stop = True)

