import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


def get_id(token):
    session = vk_api.VkApi(token=token)
    session_api = session.get_api()
    longpool = VkLongPoll(session)
    for event in longpool.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                return event.user_id
