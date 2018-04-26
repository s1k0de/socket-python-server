# Работа с конфигом

# ========= Imports ===========
import json
import sys
import os
from logger import write_exception_to_error_log


# ========= Functions =========


def load_configuration_file(config):

    while True:

        try:
            configuration = get_config(config)

            return configuration

        except PermissionError as perm_err:
            print(perm_err)
            write_exception_to_error_log(str(sys.exc_info()))
            config = do_user_choice_config()

        except FileNotFoundError as file_err:
            print(file_err)
            write_exception_to_error_log(str(sys.exc_info()))
            config = do_user_choice_config()

        except BaseException as other_err:
            print("unhandle error")
            write_exception_to_error_log(str(sys.exc_info()))
            print(other_err)


def get_config(config_path=None):

    if os.path.exists(config_path):

        if os.access(config_path, os.R_OK):
            with open(config_path, 'r') as config_file:
                return json.load(config_file)
        else:
            raise(PermissionError("Unreadable config because of access"))

    else:
        raise(FileNotFoundError("Config has not been found"))


def do_user_choice_config():

    choice = input('Print "q" to break, "e" to edit path: ')

    while choice not in ('q','e'):
        choice = input('Print "q" to break, "e" to edit path: ')

    if choice == 'q':
        sys.exit()

    else:
        print('Enter path')
        return input()