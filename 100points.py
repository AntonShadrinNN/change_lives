from bs4 import BeautifulSoup
import requests
import fake_useragent


class PreProcessorMixIn:
    """
         Предобработка данных их текстового файла в нужный для парсера формат
         Данные ожидаются в виде: Имя Фамилия  Жизни на сайте
         Имя и фамилия отделены от жизней символом \t
         Функция pre_process() принимает относительный путь к файлу, возвращает словарь
         Ключ - имя ученика, значение - количество жизней в журнале
    """
    @staticmethod
    def pre_process(file_name):
        pre_processed = dict()
        with open(file_name, encoding='utf-8') as file:
            data = file.readlines()

        for record in data:
            split_record = record.split('\t')
            name = split_record[0]
            pre_processed[name] = int(split_record[1])

        return pre_processed


class ParsePoints(PreProcessorMixIn):
    """
        Статические переменные:
            LINK - путь к API для авторизации
            INPUT_LIVES - относительный путь к файлу с жизнями из журнала
        Публичные функции:
            auth(email, password)
            parse()
            change_lives()
        Приватные функции:
            __parse_life()
            __normalize_lives(name, diff)
    """
    LINK = 'https://api.100points.ru/login'
    INPUT_LIVES = 'example.txt'

    def __init__(self):
        self.data = None
        self.session = requests.Session()
        self.__students = dict()
        self.user = fake_useragent.UserAgent().random

    def __normalize_lives(self, name, diff):
        """
            GET-запрос к API по id ученика с именем name для изменения баланса жизней
            Если diff > 0, то жизни нужно уменьшить, иначе увеличить
        """
        base_link = 'https://api.100points.ru/course_progress'
        ident = self.__students[name]['id']
        if diff > 0:
            while diff > 0:
                self.session.get(f'{base_link}/remove_live/36/{ident}')
                diff -= 1
        else:
            while diff < 0:
                self.session.get(f'{base_link}/add_live/36/{ident}')
                diff += 1

    def __parse_life(self):
        """
            Парсинг индивидуальной карточки учащегося с целью получения количества жизней на сайте
            Если "курс не начат", в значении жизней будет "Неизвестно"
        """
        for student in self.__students:
            response = self.session.get(self.__students[student]['url']).text
            parse_card = BeautifulSoup(response, 'lxml')
            name = parse_card.find('input', id='name').get('value')
            try:
                lives = parse_card.find('tr', class_='odd').find_all('td')[1].find('b').text.strip()
            except AttributeError:
                lives = 'Неизвестно'
            self.__students[name]['lives'] = lives

    def auth(self, email: str, password: str):
        """
            Авторизация на сайте при помощи подделки user-agent
            email и password являются строковыми параметрами
            Авторизация работает посредством сессии, поэтому перелогин не требуется
        """
        self.data = {'email': email,
                     'password': password}
        header = {'user-agent': self.user,
                  }
        self.session.post(ParsePoints.LINK, headers=header, data=self.data)

    def parse(self):
        """
            Основная функция получения данных об учащихся.
            Занесение данных всех учеников в словарь __students (id, ссылка для изменения, число жизней на сайте)
        """
        n = 1
        is_next_page = None

        while not is_next_page:
            response = self.session.get(f'https://api.100points.ru/user/index?page={n}')
            soup = BeautifulSoup(response.text, 'lxml')
            is_next_page = soup.find('li', id='example2_next').find('a').get('disabled')
            students = soup.find_all('tr', class_='odd')

            for i in range(len(students)):
                student = students.pop()
                name = student.find('a').text.strip()
                ident = int(student.find('td').text.strip())
                url = student.find('a').get('href')
                self.__students[name] = {'id': ident,
                                         'url': url}
            self.__parse_life()
            n += 1

    def change_lives(self):
        """
            Изменение жизней на сайте после сравнение значений из входного файла INPUT_LIVES с данным на сайте
            ИМЕНА УЧЕНИКОВ СТРОГО КАК НА САЙТЕ
        """
        data = self.pre_process(ParsePoints.INPUT_LIVES)
        print('Жизни изменены у:')
        for name in data:
            j_lives = data[name]
            s_lives = int(self.__students[name]['lives']) if self.__students[name]['lives'].isdigit() else None
            if s_lives is not None and j_lives != s_lives:
                diff = s_lives - j_lives
                self.__normalize_lives(name, diff)
                print(f'{name} теперь имеет {data[name]} жизней на сайте')


if __name__ == '__main__':
    session = ParsePoints()
    session.auth('example@example.com', 'example')
    session.parse()
    session.change_lives()