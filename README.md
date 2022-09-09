<h1 align="center">VKinder</h1>

![logo](https://i.ibb.co/FXRJpCM/Vkinder.png)

<h2 align="center">Описание</h2>

VKinder - это бот для VKontakte, написанный на языке Python, который подбирает подходящих пользователю партнеров в сети Vkontakte, показывает пользователю их, а также три самые популярные фотографии из их профиля и фотографий, где они отмечены, и позволяет производить ряд действий: лайкать и удалять лайки с фотографий потенциальных партнеров, добавлять их в список избранных, просматривать список избранных и добавлять в черный список.

Бот написан на языке Python 3 и использует несколько дополнительных модулей, таких как vk_api, requests, nltk, regex, pymorphy2, psycopg2 и sqlalchemy и взаимодействует с PostgreSQL для создания собственной базы данных. VKinder написан в ООП стиле группой студентов в рамках командного курсового проекта

<h2 align="center">Клонирование репозитория и подготовка к запуску</h2>

Выполните в консоли:

```
git clone https://github.com/KateMikhaylova/ADPY_team_project.git
pip install -r requirements.txt
```

<h2 align="center">Авторизация</h2>

Авторизационная информация хранится в файле settings.ini в следующем виде:

```
[VK]
token = 
bot_token = 
[DB]
username = 
password = 
```

**Инструкция по получению авторизационных данных и заполнению файла settings.ini.**

1. Инструкция по получению токена пользователя https://docs.google.com/document/d/1_xt16CMeaEir-tWLbUFyleZl6woEdJt-7eyva1coT3w/edit
Обратите внимание, для осуществления некоторых действий токен должен иметь права доступа 'wall'

2. Инструкция по получению токена сообщества (бота) https://github.com/netology-code/adpy-team-diplom/blob/main/group_settings.md

3. В поля username и password добавьте ваш логин и пароль от PostgreSQL

Пример заполнения файла settings.ini
```
[VK]
token = vk1.a.qwmkArb16JMhvxb19-kCwzR03Ad6Quq-peDzqMe21ERatpqVnsXWg3_qGtH55vC0WQ3c51x8OMeO0CwFc7ohDRoF624BTzCMBBSxBehwGBrBxtnjUSmnVQBNfowGoxnp4AkiVDvJpdkYIyo0aOfYdKFP0CeJ7w3CX0pk2wtQ0ZEoxtMBMSk0N
bot_token = a0b53a73b5d8442b57079745da61316893afnbb0931eb89b47c384fc5ea0ead7cc9ea8
[DB]
username = postgres
password = postgres
```

Вы можете открыть для заполнения файл settings.ini в любом редакторе (например, в Блокноте).

<h2 align="center">Запуск</h2>

Чтобы запустить бота, выполните в консоли:

```
python main.py
```

При первом запуске будет создана база данных VKinder и таблицы в ней. Впоследствии при каждом запуске таблицы будут удаляться и создаваться заново. Это можно отключить, закомментировав соответствующую часть метода run_bot в файле vk_bot.py 

После запуска, можно перейти в сообщения сообщества и начать диалог с ботом. Доступные команды будет предложено вводить с помощью удобных кнопок.

Обратите внимание, что в силу специфики работы поиска VKontakte, результаты поиска могут быть очень сильно искажены в сторону параметров держателя токена пользователя. То есть при поиске пары для москвича под токеном санкт-петербуржца, в результаты все равно будут попадать потенциальные партнеры из Санкт-Петербурга. Если это станет проблемой для пользователя из малонаселенного города (не будет результатов поиска), необходимо увеличить выборку count в строке 134 файла vkontakte.py, что, разумеется, приведет к замедлению поиска ботом.

В боте также реализовано получение большого количества партнеров (>1000) с помощью VkRequestPool, однако запуск не рекомендуется в связи с очень большой продолжительностью работы поиска и записи найденных партнеров.

Также в рамках реализованного функционала лайки ставятся и удаляются от лица держателя токена пользователя, а не пользователя бота, если они не совпадают.

В скрипте реализован метод сортировки потенциальных партнеров по степени схожести с пользователем бота. В целях сортировки учитывается семейное положение, и сравниваются возрасты, города проживания, языки, деательность, интересы, источники вдохновения, предпочтения в музыке, фильмах, телешоу, книгах, играх, политические и религиозные взгляды, главное в жизни и людях, отношение к курению и алкоголю, общие друзья и группы. На основании этих факторов расчитывается оценка для каждого подобранного партнера, а потом партнеры сортируются, причем первыми будут выводиться партнеры, имеющие больший индекс совпадения с пользователем бота. В случае необходимости можно вручную изменить веса тех или иных параметров. Оценка общих групп и друзей вызывает несколько обращений по API для каждого из потенциальных партнеров, что существенно замедляет процедуру поиска. При необходимости эту опцию можно закомментировать. 

