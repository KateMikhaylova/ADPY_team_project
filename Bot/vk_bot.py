import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from VK.vkontakte import VkontakteApi
from DB.database import DB

import datetime
from time import sleep


class BotApi(VkontakteApi, DB):
    """
    Class for Vkontakte bot (inherited from VkontakteAPI to call its methods and from DB class to work with database)

    Attributes:
        user_token: str
                    users token used to get access to VkApi methods
        vk_session: class vk_api.vk_api.VkApi object
                    used to create vk attribute and to create VkRequestsPool object
        vk:         class vk_api.vk_api.VkApiMethod object
                    used to call VkApi methods
        bot_token:  str
                    bot token used to send messages in group chat on behalf of the group
        bot_session:class vk_api.vk_api.VkApi object
                    used to create bot, longpool attributes and to send messages to bot user
        bot:        class vk_api.vk_api.VkApiMethod object
                    used to send keyboards to bot user
        longpool:   class vk_api.longpoll.VkLongPoll object
                    used to perform bot permanent run
        info:       dict to create DSN for database connection
        engine:     engine to work with database
        connection: connection with database via psycopg2 in order to create new database if nesessary
        cursor:     psycopg2 connection cursor

    Methods:
        execute_beginning: executes Begin command
        execute_help: executes Help command
        execute_start: executes Start command
        execute_age: executes different Age commands
        execute_city: executes different City commands
        execute_search: executes Search command
        execute_next: executes Next command
        execute_like_photo: executes different photo like commands
        execute_delete_like_photo: executes different photo delete like commands command
        execute_add_to_favourite: executes Add to favourite command
        execute_show_favourite: executes Show favourite command
        execute_add_to_blacklist: executes Add to blacklist command
        send_any_msg: sends message to user with any text
        send_person_msg: sends message to user wth mate name, surname link and photos
        send_empty_keyboard: sends empty keyboard to user (deletes previous active keyboard)
        send_search_keyboard: sends search keyboard to user
        send_start_keyboard: sends start keyboard to user
        send_age_city_keyboard: sends age and city choise keyboard to user
        send_age_keyboard: sends age choise keyboard to user
        send_city_keyboard: sends city choise keyboard to user
        send_next_keyboard: sends next keyboard to user
        run_bot: creates/updates database and permanently runs bot to chat with users
    """

    def __init__(self, user_token: str, bot_token: str, **info: dict) -> None:
        """
        Sets attributes user_token, vk_session, vk, bot_token, bot_session, bot, longpool, info, engine for object
        BotApi
        :param user_token: str, users token with necessary rights ('wall' rights are obligatory)
        :param bot_token: str, bot token of the community
        """

        VkontakteApi.__init__(self, user_token)
        DB.__init__(self, **info)
        self.bot_token = bot_token
        self.bot_session = vk_api.VkApi(token=self.bot_token)
        self.bot = self.bot_session.get_api()
        self.longpool = VkLongPoll(self.bot_session)

    def execute_beginning(self, uid: int) -> bool:
        """
        Executes 'Начать' command, sends user start keyboard
        :param uid: user id
        :return:
        """

        self.send_start_keyboard(uid)

        return True

    def execute_help(self, uid: int) -> bool:
        """
        Checks whether user has started work with bot or not
        If yes, sends him next keyboard, if not, sends him start keyboard
        :param uid: user id
        :return:
        """

        global select_dict
        global current_photos

        if uid not in select_dict and uid not in current_photos:
            self.send_start_keyboard(uid)

        else:
            text = '''Вы уже произвели поиск. 
Вы можете произвести действия с последним полученным пользователем или перейти к следующему'''
            self.send_any_msg(uid, text)
            self.send_next_keyboard(uid)

        return True

    def execute_start(self, uid: int) -> bool:
        """
        Checks whether user has started work with bot or not
        If yes, sends him next keyboard, if not, writes him in database, determinates search parameters and either
        sends search keyboard to user or sends him age/city/age-city keyboards if these parameters are absent on user
        page and need to be filled
        :param uid: user id
        :return:
        """
        global select_dict
        global current_photos
        global search_parameters

        if uid not in select_dict and uid not in current_photos:

            user_info = self.get_user_info(uid)
            self.writeUser(user_info)

            search_info = self.determinate_search_parameters(user_info)
            search_parameters[uid] = search_info

            if search_info[0] and search_info[2]:
                self.send_search_keyboard(uid)

            elif not search_info[0] and not search_info[2]:
                self.send_age_city_keyboard(uid)

            elif not search_info[2]:
                self.send_age_keyboard(uid)

            elif not search_info[0]:
                self.send_city_keyboard(uid)

        else:
            text = '''Вы уже произвели поиск. 
Вы можете произвести действия с последним полученным пользователем или перейти к следующему'''
            self.send_any_msg(uid, text)
            self.send_next_keyboard(uid)

        return True

    def execute_age(self, uid, message_command):
        global search_parameters
        if uid in search_parameters and search_parameters[uid][2] is None:
            try:
                age = int(message_command.split()[-1])
                search_parameters[uid][2] = age
            except ValueError:
                self.send_any_msg(uid, 'Неизвестная команда')
        elif uid in search_parameters:
            pass
        else:
            text = 'Вы еще не начинали или уже закончили поиск. Нажмите start, чтобы начать новый поиск'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)

    def execute_city(self, uid, message_command):
        global search_parameters
        if uid in search_parameters and search_parameters[uid][0] is None:
            city_title = message_command.split()[-1]
            city_dict = {'москва': 1,
                         'санкт-петербург': 2,
                         'казань': 60,
                         'ростов-на-дону': 119,
                         'махачкала': 85,
                         'екатеринбург': 49,
                         'новосибирск': 99,
                         'норильск': 102,
                         'владивосток': 37,
                         'якутск': 168,
                         }
            city_id = city_dict.get(city_title)
            search_parameters[uid][0] = city_id
        elif uid in search_parameters:
            pass
        else:
            text = 'Вы еще не начинали или уже закончили поиск. Нажмите start, чтобы начать новый поиск'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)

    def execute_search(self, uid: int):
        global select_dict
        global current_photos
        global search_parameters

        if uid not in select_dict and uid not in current_photos:

            if uid not in search_parameters:
                self.send_start_keyboard(uid)
                return
            search_info = search_parameters[uid][:]
            search_info_dict = {'gender': search_info[1],
                                'city': search_info[0],
                                'age': search_info[2]
                                }

            if search_info[0] and search_info[2]:
                self.send_empty_keyboard(uid, 'Начинаю поиск')
                del(search_parameters[uid])

                people_list = self.search_people(*search_info)
                # people_list = self.search_many_people(*search_info)
                # поиск с большим кол-вом результатов, при поиске фото по всем этим людям возможен таймаут

                for person in people_list:
                    photos = self.get_3_photos(person['id'])
                    sleep(0.34)

                    if len(photos) < 3:
                        continue

                    user_gender_id = person['sex']
                    if user_gender_id == 1:
                        user_gender_title = 'женский'
                    else:
                        user_gender_title = 'мужской'

                    birth_day = person['bdate'].split('.')
                    user_birthday_date = datetime.date(int(birth_day[2]), int(birth_day[1]), int(birth_day[0]))
                    user_age = int((datetime.date.today() - user_birthday_date).days // 365.25)

                    person_info = {'last_name': person['last_name'],
                                   'first_name': person['first_name'],
                                   'id_user': person['id'],
                                   'city': person['city']['id'],
                                   'city_title': person['city']['title'],
                                   'gender': person['sex'],
                                   'gender_title': user_gender_title,
                                   'age': user_age,
                                   'photos': photos,
                                   'middle_name': None
                                   }

                    self.writeFoundUser(person_info)

                select_result = self.readFoundUser(uid, search_info_dict)

                select_dict[uid] = [0, select_result]
                first_person = select_dict[uid][1][select_dict[uid][0]]
                first_person_photos = self.query_photo(first_person['id_user'])

                current_photos[uid] = first_person_photos
                self.send_person_msg(uid, first_person['id_user'],
                                     first_person['first_name'], first_person['last_name'],
                                     first_person_photos[0], first_person_photos[1], first_person_photos[2])

                self.send_next_keyboard(uid)
            elif not search_info[0] and not search_info[2]:
                self.send_age_city_keyboard(uid)
            elif not search_info[2]:
                self.send_age_keyboard(uid)
            elif not search_info[0]:
                self.send_city_keyboard(uid)

        else:
            text = '''Вы уже произвели поиск. 
Вы можете произвести действия с последним полученным пользователем или перейти к следующему'''
            self.send_any_msg(uid, text)
            self.send_next_keyboard(uid)

    def execute_next(self, uid):
        global select_dict
        global current_photos
        if uid in select_dict and uid in current_photos:
            select_dict[uid][0] += 1
            if select_dict[uid][0] < len(select_dict[uid][1]):
                next_person = select_dict[uid][1][select_dict[uid][0]]
                next_person_photos = self.query_photo(next_person['id_user'])
                current_photos[uid] = next_person_photos
                self.send_person_msg(uid, next_person['id_user'], next_person['first_name'], next_person['last_name'],
                                     next_person_photos[0], next_person_photos[1], next_person_photos[2])
                self.send_next_keyboard(uid)
            else:
                del(select_dict[uid])
                del(current_photos[uid])
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('посмотреть избранных', color=VkKeyboardColor.SECONDARY)
                keyboard.add_line()
                keyboard.add_button('start', color=VkKeyboardColor.SECONDARY)
                self.bot.messages.send(peer_id=uid,
                                       random_id=get_random_id(),
                                       keyboard=keyboard.get_keyboard(),
                                       message=f'''Вы посмотрели всех подобранных пользователей.
Можете посмотреть избранных пользователей или начать заново.
Благодарим за использование бота''')
        else:
            text = 'Вы еще не начинали или уже закончили поиск. Нажмите start, чтобы начать новый поиск'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)

    def execute_like_photo(self, uid, photo_number):
        global current_photos
        if uid in current_photos:
            three_photos = current_photos[uid]
            photo = three_photos[photo_number-1]
            owner_id, photo_id = photo.split('_')
            self.like_photo(owner_id, photo_id)
        else:
            text = 'Вы еще не начинали или уже закончили поиск. Нажмите start, чтобы начать новый поиск'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)

    def execute_delete_like_photo(self, uid, photo_number):
        global current_photos
        if uid in current_photos:
            three_photos = current_photos[uid]
            photo = three_photos[photo_number - 1]
            owner_id, photo_id = photo.split('_')
            if self.check_like_presence(photo):
                self.delete_like_photo(owner_id, photo_id)
        else:
            text = 'Вы еще не начинали или уже закончили поиск. Нажмите start, чтобы начать новый поиск'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)

    def execute_add_to_favourite(self, uid):
        global select_dict
        if uid in select_dict:
            current_person = select_dict[uid][1][select_dict[uid][0]]
            self.add_to_favourite(uid, current_person['id_user'])
        else:
            text = 'Вы еще не начинали или уже закончили поиск. Нажмите start, чтобы начать новый поиск'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)

    def execute_show_favourite(self, uid):
        favourites = self.query_favourite(uid)
        text = ''
        for favourite in favourites:
            text += f'{favourite.first_name} {favourite.last_name}\nhttps://vk.com/id{favourite.id}\n'
        if not text:
            text = '''Вы еще никого не добавили в избранное 
(ну или отправили в черный список всех, кого ранее добавляли в избранное)'''
        self.send_any_msg(uid, text)

    def execute_add_to_blacklist(self, uid):
        global select_dict
        if uid in select_dict:
            current_person = select_dict[uid][1][select_dict[uid][0]]
            self.add_to_blacklist(uid, current_person['id_user'])
            self.delete_from_favourites(uid, current_person['id_user'])
        else:
            text = 'Вы еще не начинали или уже закончили поиск. Нажмите start, чтобы начать новый поиск'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)

    def send_any_msg(self, uid, text):
        self.bot_session.method('messages.send', {'user_id': uid, 'message': text, 'random_id': get_random_id()})

    def send_person_msg(self, uid, person_id, name, surname, photo1, photo2, photo3):
        message = f'''{name} {surname}
https://vk.com/id{person_id}    
        '''
        photo = f'photo{photo1},photo{photo2},photo{photo3}'
        self.bot_session.method('messages.send', {'user_id': uid, 'message': message,
                                                  'attachment': photo, 'random_id': get_random_id()})

    def send_empty_keyboard(self, uid, message=None):
        self.bot.messages.send(peer_id=uid,
                               random_id=get_random_id(),
                               keyboard=VkKeyboard.get_empty_keyboard(),
                               message=message)

    def send_search_keyboard(self, uid):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('search', color=VkKeyboardColor.SECONDARY)
        self.bot.messages.send(peer_id=uid,
                               random_id=get_random_id(),
                               keyboard=keyboard.get_keyboard(),
                               message=f'''Мы собираемся поискать для вас пользователей вашего возраста, 
противоположного пола, проживающих в вашем городе.
Нажмите кнопку search, чтобы начать поиск''')

    def send_start_keyboard(self, uid: int) -> bool:
        """
        Sends keyboard with 'start' button to user with indicated id
        :param uid: user id
        :return:
        """
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('start', color=VkKeyboardColor.SECONDARY)
        self.bot.messages.send(peer_id=uid,
                               random_id=get_random_id(),
                               keyboard=keyboard.get_keyboard(),
                               message=f'''Вас приветствует бот для знакомств VKinder.
Для начала работы просто нажмите start.''')
        return True

    def send_age_city_keyboard(self, uid):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('возраст 20', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 25', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 30', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('возраст 35', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 40', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 45', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('возраст 50', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 60', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 70', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Москва', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Санкт-Петербург', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Казань', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Ростов-на-Дону', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Махачкала', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Екатеринбург', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Новосибирск', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Норильск', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Владивосток', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Якутск', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('search', color=VkKeyboardColor.PRIMARY)
        self.bot.messages.send(peer_id=uid,
                               random_id=get_random_id(),
                               keyboard=keyboard.get_keyboard(),
                               message=f'''
У вас не указана или скрыта дата рождения и город проживания.
Отредактируйте личные данные для наиболее точного поиска или
выберите возраст, город для поиска, после чего нажмите search''')

    def send_age_keyboard(self, uid):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('возраст 20', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 25', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 30', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('возраст 35', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 40', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 45', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('возраст 50', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 60', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст 70', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('search', color=VkKeyboardColor.PRIMARY)
        self.bot.messages.send(peer_id=uid,
                               random_id=get_random_id(),
                               keyboard=keyboard.get_keyboard(),
                               message=f'''
У вас не указана или скрыта дата рождения.
Отредактируйте личные данные для наиболее точного поиска или
выберите возраст для поиска, после чего нажмите search''')

    def send_city_keyboard(self, uid):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('г. Москва', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Санкт-Петербург', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Казань', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Ростов-на-Дону', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Махачкала', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Екатеринбург', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Новосибирск', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Норильск', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('г. Владивосток', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('г. Якутск', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('search', color=VkKeyboardColor.PRIMARY)
        self.bot.messages.send(peer_id=uid,
                               random_id=get_random_id(),
                               keyboard=keyboard.get_keyboard(),
                               message=f'''
У вас не указан или скрыт город проживания.
Отредактируйте личные данные для наиболее точного поиска или
выберите город для поиска, после чего нажмите search''')

    def send_next_keyboard(self, uid):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('лайк фото 1', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('лайк фото 2', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('лайк фото 3', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('не лайк фото 1', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('не лайк фото 2', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('не лайк фото 3', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('в избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('посмотреть избранных', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('в черный список', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('next', color=VkKeyboardColor.PRIMARY)
        self.bot.messages.send(peer_id=uid,
                               random_id=get_random_id(),
                               keyboard=keyboard.get_keyboard(),
                               message=f'''
Вы можете лайкнуть любую из фотографий, отменить лайк, добавить пользователя в избранное, 
в черный список, посмотреть избранное или перейти к следующему пользователю''')

    def run_bot(self):

        engine = self.preparation()
        test_create = self.createtable(engine)
        if not test_create:
            test_new_db = self.newdatabase()
            if test_new_db:
                self.createtable(engine)
            else:
                print(test_new_db)
                print('НИЧЕГО НЕ РАБОТАЕТ!')

        for event in self.longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    user_message = event.text.lower()
                    user_id = event.user_id
                    if user_message == 'начать':
                        self.execute_beginning(user_id)
                    elif user_message == 'help':
                        self.execute_help(user_id)
                    elif user_message == 'start':
                        self.execute_start(user_id)
                    elif user_message == 'search':
                        self.execute_search(user_id)
                    elif user_message == 'next':
                        self.execute_next(user_id)
                    elif user_message == 'лайк фото 1':
                        self.execute_like_photo(user_id, 1)
                    elif user_message == 'лайк фото 2':
                        self.execute_like_photo(user_id, 2)
                    elif user_message == 'лайк фото 3':
                        self.execute_like_photo(user_id, 3)
                    elif user_message == 'не лайк фото 1':
                        self.execute_delete_like_photo(user_id, 1)
                    elif user_message == 'не лайк фото 2':
                        self.execute_delete_like_photo(user_id, 2)
                    elif user_message == 'не лайк фото 3':
                        self.execute_delete_like_photo(user_id, 3)
                    elif user_message == 'в избранное':
                        self.execute_add_to_favourite(user_id)
                    elif user_message == 'посмотреть избранных':
                        self.execute_show_favourite(user_id)
                    elif user_message == 'в черный список':
                        self.execute_add_to_blacklist(user_id)
                    elif user_message.startswith('возраст'):
                        self.execute_age(user_id, user_message)
                    elif user_message.startswith('г.'):
                        self.execute_city(user_id, user_message)
                    else:
                        self.bot_session.method('messages.send', {'user_id': user_id,
                                                                  'message': 'Неизвестная команда',
                                                                  'random_id': get_random_id()})


search_parameters = dict()
select_dict = dict()
current_photos = dict()
