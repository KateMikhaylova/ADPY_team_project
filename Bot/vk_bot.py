import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from VK.vkontakte import VkontakteApi
import configparser
from time import sleep

class BotApi(VkontakteApi):

    def __init__(self, user_token: str, bot_token: str) -> None:  # переписать инициализацию с super
        """
        Sets attributes user_token, vk_session and vk for object BotApi
        :param user_token: str, users token with necessary rights ('wall' rights are obligatory)
        """
        self.user_token = user_token
        self.vk_session = vk_api.VkApi(token=self.user_token)
        self.vk = self.vk_session.get_api()
        self.bot_token = bot_token
        self.bot_session = vk_api.VkApi(token=self.bot_token)
        self.bot = self.bot_session.get_api()
        self.longpool = VkLongPoll(self.bot_session)


    def execute_help(self, uid: int):
        help_text = '''Вас приветствует бот для знакомств VKinder.
        Для начала работы просто введите start в поле ниже.
        '''
        self.bot_session.method('messages.send', {'user_id': uid, 'message': help_text, 'random_id': get_random_id()})

    def execute_start(self, uid: int):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('search', color=VkKeyboardColor.SECONDARY)
        self.bot.messages.send(peer_id=uid,
                                  random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),  # получаем Json клавиатуры
                                  message=f'''Мы собираемся поискать для вас пользователей вашего возраста, 
противоположного пола, проживающих в вашем городе
Нажмите кнопку search, чтобы начать поиск''')

    def execute_search(self, uid: int):
        user_info = self.get_user_info(uid)
        search_info = self.determinate_search_parameters(user_info)
        # тут можно записать юзера в БД. Надо ему еще фамилию и имя в выдачу добавить

        people_list = self.search_people(*search_info)
        # people_list = self.search_many_people(*search_info) # поиск с большим кол-вом результатов, при поиске фото по всем этим людям возможен таймаут

        for person in people_list:
            photos = self.get_3_photos(person['id'])
            sleep(0.34)

            if len(photos) < 3: # Скрипт же поломается, если скормить ему меньше фото, чем 3? Если нет, это можно убрать
                continue
            # здесь записываем людей и их фотографии в БД

        # теперь вызываем селект всех людей подходящих по search_info из бд. Там наверное какой-нибудь список кортежей вернется.
        select_result = [(195253, 'Вася', 'Васильев'), (333888, 'Иван', 'Иванов'), (22256, 'Петр', 'Петров')] # для имитации работы
        global select_dict
        select_dict[uid] = [0, select_result]
        first_person = select_dict[uid][1][select_dict[uid][0]]
        # тут наверное отдельно придется селектнуть фотки человека, потому что если в верхнем селекте сделать джойн, люди затроятся
        first_person_photos = [('1_456264771', (50,0)), ('1_376599151', (30,0)), ('1_288668576', (25,1))] # для имитации работы
        self.send_person_msg(uid, first_person[0], first_person[1], first_person[2],
                             first_person_photos[0][0], first_person_photos[1][0], first_person_photos[2][0])
        select_dict[uid][0] += 1
        self.send_next_keyboard(uid)

    def execute_next(self, uid):
        global select_dict
        if select_dict[uid][0] < len(select_dict[uid][1]):
            next_person = select_dict[uid][1][select_dict[uid][0]]
            # селектим фотки человека
            next_person_photos = [('1_456264771', (50, 0)), ('1_376599151', (30, 0)), ('1_288668576', (25, 1))]
            self.send_person_msg(uid, next_person[0], next_person[1], next_person[2],
                                 next_person_photos[0][0], next_person_photos[1][0], next_person_photos[2][0])
            select_dict[uid][0] += 1
            self.send_next_keyboard(uid)
        else:
            self.bot_session.method('messages.send', {'user_id': uid, 'message': 'Вы посмотрели всех подобранных пользователей',
                                                      'random_id': get_random_id()})
            self.send_empty_keyboard(uid, 'Благодарим за использование бота')

    def send_person_msg(self, uid, person_id, name, surname, photo1, photo2, photo3):
        message = f'''{name} {surname}
    https://vk.com/id{person_id}    
        '''
        photo = f'photo{photo1},photo{photo2},photo{photo3}'
        self.bot_session.method('messages.send', {'user_id': uid, 'message': message, 'attachment': photo, 'random_id': get_random_id()})

    def send_empty_keyboard(self, uid, message):
        self.bot.messages.send(peer_id=uid,
                               random_id=get_random_id(),
                               keyboard=VkKeyboard.get_empty_keyboard(),  # получаем Json клавиатуры
                               message=message)

    def send_next_keyboard(self, uid):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('лайк фото 1', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('лайк фото 2', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('лайк фото 3', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('в избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('в черный список', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('next', color=VkKeyboardColor.PRIMARY)
        self.bot.messages.send(peer_id=uid,
                                  random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),  # получаем Json клавиатуры
                                  message=f'''
Вы можете лайкнуть любую из фотографий, добавить пользователя в избранное, в черный список или перейти к следующему пользователю''')


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    user_token = config['VK']['token']
    bot_token = config['VK']['bot_token']

    vkontakte_bot = BotApi(user_token, bot_token)

    select_dict = dict()

    for event in vkontakte_bot.longpool.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            # pprint(event.__dict__) посмотреть внутренности
            if event.to_me:
                user_message = event.text.lower()
                user_id = event.user_id
                if user_message == 'help':
                    vkontakte_bot.execute_help(user_id)
                elif user_message == 'start':
                    vkontakte_bot.execute_start(user_id)
                elif user_message == 'search':
                    vkontakte_bot.execute_search(user_id)
                elif user_message == 'next':
                    vkontakte_bot.execute_next(user_id)
                else:
                    vkontakte_bot.bot_session.method('messages.send',
                                        {'user_id': user_id, 'message': 'Неизвестная команда', 'random_id': get_random_id()})