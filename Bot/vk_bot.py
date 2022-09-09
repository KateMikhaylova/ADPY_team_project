import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from VK.vkontakte import VkontakteApi
from DB.database import DB
from interests.interests import InterestsComparison
import keyboard.keyboard as kb

import nltk
from nltk.corpus import stopwords


class BotApi:
    """
    Class for Vkontakte bot

    Attributes:
        bot_token:  str
                    bot token used to send messages in group chat on behalf of the group
        bot_session:class vk_api.vk_api.VkApi object
                    used to create bot, longpool attributes and to send messages to bot user
        bot:        class vk_api.vk_api.VkApiMethod object
                    used to send keyboards to bot user
        longpool:   class vk_api.longpoll.VkLongPoll object
                    used to perform bot permanent run
        search_parameters:  attribute to store each bot users search parameters while they are prepared before sending
                            to search method
        select_dict:        attribute to save each bot users select results and position on watching through them
        current_photos:     attribute to save each bot users current showing mate, needed to action with photos
        interests:          attribute for class InterestsComparison object to call this class methods
        apivk:              attribute for class VkontakteApi object to call this class methods
        db:                 attribute for class DB object to call this class methods

    Methods:
        execute_beginning: executes Begin command
        execute_help: executes Help command
        execute_start: executes Start command
        execute_age: executes different Age commands
        execute_city: executes different City commands
        execute_search: executes Search command
        sort_found_user_by_match: sorts list of found users based on their likeness with bot user
        execute_next: executes Next command
        execute_like_photo: executes different photo like commands
        execute_delete_like_photo: executes different photo delete like commands command
        execute_add_to_favourite: executes Add to favourite command
        execute_show_favourite: executes Show favourite command
        execute_add_to_blacklist: executes Add to blacklist command
        send_any_msg: sends message to user with any text
        send_person_msg: sends message to user wth mate name, surname link and photos
        send_empty_keyboard: sends empty keyboard to user (deletes previous active keyboard)
        send_favourite_start_keyboard: sends keyboard with show favourite and next buttons
        send_search_keyboard: sends search keyboard to user
        send_start_keyboard: sends start keyboard to user
        send_age_city_keyboard: sends age and city choose keyboard to user
        send_age_keyboard: sends age choose keyboard to user
        send_city_keyboard: sends city choose keyboard to user
        send_next_keyboard: sends next keyboard to user
        run_bot: creates/updates database and permanently runs bot to chat with users
    """

    def __init__(self, user_token: str, bot_token: str, **info: dict) -> None:
        """
        Sets attributes bot_token, bot_session, bot, longpool, search_parameters, select_dict, current_photos,
        interests, apivk, db for object BotApi
        :param user_token: str, users token with necessary rights ('wall' rights are obligatory)
        :param bot_token: str, bot token of the community
        :param info: info for database connection
        """
        self.bot_token = bot_token
        self.bot_session = vk_api.VkApi(token=self.bot_token)
        self.bot = self.bot_session.get_api()
        self.longpool = VkLongPoll(self.bot_session)
        self.search_parameters = dict()
        self.select_dict = dict()
        self.current_photos = dict()
        self.interests = InterestsComparison()
        self.apivk = VkontakteApi(user_token)
        self.db = DB(**info)

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
        if uid not in self.select_dict and uid not in self.current_photos:
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
        If yes, sends him next keyboard, if not, writes him in database, determines search parameters and either
        sends search keyboard to user or sends him age/city/age-city keyboards if these parameters are absent on user
        page and need to be filled
        :param uid: user id
        :return:
        """
        if uid not in self.select_dict and uid not in self.current_photos:

            user_info = self.apivk.get_user_info(uid)
            self.db.write_user(user_info)

            search_info = self.apivk.determinate_search_parameters(user_info)
            self.search_parameters[uid] = search_info

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

    def execute_age(self, uid: int, message_command: str) -> bool:
        """
        Checks whether user has started work with bot or not.
        If not, sends him start keyboard, if yes, checks whether users age is determined.
        If yes, it does nothing, if not it proceeds entered through button age command (mask 'Возраст ...') takes age
        integer from it and fills in search parameters dict for this user
        :param uid: user id
        :param message_command: button age command (mask 'Возраст ...')
        :return:
        """
        if uid in self.search_parameters and self.search_parameters[uid][2] is None:

            try:
                age = int(message_command.split()[-1])
                self.search_parameters[uid][2] = age
                return True

            except ValueError:
                self.send_any_msg(uid, 'Неизвестная команда')
                return False

        elif uid in self.search_parameters:
            return False

        else:
            text = 'Вы еще не начинали или уже закончили поиск.'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)
            return True

    def execute_city(self, uid: int, message_command: str) -> bool:
        """
        Checks whether user has started work with bot or not.
        If not, sends him start keyboard, if yes, checks whether users city is determined.
        If yes, it does nothing, if not it proceeds entered through button city command (mask 'г. ...') takes city
        name from it, determines its id and fills in search parameters dict for this user
        :param uid: user id
        :param message_command: button city command (mask 'г. ...')
        :return:
        """
        if uid in self.search_parameters and self.search_parameters[uid][0] is None:

            city_title = message_command.split()[-1]
            city_dict = {'москва': 1, 'санкт-петербург': 2, 'казань': 60, 'ростов-на-дону': 119, 'махачкала': 85,
                         'екатеринбург': 49, 'новосибирск': 99, 'норильск': 102, 'владивосток': 37, 'якутск': 168}
            city_id = city_dict.get(city_title)
            self.search_parameters[uid][0] = city_id
            return True

        elif uid in self.search_parameters:
            return False

        else:
            text = 'Вы еще не начинали или уже закончили поиск.'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)
            return True

    def execute_search(self, uid: int) -> bool:
        """
        Checks whether user has started work with bot or not.
        If yes, sends him next keyboard, if no, checks whether search parameters for user are present.
        If no, sends him start keyboard, if yes, checks whether age and city present in search parameters.
        If yes, launches search, if no, sends user age/city/age-city keyboard.
        When search in API is performed, users search parameters are cleared. For each found user top 3 photos are
        searched and found user with photos is written to database
        After it all corresponding to search parameters people are selected from database, written in select_dict and
        first one is sent to bot user
        :param uid: user id
        :return:
        """
        if uid in self.select_dict and uid in self.current_photos:
            text = '''Вы уже произвели поиск. 
            Вы можете произвести действия с последним полученным пользователем или перейти к следующему'''
            self.send_any_msg(uid, text)
            self.send_next_keyboard(uid)
            return False

        if uid not in self.search_parameters:
            self.send_start_keyboard(uid)
            return False

        search_info = self.search_parameters[uid][:]
        search_info_dict = {'gender': search_info[1], 'city': search_info[0], 'age': search_info[2]}

        if search_info[0] and search_info[2]:
            self.send_empty_keyboard(uid, 'Начинаю поиск')
            del(self.search_parameters[uid])

            people_list = self.apivk.search_people(*search_info)
            # people_list = self.apivk.search_many_people(*search_info)
            # поиск с большим кол-вом результатов, при поиске фото по всем этим людям возможен таймаут
            people_list = self.apivk.prepare_found_users_info(people_list)
            for person in people_list:
                self.db.write_found_user(person)

            select_result = self.db.read_found_user(uid, search_info_dict)

            if not select_result:
                self.send_any_msg(uid, 'В базе пока нет для вас пары. Возвращайтесь позже, база все время обновляется')
                return False

            select_result = self.sort_found_user_by_match(uid, select_result)

            self.select_dict[uid] = [0, select_result]
            first_person = self.select_dict[uid][1][self.select_dict[uid][0]]

            first_person_photos = self.db.query_photo(first_person['id_user'])
            self.current_photos[uid] = first_person_photos

            self.send_person_msg(uid, first_person['id_user'],
                                 first_person['first_name'], first_person['last_name'],
                                 first_person_photos[0], first_person_photos[1], first_person_photos[2])

            self.send_next_keyboard(uid)

            return True

        elif not search_info[0] and not search_info[2]:
            self.send_age_city_keyboard(uid)
            return False

        elif not search_info[2]:
            self.send_age_keyboard(uid)
            return False

        elif not search_info[0]:
            self.send_city_keyboard(uid)
            return False

    def sort_found_user_by_match(self, uid: int, found_users: list) -> list:
        """
        Sorts list of found users based on their likeness with bot user
        :param uid: bot user id
        :param found_users: list of found users
        :return: sorted list of found users
        """
        user_dict = self.db.read_user(uid)[0]

        nltk.download('stopwords')  # line may be commented after first launch to avoid download warning in console
        all_stopwords = stopwords.words("russian") + stopwords.words("english")
        all_stopwords.extend(['всюду', 'очень', 'совместно', 'разный', 'самый', 'просто', 'наш', 'большой',
                              'любой', 'далее', 'круто', 'личный', 'завтра', 'вокруг', 'возможно', 'именно',
                              'помаленьку', 'многое', 'основное', 'это', 'всякий', 'поскольку', 'ещё', 'частенько',
                              'бывший', 'рабочий', 'практически', 'вообще', 'ненадолго', 'свой', 'немного',
                              'также', 'широкий', 'весь', 'хороший', 'каждый', 'внутренний', 'всё', 'пока',
                              'круглогодично', 'твой'])  # words can be added if necessary

        result = []
        for found_user in found_users:
            count = 0

            count += self.interests.compare_age(user_dict['age'], found_user['age'])
            count += self.interests.compare_city(user_dict['city'], found_user['city'])

            count += self.interests.evaluate_relations(found_user['relation'])
            count += self.interests.compare_languages(user_dict['langs'], found_user['langs'])

            count += self.interests.compare_interests_words(user_dict['activities'], found_user['activities'],
                                                            all_stopwords, 2, 4, 6)
            count += self.interests.compare_interests_words(user_dict['interests'], found_user['interests'],
                                                            all_stopwords, 2, 4, 6)
            count += self.interests.compare_interests_words(user_dict['inspired_by'], found_user['inspired_by'],
                                                            all_stopwords, 1, 2, 3)

            count += self.interests.compare_interests_phrases(user_dict['music'], found_user['music'], 2, 3, 4)
            count += self.interests.compare_interests_phrases(user_dict['movies'], found_user['movies'], 2, 3, 4)
            count += self.interests.compare_interests_phrases(user_dict['tv'], found_user['tv'], 1, 2, 3)
            count += self.interests.compare_interests_phrases(user_dict['books'], found_user['books'], 1, 2, 3)
            count += self.interests.compare_interests_phrases(user_dict['games'], found_user['games'], 1, 2, 3)

            count += self.interests.compare_main_things(user_dict['political'], found_user['political'])
            count += self.interests.compare_main_things(user_dict['religion_id'], found_user['religion_id'])
            count += self.interests.compare_main_things(user_dict['life_main'], found_user['life_main'])
            count += self.interests.compare_main_things(user_dict['people_main'], found_user['people_main'])

            count += self.interests.compare_smoking_alcohol(user_dict['smoking'], found_user['smoking'])
            count += self.interests.compare_smoking_alcohol(user_dict['alcohol'], found_user['alcohol'])

            mutual_friends = self.apivk.get_mutual_friends(user_dict['id_user'], found_user['id_user'])
            count += self.interests.evaluate_mutual_friends(mutual_friends)

            mutual_groups = self.apivk.get_groups(user_dict['id_user']) & self.apivk.get_groups(found_user['id_user'])
            count += self.interests.evaluate_mutual_groups(mutual_groups)

            result.append([count, found_user])

        result = sorted(result, key=lambda x: x[0], reverse=True)

        return [i[1] for i in result]

    def execute_next(self, uid: int) -> bool:
        """
        Checks whether user has started work with bot or not.
        If no, sends him start keyboard, if yes, switches counter in select_dict and sends to user next found person.
        If next person is absent, clears select_dict and current_photos and sends to user keyboard with favourite
        and start again buttons
        :param uid: user id
        :return:
        """
        if uid in self.select_dict and uid in self.current_photos:
            self.select_dict[uid][0] += 1

            if self.select_dict[uid][0] < len(self.select_dict[uid][1]):
                next_person = self.select_dict[uid][1][self.select_dict[uid][0]]
                next_person_photos = self.db.query_photo(next_person['id_user'])
                self.current_photos[uid] = next_person_photos

                self.send_person_msg(uid, next_person['id_user'], next_person['first_name'], next_person['last_name'],
                                     next_person_photos[0], next_person_photos[1], next_person_photos[2])
                self.send_next_keyboard(uid)
                return True

            else:

                del(self.select_dict[uid])
                del(self.current_photos[uid])
                self.send_favourite_start_keyboard(uid)

                return False

        else:
            text = 'Вы еще не начинали или уже закончили поиск.'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)
            return False

    def execute_like_photo(self, uid: int, photo_number: int) -> bool:
        """
        Checks whether user has started work with bot or not.
        If no, sends him start keyboard, if yes, likes photo with corresponding photo number
        :param uid: user id
        :param photo_number: photo number (1, 2 or 3)
        :return:
        """
        if uid in self.current_photos:
            three_photos = self.current_photos[uid]
            photo = three_photos[photo_number-1]
            owner_id, photo_id = photo.split('_')
            self.apivk.like_photo(owner_id, photo_id)
            return True

        else:
            text = 'Вы еще не начинали или уже закончили поиск.'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)
            return False

    def execute_delete_like_photo(self, uid: int, photo_number: int) -> bool:
        """
        Checks whether user has started work with bot or not.
        If no, sends him start keyboard, if yes, checks if photo with corresponding number is liked and if yes,
        deletes like
        :param uid: user id
        :param photo_number: photo number (1, 2 or 3)
        :return:
        """
        if uid in self.current_photos:
            three_photos = self.current_photos[uid]
            photo = three_photos[photo_number - 1]
            owner_id, photo_id = photo.split('_')
            if self.apivk.check_like_presence(photo):
                self.apivk.delete_like_photo(owner_id, photo_id)
                return True
            return False
        else:
            text = 'Вы еще не начинали или уже закончили поиск.'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)
            return False

    def execute_add_to_favourite(self, uid: int) -> bool:
        """
        Checks whether user has started work with bot or not.
        If no, sends him start keyboard, if yes, adds current shown person to favourites
        :param uid: user id
        :return:
        """
        if uid in self.select_dict:
            current_person = self.select_dict[uid][1][self.select_dict[uid][0]]
            self.db.add_to_favourite(uid, current_person['id_user'])
            return True

        else:
            text = 'Вы еще не начинали или уже закончили поиск.'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)
            return False

    def execute_show_favourite(self, uid: int) -> bool:
        """
        Selects favourited by bot user found users and sends message to bot user
        :param uid: user id
        :return:
        """
        favourites = self.db.query_favourite(uid)

        text = ''
        for favourite in favourites:
            text += f'{favourite.first_name} {favourite.last_name}\nhttps://vk.com/id{favourite.id}\n'

        if not text:
            text = '''Вы еще никого не добавили в избранное 
(ну или отправили в черный список всех, кого ранее добавляли в избранное)'''

        self.send_any_msg(uid, text)
        return True

    def execute_add_to_blacklist(self, uid: int) -> bool:
        """
        Checks whether user has started work with bot or not.
        If no, sends him start keyboard, if yes, adds current shown person to blacklist and deletes him from favourites
        if he was added there
        :param uid: use id
        :return:
        """
        if uid in self.select_dict:
            current_person = self.select_dict[uid][1][self.select_dict[uid][0]]
            self.db.add_to_blacklist(uid, current_person['id_user'])
            self.db.delete_from_favourites(uid, current_person['id_user'])
            return True

        else:
            text = 'Вы еще не начинали или уже закончили поиск.'
            self.send_any_msg(uid, text)
            self.send_start_keyboard(uid)
            return False

    def send_any_msg(self, uid: int, text: str) -> bool:
        """
        Sends any message to user
        :param uid: user id
        :param text: text message
        :return:
        """
        self.bot_session.method('messages.send', {'user_id': uid, 'message': text, 'random_id': get_random_id()})
        return True

    def send_person_msg(self, uid: int, person_id: int, name: str, surname: str,
                        photo1: str, photo2: str, photo3: str) -> bool:
        """
        Sends user message with found users name, surname, link and three photos
        :param uid: user id
        :param person_id: found user id to create link
        :param name: users name
        :param surname: user surname
        :param photo1: users first photo id
        :param photo2: users second photo id
        :param photo3: users third photo id
        :return:
        """
        message = f'''{name} {surname}
https://vk.com/id{person_id}    
        '''
        photo = f'photo{photo1},photo{photo2},photo{photo3}'
        self.bot_session.method('messages.send', {'user_id': uid, 'message': message,
                                                  'attachment': photo, 'random_id': get_random_id()})
        return True

    def send_empty_keyboard(self, uid: int, message: str) -> bool:
        """
        Sends empty keyboard to user (takes away previous one)
        :param uid: user id
        :param message: message text
        :return:
        """
        self.bot.messages.send(peer_id=uid, random_id=get_random_id(), keyboard=kb.create_empty_keyboard(),
                               message=message)
        return True

    def send_favourite_start_keyboard(self, uid: int) -> bool:
        """
        Sends keyboard with show favourite and start buttons
        :param uid: user id
        :return:
        """
        self.bot.messages.send(peer_id=uid, random_id=get_random_id(), keyboard=kb.create_favourite_start_keyboard(),
                               message=f'''Вы посмотрели всех подобранных пользователей.
Можете посмотреть избранных пользователей или начать заново.
Благодарим за использование бота''')
        return True

    def send_search_keyboard(self, uid: int) -> bool:
        """
        Sends keyboard with 'search' button to user with indicated id
        :param uid: user id
        :return:
        """
        self.bot.messages.send(peer_id=uid, random_id=get_random_id(), keyboard=kb.create_search_keyboard(),
                               message=f'''Мы собираемся поискать для вас пользователей вашего возраста, 
противоположного пола, проживающих в вашем городе.
Нажмите кнопку search, чтобы начать поиск''')
        return True

    def send_start_keyboard(self, uid: int) -> bool:
        """
        Sends keyboard with 'start' button to user with indicated id
        :param uid: user id
        :return:
        """
        self.bot.messages.send(peer_id=uid, random_id=get_random_id(), keyboard=kb.create_start_keyboard(),
                               message=f'''Вас приветствует бот для знакомств VKinder.
Для начала работы просто нажмите start.''')
        return True

    def send_age_city_keyboard(self, uid: int) -> bool:
        """
        Sends keyboard with age and city options to bot user
        :param uid: user id
        :return:
        """
        self.bot.messages.send(peer_id=uid, random_id=get_random_id(), keyboard=kb.create_age_city_keyboard(),
                               message=f'''У вас не указана или скрыта дата рождения и город проживания.
Отредактируйте личные данные для наиболее точного поиска или
выберите возраст, город для поиска, после чего нажмите search''')
        return True

    def send_age_keyboard(self, uid: int) -> bool:
        """
        Sends keyboard with age options to bot user
        :param uid: user id
        :return:
        """
        self.bot.messages.send(peer_id=uid, random_id=get_random_id(), keyboard=kb.create_age_keyboard(),
                               message=f'''У вас не указана или скрыта дата рождения.
Отредактируйте личные данные для наиболее точного поиска или
выберите возраст для поиска, после чего нажмите search''')
        return True

    def send_city_keyboard(self, uid: int) -> bool:
        """
        Sends keyboard with city options to bot user
        :param uid: user id
        :return:
        """
        self.bot.messages.send(peer_id=uid, random_id=get_random_id(), keyboard=kb.create_city_keyboard(),
                               message=f'''У вас не указан или скрыт город проживания.
Отредактируйте личные данные для наиболее точного поиска или
выберите город для поиска, после чего нажмите search''')
        return True

    def send_next_keyboard(self, uid: int) -> bool:
        """
        Sends next keyboard with buttons for likes, dislikes, favourites, blacklist and next person view
        :param uid: user id
        :return:
        """
        self.bot.messages.send(peer_id=uid, random_id=get_random_id(), keyboard=kb.create_next_keyboard(),
                               message=f'''
Вы можете лайкнуть любую из фотографий, отменить лайк, добавить пользователя в избранное, 
в черный список, посмотреть избранное или перейти к следующему пользователю''')
        return True

    def run_bot(self):
        """
        Creates database and/or tables and performs bot permanent work
        :return:
        """
        engine = self.db.preparation()
        test_create = self.db.create_table(engine)
        if not test_create:
            test_new_db = self.db.new_database()
            if test_new_db:
                self.db.create_table(engine)
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
