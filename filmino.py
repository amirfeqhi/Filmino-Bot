import json
import sys
import time

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import (
        InlineKeyboardMarkup, InlineKeyboardButton, ForceReply)
import urllib3


bot_token = 'Telegram-Bot-Token'
bot = telepot.Bot(bot_token)

omdb_token = 'Omdb-Token'
markup = None

print('Listening...')

def on_chat_message(msg):
    global markup
    content_type, chat_type, chat_id = telepot.glance(msg)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='جستجو', 
                                    callback_data='search')],
                    ])
    
    if msg['text'] == '/start':
        bot.sendMessage(chat_id, 'شروع کن!\n/search\n/help')
    elif msg['text'] == '/help':
        bot.sendMessage(chat_id, 'راهنما:\n/start - شروع\n/help - راهنما')
    elif msg['text'] == '/search':
        bot.sendMessage(chat_id, 'جستجوی فیلم موردنظر', reply_markup=keyboard)
    elif markup:
        text = msg['text'].replace(' ', '%20')
        url = 'http://www.omdbapi.com/?apikey={0}&s={1}&t=movie'.format(
              omdb_token,
              text)
        http = urllib3.PoolManager()
        request = http.request('GET', url)
        json_obj = json.loads(request.data.decode('utf-8'))
        if json_obj['Response'] == 'True':
            for item in json_obj['Search']:
                text = "<b>عنوان:\n</b>{0}\n<b>سال تولید:\n</b>{1}\n<b>شناسه imdb: \n</b>{2}\n".format(
                        item['Title'], item['Year'], item['imdbID']) 
                bot.sendMessage(chat_id, text, parse_mode='html') 
                if item['Poster'] != 'N/A':
                    bot.sendPhoto(chat_id, item['Poster'])
                else:
                    bot.sendPhoto(chat_id,
                                  'shorturl.at/kvDMQ')
        else:
            bot.sendMessage(chat_id, 'متاسفانه فیلمی با این عنوان یافت نشد!')
        markup = None
    else:
        bot.sendMessage(chat_id,
                        'دستور مورد نظر یافت نشد\nبرای راهنمایی از /help استفاده کنید\n/search')


def on_callback_query(msg):
    global markup
    query_id, from_id, query_data = telepot.glance(msg, 
                                                   flavor='callback_query')

    print('Callback Query: ', query_id, from_id, query_data)

    if query_data == 'search':
        markup = ForceReply()
        bot.sendMessage(from_id, 'عنوان فیلم مورد نظرتان را ارسال کنید', 
                        reply_markup=markup)


MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()

while(1):
    time.sleep(10)
