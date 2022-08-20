import configparser
from VK.vkontakte import Vkontakte
from Bot.vk_bot import Bot

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    token = config['VK']['token']

    vk = Vkontakte(token)
    bot = Bot(token)

    bot.connect()
    bot.get_id()
