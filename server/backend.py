# Бэкэнд

# ========= Imports ===========
import re
import sys
import calculations
from http_handler import process_response
from logger import write_exception_to_error_log
from cookie_handler import validate_cookie_and_add_if_correct
from cookie_handler import change_to_green_if_request_has_that_cookie
# ========= Constants =========

GET_POST_CHECKER = r'^(?:GET|POST)'
DIVIDING_REQUEST_CHECKER = r'^\/div\/.+?\/to\/.+$'
COOKIE_REQUEST_CHECKER = r'^/set_cookie/.+$'

# ========= Functions =========


def validate_get_post(data):

    if re.match(GET_POST_CHECKER, data) is None:

        return {'http_code': 403,
                'text_answer': 'Сервер обрабатывает только GET/POST запросы'}

    return None


def handle_change_log_post_request(http_method, http_url, changeable_strings):

    if http_method is not None and http_url is not None:

        if http_url == '/short_log/1':

            if http_method == 'POST':
                changeable_strings['if_full_logger'] = False
                print('Лог изменен на укороченный')

                return {'http_code': 200,
                        'text_answer': "Лог изменен на укороченный"}

            else:

                return {'http_code': 200, 'text_answer': "Ожидался POST"}

        elif http_url == '/short_log/0':

            if http_method == 'POST':

                changeable_strings['if_full_logger'] = True
                print('Лог изменен на длинный')

                return {'http_code': 200,
                        'text_answer': "Лог изменен на длинный"}

            else:

                return {'http_code': 200, 'text_answer': "Ожидался POST"}
    return None


def handle_change_error_post_request(http_method, http_url, changeable_strings):

    if http_method is not None and http_url is not None:

        if http_url == '/show_errors/1':

            if http_method == 'POST':

                changeable_strings['if_need_send_error'] = True
                print('Подробный ответ если ошибка включен')

                return {'http_code': 200,
                        'text_answer': "Подробный ответ если ошибка включен"}

            else:
                return {'http_code': 200,
                        'text_answer': "Ожидался POST"}

        elif http_url == '/show_errors/0':

            if http_method == 'POST':

                changeable_strings['if_need_send_error'] = False
                print('Краткий ответ если ошибка')

                return {'http_code': 200,
                        'text_answer': "Краткий ответ если ошибка"}

            else:
                return {'http_code': 200,
                        'text_answer': "Ожидался POST"}

    return None

def check_dividing_request_and_get_elements(http_url):

    if re.match(DIVIDING_REQUEST_CHECKER, http_url):
        http_url_splitted = http_url.split('/')
        element1 = http_url_splitted[2]
        element2 = http_url_splitted[4]
        return (element1, element2)
    else:
        return None



def handle_dividing_request(http_method, http_url):

    if http_method is not None and http_url is not None:

        elements = check_dividing_request_and_get_elements(http_url)

        if elements is not None and http_method == 'GET':

            answer = "Ответ:\n" + calculations.divide(elements[0], elements[1])
            return {'http_code': 200, 'text_answer': answer}

        elif elements is not None and http_method == 'POST':

            return {'http_code': 200, 'text_answer': "Ожидался GET"}

    return None


def check_cookie_request_and_get(http_url):

    if re.match(COOKIE_REQUEST_CHECKER, http_url):
        http_url_splitted = http_url.split('/')
        cookie = http_url_splitted[2]
        return cookie
    else:
        return None


def handle_cookie_request(connection, http_method, http_url, changeable_strings, encoding):

    if http_method is not None and http_url is not None:

        cookie = check_cookie_request_and_get(http_url)


        if cookie is not None and http_method == 'POST':

            try:
                answer_dict = validate_cookie_and_add_if_correct(cookie)
                return answer_dict

            except ValueError:

                if_need_send_err = changeable_strings.get('if_need_send_error')

                exception = str(sys.exc_info())
                write_exception_to_error_log(exception)

                exception_answer_to_client = "Неверные куки\n" + (
                    exception if if_need_send_err else "")

                process_response(connection, 403, exception_answer_to_client, encoding, changeable_strings)


        elif cookie is not None and http_method == 'GET':

            return {'http_code': 200, 'text_answer': "Ожидался POST"}

    return None


def run(essential_data_from_request, connection, encoding, changeable_strings, data):

    http_method = essential_data_from_request.get('method')
    http_url = essential_data_from_request.get('url')
    http_cookie = essential_data_from_request.get('cookies')

    # Если присутствуют куки изменения цвета
    change_to_green_if_request_has_that_cookie(http_cookie, changeable_strings)

    # Ответ если не GET/POST
    answer_dict = validate_get_post(data)
    if answer_dict is not None: return answer_dict

    # Ответ на запрос об изменении формата лога
    answer_dict = handle_change_log_post_request(http_method, http_url, changeable_strings)
    if answer_dict is not None: return answer_dict

    # Ответ на запрос об изменении формата ответа ошибок
    answer_dict = handle_change_error_post_request(http_method, http_url, changeable_strings)
    if answer_dict is not None: return answer_dict

    # Ответ на запрос деления чисел
    answer_dict = handle_dividing_request(http_method, http_url)
    if answer_dict is not None: return answer_dict

    # Ответ на запрос добавления куков
    answer_dict = handle_cookie_request(connection, http_method, http_url, changeable_strings, encoding)
    if answer_dict is not None: return answer_dict

    # Ответ если страница не найдена
    return {'http_code': 404, 'text_answer': 'Запрашиваемая страница не найдена'}