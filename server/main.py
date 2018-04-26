# Серверная логика

# ========= Imports ===========

import socket
import config_handler as conf
import sys
from logger import write_exception_to_error_log
from http_handler import process_request
from http_handler import process_response
from backend import run

# ========= Constants =========

CONFIG = 'config.json'

# ========= Global variables =========

changeable_strings = {
    'if_full_logger': True,
    'if_need_send_error': False,
    'green_color': False
}

# ========= Functions =========


def listen(socket, pack_size, encoding):

    socket.listen()
    print("Listening...")

    try:

        while True:
            conn, addr = socket.accept()
            print("Have got client:")
            print("Address: {}:{}".format(addr[0], addr[1]))

            handle_client_data(conn, pack_size, encoding)

    except BaseException as bs_err:

        write_exception_to_error_log(str(sys.exc_info()))
        print("В процессе установки соединения произошла ошибка")
        print(bs_err)

    finally:

        socket.close()


def handle_client_data(connection, pack_size, encoding):

    udata = ""

    with connection:

        try:
            while True:

                    data = connection.recv(pack_size)

                    if not data:
                        break
                    else:
                        udata += data.decode()
                        break

# Проверка и обработка http запроса, возращает
# необходимые данные для дальнеших действий
            necessary_data = process_request(connection, changeable_strings,
                                             encoding, udata)

# Бэкэнд код, возвращает необходимые данные, которые нужно отправить
            answer_to_client = run(necessary_data, connection, encoding,
                                   changeable_strings, udata)

# Распаковка необходимых данных
            http_code = answer_to_client.get('http_code')
            text_answer = answer_to_client.get('text_answer')
            cookie = answer_to_client.get('cookie')

# Отправка данных
            process_response(connection, http_code, text_answer,
                             encoding, changeable_strings, cookie)

        except UnicodeError:

            print("Ошибка декодирования данных")
            if_need_send_err = changeable_strings.get('if_need_send_error')

            excption = str(sys.exc_info())
            write_exception_to_error_log(excption)

            exception_answer_to_client = "Ошибка декодирования данных\n" + \
                                         (excption if if_need_send_err else '')

            process_response(connection, 403, exception_answer_to_client,
                             encoding, changeable_strings)

            connection.close()

        except BaseException as bs_err:

            print("При соединении произошли ошибки")
            print(bs_err)
            if_need_send_err = changeable_strings.get('if_need_send_error')

            excption = str(sys.exc_info())
            write_exception_to_error_log(excption)

            exception_answer_to_client = "При соединении произошли ошибки\n" +\
                                         (excption if if_need_send_err else "")

            process_response(connection, 403, exception_answer_to_client,
                             encoding, changeable_strings)


def start():
    config = conf.load_configuration_file(CONFIG)
    ip = config.get('ip')
    port = int(config.get('port'))
    package_size = int(config.get('bytes_per_iter'))
    encoding = config.get('encoding')

    try:
        print("Trying to start server with {}:{}".format(ip, port))

        sock = socket.socket()
        sock.bind((ip, port))

        print("Successfully started with {}:{}".format(ip, port))

    except BaseException as e_err:
        print("Couldn't bind port with {}:{}".format(ip, port))
        write_exception_to_error_log(str(sys.exc_info()))
        print(e_err)
        sys.exit()

    else:
        listen(sock, package_size, encoding)

# Запуск


start()
