import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import WorksheetsBD
from data_store import engine


class BotInterface :
    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.bd = WorksheetsBD(engine)
        self.check_user = WorksheetsBD(engine)
        self.params = {}
        self.worksheets = []
        self.offset = 0
    def message_send(self, user_id: int, attachment: any, message: str) -> None:
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )
    # Обработка событий / получение сообщений
    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    # Логика для получения данных о пользователе
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(
                        event.user_id, f'Привет {self.params["name"]}')
                    if not self.params['city']:
                        self.message_send(event.user_id, 'Введите ваш город')
                        while True:
                            for event_ in self.longpoll.listen():
                                if (event_.type == VkEventType.MESSAGE_NEW and
                                    event_.to_me and event_.user_id == event.user_id):
                                    self.params = (self.vk_tools.get_profile_info
                                                   (event.user_id))
                                    self.params['city'] = event_.text
                                    break
                            if self.params['city']:
                                self.message_send(event.user_id,
                                                  'Принято, введите команду "поиск"')
                                break
                elif event.text.lower() == 'поиск':
                    # Логика для поиска анкет
                    self.message_send(
                        event.user_id, 'Начинаем поиск')
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.worksheets = (self.vk_tools.search_worksheet
                                           (self.params, self.offset))
                        worksheet = self.worksheets.pop()

                    # Проверка анкеты в базе данных в соотвествии с event.user_id
                    while self.bd.check_user(event.user_id, worksheet["id"]) is True:
                        if len(self.workseets):
                            worksheet = self.worksheets.pop()
                        else:
                            self.message_send(
                                event.user_id, 'Анкеты кончились!')

                    # Добавление анкеты в базу данных в соотвествии с event.user_id
                    if self.bd.check_user(event.user_id, worksheet["id"]) is False:
                        self.bd.add_user(event.user_id, worksheet["id"])

                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        self.offset += 50

                        self.message_send(
                        event.user_id,
                        f'имя: {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}',
                    )

                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'До новых встреч!')
                else:
                    self.message_send(
                        event.user_id, 'Неизвестная команда!')

if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    bot_interface.event_handler()