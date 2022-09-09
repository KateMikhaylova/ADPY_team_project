import re
import pymorphy2
from typing import Optional


class InterestsComparison:
    """
    Class for evaluation of users interests likeness with other users interests

    Methods: most methods returns number of points to be added to total index of likeness

    compare_age: compares users and other user ages
    compare_city: compares users and other users cities
    evaluate_relations: evaluates other users relation status (more points if he is single, less if he is in relations)
    compare_languages: evaluates how many mutual languages do both users know
    evaluate_intersection_in_3_grades: supplementary method to return some number of points based on quantity of
    mutual interests
    tokenize_to_words: splits text to words, normalizes them and deletes short ones and included in stop list
    tokenize_to_phrases: splits text into phrases on commas
    compare_interests_words: compares some users and other users interest based on words split
    compare_interests_phrases: compares some users and other users interest based on phrases split
    compare_main_things: compares main things in life or people for user and other user
    compare_smoking_alcohol: compares relation to smoking or alcohol for user and other user
    evaluate_mutual_friends: evaluates quantity of users and other users mutual friends
    evaluate_mutual_groups: evaluates quantity of users and other users mutual groups
    """

    @staticmethod
    def compare_age(user_age: Optional[int], found_user_age: int) -> int:
        """
        Compares users and other user ages
        :param user_age: users age int or None
        :param found_user_age: found user age
        :return: 13 in case of correspondence, otherwise 0
        """
        if user_age and user_age == found_user_age:
            return 13
        return 0

    @staticmethod
    def compare_city(user_city: Optional[int], found_user_city: int) -> int:
        """
        Compares users and other user cities
        :param user_city: users city id or None
        :param found_user_city: found user city id
        :return: 13 in case of correspondence, otherwise 0
        """
        if user_city and user_city == found_user_city:
            return 13
        return 0

    @staticmethod
    def evaluate_relations(found_user_relations: Optional[int]) -> int:
        """
        Evaluates other user relation status (more points if he is single, less if he is in relations)
        :param found_user_relations: found user relationship id
        :return: point based on status
        """
        if found_user_relations in [1, 6]:
            return 5
        elif found_user_relations == 0:
            return 2
        elif found_user_relations in [2, 3, 4, 7, 8]:
            return -5
        return 0

    @staticmethod
    def compare_languages(user_languages: Optional[str], found_user_languages: Optional[str]) -> int:
        """
        Evaluates how many mutual languages do both users know, more they now - more points returned
        :param user_languages: users languages
        :param found_user_languages:  found users languages
        :return: points based on match quantity
        """
        if user_languages and found_user_languages:
            user_langs = set(user_languages[1:-1].split(','))
            found_user_langs = set(found_user_languages[1:-1].split(','))
            lang_intersection = user_langs & found_user_langs
            if len(lang_intersection) == 2:
                return 1
            elif len(lang_intersection) == 3:
                return 2
            elif len(lang_intersection) == 4:
                return 3
            elif len(lang_intersection) > 4:
                return 4
        return 0

    @staticmethod
    def evaluate_intersection_in_3_grades(intersection: set, res1: int, res2: int, res3: int) -> int:
        """
        supplementary method to return some number of points based on quantity of mutual interests
        :param intersection: set of mutual interests
        :param res1: result 1 if len(set) is 1
        :param res2: result 2 if len(set) is from 2 to 7
        :param res3: result 3 if len(set) is 7 or more
        :return: resulting quantity of points
        """
        if len(intersection) == 1:
            return res1
        elif len(intersection) in range(2, 7):
            return res2
        elif len(intersection) > 6:
            return res3
        return 0

    @staticmethod
    def tokenize_to_words(interests_string: str, stop_words: list) -> set:
        """
        Splits text to words, normalizes them and deletes short ones and included in stop list
        :param interests_string: string with interests
        :param stop_words: list of common insignificant stop words to be deleted from interests
        :return: set with interest based words
        """
        split_pattern = re.compile(r'[а-яёa-z]+(?:-[а-яёa-z]+)?', re.I)
        interests_tokens = split_pattern.findall(interests_string.lower())
        morph = pymorphy2.MorphAnalyzer()
        normalized_tokens = []
        for token in interests_tokens:
            normalized_tokens.append(morph.parse(token)[0].normal_form)
        normalized_tokens = [token for token in normalized_tokens if token not in stop_words and len(token) > 2]
        result = set(normalized_tokens)
        return result

    @staticmethod
    def tokenize_to_phrases(interests_string: str) -> set:
        """
        splits text into phrases on commas
        :param interests_string: string with interests
        :return: set with interest based phrases
        """
        tokens = [i.strip() for i in interests_string.lower().split(',')]
        return set(tokens)

    def compare_interests_words(self, user_interests: Optional[str], found_user_interests: Optional[str],
                                stop_words: list, res1: int, res2: int, res3: int) -> int:
        """
        Compares some users and other users interest based on words split, used for activities, interests, inspiration
        :param user_interests: string with users interests
        :param found_user_interests: string with found users interests
        :param stop_words: list of common insignificant stop words to be deleted from interests
        :param res1: result1 based on intersection len
        :param res2: result2 based on intersection len
        :param res3: result3 based on intersection len
        :return: resulting quantity of points
        """
        if user_interests and found_user_interests:
            user_tokens = self.tokenize_to_words(user_interests, stop_words)
            found_user_tokens = self.tokenize_to_words(found_user_interests, stop_words)
            interests_intersection = user_tokens & found_user_tokens
            evaluated_intersection = self.evaluate_intersection_in_3_grades(interests_intersection, res1, res2, res3)
            return evaluated_intersection
        return 0

    def compare_interests_phrases(self, user_interests: Optional[str], found_user_interests: Optional[str],
                                  res1: int, res2: int, res3: int) -> int:
        """
        compares some users and other users interest based on phrases split, used for music, movies, tv, books, games
        :param user_interests: string with users interests
        :param found_user_interests: string with found users interests
        :param res1: result1 based on intersection len
        :param res2: result2 based on intersection len
        :param res3: result3 based on intersection len
        :return: resulting quantity of points
        """
        if user_interests and found_user_interests:
            user_tokens = self.tokenize_to_phrases(user_interests)
            found_user_tokens = self.tokenize_to_phrases(found_user_interests)
            interests_intersection = user_tokens & found_user_tokens
            evaluated_intersection = self.evaluate_intersection_in_3_grades(interests_intersection, res1, res2, res3)
            return evaluated_intersection
        return 0

    @staticmethod
    def compare_main_things(user_main: Optional[int], found_user_main: Optional[int]) -> int:
        """
        Compares main things in life or people or political or religion views for user and other user
        :param user_main: users parameter
        :param found_user_main: found users parameter
        :return:
        """
        if user_main and user_main == found_user_main:
            return 2
        return 0

    @staticmethod
    def compare_smoking_alcohol(user_addict: Optional[int], found_user_addict: Optional[int]) -> int:
        """
        compares relation to smoking or alcohol for user and other user
        :param user_addict: user relation id to addict
        :param found_user_addict: found user relation id to addict
        :return: resulting quantity of points
        """
        if user_addict and found_user_addict:
            if user_addict == found_user_addict:
                return 2
            elif abs(int(user_addict) - int(found_user_addict)) == 3:
                return -1
            elif abs(int(user_addict) - int(found_user_addict)) == 4:
                return -2
        return 0

    @staticmethod
    def evaluate_mutual_friends(mutual_quantity: int) -> int:
        """
        Evaluates quantity of users and other users mutual friends
        :param mutual_quantity: quantity of mutual users friends
        :return: resulting quantity of points
        """
        if mutual_quantity in range(1, 3):
            return 3
        elif mutual_quantity in range(3, 6):
            return 8
        elif mutual_quantity in range(6, 11):
            return 13
        elif mutual_quantity > 10:
            return 18
        return 0

    @staticmethod
    def evaluate_mutual_groups(mutual_groups: set) -> int:
        """
        evaluates quantity of users and other users mutual groups
        :param mutual_groups: set of mutual users groups
        :return: resulting quantity of points
        """
        if len(mutual_groups) == 1:
            return 1
        elif len(mutual_groups) == 2:
            return 2
        elif len(mutual_groups) > 2:
            return 3
        return 0
