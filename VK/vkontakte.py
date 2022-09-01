import requests
import vk_api
import datetime
from Bot.vk_bot import get_id
from pprint import pprint
from string import punctuation as symbols


class Vkontakte:

    def __init__(self, token):
        self.token = token
        self.id = get_id(token)
        self.session = vk_api.VkApi(token=token)
        self.session_api = self.session.get_api()
        self.customer_portrait = None

    def get_customer_info(self):
        user_id = self.id
        response = self.session_api.users.get(user_ids=1913781, fields='city, sex, bdate, interests, personal, music,'
                                                                       'movies, books')
        customer_portrait = {}

        if 'city' in response[0]:
            customer_portrait['city'] = response[0]['city']['id']
        else:
            customer_portrait['city'] = None

        if 'sex' in response[0] and response[0]['sex'] in [1, 2]:
            customer_portrait['sex'] = response[0]['sex']
        else:
            customer_portrait['sex'] = None

        if 'bdate' in response[0] and len(response[0]['bdate'].split('.')) == 3:
            customer_birth_day = datetime.datetime.strptime(response[0]['bdate'], '%d.%m.%Y').date()
            customer_portrait['age'] = int((datetime.date.today() - customer_birth_day).days // 365.25)
        else:
            customer_portrait['age'] = None

        if 'interests' in response[0]:
            customer_interests = response[0]['interests'].lower()
            for item in customer_interests:
                if item in symbols or item == ' ' and item != ',':
                    customer_interests = customer_interests.replace(item, ',')
            customer_interests = customer_interests.split(',')
            temp_new_interests = []
            for item in customer_interests:
                if len(item) > 1:
                    temp_new_interests.append(item)
            customer_portrait['interests'] = temp_new_interests
        else:
            customer_portrait['interests'] = None

        if 'books' in response[0]:
            customer_books = response[0]['books'].lower()
            for item in customer_books:
                if item in symbols and item != ',':
                    customer_books = customer_books.replace(item, ',')
            customer_books = customer_books.split(',')
            temp_new_books = []
            for num in range(len(customer_books)):
                customer_books[num] = customer_books[num].strip()
                if len(customer_books[num]) > 1:
                    temp_new_books.append(customer_books[num])
            customer_portrait['books'] = temp_new_books
        else:
            customer_portrait['books'] = None

        if 'personal' in response[0] and 'alcohol' in response[0]['personal']:
            customer_portrait['alcohol'] = response[0]['personal']['alcohol']
        else:
            customer_portrait['alcohol'] = None

        if 'personal' in response[0] and 'inspired_by' in response[0]['personal']:
            customer_portrait['inspiration'] = response[0]['personal']['inspired_by'].lower().split(', ')
        else:
            customer_portrait['inspiration'] = None

        if 'personal' in response[0] and 'people_main' in response[0]['personal']:
            customer_portrait['people_main'] = response[0]['personal']['people_main']
        else:
            customer_portrait['people_main'] = None

        if 'personal' in response[0] and 'smoking' in response[0]['personal']:
            customer_portrait['smoking'] = response[0]['personal']['smoking']
        else:
            customer_portrait['smoking'] = None

        if 'personal' in response[0] and 'music' in response[0]['personal']:
            customer_portrait['smoking'] = response[0]['personal']['smoking']
        else:
            customer_portrait['smoking'] = None

        self.customer_portrait = customer_portrait
        return self.customer_portrait
