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

    def get_id(self):
        for event in self.longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    return event.user_id

