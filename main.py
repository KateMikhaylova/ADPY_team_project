import configparser

from Bot.vk_bot import BotApi


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    user_token = config['VK']['token']
    bot_token = config['VK']['bot_token']
    postgres_username = config['DB']['username']
    postgres_password = config['DB']['password']

    connect_info = {'drivername': 'postgresql+psycopg2',
                    'username': postgres_username,
                    'password': postgres_password,
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'vkinder'
                    }

    vkontakte_bot = BotApi(user_token, bot_token, **connect_info)

    vkontakte_bot.run_bot()
