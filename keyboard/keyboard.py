from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_favourite_start_keyboard() -> dict:
    """
    Creates vk keyboard with favourite and start buttons
    :return: keyboard json
    """
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('посмотреть избранных', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('start', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def create_empty_keyboard() -> dict:
    """
    Creates empty vk keyboard
    :return: keyboard json
    """
    return VkKeyboard.get_empty_keyboard()


def create_search_keyboard() -> dict:
    """
    Creates vk keyboard with search button
    :return: keyboard json
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('search', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def create_start_keyboard() -> dict:
    """
    Creates vk keyboard with start button
    :return: keyboard json
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('start', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def create_age_city_keyboard() -> dict:
    """
    Creates vk keyboard with age, city and search buttons
    :return: keyboard json
    """
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
    return keyboard.get_keyboard()


def create_age_keyboard() -> dict:
    """
    Creates vk keyboard with age and search buttons
    :return: keyboard json
    """
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
    return keyboard.get_keyboard()


def create_city_keyboard() -> dict:
    """
    Creates vk keyboard with city and search buttons
    :return: keyboard json
    """
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
    return keyboard.get_keyboard()


def create_next_keyboard() -> dict:
    """
    Creates vk keyboard with likes, favourites, blacklist and next buttons
    :return: keyboard json
    """
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
    return keyboard.get_keyboard()
