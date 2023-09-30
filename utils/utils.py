import json
import sys
import time
import argparse
from app_logger.logger import MyLogger
from pathlib import Path
import socket


def pop_null(dictionary: dict):
    return {k: v for k, v in dictionary.items() if v}


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_main_logger(name=__name__):
    return MyLogger(logger_name=name).get_logger()


# return get_result(items=None, message=func_name() + '_ERROR', error=get_error(func_name(), e.__str__(), '', dmsg('')))
def get_result(items, message: str, error, page: int = 1, page_size: int = 20, total: int = 0):
    temp = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": 0,
        "message": message,
        "items": [],
        "error": error
    }

    if items is not None:
        temp['count'] = len(items)
        temp['items'] = [json.loads(i.to_json()) for i in items if i is not None]
    else:
        temp['items'] = []
        temp['count'] = 0
    return temp


def get_error(_func, error, details, place):
    return {
        'function': _func,
        'message': error,
        'details': details,
        'location': place
    }


def dmsg(text_s):
    import inspect
    import os
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    filename = os.path.splitext(os.path.basename(caller_filename))[0]
    return filename + '.py:' + str(inspect.currentframe().f_back.f_lineno) + '| ' + text_s


def func_name():
    import inspect
    return inspect.stack()[1][3].upper()


def getPagination(page_nb: int, items_per_page: int):
    offset = 0
    try:
        if (page_nb is not None) and (items_per_page is not None):
            assert isinstance(page_nb, int), '"page_nb" should be of type int'
            assert isinstance(items_per_page, int), '"items_per_page" should be of type int'

            if page_nb > 0:
                offset = (page_nb - 1) * items_per_page
            else:
                offset = items_per_page
            return offset
        else:
            return offset
    except Exception as e:
        # logger.error("Either page_nb or items_per_page is Null " + e.__str__())
        return offset


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def get_mode():
    options = get_args()
    MODE = 'DEV'
    if options.mode:
        MODE = ('DEV' if options.mode.upper() == 'DEV' else 'PROD')
    else:
        MODE = 'DEV'
    return MODE


def wait_until(smth):
    aa = True
    while aa:
        if smth:
            aa = False
            time.sleep(1)
        else:
            continue


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', dest='mode', help='Set the running mode (dev/prod)')
    options = parser.parse_args()

    # Check for errors i.e if the user does not specify the target IP Address
    # Quit the program if the argument is missing
    # While quitting also display an error message
    if not options.mode:
        # Code to handle if interface is not specified
        parser.error("[-] Please specify the running mode (dev/prod), use --help for more info.")
    return options


def get_slash():
    if sys.platform == 'win32':
        return '\\'
    else:
        return '/'


def check_connection(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except Exception as e:
        return False
    finally:
        s.shutdown(socket.SHUT_RDWR)
        s.close()
