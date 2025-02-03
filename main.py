from telebot import TeleBot,types
from Control.botManager import botManager
from Model.redisManager import redisManager

from CONSTANTS import TOKEN

redis_manager = redisManager()
bot = TeleBot(TOKEN)
bot.set_my_commands([
            types.BotCommand("/start", "شروع بازارگردی"),
        ])
bot_manager = botManager(bot, redis_manager)

bot.polling(non_stop=True)
