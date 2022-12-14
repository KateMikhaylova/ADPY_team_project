import vk_api
import requests
import datetime
from time import sleep


class VkontakteApi:
    """
    Class for interaction with Vkontakte API

    Attributes:
        user_token: str
                    users token used to get access to VkApi methods
        vk_session: class vk_api.vk_api.VkApi object
                    used to create vk attribute and to create VkRequestsPool object
        vk:         class vk_api.vk_api.VkApiMethod object
                    used to call VkApi methods

    Methods:
        get_user_info: gets info on VK user based in his id
        determinate_search_parameters: staticmethod, returns parameters for search (same age, city and opposite gender)
        filter_search_results: clears list of users info from users with closed profiles, without full birthdate and
        city indication
        search_people: gets list of VK users with open profiles based on indicated gender, city and age
        search_many_people: same as previous, but uses Vk Request Pool to get more search results
        get_3_photos: gets users profile and marked photos and takes three most liked of them
        prepare_found_users_info: prepares list of users dicts from API to necessary for database form
        like_photo: likes requested photo by token user
        delete_like_photo: deletes likes from requested photo by token user
        check_like_presence: checks whether photo is liked by token user or not
        get_mutual_friends: checks how many mutual friends  do users have
        get_groups: get set of users groups ids
    """

    def __init__(self, user_token: str) -> None:
        """
        Sets attributes user_token, vk_session and vk for object VkontakteApi
        :param user_token: str, users token with necessary rights ('wall' rights are obligatory)
        """
        self.user_token = user_token
        self.vk_session = vk_api.VkApi(token=self.user_token)
        self.vk = self.vk_session.get_api()

    def get_user_info(self, user_id: int) -> dict:
        """
        Gets info on VK user based in his id
        :param user_id: integer, unique users id
        :return: dict with user information
        """
        response = self.vk.users.get(user_ids=user_id, fields='''activities, bdate, books, city, games, 
                                     interests, movies, music, personal, relation, sex, tv''')

        if 'city' in response[0]:
            user_city_id = response[0]['city']['id']
            user_city_title = response[0]['city']['title']
        else:
            user_city_id = None
            user_city_title = None

        user_gender_id = response[0]['sex']
        if user_gender_id == 1:
            user_gender_title = '??????????????'
        else:
            user_gender_title = '??????????????'

        if 'bdate' in response[0] and len(response[0]['bdate'].split('.')) > 2:
            birth_day = response[0]['bdate'].split('.')
            user_birthday_date = datetime.date(int(birth_day[2]), int(birth_day[1]), int(birth_day[0]))
            user_age = int((datetime.date.today() - user_birthday_date).days//365.25)
        else:
            user_age = None

        user = {'last_name': response[0]['last_name'],
                'first_name': response[0]['first_name'],
                'id': response[0]['id'],
                'city': user_city_id,
                'city_title': user_city_title,
                'gender': user_gender_id,
                'gender_title': user_gender_title,
                'age': user_age,
                'middle_name': None,
                'activities': response[0].get('activities'),
                'books': response[0].get('books'),
                'games': response[0].get('games'),
                'interests': response[0].get('interests'),
                'movies': response[0].get('movies'),
                'music': response[0].get('music'),
                'personal': response[0].get('personal'),
                'relation': response[0].get('relation'),
                'tv': response[0].get('tv')
                }

        return user

    @staticmethod
    def determinate_search_parameters(user_information: dict) -> list:
        """
        Staticmethod, returns parameters for search (same age and city and opposite gender)
        :param user_information: dict with user information
        :return: list with search parameters: city id, gender id, age
        """

        search_city_id = user_information['city']

        if user_information['gender'] == 1:
            search_gender_id = 2
        else:
            search_gender_id = 1

        search_age = user_information['age']

        return [search_city_id, search_gender_id, search_age]

    @staticmethod
    def filter_search_results(found_users: list) -> list:
        """
        Clears list of users info from users with closed profiles, without full birthdate and city indication
        :param found_users: list of found users
        :return: filtered list of found users
        """
        return [person for person in found_users if not person['is_closed']
                                                    and 'city' in person
                                                    and 'bdate' in person and len(person['bdate'].split('.')) > 2]

    def search_people(self, city_id: int, sex: int, age: int) -> list:
        """
        Gets list of VK users with open profiles based on indicated gender, city and age
        :param city_id: integer, city id used in VK database
        :param sex: integer, gender id used in VK database
        :param age: integer, age of searched users
        :return: list of dicts with users information
        """

        response = self.vk.users.search(city=city_id, sex=sex, age_from=age, age_to=age, count=100,
                                        fields='''activities, bdate, books, city, games, interests, movies, 
                                        music, personal, relation, sex, tv''')

        return self.filter_search_results(response['items'])

    def search_many_people(self, city_id: int, sex: int, age: int) -> list:
        """
        Gets list of VK users with open profiles based on indicated gender, city and age. Uses Vk Request Pool to get
        more search results
        :param city_id: integer, city id used in VK database
        :param sex: integer, gender id used in VK database
        :param age: integer, age of searched users
        :return: list of dicts with users information
        """
        people = {}

        with vk_api.VkRequestsPool(self.vk_session) as pool:
            for birth_month in range(1, 13):
                # second for (days from 1 to 31) may be added for more results (search and proceed will be very long)
                people[birth_month] = pool.method('users.search',
                                                  {'age_from': age,
                                                   'birth_month': birth_month,
                                                   'count': 1000, 'sex': sex, 'city': city_id,
                                                   'age_to': age,
                                                   'fields': '''activities, bdate, books, city, games, interests,
                                                   movies, music, personal, relation, sex, tv'''})

        people_list = []
        for value in people.values():
            people_list.extend(value.result['items'])

        return self.filter_search_results(people_list)

    def get_3_photos(self, user_id: int) -> list:
        """
        Gets users profile and marked photos and takes three most liked of them
        :param user_id: users id to search photos
        :return: list with photo ids
        """
        response = self.vk.photos.get(owner_id=user_id, album_id='profile', extended=1)

        photo_dict = {}
        for photo in response['items']:
            photo_dict[f"{photo['owner_id']}_{photo['id']}"] = photo['likes']['count']

        # Get photos where user is marked

        # Query via vk_api demands try except statement in case access to marked photos is denied
        # In request library this case can be proceeded without try except statement
        # try:
        #     response = self.vk.photos.getUserPhotos(user_id=user_id, extended=1)
        # except vk_api.exceptions.ApiError:
        #     response = {}
        # if response:
        #     for photo in response['items']:
        #         photo_dict[f"{photo['owner_id']}_{photo['id']}"] = photo['likes']['count']

        URL = 'https://api.vk.com/method/photos.getUserPhotos'
        params = {'user_id': user_id, 'extended': '1', 'access_token': self.user_token, 'v': '5.131'}
        response = requests.get(URL, params=params).json()

        if 'error' in response:
            pass
        else:
            for photo in response['response']['items']:
                photo_dict[f"{photo['owner_id']}_{photo['id']}"] = photo['likes']['count']

        three_photos = sorted(photo_dict.items(), key=lambda x: x[1], reverse=True)[0:3]

        return [photo[0] for photo in three_photos]

    def prepare_found_users_info(self, found_users: list) -> list:
        """
        Prepares list of users dicts from API to necessary for database form
        :param found_users: list of dicts with found users info
        :return: list of dicts with prepared users info
        """
        result = []
        for person in found_users:

            photos = self.get_3_photos(person['id'])
            sleep(0.34)

            if len(photos) < 3:
                continue

            user_gender_id = person['sex']
            if user_gender_id == 1:
                user_gender_title = '??????????????'
            else:
                user_gender_title = '??????????????'

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
                           'age': user_age, 'photos': photos,
                           'middle_name': None,
                           'activities': person.get('activities'),
                           'books': person.get('books'),
                           'games': person.get('games'),
                           'interests': person.get('interests'),
                           'movies': person.get('movies'),
                           'music': person.get('music'),
                           'personal': person.get('personal'),
                           'relation': person.get('relation'),
                           'tv': person.get('tv')
                           }

            result.append(person_info)

        return result

    def like_photo(self, owner_id: int, photo_id: int) -> bool:
        """
        Likes requested photo by token user
        :param owner_id: id of user who published photo
        (in case if marked photo it may not be the same as searched user id)
        :param photo_id: id of photo
        :return: bool, True if method returned information on likes quantity, otherwise False
        """
        try:
            response = self.vk.likes.add(type='photo', owner_id=owner_id, item_id=photo_id)
            return 'likes' in response
        except vk_api.exceptions.ApiError:
            return False

    def delete_like_photo(self, owner_id: int, photo_id: int) -> bool:
        """
        Deletes likes from requested photo by token user
        :param owner_id: id of user who published photo
        (in case if marked photo it may not be the same as searched user id)
        :param photo_id: id of photo
        :return: bool, True if method returned information on likes quantity, otherwise False
        """

        response = self.vk.likes.delete(type='photo', owner_id=owner_id, item_id=photo_id)
        return 'likes' in response

    def check_like_presence(self, photo: str) -> bool:
        """
        Check whether photo liked by token user or not
        :param photo: photo id
        :return: True if like present, otherwise false
        """
        try:
            response = self.vk.photos.getById(photos=photo, extended=1)
            return bool(response[0]['likes']['user_likes'])
        except vk_api.exceptions.ApiError:
            return False

    def get_mutual_friends(self, uid: int, other_uid: int) -> int:
        """
        Returns how many mutual friends two users have
        :param uid: first user id
        :param other_uid: second user id
        :return: quantity of mutual friends
        """
        friends = self.vk.friends.getMutual(source_uid=uid, target_uid=other_uid)
        return len(friends)

    def get_groups(self, uid: int) -> set:
        """
        Returns set of users groups ids
        :param uid: user id
        :return: set of group ids
        """
        groups = self.vk.groups.get(user_id=uid, count=1000)
        return set(groups['items'])
