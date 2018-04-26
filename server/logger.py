# Настройки логгера и сам логгер

# ========= Imports ===========

import logging
import logging.config
import sys
# ========= Functions =========


log_config = {
        "version":1,
        "handlers":{
            "file_log_handler":{
                "class":"logging.FileHandler",
                "formatter":"log_formater",
                "filename":"access.log"
            },
            "file_error_handler":{
                "class":"logging.FileHandler",
                "formatter":"log_formater",
                "filename":"error.log"
            }
        },
        "loggers":{
            "main_logger":{
                "handlers":["file_log_handler"],
                "level":"INFO"
            },
            "error_logger":{
                "handlers":["file_error_handler"],
                "level":"ERROR"
            }

        },
        "formatters":{
            "log_formater":{
                "format":"%(asctime)s: %(message)s"
            }
        }
    }

def get_logger(logger_name):

    try:

        logging.config.dictConfig(log_config)

        if logger_name == "main_logger" or logger_name == "error_logger":
            return logging.getLogger(logger_name)

        else:
            print("Такого логера нет")
            return None

    except BaseException as excpt:

        write_exception_to_error_log(str(sys.exc_info()))
        print("Config hasn't been loaded because of:\n" + str(excpt))


def decorate_environment_depending_on_choice(logger_name):

    def logger_environment_decorator(function_to_decorate):

        def return_function(*args, **kwargs):

            logger = get_logger(logger_name)

            if logger is not None:
                function_to_decorate(logger, *args, **kwargs)

        return return_function

    return logger_environment_decorator


@decorate_environment_depending_on_choice("main_logger")
def write_full_log(logger, data):
    logger.info("\n" + data)



@decorate_environment_depending_on_choice("main_logger")
def write_brief_log(logger, essential_info_dictionary):

    method_http = essential_info_dictionary.get('method')
    url_http = essential_info_dictionary.get('url')
    cookie = essential_info_dictionary.get('cookies')

    if method_http is None or url_http is None:

        if cookie is not None:
            logger.info(method_http + ' ' + url_http +'\r\nCookie: '+ cookie)

        else:
            logger.info(method_http + ' ' + url_http)
    else:
        logger.info('Request is incomplete. Method: ' + str(method_http) +
                        ' URL: ' + str(url_http) + ' Cookies: ' + str(cookie))


@decorate_environment_depending_on_choice("error_logger")
def write_exception_to_error_log(logger, exception_info):

    logger.exception("\n" + exception_info)


