import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


class Bot:
    def __init__(self, token):
        self.token = token
        self.longpool = None

    def connect(self):
        vk_session = vk_api.VkApi(token=self.token)
        vk_session.get_api()
        self.longpool = VkLongPoll(vk_session)

