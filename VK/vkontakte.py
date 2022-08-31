import requests
import vk_api
import datetime
from Bot.vk_bot import get_id
from pprint import pprint


class Vkontakte:

    def __init__(self, token):
        self.token = token
        self.id = get_id(token)
        self.session = vk_api.VkApi(token=token)
        self.session_api = self.session.get_api()

    def get_customer_info(self):
        user_id = self.id
        response = self.session_api.users.get(user_ids=user_id, fields='city, sex, bdate, interests, personal')
        customer_city = response[0]['city']['id']
        customer_sex = response[0]['sex']
        customer_birth_day = datetime.datetime.strptime(response[0]['bdate'], '%d.%m.%Y').date()
        customer_age = int((datetime.date.today() - customer_birth_day).days // 365.25)
        customer_interests = response[0]['interests']
        customer_alcohol = response[0]['personal']['alcohol']
        customer_inspiration = response[0]['personal']['inspired_by']
        customer_people_main = response[0]['personal']['people_main']
        customer_smoking = response[0]['personal']['smoking']
        cutomer_portrait = {
            'customer_city': customer_city,
            'customer_sex': customer_sex,
            'customer_age': customer_age,
            'customer_interests': customer_interests,
            'customer_alcohol': customer_alcohol,
            'customer_inspiration': customer_inspiration,
            'customer_people_main': customer_people_main,
            'customer_smoking': customer_smoking
        }
        return pprint(cutomer_portrait)
