import os
import re
from datetime import datetime
from datetime import timedelta
import telebot
from telebot import types
import ploterWork as ploter
import personalSettings as ps
# in ps store bot token and
# id with which the bot works
bot = telebot.TeleBot(ps.token)
# use pyTelegramBotAPI
print('start')

def recognazeCustomer(message):
    canWork = False
    for key, value in ps.availableId.items():
        if (value == message.from_user.id):
            canWork = True
            break
    if(canWork!=True):
        bot.send_message(message.chat.id, "вы не можете пользоваться данным ботом")
    return canWork

@bot.message_handler(commands=['start', 's'])
def send_welcome(message):
    if(recognazeCustomer(message)):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        item1 = types.KeyboardButton('график за все даты\n(с нормализацией)')
        item6 = types.KeyboardButton('график за все даты\n(без нормализации)')
        item2 = types.KeyboardButton('график за последнию неделю')
        item3 = types.KeyboardButton('график за последний месяц')
        item4 = types.KeyboardButton('график за кастомный диапазон')
        item5 = types.KeyboardButton('очистить список')
        item7= types.KeyboardButton('удалить последний')
        markup.add(item1,item6, item3, item2, item4, item5,item7)
        print(message)
        print(message.from_user.id)
        bot.send_message(message.chat.id, "при вводе числа(1, 2, 1.5, 8.56) оно добавится в список\n",
                     reply_markup=markup)


def customDateRangeForGraphic(message):
    result1 = re.fullmatch(r'\d{1,2}[.]\d{1,2}[.]\d{2},\d{1,2}[.]\d{1,2}[.]\d{2}', message.text)
    result2 = re.fullmatch(r'\d{1,2}[.]\d{1,2}[.]\d{2}', message.text)
    if (result1 == None and result2 == None):
        bot.send_message(message.chat.id, "вы ввели неверные данные проверьте их и попробуйте снова")
    elif (result1 != None and result2 == None):
        firstDateStrFormatting = datetime.strptime(message.text.split(',')[0], "%d.%m.%y").date().strftime("%d.%m.%y")
        secondDateStrFormatting = datetime.strptime(message.text.split(',')[1], "%d.%m.%y").date().strftime("%d.%m.%y")
        firstDate = datetime.strptime(message.text.split(',')[0], "%d.%m.%y")
        secondDate = datetime.strptime(message.text.split(',')[1], "%d.%m.%y")
        if ((secondDate - firstDate).days >= 0):
            ploter.createAndSaveGraphic(firstDateStrFormatting + ',' + secondDateStrFormatting)
            bot.send_photo(message.chat.id, open('graphic.png', 'rb'))
            os.remove('graphic.png')
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            itembtn1 = types.InlineKeyboardButton('поменять даты местами',
                                                  callback_data=firstDateStrFormatting + ',' + secondDateStrFormatting)
            markup.add(itembtn1)
            bot.send_message(message.chat.id, "вы перепутали даты местами\n", reply_markup=markup)
        return 0
    elif (result2 != None and result1 == None):
        firstDateStrFormatting = datetime.strptime(message.text, "%d.%m.%y").date().strftime("%d.%m.%y")
        ploter.createAndSaveGraphic(firstDateStrFormatting)
        bot.send_photo(message.chat.id, open('graphic.png', 'rb'))
        os.remove('graphic.png')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if (recognazeCustomer(call.message)):
        ploter.createAndSaveGraphic(call.data.split(',')[1] + ',' + call.data.split(',')[0])
        bot.send_photo(call.message.chat.id, open('graphic.png', 'rb'))
        os.remove('graphic.png')

def whoIAm(message):
    for key, value in ps.availableId.items():
        if (value == message.from_user.id):
            bot.send_message(message.chat.id,'you '+key)
            break

@bot.message_handler(content_types=['text'])
def buttonsRecognize(message):
    if (recognazeCustomer(message)):
        if (message.text == 'график за все даты\n(с нормализацией)'):
            sendGraphicFull(message,True)
        elif (message.text == 'график за все даты\n(без нормализации)'):
            sendGraphicFull(message,False)
        elif (message.text == 'очистить список'):
            clearDataFile(message)
        elif (message.text == 'удалить последний'):
            clearLast(message)
        elif (message.text == 'график за кастомный диапазон'):
            bot.send_message(message.chat.id, 'введите дату в формате\n'
                                              'с даты А по дату Б \n'
                                              '\'1.1.22,1.1.22\'\n'
                                              '\'1.01.22,01.1.22\'\n'
                                              '\'01.01.22,01.01.22\''
                                              'с даты А по сегодняшнюю\n'
                                              '\'01.01.22\''
                                              '\'1.1.22\''
                                              '\'1.01.22\''
                                              '')
            bot.register_next_step_handler(message, customDateRangeForGraphic)
        elif (message.text == 'график за последнию неделю'):
            sendGraphicLastWeek(message)
        elif (message.text == 'график за последний месяц'):
            sendGraphicLastMounth(message)
        elif (message.text == 'who I am?'):
            whoIAm(message)
        else:
            command = message.text
            try:
                float(command)
                addToDataFile(command)
            except Exception:
                str(command)


def sendGraphicLastWeek(message):
    currentDate = datetime.now()
    while (datetime.weekday(currentDate) != 0):
        currentDate = currentDate - timedelta(days=1)
    ploter.createAndSaveGraphic(currentDate.strftime("%d.%m.%y"))
    bot.send_photo(message.chat.id, open('graphic.png', 'rb'))
    os.remove('graphic.png')


def sendGraphicLastMounth(message):
    ploter.createAndSaveGraphic(('01' + getCurrentDate()[2:]))
    bot.send_photo(message.chat.id, open('graphic.png', 'rb'))
    os.remove('graphic.png')


def sendGraphicFull(message,needNormal):
    ploter.createAndSaveGraphic(dateRange='',needNormal=needNormal)
    bot.send_photo(message.chat.id, open('graphic.png', 'rb'))
    os.remove('graphic.png')


def getCurrentDate():
    today = datetime.today()
    # mm/dd/y
    return str(today.strftime("%d.%m.%y"))


def buildGraphic(message):
    ploter.createAndSaveGraphic()
    os.system('ploterWork.py')


def clearDataFile(message):
    f = open('coordinatesXY', 'w')
    f.write("")
    f.close()
    bot.send_message(message.chat.id, 'лист очищен')

def clearLast(message):
    f = open('coordinatesXY', 'r')
    data=f.read();
    f.close()
    data=data.split(('\n'))
    data.pop(len(data)-2)
    data='\n'.join(data)
    f = open('coordinatesXY', 'w')
    f.write(data)
    f.close()
    bot.send_message(message.chat.id, 'последний элемент листа удален')

def addToDataFile(data):
    f = open('coordinatesXY', 'r')
    coordinates = f.read().split('\n')
    coordinates.pop()
    f.close()
    countRepitDate = int(0)
    for i in coordinates:
        if (i.split(',')[0].startswith(getCurrentDate())):
            countRepitDate += 1
    dataLine = getCurrentDate()
    if (countRepitDate != 0):
        dataLine += '(' + str(countRepitDate) + ')'
    dataLine += ',' + str(data)
    f = open('coordinatesXY', 'a')
    f.write(str(dataLine) + '\n')
    f.close()


bot.infinity_polling()
