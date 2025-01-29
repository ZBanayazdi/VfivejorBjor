from telebot import TeleBot
from Control.botManager import botManager
from Model.redisManager import redisManager

from CONSTANTS import TOKEN

redis_manager = redisManager()
bot = TeleBot(TOKEN)
bot_manager = botManager(bot,redis_manager)

bot.polling(non_stop=True)
