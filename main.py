import configparser
from VK.vkontakte import Vkontakte
from pprint import pprint

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    token = config['VK']['token']

    vk = Vkontakte(token)
    pprint(vk.get_customer_info())
