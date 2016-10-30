#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This bot upload images sent from users on telegram to imgur
# This progam is licenced under the MIT license.

import os
import errno
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import random
from imgurpython import ImgurClient
import json
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
bot_key = "" # Telegram bot access token
client_id = '' #Client ID for imgur
client_secret = '' #Client secert for imgur

client = ImgurClient(client_id, client_secret) #Set imgur client
# Define needed commands
# Start: Welcome the user and guide them on how to use the bot
# Help: Refrence the user to the bug reporting URL (GitHub)
# About: Tell them about the bot
# upload_img: Downloads the image the user sent then uploads it to imgur and sends the url to the user
# upload_vid: Downloads the video the user sent then uploads it to vidme and sends the url to the user
# error: Log errors
#firstCheck: Check if the needed directories are there. If not create them
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hello, to start off just send me a photo or video')

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Please go to the following link:\n http://faisal-k.com/teleimgur')

def about(bot, update):
    bot.sendMessage(update.message.chat_id, text='This bot is under MIT license: https://github.com/kwmx/teleimgur\n'
                                                 'The following were used: \n'
                                                 'https://github.com/Imgur/imgurpython'
                                                 ' - pyton wrapper for imgur API\n'
                                                 'https://github.com/python-telegram-bot'
                                                 ' - python wrapper for telegram API\n'
                                                 'http://www.flaticon.com/free-icon/telegram-logo_87413'
                                                 ' - For icon design\n'
                                                 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Imgur_logo.svg/2000px-Imgur_logo.svg.png'
                                                 ' - For Icon design\n'
                                                 'Rate the bot on https://storebot.me/bot/teleimgurbot')


def upload_img(bot, update):
    siz = len(update.message.photo) - 1
    file_id = update.message.photo[siz].file_id
    newFile = bot.getFile(file_id)
    hash = random.getrandbits(128)
    filetemp_name = "img_" + str(update.message.chat_id) + "_" + str(hash) + ".png";
    newFile.download("images/" + filetemp_name)
    try:
        item = client.upload_from_path("images/" + filetemp_name)
        arrayJs = json.dumps(item)
        js = json.loads(arrayJs)
        bot.sendMessage(update.message.chat_id, text=js['link'])
    except Exception as e:
        print(e)
        bot.sendMessage(update.message.chat_id, text="Sorry, an error occured while uploading. Please try again later."
                                                 " If this issue continues please report it")
    os.remove('images/' + filetemp_name)
def upload_vid(bot, update):
    if(update.message.video.duration > 1800): #if the video is longer than 30 minutes. Cancle and report
        bot.sendMessage(update.message.chat_id, text="Video is too long. Maximum is 30 minutes")
        return
    if (update.message.video.file_size > 256000000):
        bot.sendMessage(update.message.chat_id, text="Video is too big. Maximum is 256 MB")
        return
    try:
        file_id = update.message.video.file_id
        newFile = bot.getFile(file_id)
        hash = random.getrandbits(128)
        filetemp_name = "vid_" + str(update.message.chat_id) + "_" + str(hash) + ".avi";
        newFile.download("videos/" + filetemp_name)

        url = 'https://api.vid.me/video/upload'
        f = open('videos/' + filetemp_name, 'rb')
        files = {'filedata': f}
        response = requests.post(url, files=files)
        js = json.loads(response.text)
        f.close()
        if (js['status'] == True):
            bot.sendMessage(update.message.chat_id, text=js['url'])
            update.message.chat_id) + ". From user:" + update.message.from_user.username)
        else:
            bot.sendMessage(update.message.chat_id, text="Unable to upload file")

    except Exception as e:
        print(e)
        bot.sendMessage(update.message.chat_id, text="Sorry, an error occured while uploading. Please try again later."
                                                 " If this issue continues please report it")
    os.remove('videos/' + filetemp_name)
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def firstCheck():
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists("videos"):
        os.makedirs("videos")
def main():
    # Create the EventHandler and pass it bot's token.
    updater = Updater(bot_key)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("about", about))

    # Handle images
    dp.add_handler(MessageHandler([Filters.photo], upload_img))
    # Handle Videos
    dp.add_handler(MessageHandler([Filters.video], upload_vid))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Keep the bot running
    updater.idle()

firstCheck()
if __name__ == '__main__':
    main()
