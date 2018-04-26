# Работа с куками

# ========= Imports ===========

import re
from http_handler import process_response

# ========= Constants =========

COOKIE_CHECKER = r'^\w+=\w+$'

# ========= Functions =========

def validate_cookie_and_add_if_correct(cookie):

    if re.match(COOKIE_CHECKER, cookie) is not None:

        return {'http_code': 200, 'text_answer': 'Куки успешно добавлены', 'cookie': cookie}

    else:

        raise(ValueError('Неверный формат куков'))


def change_to_green_if_request_has_that_cookie(http_cookie, changeable_strings):

    if http_cookie is not None:
        cookie_color = r'bg_color=green'
        color_exists = re.search(cookie_color, http_cookie)

        if color_exists is not None:
            changeable_strings['green_color'] = True
