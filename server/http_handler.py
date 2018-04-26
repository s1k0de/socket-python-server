# Обработка http запросов

# ========= Imports ===========

import re
import sys
import time
import logger as log

# ========= Constants =========

HTTP_CHECKER = r'^\w+ /(?:[\w=.]+/?)* HTTP/(?:0\.9|(1\.1)|2)\r?\n(?:[A-Za-z\-]+: \S[\S ]*\r?\n)*\r?\n'
COOKIE_SEARCH = r'Cookie: (\w+=\w+;? ?)+'
FIRST_STRING_IN_HTTP = r'^(.+?)\r?\n'

# ========= Functions =========


def generate_html_page(body, encoding, changeable_strings):

    answer = []
    answer.append('<!DOCTYPE HTML>\r\n<html>\r\n<head>\r\n\t<meta charset="'+encoding+'">\r\n\t'
                  '<title>Ответ сервера</title>\r\n\t')

    if changeable_strings['green_color']:
        answer.append('<style>\r\nbody {\r\n\tbackground-color: green;\r\n}</style>')

    answer.append('</head>\r\n<body>\r\n\t<h1>')
    answer.append(body)
    answer.append('</h1>\r\n</body>\r\n</html>')

    return ''.join(answer)


def generate_http_answer(response_code, data, encoding, cookie=None):

    answer = []
    if response_code == 200:
        answer.append('HTTP/1.1 200 OK\r\n')
    elif response_code == 404:
        answer.append('HTTP/1.1 404 Not Found\r\n')
    elif response_code == 403:
        answer.append('HTTP/1.1 403 Forbidden')

    time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

    if cookie is not None:
        answer.append('Set-Cookie: ' + cookie +'\r\n')

    answer.append('Date: {}\r\n'.format(time_now))
    answer.append('Server: python-server\r\n')
    answer.append('Content-Type: text/html; charset=utf-8\r\n')
    answer.append('Content-Length: '+str(len(data.encode(encoding)))+'\r\n')
    answer.append('Connection: close\r\n\r\n')

    answer.append(data)
    print(''.join(answer).encode(encoding))
    return ''.join(answer).encode(encoding)


def process_response(connection, response_code, body, encoding, changeable_strings, cookie=None):

    answer = generate_html_page(body, encoding, changeable_strings)
    answer = generate_http_answer(response_code, answer, encoding, cookie)
    connection.send(answer)


def validate_http_request(data):

    if re.match(HTTP_CHECKER, data) is None:
        raise(ConnectionError("Проверка на http формат провалена"))
    else:
        print("Проверка на http формат пройдена")


def get_essential_data_from_request(data):
    print(data)
    essential_data = {'method': None, 'url': None, 'cookies': None}
    first_http_string_splitted = re.match(FIRST_STRING_IN_HTTP, data)[1].split(' ')

    essential_data['method'] = first_http_string_splitted[0]
    essential_data['url'] = first_http_string_splitted[1]

    cookie = re.search(COOKIE_SEARCH, data)
    if cookie is not None:
        essential_data['cookies'] = cookie.group(0).split('Cookie: ')[1]

    return essential_data



def process_request(connection, changeable_strings, encoding, data = None):


    if data is None:
        print("Данных нет")
        sys.exit()

    else:
        try:

            # Нужно ли логгировать полностью
            if_full_logger = changeable_strings.get('if_full_logger')

            # Получение метода, url, Cookie из запроса
            essential_data_from_request = get_essential_data_from_request(data)

            # Логгирование запроса
            log.write_full_log(data) if if_full_logger else log.write_brief_log(essential_data_from_request)

            # Проверка корректности http запроса
            validate_http_request(data)


        except ConnectionError as con_err:
            print(con_err)

            if_need_send_err = changeable_strings.get('if_need_send_error')


            exception = str(sys.exc_info())
            log.write_exception_to_error_log(exception)

            exception_answer_to_client = "Некорректный запрос\n" + (exception if if_need_send_err else "")
            process_response(connection, 403, exception_answer_to_client, encoding, changeable_strings)

            sys.exit()

        else:
            print(data)
            return essential_data_from_request